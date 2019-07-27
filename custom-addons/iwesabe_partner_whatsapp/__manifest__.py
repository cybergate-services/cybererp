# -*- coding: utf-8 -*-
{
    'name': 'Send Via WhatsApp',
    'version': '1.1',
    'author': 'iWesabe',
    'summary': 'Send messages to partners via WhatsApp',
    'description': """Send messages to partners via WhatsApp""",
    'category': 'Base',
    'website': 'https://www.iwesabe.com/',
    'license': 'AGPL-3',

    'depends': ['base', ],

    'data': [
        'views/res_partner_view.xml',
    ],

    'qweb': [],
    'images': ['static/description/iWesabe-Apps-Partner-Whatsapp.png'],

    'installable': True,
    'application': True,
    'auto_install': False,
}
