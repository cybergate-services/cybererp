import logging
import os
from odoo import fields, models, api, _
from .utils import remove_empty_lines

logger = logging.getLogger(__name__)

class Menu(models.Model):
    _name = 'asterisk.menu'
    _description = "Menu"

    server = fields.Many2one(comodel_name='asterisk.server', required=True)
    name = fields.Char(size=50, required=True)
    note = fields.Text()
    extension = fields.Char(required=True)
    extension_id = fields.One2many('asterisk.extension', inverse_name='menu')
    voice_prompt_filename = fields.Char()
    voice_prompt_data = fields.Binary(required=True,
                                      string=_('Upload / Download'))
    voice_prompt_widget = fields.Char(compute='_get_voice_prompt_widget')
    choice_1_extension = fields.Many2one('asterisk.extension',
                                         string=_('On key 1'))
    choice_2_extension = fields.Many2one('asterisk.extension',
                                         string=_('On key 2'))
    choice_3_extension = fields.Many2one('asterisk.extension',
                                         string=_('On key 3'))
    choice_4_extension = fields.Many2one('asterisk.extension',
                                         string=_('On key 4'))
    choice_5_extension = fields.Many2one('asterisk.extension',
                                         string=_('On key 5'))
    choice_6_extension = fields.Many2one('asterisk.extension',
                                         string=_('On key 6'))
    choice_7_extension = fields.Many2one('asterisk.extension',
                                         string=_('On key 7'))
    choice_8_extension = fields.Many2one('asterisk.extension',
                                         string=_('On key 8'))
    choice_9_extension = fields.Many2one('asterisk.extension',
                                         string=_('On key 9'))
    choice_0_extension = fields.Many2one('asterisk.extension',
                                         string=_('On key 0'))
    choice_star_extension = fields.Many2one('asterisk.extension',
                                            string=_('On key *'))
    choice_hash_extension = fields.Many2one('asterisk.extension',
                                            string=_('On key #'))
    timeout_extension = fields.Many2one('asterisk.extension')
    allow_directory = fields.Boolean()
    timeframe = fields.Many2one('asterisk.timeframe')
    read_timeout = fields.Integer(default=5)


    @api.model
    def create(self, vals):
        res = super(Menu, self).create(vals)
        if res:
            res.extension_id = self.env['asterisk.extension'].sudo().create({
                                                     'extension_type': 'menu',
                                                     'server': res.server.id,
                                                     'menu': res.id})
            self.build_conf()
            self.env['asterisk.extension'].sudo().build_conf()
        return res


    @api.multi
    def write(self, vals):
        res = super(Menu, self).write(vals)
        if res:
            self.build_conf()
            self.env['asterisk.extension'].sudo().build_conf()
        return res


    @api.multi
    def unlink(self):
        res = super(Menu, self).unlink()
        if res:
            self.build_conf()
            self.env['asterisk.extension'].sudo().build_conf()
        return res


    @api.multi
    def _get_voice_prompt_widget(self):
        for rec in self:
            rec.voice_prompt_widget = '<audio id="sound_file" preload="auto" ' \
                    'controls="controls"> ' \
                    '<source src="/web/content?model=asterisk.menu&' \
                    'id={}&filename={}&field=voice_prompt_data&' \
                    'filename_field=voice_prompt_filename&download=True" ' \
                    'type="audio/wav"/>'.format(rec.id, rec.voice_prompt_filename)


    @api.model
    def build_conf(self):
        conf_dict = {}
        for rec in self.env['asterisk.menu'].search([]):
            # Create server in conf_dict
            if not conf_dict.get(rec.server.id):
                conf_dict[rec.server.id] = ''
            # Render menu template
            menu_choices = []
            for i in range(0, 10):
                if hasattr(rec, 'choice_{}_extension'.format(i)):
                    ext = getattr(rec, 'choice_{}_extension'.format(i))
                    if not ext:
                        continue
                    menu_choices.append([str(i), ext.number])
            # Cut file extension
            voice_prompt_filename, _ = os.path.splitext(
                rec.voice_prompt_filename) if rec.voice_prompt_filename else \
                (False, False)
            # Upload sound file to Asterisk
            if rec.voice_prompt_filename:
                rec.server.bus_call({
                                    'command': 'save_voice_prompt',
                                    'name': rec.voice_prompt_filename,
                                    'data': rec.voice_prompt_data.decode('latin-1')})
            conf_dict[rec.server.id] += self.env['ir.qweb'].render(
                       'asterisk_base.menu', {
                            'id': rec.id,
                            'name': rec.name,
                            'voice_prompt_filename': voice_prompt_filename,
                            'allow_directory': rec.allow_directory,
                            'read_timeout': rec.read_timeout,
                            'choices': menu_choices,
                        }).decode('latin-1')
        # Create conf files
        for server_id in conf_dict.keys():
            conf = self.env['asterisk.conf'].get_or_create(
                                                server_id,
                                                'extensions_odoo_menu.conf')
            conf.content = u'{}'.format(
                                remove_empty_lines(conf_dict[server_id]))
            conf.include_from('extensions.conf')

