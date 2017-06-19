# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

import odoo.addons.decimal_precision as dp

class ProductLine(models.Model):
    _name='product.bundle.line'
    product_bundle = fields.Many2one('product.template', string='Product Bundle', required=True, ondelete='cascade', index=True, copy=False)

    product_id = fields.Many2one('product.product', string='Product', change_default=True, ondelete='restrict', required=True)
    product_uom_qty = fields.Float(string='Quantity', digits=dp.get_precision('Product Unit of Measure'), required=True, default=1.0)
    product_uom = fields.Many2one('product.uom', string='Unit of Measure', required=True)
    price_unit = fields.Float('Unit Price', required=True, digits=dp.get_precision('Product Price'), default=0.0)
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', readonly=True, store=True)
    price_tax = fields.Monetary(compute='_compute_amount', string='Taxes', readonly=True, store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', readonly=True, store=True)
    currency_id = fields.Many2one("res.currency", related="product_id.currency_id",string="Currency", readonly=True, required=True)
    tax_id = fields.Many2many('account.tax', string='Taxes', domain=['|', ('active', '=', False), ('active', '=', True)])
    @api.depends('product_id','product_uom_qty', 'price_unit', 'tax_id')
    def _compute_amount(self):
        for line in self:
            taxes = line.tax_id.compute_all(line.price_unit, line.currency_id, line.product_uom_qty, product=line.product_id)
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })

    @api.multi
    @api.onchange('product_id')
    def product_id_change(self):
        if not self.product_id:
            return {'domain': {'product_uom': []}}

        vals = {}
        domain = {'product_uom': [('category_id', '=', self.product_id.uom_id.category_id.id)]}
        if not self.product_uom or (self.product_id.uom_id.id != self.product_uom.id):
            vals['product_uom'] = self.product_id.uom_id
            vals['product_uom_qty'] = 1.0

        product = self.product_id.with_context(
            quantity=vals.get('product_uom_qty') or self.product_uom_qty,
            uom=self.product_uom.id
        )

        vals['price_unit'] = self.env['account.tax']._fix_tax_included_price(product.lst_price, product.taxes_id, self.tax_id)
        self.update(vals)
        
        return {'domain': domain}

    @api.onchange('product_uom', 'product_uom_qty')
    def product_uom_change(self):
        if not self.product_uom:
            self.price_unit = 0.0
            return
        product = self.product_id.with_context(
            quantity=self.product_uom_qty,
            uom=self.product_uom.id
        )
        self.price_unit = self.env['account.tax']._fix_tax_included_price(product.lst_price, product.taxes_id, self.tax_id)
