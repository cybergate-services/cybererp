# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models
from odoo.tools import safe_eval


class SupportTeam(models.Model):
    _name = "helpdesk_lite.team"
    _inherit = ['mail.alias.mixin', 'mail.thread']
    _description = "Support Team"
    _order = "name"

    name = fields.Char('Support Team', required=True, translate=True)
    user_id = fields.Many2one('res.users', string='Team Leader')
    member_ids = fields.One2many('res.users', 'helpdesk_team_id', string='Team Members')
    reply_to = fields.Char(string='Reply-To',
                           help="The email address put in the 'Reply-To' of all emails sent by Odoo about cases in this support team")
    color = fields.Integer(string='Color Index', help="The color of the team")
    active = fields.Boolean(default=True, help="If the active field is set to false, it will allow you to hide the support team without removing it.")
    company_id = fields.Many2one('res.company', string='Company',
        default=lambda self: self.env['res.company']._company_default_get())

    @api.model
    def create(self, values):
        return super(SupportTeam, self.with_context(mail_create_nosubscribe=True)).create(values)

    @api.model
    @api.returns('self', lambda value: value.id if value else False)
    def _get_default_team_id(self, user_id=None):
        if not user_id:
            user_id = self.env.uid
        team_id = None
        if 'default_team_id' in self.env.context:
            team_id = self.env['helpdesk_lite.team'].browse(self.env.context.get('default_team_id'))
        if not team_id or not team_id.exists():
            team_id = self.env['helpdesk_lite.team'].sudo().search(
                ['|', ('user_id', '=', user_id), ('member_ids', '=', user_id)],
                limit=1)
        if not team_id:
            team_id = self.env.ref('helpdesk_lite.team_alpha', raise_if_not_found=False)
        return team_id


    def get_alias_model_name(self, vals):
        return 'helpdesk_lite.ticket'

    def get_alias_values(self):
        values = super(SupportTeam, self).get_alias_values()
        defaults = safe_eval(self.alias_defaults or "{}")
        defaults['team_id'] = self.id
        values['alias_defaults'] = defaults
        return values
