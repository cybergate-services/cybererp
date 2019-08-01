# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class ResUsers(models.Model):
    _inherit = 'res.users'

    helpdesk_team_id = fields.Many2one(
        'helpdesk_lite.team', 'Support Team',
        help='Support Team the user is member of. Used to compute the members of a support team through the inverse one2many')
