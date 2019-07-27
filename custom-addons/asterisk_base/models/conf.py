import base64
import json
import logging
from odoo import models, fields, api, _
from odoo.exceptions import UserError, Warning, ValidationError
from .utils import remove_empty_lines


logger = logging.getLogger(__name__)


class AsteriskConf(models.Model):
    _name = 'asterisk.conf'
    _description = 'Configuration Files'
    _rec_name = 'name'
    _order = 'name'

    name = fields.Char(required=True)
    server = fields.Many2one(comodel_name='asterisk.server', required=True,
                             ondelete='cascade')
    content = fields.Text()
    is_updated = fields.Boolean(string=_('Updated'))
    sync_date = fields.Datetime(readonly=True)
    sync_uid = fields.Many2one('res.users', readonly=True, string='Sync by')
    version = fields.Integer(default=1, required=True,
                             index=True, readonly=True)

    _sql_constraints = [
        ('name_server_idx', 'unique(name,server)',
            _('This file already exists on this server.')),
    ]


    @api.model
    def create(self, vals):
        if not self.env.context.get('conf_no_update'):
            vals['is_updated'] = True
        rec = super(AsteriskConf, self).create(vals)
        return rec


    @api.multi
    def write(self, vals):
        if 'content' in vals and not self.env.context.get('conf_no_update'):
            vals['is_updated'] = True
        if 'content' in vals and 'version' not in vals:
            # Inc version
            for rec in self:
                vals['version'] = rec.version + 1
                super(AsteriskConf, rec).write(vals)
        else:
            super(AsteriskConf, self).write(vals)
        return True


    # TODO: check all unlink methods all models!
    @api.multi
    def unlink(self):
        names = self.mapped('name')
        servers = self.mapped('server')
        for server in servers:
            try:
                server.bus_call({'command': 'delete_conf', 'names': names})
            except Exception as e:
                logger.exception(e)
        return super(AsteriskConf, self).unlink()


    @api.model
    def get_or_create(self, server_id, name):
        # First try to get existing conf
        conf = self.env['asterisk.conf'].search(
                           [('server', '=', server_id),
                            ('name', '=', name)])
        if not conf:
            # Create a new one
            conf = self.env['asterisk.conf'].create(
                                   {'server': server_id,
                                    'name': name})
        return conf



    @api.multi
    def include_from(self, from_name):
        self.ensure_one()
        from_conf = self.env['asterisk.conf'].search([
                                            ('name', '=', from_name),
                                            ('server', '=', self.server.id)])
        if not from_conf:
            raise ValidationError(_('Parent conf {} not found!').format(
                                                                from_name))
        if ('#include {}'.format(self.name) not in from_conf.content and
                 '#tryinclude {}'.format(self.name) not in from_conf.content):
            from_conf.content += '\n#tryinclude {}\n'.format(self.name)


    @api.multi
    def upload_conf_button(self):
        self.upload_conf(silent=False)


    @api.multi
    def upload_conf(self, silent=True):
        # Upload conf to server
        self.ensure_one()
        res = self.server.bus_call({
                        'command': 'save_conf',
                        'name': self.name,
                        'version': self.version,
                        'content': self.content}, silent=silent)
        if res:
            self.write({
                'is_updated': False,
                'sync_date': fields.Datetime.now(),
                'sync_uid': self.env.user.id,
            })
        return res


    @api.multi
    def download_conf_button(self):
        self.download_conf(silent=False)


    @api.multi
    def download_conf(self, silent=True):
        self.ensure_one()
        res = self.server.bus_call({'command': 'get_conf',
                                    'name': self.name})
        if res.get('content'):
            self.with_context({'conf_no_update': True}).write({
                'content': res['content'],
                'sync_date': fields.Datetime.now(),
                'sync_uid': self.env.user.id,
                'version': res['version'],
            })
            return True
        elif res.get('error'):
            if not silent:
                raise UserError(res['error'])
        return res


    @api.model
    def apply_all_changes(self):
        servers_to_update = self.search(
                                [('is_updated', '=', True)]).mapped('server')
        for server in servers_to_update:
            server.apply_changes(notify_offline=True)
        return True


    @api.model
    def rpc_upload_conf(self, conf):
        if type(conf) == list:
            conf = conf[0]
        conf_file = self.search([('server', '=', conf['server']),
                                 ('name', '=', conf['name'])])
        if not conf_file:
            conf_file = self.with_context({'conf_no_update': True}).create({
                                                    'server': conf['server'],
                                                    'name': conf['name']})
        data = base64.b64decode(conf['data']).decode('latin-1')
        conf_file.with_context({'conf_no_update': True}).write({
                                                'content': data,
                                                'version': conf['version']})
        return True
