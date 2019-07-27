# -*- coding: utf-8 -*-
from collections import defaultdict
from datetime import datetime, timedelta
import json
import logging
from hashlib import md5
from requests import ConnectionError
import time
from xml.etree import cElementTree as ET
import uuid
from odoo import api, models, fields, _, registry, SUPERUSER_ID
from odoo.http import request
from odoo.exceptions import UserError, Warning, ValidationError
from odoo.addons.bus.models.bus import dispatch
try:
    import humanize
    HUMANIZE = True
except ImportError:
    HUMANIZE = False
from .utils import generate_password, slugify


logger = logging.getLogger(__name__)

POLL_TIMEOUT = 10


def etree_to_dict(t):
    """
    Helper function to parse Asterisk mxml responses over AJAM.
    """
    d = {t.tag: {} if t.attrib else None}
    children = list(t)
    if children:
        dd = defaultdict(list)
        for dc in map(etree_to_dict, children):
            for k, v in dc.items():
                dd[k].append(v)
        d = {t.tag: {k:v[0] if len(v) == 1 else v for k, v in dd.items()}}
    if t.attrib:
        d[t.tag].update(('@' + k, v) for k, v in t.attrib.items())
    if t.text:
        text = t.text.strip()
        if children or t.attrib:
            if text:
              d[t.tag]['#text'] = text
        else:
            d[t.tag] = text
    return d



