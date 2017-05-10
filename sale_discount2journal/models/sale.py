# -*- coding: utf-8 -*-
# Mark Justin Henry I. Talingdan
#Modify Sales Order to show discount amount and discount total

from odoo import fields, models, api


class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    #PHMTB4 add total discount field and undiscounted amount to SO
    amount_total_discount = fields.Monetary(string='Total Discount', store=True, readonly=True, compute='_amount_all', track_visibility='always')
    amount_total_base = fields.Monetary(string='Base Amount', store=True, readonly=True, compute='_amount_all', track_visibility='always')
    
    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        #PHMTB4 add amount_undiscounted, amount_discount
        for order in self:
            amount_untaxed = amount_tax = 0.0
            amount_discount = 0.0
            amount_undiscounted = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal 
                amount_undiscounted += line.price_unit * line.product_uom_qty
                
                #amount_discount += (line.price_unit - line.price_reduce) * (line.product_uom_qty)
                amount_discount += (line.price_subtotal - line.price_unit * line.product_uom_qty)
                # FORWARDPORT UP TO 10.0
                if order.company_id.tax_calculation_rounding_method == 'round_globally':
                    price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
                    taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_id)
                    amount_tax += sum(t.get('amount', 0.0) for t in taxes.get('taxes', []))
                else:
                    amount_tax += line.price_tax
            order.update({
                'amount_untaxed': order.pricelist_id.currency_id.round(amount_untaxed),
                'amount_tax': order.pricelist_id.currency_id.round(amount_tax),
                'amount_total': amount_untaxed + amount_tax,
              #PHMTB4
                'amount_total_discount': order.pricelist_id.currency_id.round(amount_discount),
                'amount_total_base' : order.pricelist_id.currency_id.round(amount_undiscounted)
            }) 
            
'''
class SaleOrderLine(models.Model):           
    _inherit = 'sale.order.line' 
    
    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            #price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            price = line.price_unit
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_id)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })    
'''   
    

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):

        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_id)
            #PHMTB4 add discount amount in array Line
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
                'price_discountsubtotal': (line.price_unit - line.price_reduce) * (line.product_uom_qty),
                #'price_subtotal_undiscounted': taxes['total_excluded'] - 
            })

    #PHMTB4 new price_discountamount, price_subtotal_undiscounted
    price_discountsubtotal = fields.Float(compute='_compute_amount', string='Discount Amount', require=True, readonly=True, store=True)
    #price_subtotal_undiscounted = fields.Monetary(compute='_compute_amount', string='Undiscounted Subtotal', readonly=True, store=True)
