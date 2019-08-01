# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models



class Stage(models.Model):
    """ Model for case stages. This models the main stages of a document
        management flow. Tickets will now use only stages, instead of state and stages.
        Stages are for example used to display the kanban view of records.
    """
    _name = "helpdesk_lite.stage"
    _description = "Stage of case"
    _rec_name = 'name'
    _order = "sequence, name, id"

    name = fields.Char('Stage Name', required=True, translate=True)
    sequence = fields.Integer('Sequence', default=1, help="Used to order stages. Lower is better.")
    requirements = fields.Text('Requirements', help="Enter here the internal requirements for this stage (ex: Offer sent to customer). It will appear as a tooltip over the stage's name.")
    fold = fields.Boolean('Folded in Pipeline',
        help='This stage is folded in the kanban view when there are no records in that stage to display.')
    legend_blocked = fields.Char(
        string='Kanban Blocked Explanation', translate=True,
        help='Override the default value displayed for the blocked state for kanban selection, when the ticket is in that stage.')
    legend_done = fields.Char(
        string='Kanban Done Explanation', translate=True,
        help='Override the default value displayed for the done state for kanban selection, when the ticket is in that stage.')
    legend_normal = fields.Char(
        string='Kanban Normal Explanation', translate=True,
        help='Override the default value displayed for the normal state for kanban selection, when the ticket is in that stage.')
    last = fields.Boolean('Last in Pipeline',
        help='This stage is last for closed tickets.')
