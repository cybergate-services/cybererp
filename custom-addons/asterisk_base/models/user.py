import json
import logging
from odoo import models, fields, api, _
from .utils import remove_empty_lines

logger = logging.getLogger(__name__)


class AsteriskUser(models.Model):
    _name = 'asterisk.user'
    _order = 'user'
    _description = _('Asterisk User')
    _rec_name = 'user'

    server = fields.Many2one(comodel_name='asterisk.server', required=True)
    user = fields.Many2one('res.users', required=True,
                           ondelete='cascade',
                           domain=[('share', '=', False)])
    peer = fields.Many2one('asterisk.sip_peer', required=True,
                           ondelete='restrict')
    extension = fields.Char(required=True)
    extension_id = fields.One2many('asterisk.extension', inverse_name='user')
    partner = fields.Many2one(related='user.partner_id', readonly=True,
                              string=_('Contact'))
    phone = fields.Char(related='partner.phone')
    mobile = fields.Char(related='partner.mobile')
    voicemail = fields.Char(related='partner.email', string="Voicemail")
    voicemail_enabled = fields.Boolean()
    voicemail_password = fields.Char()
    ring_timeout = fields.Integer(default=30, required=True)
    ring_timeout_estimation = fields.Char(
                                    compute='_get_ring_timeout_estimation',
                                    string=_('Ring timeout'))
    forward_on_timeout = fields.Boolean()
    forward_on_busy = fields.Boolean()
    route_group = fields.Many2one('asterisk.outgoing_route_group',
                                  ondelete='restrict')
    alert_info = fields.Char()
    # TODO
    """
    forward_on_busy_type = fields.Selection([('mobile', 'Mobile phone'),
                                             ('custom', 'Custom phone number')],
                                            default='mobile',
                                            string=_('Forward to'))
    """
    forward_on_unavailable = fields.Boolean()
    timeout_number = fields.Char(string=_('Number to forward'))
    on_busy_number = fields.Char(string=_('Number to forward'))
    on_unavailable_number = fields.Char(string=_('Number to forward'))
    forward_unconditional = fields.Boolean()
    unconditional_number = fields.Char(string=_('Number to forward'))
    dialplan = fields.Text(compute='_get_dialplan')

    _sql_constraints = [
        ('extension_uniq', 'unique(server,extension)', _('This extension is already defined on this server!')),
        ('user_uniq', 'unique(server,"user")', _('This user is already defined on this server!')),
        ('peer_uniq', 'unique(server,peer)', _('This peer is already defined on this server!')),
    ]


    @api.model
    def create(self, vals):
        res = super(AsteriskUser, self).create(vals)
        if res:
            if res.peer.extension_id:
                res.peer.extension_id.unlink()
            res.extension_id = self.env['asterisk.extension'].create({
                                                     'extension_type': 'user',
                                                     'server': res.server.id,
                                                     'user': res.id})
            self.build_conf()
            self.build_voicemail()
            self.env['asterisk.extension'].sudo().build_conf()
        return res


    @api.multi
    def write(self, vals):
        super(AsteriskUser, self).write(vals)
        self.build_conf()
        self.build_voicemail()
        self.env['asterisk.extension'].sudo().build_conf()
        return True


    @api.multi
    def unlink(self):
        for rec in self:
            # Copy routing group on peer level
            group_id = rec.route_group.id
            extension = rec.extension
            peer = rec.peer
            rec.extension_id.unlink()
            peer.write({
                'route_group': group_id,
                'extension': extension  # Extension will be created on peer create()
            })
            super(AsteriskUser, rec).unlink()
        self.build_conf()
        self.build_voicemail()
        self.env['asterisk.extension'].sudo().build_conf()
        return True


    @api.model
    def build_conf(self):
        conf_dict = {}
        users = self.env['asterisk.user'].search([])
        for rec in users:
            # Init server config data
            if not conf_dict.get(rec.server.id):
                conf_dict[rec.server.id] = '[odoo-users]\n'
            conf_dict[rec.server.id] += \
                'exten => {},1,Gosub(odoo-user-{},${{EXTEN}},1)\n'.format(
                                                            rec.extension,
                                                            rec.extension)
        # Now render common dialplan
        for server_id in conf_dict.keys():
            conf_dict[rec.server.id] += self.env['ir.qweb'].render(
                'asterisk_base.asterisk_users_extensions', {}).decode('latin-1')
        # Now add personal users contexts
        for rec in users:
            conf_dict[rec.server.id] += '{}\n'.format(
                                                self.build_user_context(rec))
        # Create asterisk conf
        for server_id in conf_dict.keys():
            conf = self.env['asterisk.conf'].get_or_create(
                                            server_id,
                                            'extensions_odoo_users.conf')
            # Set conf content
            conf.content = u'{}'.format(
                                remove_empty_lines(conf_dict[server_id]))
            conf.include_from('extensions.conf')



    @api.model
    def build_user_context(self, rec):
        rec.ensure_one()
        res = self.env['ir.qweb'].render(
                   'asterisk_base.asterisk_user_context',
                   {'extension': rec.extension,
                    'user_name': rec.partner.name,
                    'voicemail_enabled': rec.voicemail_enabled,
                    'peer_name': rec.peer.name,
                    'ring_timeout': rec.ring_timeout,
                    'timeout_number': rec.timeout_number,
                    'on_busy_number': rec.on_busy_number,
                    'on_unavailable_number': rec.on_unavailable_number,
                    'unconditional_number': rec.unconditional_number,
                    }).decode('latin-1')
        return remove_empty_lines(res)


    # LITNIALEX TODO: Set peer' mailbox??'
    def build_voicemail(self):
        conf_dict = {}
        for rec in self.env['asterisk.user'].search([]):
            if not conf_dict.get(rec.server.id):
                conf_dict[rec.server.id] = '[odoo-default]\n'
            if rec.extension and rec.voicemail_enabled and rec.voicemail_password:
                conf_dict[rec.server.id] += '{} => {},{},{}\n'.format(
                                                    rec.extension,
                                                    rec.voicemail_password,
                                                    rec.partner.name,
                                                    rec.voicemail)
                # Update peer's mailbox'
                # PJSIP: check
                if rec.peer:
                    rec.peer.mailbox = '{}@odoo-default'.format(rec.extension)
        # Build conf files
        # Create conf files
        for server_id in conf_dict.keys():
            # First try to get existing conf
            conf = self.env['asterisk.conf'].get_or_create(
                                                    server_id,
                                                    'voicemail_odoo.conf')
            conf.content = u'{}'.format(conf_dict[server_id])
            conf.is_updated = True
            conf.include_from('voicemail.conf')



    @api.multi
    def _get_dialplan(self):
        for rec in self:
            rec.dialplan = rec.build_user_context(rec)

    @api.multi
    def _get_ring_timeout_estimation(self):
        for rec in self:
            rec.ring_timeout_estimation = _('{} seconds (~ {} rings)').format(
                                                        rec.ring_timeout,
                                                        rec.ring_timeout // 5)

    @api.onchange('server')
    def _set_peers(self):
        if self.peer:
            self.peer = False


    @api.onchange('peer')
    def _set_peer_extension(self):
        if self.peer.extension:
            self.extension = self.peer.extension


    @api.multi
    def call_user(self):
        # Used from tree view button
        self.ensure_one()
        self.server.originate_call(self.extension)