from odoo import models, api, fields


class MSSWhatsappSendMessage(models.TransientModel):

    _name = 'mss.whatsapp.message.wizard'

    mobile = fields.Char(string='User Whatsapp Number', required=True)
    message = fields.Text(string="Message", required=True)

    def send_message(self):
        if self.message and self.mobile:
            message_string = ''
            message = self.message.split(' ')
            for msg in message:
                message_string = message_string + msg + '%20'
            message_string = message_string[:(len(message_string) - 3)]
            return {
                'type': 'ir.actions.act_url',
                'url': "https://api.whatsapp.com/send?phone="+self.mobile+"&text=" + message_string,
                'target': 'new',
                'res_id': self.id,
            }