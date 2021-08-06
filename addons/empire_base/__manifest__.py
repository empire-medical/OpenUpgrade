# -*- coding: utf-8 -*-
{
    'name': "Empire Base",

    'summary': """
        This module adds fields necessary for Empires export process""",

    'description': """
        This module adds fields necessary for Empires export process
    """,

    'author': "Empire Medical",
    'website': "https://www.empire-medical.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/14.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '14.0.1.0.1',
    
    # any module necessary for this one to work correctly
    'depends': ['base', 'account_accountant'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'data/analytic_accounts.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
