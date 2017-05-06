# -*- coding: utf-8 -*-
# Mark Justin Henry I. Talingdan
#Modify Pricelist to add new field Accounting code with relation to CoA Accounting code

from odoo import fields, models


class ProductPricelist(models.Model):
    _inherit = 'product.pricelist'

    acc_code_ids = fields.Many2one('account.account',
        ondelete='set null', string="Sales Expense")
