import string
import logging
from odoo import models, fields, api, _
from odoo.exceptions import ValidationError
from .utils import remove_empty_lines

logger = logging.getLogger(__name__)


class Extension(models.Model):
    _name = 'asterisk.extension'
    _order = 'number'
    _description = "Extension"

    name = fields.Char(compute='_get_name')
    server = fields.Many2one(comodel_name='asterisk.server', store=True,
                             compute='_get_server')
    number = fields.Char(compute='_get_number', store=True,
                         inverse='_set_number')
    extension_type = fields.Char(required=True, readonly=True,
                                 string=_('Type'))
    user = fields.Many2one('asterisk.user', ondelete='cascade',
                           readonly=True)
    queue = fields.Many2one('asterisk.queue', ondelete='cascade',
                            readonly=True)
    menu = fields.Many2one('asterisk.menu', ondelete='cascade',
                           readonly=True)
    dialplan = fields.Many2one('asterisk.dialplan', ondelete='cascade',
                               readonly=True)
    sip_peer = fields.Many2one('asterisk.sip_peer', ondelete='cascade',
                               readonly=True, string=_('SIP peer'))
    sip_peer_dial_timeout = fields.Integer(default=90,
                                           string=_('Dial timeout'))
    sip_peer_dial_options = fields.Char(default='TK',
                                        string=_('Dial options'))
    record_calls = fields.Boolean()


    @api.model
    def create(self, vals):
        res = super(Extension, self).create(vals)
        if res:
            self.build_conf()
        return res


    @api.multi
    def write(self, vals):
        res = super(Extension, self).write(vals)
        if res:
            self.build_conf()
        return res


    @api.constrains('number')
    def _check_number(self):
        if not self.number:
            return
        # Check for existance
        count = self.env['asterisk.extension'].search_count([
                                            ('server', '=', self.server.id),
                                            ('number', '=', self.number)])
        if count > 1:
            raise ValidationError(_('This extension number is already used!'))
        # Check number for valid patterns
        allowed_patterns = string.digits + string.ascii_letters + '_-+.[]!'
        for l in self.number:
            if l not in allowed_patterns:
                raise ValidationError(
                                _('Extension number has illegal characters!'))



    @api.multi
    def _get_server(self):
        for rec in self:
            rec.server = eval('rec.{}.server'.format(rec.extension_type))


    @api.multi
    @api.depends('extension_type', 'user.extension', 'menu.extension',
                 'dialplan.extension', 'queue.extension',
                 'sip_peer.extension')
    def _get_number(self):
        for rec in self:
                rec.number = eval('rec.{}.extension'.format(
                                                        rec.extension_type))

    @api.multi
    def _set_number(self):
        for rec in self:
            exec('rec.sudo().{}.extension = "{}"'.format(rec.extension_type,
                                                         rec.number))


    @api.multi
    def _get_name(self):
        for rec in self:
            if rec.extension_type == 'user':
                rec.name = '{} ({}) @ {}'.format(rec.number,
                                                 rec.user.partner.name,
                                                 rec.server.name)
            elif rec.extension_type == 'queue':
                rec.name = '{} (Queue {}) @ {}'.format(rec.number,
                                                       rec.queue.name,
                                                       rec.server.name)
            elif rec.extension_type == 'menu':
                rec.name = '{} (Menu {}) @ {}'.format(rec.number,
                                                      rec.menu.name,
                                                      rec.server.name)
            elif rec.extension_type == 'dialplan':
                rec.name = '{} (Dialplan {}) @ {}'.format(rec.number,
                                                          rec.dialplan.context,
                                                          rec.server.name)
            elif rec.extension_type == 'sip_peer':
                rec.name = '{} (SIP peer {}) @ {}'.format(rec.number,
                                                          rec.sip_peer.name,
                                                          rec.server.name)

    @api.model
    def build_conf(self):
        conf_dict = {}
        for rec in self.env['asterisk.extension'].search([]):
            # Create server in conf_dict
            if not conf_dict.get(rec.server.id):
                conf_dict[rec.server.id] = '[odoo-extensions]\n'
            conf_dict[rec.server.id] += self.env['ir.qweb'].render(
                                    'asterisk_base.extensions', {
                                        'rec': rec,
                                    }).decode('latin-1')
        # Create conf files
        for server_id in conf_dict.keys():
            conf = self.env['asterisk.conf'].get_or_create(
                                                server_id,
                                                'extensions_odoo.conf')
            conf.content = u'{}'.format(
                                remove_empty_lines(conf_dict[server_id]))
            conf.include_from('extensions.conf')


    @api.multi
    def open_extension(self):
        self.ensure_one()
        res = {
            'type': 'ir.actions.act_window',
            'res_model': 'asterisk.{}'.format(self.extension_type),
            'view_mode': 'form',
            'view_type': 'form',
            'target': 'current',
            'res_id': eval('self.{}.id'.format(self.extension_type)),
            'context': {} if self.extension_type != 'sip_peer' else {
                'form_view_ref': 'asterisk_base.asterisk_sip_peer_user_form',
                },
        }
        return res
