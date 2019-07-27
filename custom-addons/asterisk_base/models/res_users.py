from odoo import models, fields, api
from odoo.exceptions import UserError


class ResUser(models.Model):
    _name = 'res.users'
    _inherit = 'res.users'

    asterisk_base_user = fields.Many2one('asterisk.user', inverse_name='user',
                                    compute='_get_asterisk_user',
                                    readonly=True)
    asterisk_base_peer = fields.Many2one('asterisk.sip_peer', readonly=True,
                                    compute='_get_asterisk_base_user_peer')
    # Server fields
    asterisk_base_server = fields.One2many('asterisk.server', inverse_name='login',
                                      readonly=True,
                                      compute='_get_asterisk_server')


    @api.multi
    def _get_asterisk_user(self):
        # This is a trick not to give users access to asterisk.* models allowing
        # read operations on res.users object. The below methods serve the same
        # purpose.
        for rec in self:
            ast_user = self.env['asterisk.user'].sudo().search(
                                                    [('user', '=', rec.id)])
            if ast_user:
                rec.asterisk_base_user = ast_user[0]


    @api.multi
    def _get_asterisk_base_user_peer(self):
        for rec in self:
            if rec.asterisk_base_user:
                rec.asterisk_base_peer = self.env[
                    'asterisk.user'].sudo().browse(
                                    rec.asterisk_base_user.id).peer


    @api.multi
    def _get_asterisk_server(self):
        for rec in self:
            rec.asterisk_base_server = [k.id for k in self.env[
                'asterisk.server'].sudo().search([('login', '=', rec.id)])]


    @api.multi
    def ast_notify_info(self, message, title=None, sticky=False):
        if hasattr(self.env['res.users'], 'notify_info'):
            return self.env.user.notify_info(message, title=title,
                                             sticky=sticky)
        else:
            raise UserError(message)


    @api.multi
    def ast_notify_warning(self, message, title=None, sticky=False):
        if hasattr(self.env['res.users'], 'notify_warning'):
            return self.env.user.notify_warning(message, title=title,
                                                sticky=sticky)
        else:
            raise UserError(message)


    @api.multi
    def originate_call(self, number):
        # Used from originate_call widget
        self.ensure_one()
        self.asterisk_base_user.server.originate_call(number)
