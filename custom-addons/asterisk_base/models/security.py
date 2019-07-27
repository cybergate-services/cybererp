import logging
from odoo import models, fields, api, _

logger = logging.getLogger(__name__)

class AccessList(models.Model):
    _name = 'asterisk.access_list'
    _description = 'Access Lists of IP/Nets'
    _order = 'address'

    server = fields.Many2one('asterisk.server', required=True,
                             ondelete='cascade')
    name = fields.Char(compute='_get_name')
    address = fields.Char(required=True, index=True)
    netmask = fields.Char()
    address_type = fields.Selection([('ip', 'IP Address'), ('net', 'Network')],
                                    required=True, default='ip')
    access_type = fields.Selection([('allow', 'Allow'), ('deny', 'Deny')],
                                   required=True, default='deny')



    @api.multi
    def _get_name(self):
        for rec in self:
            rec.name = rec.address if rec.address_type == 'ip' else \
                '{}/{}'.format(rec.address, rec.netmask)


    @api.model
    def create(self, vals):
        # TODO: Handle CSV import
        res = super(AccessList, self).create(vals)
        if res.server.ip_security_enabled:
            res.server.bus_send({'command': 'update_access_rules'})
        return res


    @api.multi
    def write(self, vals):
        res = super(AccessList, self).write(vals)
        for server in self.mapped('server'):
            if server.ip_security_enabled:
                server.bus_send({'command': 'update_access_rules'})
        return res


    @api.multi
    def unlink(self):
        servers = self.mapped('server')
        res = super(AccessList, self).unlink()
        for server in servers:
            if server.ip_security_enabled:
                server.bus_send({'command': 'update_access_rules'})
        return res



class Ban(models.Model):
    _name = 'asterisk.access_ban'
    _description = 'Access Bans'
    _order = 'address'

    server = fields.Many2one('asterisk.server', required=True,
                             ondelete='cascade')
    address = fields.Char(index=True, required=True)
    timeout = fields.Integer()
    packets = fields.Integer()
    bytes = fields.Integer()
    comment = fields.Char(index=True)


    @api.multi
    def unlink(self):
        entries = {}
        # Populate entries for agent
        for rec in self:
            entries.setdefault(rec.server, []).append(rec.address)
        res = super(Ban, self).unlink()
        # Now send to agent
        if res:
            for server in entries.keys():
                server.bus_send({
                    'command': 'ip_security_remove_banned',
                    'entries': entries[server],
                })
        return res


    @api.model
    def reload_bans(self):
        self.search([]).unlink()  # Remove all entries
        servers = self.env['asterisk.server'].search([('state', '=', 'online')])
        for server in servers:
            result = server.bus_call({'command': 'ip_security_get_banned'})
            entries = result['entries']
            for entry in entries:
                self.create({
                    'server': server.id,
                    'address': entry['address'],
                    'timeout': entry['timeout'],
                    'packets': entry['packets'],
                    'bytes': entry['bytes'],
                    'comment': entry['comment'],
                })

