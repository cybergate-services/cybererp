#-*- encoding: utf-8 -*-
import logging
from odoo import fields, models, api, _
from .utils import remove_empty_lines
from .settings import INTER_PROTOCOLS
from .help import DIAL_OPTIONS

logger = logging.getLogger(__name__)

class OutgoingRouteGroup(models.Model):
    _name = 'asterisk.outgoing_route_group'
    _description = 'Outgoing Route Group'

    name = fields.Char(required=True)
    server = fields.Many2one(comodel_name='asterisk.server', required=True)
    note = fields.Text()
    routes = fields.Many2many(comodel_name='asterisk.outgoing_route',
                              relation='asterisk_outgoing_routes_groups',
                              column1='group_id', column2='route_id')
    routes_count = fields.Char(string=_('Routes'),
                            compute=lambda self: self._compute_routes_count())
    peers = fields.One2many('asterisk.sip_peer', readonly=True,
                            inverse_name='route_group')
    include_extensions = fields.Boolean(default=True)

    @api.model
    def create(self, vals):
        rec = super(OutgoingRouteGroup, self).create(vals)
        if rec and not self.env.context.get('no_build_conf'):
            self.env['asterisk.outgoing_route'].sudo().build_conf()
        return rec


    @api.multi
    def write(self, vals):
        res = super(OutgoingRouteGroup, self).write(vals)
        if res and not self.env.context.get('no_build_conf'):
            self.env['asterisk.outgoing_route'].sudo().build_conf()
            # Check context of trunk
        return res



    @api.multi
    def unlink(self):
        res = super(OutgoingRouteGroup, self).unlink()
        if res:
            self.env['asterisk.outgoing_route'].sudo().build_conf()
        return res


    @api.multi
    def _compute_routes_count(self):
        for rec in self:
            rec.routes_count = _('({} records)').format(len(rec.routes))


class OutgoingRoute(models.Model):
    _name = 'asterisk.outgoing_route'
    _order = 'pattern'
    _description = "Outgoing route"

    server = fields.Many2one(comodel_name='asterisk.server', required=True)
    name = fields.Char(required=True, help=DIAL_OPTIONS)
    groups = fields.Many2many(comodel_name='asterisk.outgoing_route_group',
                              relation='asterisk_outgoing_routes_groups',
                              column2='group_id', column1='route_id',
                              required=True)
    note = fields.Text()
    route_type = fields.Selection([('trunk', 'Trunk'),
                                  ('block', 'Block'),
                                  ('server', 'Asterisk Server')],
                                  default='trunk',
                                  required=True)
    trunk = fields.Many2one('asterisk.sip_peer',
                            domain=[('peer_type', '=', 'trunk')])
    dial_timeout = fields.Integer(default=60)
    dial_options = fields.Char(default='TKS(7200)', help=DIAL_OPTIONS)
    dst_server = fields.Many2one('asterisk.server', string=_('Server'),
                                 domain=[('is_interconnected', '=', True)])
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
    destination = fields.Char(compute='_get_destination')
    dialplan = fields.Text(help=DIAL_OPTIONS)
    record_calls = fields.Boolean()


    @api.model
    def create(self, vals):
        rec = super(OutgoingRoute, self).create(vals)
        if rec and not self.env.context.get('no_build_conf'):
            self.sudo().build_conf()
        return rec


    @api.multi
    def write(self, vals):
        res = super(OutgoingRoute, self).write(vals)
        if res and not self.env.context.get('no_build_conf'):
            self.sudo().build_conf()
            # Check context of trunk
        return res


    @api.multi
    def unlink(self):
        res = super(OutgoingRoute, self).unlink()
        if res:
            self.sudo().build_conf()
        return res


    @api.onchange('server')
    def reset_server(self):
        self.dst_server = False
        self.trunk = False
        self.groups = False


    @api.onchange('name', 'server', 'pattern', 'route_type', 'dst_server',
                  'dial_options', 'dial_timeout', 'trunk', 'trim_digits', 
                  'prefix', 'record_calls')
    def _set_dialplan(self):
        self.ensure_one()
        self.dialplan = self.build_route_dialplan(self)


    @api.multi
    def _get_destination(self):
        for rec in self:
            if rec.route_type == 'trunk':
                rec.destination = rec.trunk.name
            elif rec.route_type == 'server':
                rec.destination = rec.dst_server.name
            else:
                rec.destination = ''

    @api.model
    def build_route_dialplan(self, record):
        interconnection_protocol = dict(INTER_PROTOCOLS).get(
            self.env['res.config.settings']._get_asterisk_param(
                                        'interconnection_protocol', 'iax'))
        return '{}'.format(remove_empty_lines(self.env['ir.qweb'].render(
                   'asterisk_base.extensions_outgoing_route', {
                        'rec': record,
                        'protocol': interconnection_protocol}).decode('latin-1')))

    @api.model
    def build_conf(self, no_create_conf=False):
        conf_dict = {}
        all_groups = self.env['asterisk.outgoing_route_group'].search([])
        servers = all_groups.mapped('server')
        for server in servers:
            conf_dict[server.id] = '[odoo-outgoing]\n\n'
            conf_dict[server.id] += '{}\n'.format(self.env['ir.qweb'].render(
                            'asterisk_base.extensions_outgoing', {}).decode('latin-1'))
            # Take the groups of the server
            for group in self.env['asterisk.outgoing_route_group'].search(
                                            [('server', '=', server.id)]):
                conf_dict[server.id] += '{}'.format(self.env['ir.qweb'].render(
                                'asterisk_base.extensions_outgoing_group', {
                                'group': group}).decode('latin-1'))
                # Now take the routes for group
                for rec in self.env['asterisk.outgoing_route'].search(
                                            [('server', '=', server.id),
                                             ('groups', 'in', [group.id])]):
                    record_block = self.build_route_dialplan(rec)
                    conf_dict[rec.server.id] += record_block
                    rec.with_context({'no_build_conf': True}).write(
                                        {'dialplan': record_block})
        # Create conf files
        if no_create_conf:
            return conf_dict
        for server_id in conf_dict.keys():
            conf = self.env['asterisk.conf'].get_or_create(
                                            server_id,
                                            'extensions_odoo_outgoing.conf')
            conf.content = u'{}'.format(
                                remove_empty_lines(conf_dict[server_id]))
            conf.include_from('extensions.conf')
