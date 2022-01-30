# -*- coding: utf-8 -*-
{
    'name': "help_desk_ticket",

    'summary': """ Extending functionalities to Helpdesk module""",

    'description': """
        Extending functionalities to Helpdesk module
    """,

    'sequence': -15,


    'author': "Raveel",
    'website': "http://www.z2c.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '1.0',

    # any module necessary for this one to work correctly
    'depends': ['base','helpdesk','mail'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/views.xml',
        'views/email_templete.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
