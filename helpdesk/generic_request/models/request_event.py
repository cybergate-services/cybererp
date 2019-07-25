import logging
import datetime
from odoo import models, fields, api

_logger = logging.getLogger(__name__)


class RequestEvent(models.Model):
    _name = 'request.event'
    _description = 'Request Event'
    _order = 'date DESC'
    _log_access = False

    event_type_id = fields.Many2one(
        'request.event.type', required=True, readonly=True)
    event_code = fields.Char(
        related='event_type_id.code', readonly=True)
    request_id = fields.Many2one(
        'request.request', index=True, required=True, readonly=True,
        ondelete='cascade')
    date = fields.Datetime(
        default=fields.Datetime.now, required=True, index=True, readonly=True)
    user_id = fields.Many2one('res.users', required=True, readonly=True)

    # Assign related events
    old_user_id = fields.Many2one('res.users', readonly=True)
    new_user_id = fields.Many2one('res.users', readonly=True)

    # Change request description
    old_text = fields.Html(readonly=True)
    new_text = fields.Html(readonly=True)

    # Request stage change
    route_id = fields.Many2one('request.stage.route', readonly=True)
    old_stage_id = fields.Many2one('request.stage', readonly=True)
    new_stage_id = fields.Many2one('request.stage', readonly=True)

    @api.multi
    def name_get(self):
        res = []
        for record in self:
            res.append((
                record.id,
                "%s [%s]" % (
                    record.request_id.name,
                    record.event_type_id.display_name)
            ))
        return res

    def get_context(self):
        """ Used in notifications and actions to be backward compatible
        """
        self.ensure_one()
        return {
            'old_user': self.old_user_id,
            'new_user': self.new_user_id,
            'old_text': self.old_text,
            'new_text': self.new_text,
            'route': self.route_id,
            'old_stage': self.old_stage_id,
            'new_stage': self.new_stage_id,
            'request_event': self,
        }

    @api.model
    def _scheduler_vacuum(self, days=90):
        """ Run vacuum for events.
            Delete all events older than <days>
        """
        vacuum_date = datetime.datetime.now() - datetime.timedelta(days=days)
        self.sudo().search(
            [('date', '<', fields.Datetime.to_string(vacuum_date))],
        ).unlink()
