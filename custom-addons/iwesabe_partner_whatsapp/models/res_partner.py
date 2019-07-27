# -*- coding: utf-8 -*-
##############################################################################
#
#    Global Creative Concepts Tech Co Ltd.
#    Copyright (C) 2018-TODAY iWesabe (<http://www.iwesabe.com>).
#    You can modify it under the terms of the GNU LESSER
#    GENERAL PUBLIC LICENSE (LGPL v3), Version 3.
#
#    It is forbidden to publish, distribute, sublicense, or sell copies
#    of the Software or modified copies of the Software.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU LESSER GENERAL PUBLIC LICENSE (LGPL v3) for more details.
#
#    You should have received a copy of the GNU LESSER GENERAL PUBLIC LICENSE
#    GENERAL PUBLIC LICENSE (LGPL v3) along with this program.
#    If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from odoo import models, fields, api


class ResPartnerWhatsapp(models.Model):
    _inherit = 'res.partner'

    mobile_whatsapp_link = fields.Html(compute='compute_mobile_whatsapp_link')

    @api.onchange('mobile')
    def compute_mobile_whatsapp_link(self):
        for record in self:
            body = ''

            if record.mobile:
                body = """
                <a target="_blank" href="https://api.whatsapp.com/send?phone=%s">
                    <i class="fa fa-whatsapp"/> <span class="hidden-lg hidden-xl">Send via WhatsApp</span>
                </a>
                """ % record.mobile
            record.mobile_whatsapp_link = body
