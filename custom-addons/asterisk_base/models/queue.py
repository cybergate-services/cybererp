import logging
from odoo import models, fields, api, _
from .utils import remove_empty_lines

logger = logging.getLogger(__name__)

class AsteriskQueue(models.Model):
    _name = 'asterisk.queue'
    _description = "Queue"

    name = fields.Char(required=True)
    server = fields.Many2one(comodel_name='asterisk.server', required=True)
    extension = fields.Char(required=True)
    extension_id = fields.One2many('asterisk.extension', inverse_name='queue')
    strategy = fields.Selection([('ringall', 'Ring all'),
                                 ('leastrecent', 'Least recent'),
                                 ('fewestcalls', 'Fewest calls'),
                                 ('random', 'Random'),
                                 ('rrmemory', 'Rrmemory'),
                                 ('linear', 'Linear'),
                                 ('wrandom', 'Wrandom')],
                                default='ringall', required=True)
    timeout = fields.Integer(default='300')
    options = fields.Char(default='ht')
    members = fields.Many2many('asterisk.sip_peer',
                               domain=[('peer_type', '=', 'user')])
    members_list = fields.Char(compute='_get_members_list',
                               string=_('Members'))

    @api.model
    def create(self, vals):
        res = super(AsteriskQueue, self).create(vals)
        if res:
            res.extension_id = self.env['asterisk.extension'].sudo().create({
                                         'extension_type': 'queue',
                                         'server': res.server.id,
                                         'queue': res.id})
            self.sudo().build_conf()
            self.env['asterisk.extension'].sudo().build_conf()
        return res


    @api.multi
    def write(self, vals):
        res = super(AsteriskQueue, self).write(vals)
        if res:
            self.sudo().build_conf()
            self.env['asterisk.extension'].sudo().build_conf()
        return res


    @api.multi
    def unlink(self):
        res = super(AsteriskQueue, self).unlink()
        if res:
            self.sudo().build_conf()
            self.env['asterisk.extension'].sudo().build_conf()
        return res


    @api.multi
    def _get_members_list(self):
        for rec in self:
            members = [k.name for k in rec.members]
            members.sort()
            rec.members_list = ', '.join(members)


    @api.onchange('server')
    def _set_members(self):
        if self.members:
            self.members = False
        return {'domain': {'members': [('server', '=', self.server.id)]}}


    def build_conf(self):
        conf_dict = {}
        for rec in self.env['asterisk.queue'].search([]):
            if not conf_dict.get(rec.server.id):
                conf_dict[rec.server.id] = ''
            conf_dict[rec.server.id] += self.env['ir.qweb'].render(
               'asterisk_base.asterisk_queue',
               {'rec': rec,
                'members': [
                    'SIP/{}'.format(k.name) for k in rec.members]}).decode('latin-1')
        # Create conf files
        for server_id in conf_dict.keys():
            conf = self.env['asterisk.conf'].get_or_create(
                                                        server_id,
                                                        'queues_odoo.conf')
            conf.content = u'{}'.format(
                                remove_empty_lines(conf_dict[server_id]))
            conf.include_from('queues.conf')
