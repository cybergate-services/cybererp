# -*- coding: utf-8 -*-

{
    'name': 'Financial Report configuration',
    'version': '1.1',
    'summary': 'This module helps to view Financial reports configuration screen.',
    'author': 'Srikesh Infotech',
    'license': "AGPL-3",
    'website': 'http://www.srikeshinfotech.com',
    'description': """
        This module helps to view Financial reports configuration screen.
        """,
    'images': ['images/main_screenshot.png'],
    'category': "Accounting",
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_financial_report_data.xml',
        'views/account_menuitem.xml',
        'views/account_view.xml',   
    ],
    'installable': True,    
    'auto_install': False,
    'application': True,
}
