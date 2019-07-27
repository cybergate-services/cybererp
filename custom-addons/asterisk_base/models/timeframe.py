from datetime import datetime
import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

logger = logging.getLogger(__name__)

HOUR_SELECTION = [
]
for h in range(0, 24):
    f = str(h)
    if len(f) == 1:
        f ='0{}'.format(f)
    HOUR_SELECTION.append((f, f))


MINUTE_SELECTION = [
]
for m in range(0, 60):
    f = str(m)
    if len(f) == 1:
        f ='0{}'.format(f)
    MINUTE_SELECTION.append((f, f))

DAYS_SELECTION = [
    ('0', 'Monday'),
    ('1', 'Tuesday'),
    ('2', 'Wednesday'),
    ('3', 'Thursday'),
    ('4', 'Friday'),
    ('5', 'Saturday'),
    ('6', 'Sunday'),
]


class TimeFrame(models.Model):
    _name = 'asterisk.timeframe'
    _description = "Timeframe"


    name = fields.Char(required=True)
    active_from = fields.Datetime()
    active_till = fields.Datetime()
    periods = fields.Many2many('asterisk.timeframe_period')
    is_active_now = fields.Boolean(compute='_is_active_now', 
                                   string=_('Active now'))


    @api.constrains('active_from', 'active_till')
    def _check_dates(self):
        if self.active_from and self.active_till:
            if fields.Datetime.from_string(self.active_from) > \
                            fields.Datetime.from_string(self.active_till):
                raise ValidationError(_('From time must be less then till time!'))


    @api.multi
    def _is_active_now(self):
        now = fields.Datetime.context_timestamp(self,
                        fields.Datetime.from_string(fields.Datetime.now()))
        today = now.weekday()
        for rec in self:
            if rec.active_from and \
                    fields.Datetime.from_string(rec.active_from) > now:
                continue
            if rec.active_till and \
                    fields.Datetime.from_string(rec.active_till) < now:
                continue
            for period in rec.periods:
                if int(period.day) == today:
                    field_start_minutes = int(period.start_hour) * 60 + int(period.start_minute)
                    field_end_minutes = int(period.end_hour) * 60 + int(period.end_minute)
                    now_minutes = int(now.hour) * 60 + int(now.minute)
                    if now_minutes >= field_start_minutes and \
                                        now_minutes <= field_end_minutes:
                        # Bingo!
                        rec.is_active_now = True
                        break



class TimeFramePeriod(models.Model):
    _name = 'asterisk.timeframe_period'
    _order = 'sequence'
    _description = "Timeframe period"


    name = fields.Char(compute='_get_name')
    sequence = fields.Integer()
    start_hour = fields.Selection(HOUR_SELECTION, required=True)
    end_hour = fields.Selection(HOUR_SELECTION, required=True)
    start_minute = fields.Selection(MINUTE_SELECTION, required=True)
    end_minute = fields.Selection(MINUTE_SELECTION, required=True)
    day = fields.Selection(DAYS_SELECTION, required=True)
    start_time = fields.Char(compute='_get_start_time')
    end_time = fields.Char(compute='_get_end_time')


    @api.multi
    def _get_name(self):
        for rec in self:
            rec.name = '{} {}:{} - {}:{}'.format(rec.day.capitalize(), rec.start_hour,
                                                 rec.start_minute, rec.end_hour,
                                                 rec.end_minute)

    @api.multi
    def _get_start_time(self):
        for rec in self:
            rec.start_time = '{}:{}'.format(rec.start_hour, rec.start_minute)

    @api.multi
    def _get_end_time(self):
        for rec in self:
            rec.end_time = '{}:{}'.format(rec.end_hour, rec.end_minute)


