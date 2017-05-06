# -*- coding: utf-8 -*-
{
    'name': "Sales Discount to Journal",

    'summary': """
       Add chargeability of Sales discount to an Accounting code""",

    'description': """
        Adds Charging of total Discount to a Sales Order. Chargeability depends on the accounting code set in the pricelist menu.
    """,

    'author': "Justin Talingdan",
    'website': "Rieki",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Sales',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','sale','product'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/views.xml',
        'views/sale_views.xml',
        'views/product_pricelist_views.xml',
        'views/templates.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}