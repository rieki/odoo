# -*- coding: utf-8 -*-
{
    'name': "sale_credit_limit",

    'summary': """
       Credit Exception""",

    'description': """
        Modifies sale module, that adds a credit limit to every customers, a credit exception state is raised for customers who exceeds their credit limit which can be approved or denied. 
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account','sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/salexception.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}