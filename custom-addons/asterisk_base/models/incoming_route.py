from odoo import fields, models, api, _
from .utils import remove_empty_lines


class IncomingRoute(models.Model):
    _name = 'asterisk.incoming_route'
    _description = "Incoming route"


    server = fields.Many2one(comodel_name='asterisk.server', required=True)
    name = fields.Char(required=True)
    note = fields.Text()
    trunk = fields.Many2one('asterisk.sip_peer',
                            domain=[('peer_type', '=', 'trunk')])
    route_type = fields.Selection([('did', 'DID Route'),
                                  ('callerid', 'Caller ID Route')],
                                  required=True, default='did')
    callerid_route_type = fields.Selection([('transfer', 'Call Transfer Rule'),
                                            ('block', 'Block Number Rule')],
                                           default='transfer')
    block_type = fields.Selection([('busy', 'Play busy signal'),
                                   ('ring', 'Ring forever'),
                                   ('monkeys', 'Play monkeys')],
                                  default='busy')
    pattern = fields.Char(
                  required=True,
                  help=('Patterns: \n'
                        'X matches any digit from 0-9. \n'
                        'Z matches any digit from 1-9.\n'
                        'N matches any digit from 2-9.\n'
                        '[1237-9] matches any digit or letter in the brackets'
                        '(in this example, 1,2,3,7,8,9)\n'
                        '[a-z] matches any lower case letter.\n'
                        '[A-Z] matches any UPPER case letter.\n'
                        '. wildcard, matches one or more characters.\n'
                        '! wildcard, matches zero or more characters immediately.\n'
                        ))
    prefix = fields.Char()
    trim_digits = fields.Integer(
                        help=_('Number of digits to trim from the front.'))
    extension = fields.Many2one('asterisk.extension', required=True)
    dialplan = fields.Text()
    record_calls = fields.Boolean()


    @api.model
    def create(self, vals):
        rec = super(IncomingRoute, self).create(vals)
        if rec and not self.env.context.get('no_build_conf'):
            self.build_conf()
            if rec.trunk and rec.trunk.context != 'odoo-incoming':
                rec.trunk.context = 'odoo-incoming'
                rec.trunk.sudo().build_conf()
        return rec


    @api.multi
    def write(self, vals):
        res = super(IncomingRoute, self).write(vals)
        if res and not self.env.context.get('no_build_conf'):
            self.sudo().build_conf()
            # Check context of trunk
            for rec in self:
                if rec.trunk and rec.trunk.context != 'odoo-incoming':
                    rec.trunk.context = 'odoo-incoming'
                    rec.trunk.sudo().build_conf()
        return res


    @api.multi
    def unlink(self):
        res = super(IncomingRoute, self).unlink()
        if res:
            self.sudo().build_conf()
        return res


    @api.onchange('route_type')
    def _reset_callerid_route_type(self):
        if self.route_type == 'did':
            self.callerid_route_type = 'transfer'


    @api.onchange('server')
    def reset_server(self):
        self.trunk = False


    @api.model
    def build_conf(self):
        conf_dict = {}
        server_interconnect_protocol = self.env[
            'res.config.settings']._get_asterisk_param(
                'interconnection_protocol', 'iax').upper()
        if server_interconnect_protocol == 'IAX':
            # For channel prefix we should make iax -> iax2
            server_interconnect_protocol = 'IAX2'
        for rec in self.env['asterisk.incoming_route'].search([]):
            # Create server in conf_dict
            if not conf_dict.get(rec.server.id):
                conf_dict[rec.server.id] = '[odoo-incoming]\n'
            # Render menu template
            record_block = self.env['ir.qweb'].render(
                       'asterisk_base.incoming_route', {
                            'id': rec.id,
                            'name': rec.name,
                            'route_type': rec.route_type,
                            'callerid_route_type': rec.callerid_route_type,
                            'block_type': rec.block_type,
                            'trunk': rec.trunk,
                            'pattern': rec.pattern,
                            'extension_number': rec.extension.number,
                            'server': rec.server,
                            'extension_server': rec.extension.server,
                            'protocol': server_interconnect_protocol,
                            'prefix': rec.prefix,
                            'trim_digits': rec.trim_digits,
                            'record_calls': rec.record_calls,
                        }).decode('latin-1')
            conf_dict[rec.server.id] += record_block
            rec.with_context({'no_build_conf': True}).write(
                                {'dialplan': remove_empty_lines(record_block)})
        # Create conf files
        for server_id in conf_dict.keys():
            conf = self.env['asterisk.conf'].get_or_create(
                                            server_id,
                                            'extensions_odoo_incoming.conf')
            conf.content = u'{}'.format(
                                remove_empty_lines(conf_dict[server_id]))
            conf.include_from('extensions.conf')


