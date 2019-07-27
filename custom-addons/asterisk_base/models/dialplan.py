from odoo import fields, models, api, _
from .utils import remove_empty_lines


class Dialplan(models.Model):
    _name = 'asterisk.dialplan'
    _rec_name = 'context'
    _description = "Dialplan"

    server = fields.Many2one(comodel_name='asterisk.server', required=True)
    context = fields.Char(required=True)
    extension = fields.Char(required=True)
    extension_id = fields.One2many('asterisk.extension', inverse_name='dialplan')
    note = fields.Text()
    lines = fields.One2many('asterisk.dialplan_line', inverse_name='dialplan')
    is_custom = fields.Boolean(string="Custom code")
    dialplan_code = fields.Text()


    @api.model
    def create(self, vals):
        rec = super(Dialplan, self).create(vals)
        if rec:
            rec.extension_id = self.env['asterisk.extension'].sudo().create({
                                                'extension_type': 'dialplan',
                                                'server': rec.server.id,
                                                'dialplan': rec.id})
            self.build_conf()
            self.env['asterisk.extension'].sudo().build_conf()
        return rec


    @api.multi
    def write(self, vals):
        res = super(Dialplan, self).write(vals)
        if res and not self.env.context.get('no_build_conf'):
            self.build_conf()
            self.env['asterisk.extension'].build_conf()
        return res


    @api.multi
    def unlink(self):
        res = super(Dialplan, self).unlink()
        if res:
            self.build_conf()
            self.env['asterisk.extension'].build_conf()
        return res


    @api.model
    def build_conf(self):
        conf_dict = {}
        for rec in self.env['asterisk.dialplan'].search([]):
            # Create server in conf_dict
            if not conf_dict.get(rec.server.id):
                conf_dict[rec.server.id] = ''
            if rec.is_custom:
                # Add custom code instead of lines
                conf_dict[rec.server.id] += rec.dialplan_code
                continue
            else:
                conf_dict[rec.server.id] = u'[{}]; {}\n'.format(
                                    rec.context, rec.note if rec.note else '')
            # Build dialplan from lines
            prio = 1
            for line in rec.lines:
                if not line.label:
                    conf_dict[rec.server.id] += 'exten => {},{},{}({})\n'.format(
                                rec.extension, prio, line.app,
                                line.app_data if line.app_data else '')
                else:
                    conf_dict[rec.server.id] += 'exten => {},{}({}),{}({})\n'.format(
                                rec.extension, prio, line.label, line.app,
                                line.app_data if line.app_data else '')
                prio += 1
            rec.with_context({'no_build_conf': True}).write(
                            {'dialplan_code': conf_dict[rec.server.id]})
        # Create conf files
        for server_id in conf_dict.keys():
            conf = self.env['asterisk.conf'].get_or_create(
                                                server_id,
                                                'extensions_odoo_custom.conf')
            conf.content = u'{}'.format(
                                remove_empty_lines(conf_dict[server_id]))
            conf.include_from('extensions.conf')


    @api.onchange('is_custom')
    def _remove_lines(self):
        self.ensure_one()
        if self.is_custom:
            self.lines = []
        else:
            self.dialplan_code = ''


class DialplanLine(models.Model):
    _name = 'asterisk.dialplan_line'
    _order = 'sequence'
    _description = "Dialplan line"

    name = fields.Char(compute='_get_name')
    dialplan = fields.Many2one('asterisk.dialplan')
    exten = fields.Char()
    sequence = fields.Integer()
    app = fields.Char()
    app_data = fields.Char()
    label = fields.Char()


    @api.multi
    def _get_name(self):
        for rec in self:
            rec.name = '{}({})'.format(rec.app, rec.app_data)
