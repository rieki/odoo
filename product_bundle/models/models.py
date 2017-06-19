# -*- coding: utf-8 -*-

import itertools
import psycopg2

import odoo.addons.decimal_precision as dp
from odoo import api, fields, models, tools, _
from odoo.exceptions import ValidationError, except_orm

class ProductTemplate (models.Model):
    _inherit = 'product.template'

    product_bundle_list = fields.One2many('product.bundle.line','product_bundle', string='Product Bundle', copy=True)
    bundle_okay = fields.Boolean('Bundle',default=False)
    amount_untaxed = fields.Monetary(string='Untaxed Amount', store=True, readonly=True, compute='_amount_all', track_visibility='always')
    amount_tax = fields.Monetary(string='Taxes', store=True, readonly=True, compute='_amount_all', track_visibility='always')
    amount_total = fields.Monetary(string='Total', store=True, readonly=True, compute='_amount_all', track_visibility='always')
    amount_cost = fields.Monetary(string='Cost', store=True, readonly=True, compute='_amount_all', track_visibility='always')

    @api.depends('product_bundle_list.price_total')
    def _amount_all(self):

        for product in self:
            amount_untaxed = amount_tax = amount_cost =0.0
            for line in product.product_bundle_list:
                amount_untaxed += line.price_subtotal
                amount_tax += line.price_tax
                amount_cost +=line.product_id.standard_price
            product.update({
                'amount_untaxed': amount_untaxed,
                'amount_tax': amount_tax,
                'amount_total': amount_untaxed + amount_tax,
                'list_price': amount_untaxed + amount_tax,
                'standard_price': amount_cost
            })

    @api.multi
    @api.onchange('bundle_okay')
    def untick_purchase(self):
    	if self.bundle_okay == True:
    		self.purchase_ok = False
