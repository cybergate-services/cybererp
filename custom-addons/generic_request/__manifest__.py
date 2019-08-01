{
    'name': "Generic Request",

    'summary': """
        Incident management and helpdesk system - logging, recording,
        tracking, addressing, handling and archiving
        issues that occur in daily routine.
    """,

    'author': "Center of Research and Development",
    'website': "https://crnd.pro",
    'category': 'Generic Request',
    'version': '12.0.1.15.3',
    'external_dependencies': {
        'python': [
            'html2text',
        ],
    },

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'mail',
        'generic_mixin',
        'crnd_web_diagram_plus',
        'web_widget_colorpicker',
        'web_settings_dashboard',
    ],

    # always loaded
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',

        'data/request_sequence.xml',
        'data/mail_subtype.xml',
        'data/request_stage_type.xml',
        'data/request_event_type.xml',
        'data/ir_cron.xml',

        'views/templates.xml',
        'views/request_views.xml',
        'views/res_config_settings_view.xml',
        'views/request_category_view.xml',
        'views/request_type_view.xml',
        'views/request_stage_route_view.xml',
        'views/request_stage_view.xml',
        'views/request_stage_type_view.xml',
        'views/request_request_view.xml',
        'views/res_partner_view.xml',
        'views/mail_templates.xml',
        'views/request_event.xml',
        'wizard/request_wizard_close_views.xml',
        'wizard/request_wizard_assign.xml',

        'templates/templates.xml',
    ],

    'qweb': [
        'static/src/xml/dashboard.xml'],

    'demo': [
        'demo/request_demo_users.xml',
        'demo/request_category_demo.xml',
        'demo/request_type_simple.xml',
        'demo/request_type_seq.xml',
        'demo/request_type_access.xml',
        'demo/request_type_non_ascii.xml',
    ],

    'images': ['static/description/banner.gif'],
    'installable': True,
    'application': True,
    'license': 'OPL-1',
}
