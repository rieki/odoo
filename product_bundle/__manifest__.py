# -*- coding: utf-8 -*-
{
    'name': "product_bundle",

    'summary': """
        Product bundle""",

    'description': """
        This module allows creation fo product bundle, products can be sold in group, sale and cost of the product bundle can be modified.
    """,

    'author': "My Company",
    'website': "http://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','product','sale','decimal_precision','account','stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/product_line.xml',
        'views/templates.xml',
        'views/product_bundle_menu.xml',
        'views/delivery_report.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}