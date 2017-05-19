# -*- coding: utf-8 -*-
{
    'name': "Forex Publish Rate",

    'summary': """
       Add Forex publish rate in Currency Maintenance Page""",

    'description': """
        Add Forex publish rate in Currency Maintenance Page
    """,

    'author': "Justin Talingdan",
    'website': "Rieki.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/templates.xml',
        'views/forex_currency_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}