class AsteriskServer(models.Model):
    _name = 'asterisk.server'
    _description = "Asterisk Server"

    name = fields.Char(required=True)
    uid = fields.Char(string='UID', required=True,
                      default=lambda self: self.generate_uid())
    note = fields.Text()
    conf_files = fields.One2many(comodel_name='asterisk.conf',
                                 inverse_name='server')
    sync_date = fields.Datetime(readonly=True)
    sync_uid = fields.Many2one('res.users', readonly=True, string='Sync by')
    cli_url = fields.Char(string='Asterisk CLI URL')
    cli_area = fields.Text(compute='_get_cli_area', inverse='_set_cli_area')
    last_ping = fields.Datetime(readonly=True)
    last_ping_human = fields.Char(compute='_get_last_ping_human',
                                  string='Last ping')
    is_interconnected = fields.Boolean(string=_('Interconnected'))
    hostname = fields.Char()
    login = fields.Many2one('res.users', readonly=True, ondelete='restrict')
    login_username = fields.Char(related='login.login', string=_('Login'))
    login_password = fields.Char(related='login.password',
                                 string='Password')
    state = fields.Selection([('online', 'Online'), ('offline', 'Offline')])
    language = fields.Char(default='en')
    ip_security_enabled = fields.Boolean(string=_('IP security'), default=True)
    filter_ports = fields.Char(default='5060,4569',
                    help=_('Comma separated ports to filter, e.g. 5060,5061'))
    ip_ban_seconds = fields.Integer(string=_('IP ban seconds'), default=600)


    _sql_constraints = [
        ('uid_unique', 'UNIQUE(uid)', 'This UID is already used.'),
    ]


    @api.model
    def create(self, vals):
        agent_group = self.env.ref('asterisk_base.group_asterisk_base_agent')
        login = self.env['res.users'].sudo().create({
            'name': vals['name'],
            'login': vals['login_username'],
            'password': vals['login_password'],
            'groups_id': [(6, 0, [agent_group.id])]
        })
        server = super(AsteriskServer, self).create(vals)
        server.login = login
        if server.is_interconnected:
            self.build_conf()
        return server


    @api.multi
    def write(self, vals):
        res = super(AsteriskServer, self).write(vals)
        if res:
            for rec in self:
                # Check is server is added to interconnection
                if 'is_interconnected' in vals or 'hostname' in vals:
                    self.build_conf()
        return res


    @api.multi
    def unlink(self):
        for rec in self:
            user = rec.login
            partner = user.partner_id
            super(AsteriskServer, rec).unlink()
            user.unlink()
            partner.unlink()
        self.build_conf()
        return True


    @api.onchange('hostname')
    def _set_cli_url(self):
        if not self.cli_url and self.hostname:
            self.cli_url = 'ws://{}:8010/websocket'.format(self.hostname)


    @api.constrains('uid')
    def _check_uid(self):
        if ' ' in self.uid:
            raise ValidationError(_('Server UID cannot contain white spaces!'))



    @api.constrains('is_interconnected')
    def _check_hostname(self):
        if self.is_interconnected and not self.hostname:
            raise ValidationError(_('Server must have hostname set!'))



    @api.multi
    def _get_last_ping_human(self):
        for rec in self:
            if HUMANIZE:
                to_translate = self.env.context.get('lang', 'en_US')
                if to_translate != 'en_US':
                    humanize.i18n.activate(to_translate)
                rec.last_ping_human = humanize.naturaltime(
                                    fields.Datetime.from_string(rec.last_ping))
            else:
                rec.last_ping_human = rec.last_ping


    @api.onchange('name')
    def _set_login(self):
        if self.name and not self.login:
            self.login_username = 'agent_{}'.format(slugify(self.name))
            self.login_password = generate_password()


    def generate_uid(self):
        return '{}'.format(uuid.uuid4().hex)


    @api.multi
    def _get_cli_area(self):
        """
        We use cli_url to set CLI URL and reflect this in cli_area to take it from JS.
        """
        for rec in self:
            rec.cli_area = rec.cli_url


    @api.multi
    def _set_cli_area(self):
        """
        STUB as I don't know yet how to extend WEB widgets and get rid of this shit.
        """
        pass


    @api.multi
    def _compute_cli_url(self):
        for self in self:
            self.cli_url = ''


    def build_conf(self):
        # Create conf file with peers for every other intercoonected server
        servers = self.search([('is_interconnected', '=', True)])
        protocol = self.env['res.config.settings']._get_asterisk_param(
                                            'interconnection_protocol', 'iax')
        if not servers or len(servers) == 1:
            # Remove all server peers conf
            conf = self.env['asterisk.conf'].search([
                    ('name', '=', '{}_odoo_servers.conf'.format(protocol))])
            conf.unlink()
            return
        # We have servers, create config files.
        for current_server in servers:
            current_server_secret = md5.md5('{}-{}'.format(
                                            current_server.id,
                                            current_server.uid)).hexdigest()
            conf_data = u''
            other_servers = self.search([
                                        ('is_interconnected', '=', True),
                                        ('id', '!=', current_server.id)])
            for server in other_servers:
                server_secret = md5.md5('{}-{}'.format(
                                        server.id, server.uid)).hexdigest()
                conf_data += self.env['ir.qweb'].render(
                            'asterisk_base.server_{}_peer'.format(protocol),
                            {'server': server,
                             'current_server': current_server,
                             'server_secret': server_secret,
                             'current_server_secret': current_server_secret,
                             }).decode('latin-1')
            conf = self.env['asterisk.conf'].get_or_create(
                                    current_server.id,
                                    '{}_odoo_servers.conf'.format(protocol))
            conf.write({'content': conf_data})
            conf.include_from('{}.conf'.format(protocol))


    @api.multi
    def bus_send(self, message):
        self.ensure_one()
        channel = 'asterisk_agent/{}'.format(self.uid)
        self.env['bus.bus'].sendone(channel, json.dumps(message))


    @api.model
    def rpc_bus_send(self, channel, message):
        # Override sendone for agent as original method does not return value for RPC
        self.env['bus.bus'].sendone(channel, message)
        return True


    @api.multi
    def bus_call(self, params, timeout=POLL_TIMEOUT, silent=False):
        self.ensure_one()
        channel = 'asterisk_agent/{}'.format(self.uid)
        reply_channel = '{}/{}'.format(channel, uuid.uuid4().hex)
        params.update({'reply_channel': reply_channel})
        # Commit sending message in separate transaction so that we could get an reply.
        with api.Environment.manage():
            with registry(self.env.cr.dbname).cursor() as new_cr:
                env = api.Environment(new_cr, self.env.uid, self.env.context)
                env['bus.bus'].sendone(channel, json.dumps(params))
                new_cr.commit()
        # Poll is done is separate transaction in bus.bus so we don't do it.
        if dispatch:
            # Gevent instance
            agent_reply = dispatch.poll(self.env.cr.dbname,
                                        [reply_channel],
                                        last=0, timeout=timeout)
        else:
            # Cron instance
            odoo_started = fields.Datetime.now()
            started = datetime.now()
            to_end = started + timedelta(seconds=timeout)
            agent_reply = None
            while datetime.now() < to_end:
                with api.Environment.manage():
                    with registry(self.env.cr.dbname).cursor() as new_cr:
                        env = api.Environment(new_cr, self.env.uid, self.env.context)
                        rec = env['bus.bus'].sudo().search(
                                [('create_date', '>=', odoo_started),
                                 ('channel', '=', '"{}"'.format(reply_channel))])
                        if not rec:
                            time.sleep(0.2)
                        else:
                            logger.debug('Got reply within {} seconds'.format(
                                    (datetime.now() - started).total_seconds()))
                            agent_reply = [
                                {'message': json.loads(
                                            rec[0].message) if rec else {}}]
                            break
        if agent_reply:
            reply_msg = agent_reply[0]['message'] if \
                type(agent_reply[0]['message']) in [dict, list] else \
                json.loads(agent_reply[0]['message'])
            self.sudo().last_ping = fields.Datetime.now()
            return reply_msg
        else:
            self.state = 'offline'
            if not silent:
                self.env.user.ast_notify_warning(
                    _('No reply from Agent, server {}!').format(self.name))
            return {}


    @api.multi
    def originate_call(self, number):
        if self.env.user.asterisk_base_peer:
            self.bus_send({
                   'command': 'originate_call',
                   'Channel': 'SIP/' + self.env.user.asterisk_base_peer.name,
                   'Exten': number,
                   'CallerID': u'<{}> "{}"'.format(
                        self.env.user.asterisk_base_user.extension,
                        self.env.user.name),
                   'uid': self.env.user.id,
                   'Variable': 'SIPADDHEADER="{}"'.format(
                        self.env.user.asterisk_base_user.alert_info or '')})
        else:
            raise UserError('You don\'t have a SIP peer to make a call!')


    @api.multi
    def apply_changes_button(self):
        self.apply_changes(try_offline=True)


    @api.multi
    def apply_changes(self, try_offline=False, notify_offline=False):
        self.ensure_one()
        if self.state == 'offline' and not try_offline:
            logger.info(_('Not applying changes, server {} is offline').format(
                                                                    self.name))
            if notify_offline:
                self.env.user.ast_notify_warning(
                    message=_('Server {} offline, not applying to it!').format(
                                                                self.name))
            return
        is_uploaded = None
        for conf in self.env['asterisk.conf'].search(
                                                [('server', '=', self.id),
                                                 ('is_updated', '=', True)]):
            is_uploaded = conf.upload_conf()
            if is_uploaded:
                conf.is_updated = False
        if is_uploaded:
            self.reload()



    @api.multi
    def upload_all_conf(self):
        self.ensure_one()
        self.bus_call({'command': 'save_all_conf',
                       'server_id': self.id,
                       'conf_ids': [rec.id for rec in self.conf_files]
                       },
                      timeout=30)
        # Update last sync
        for rec in self.conf_files:
            rec.is_updated = False
        self.sudo().write({'sync_date': fields.Datetime.now(),
                           'sync_uid': self.env.uid})


    @api.multi
    def download_all_conf(self):
        self.ensure_one()
        self.bus_call({'command': 'get_all_conf', 'server_id': self.id},
                      timeout=30)
        # Update last sync
        self.sudo().write({'sync_date': fields.Datetime.now(),
                           'sync_uid': self.env.uid})
        # For xml rpc
        return True


    @api.multi
    def reload_button(self):
        self.ensure_one()
        self.reload()


    def reload(self, module=None):
        return self.bus_call({'command': 'asterisk_reload', 'module': module})


    @api.multi
    def ping_button(self):
        self.ensure_one()
        self.ping(silent=False)


    @api.multi
    def ping(self, silent=True):
        self.ensure_one()
        reply = self.bus_call({'command': 'ping'}, timeout=5, silent=silent)
        if not reply:
            self.write({'state': 'offline'})
        else:
            self.write({'state': 'online'})
            if self.conf_files.search([('server', '=', self.id),
                                       ('is_updated', '=', True)]):
                self.apply_changes()


    @api.model
    def ping_all(self):
        for server in self.search([]):
            server.ping(silent=True)
