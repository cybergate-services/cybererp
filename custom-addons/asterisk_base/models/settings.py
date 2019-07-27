import logging
import uuid
from odoo import api, fields, models, _, SUPERUSER_ID
from odoo.exceptions import ValidationError

logger = logging.getLogger(__name__)

INTER_PROTOCOLS = [('iax', 'IAX2'), ('sip', 'SIP')]

class AsteriskBaseSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    ASTERISK_BASE_PARAMS = [
        ('interconnection_protocol', 'iax'),
        ('agents_hostname', '127.0.0.1'),
        ('agents_port', '8072'),
        ('agents_security', 'http'),
        ('device_registration_token', 'change-me')
    ]

    interconnection_protocol = fields.Selection(INTER_PROTOCOLS)
    device_registration_token = fields.Char()
    agents_hostname = fields.Char()
    agents_port = fields.Char()
    agents_security = fields.Selection([('http', 'HTTP'), ('https', 'HTTPS')])


    @api.multi
    def set_values(self):
        if not self.env.user.has_group(
                            'asterisk_base.group_asterisk_base_admin'):
            raise ValidationError(
                            _('You must be Asterisk Administrator to use it!'))
        super(AsteriskBaseSettings, self).set_values()
        for field_name, default_value in self.ASTERISK_BASE_PARAMS:
            value = getattr(self, field_name, default_value)
            self.env['ir.config_parameter'].sudo().set_param(
                'asterisk_base.' + field_name, value)

    @api.model
    def get_values(self):
        if not self.env.user.has_group(
                            'asterisk_base.group_asterisk_base_admin'):
            raise ValidationError(
                            _('You must be Asterisk Administrator to use it!'))
        res = super(AsteriskBaseSettings, self).get_values()
        for field_name, default_value in self.ASTERISK_BASE_PARAMS:
            res[field_name] = self.env[
                'ir.config_parameter'].get_param(
                    'asterisk_base.' + field_name, default_value)
        return res


    @api.model
    def _get_asterisk_param(self, param, default=None):
        result = self.env['ir.config_parameter'].sudo().get_param(
                                                    'asterisk_base.' + param)
        logger.debug(u'Param {} = {}'.format(param, result))
        return result or default


    @api.model
    def _set_asterisk_param(self, param, value):
        # set_ method are deprecated and all wrapped to set_values so we use _set_
        return self.env['ir.config_parameter'].sudo().set_param(
                'asterisk_base.' + param, value)


    @api.model
    def _set_new_param(self, param, value):
        # It's called from data/settings.xml
        if not self._get_asterisk_param(param):
            self._set_asterisk_param(param, value)


    @api.multi
    def generate_asterisk_device_registration_token_button(self):
        self.generate_asterisk_device_registration_token()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload'
        }

    @api.model
    def generate_asterisk_device_registration_token(self):
        self._set_asterisk_param('device_registration_token', '{}'.format(
                                                            uuid.uuid4().hex))
