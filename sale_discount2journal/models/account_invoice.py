# -*- coding: utf-8 -*-
# PHMTB4

from itertools import groupby
from odoo import api, fields, models, _
from odoo.tools import float_is_zero, float_compare

class AccountInvoice(models.Model):
    _inherit = 'account.invoice'   
    amt_total_discount = fields.Monetary(string='Sales Discount',
        store=True, readonly=True, compute='_compute_amount')
    
    amt_tax_with_discount = fields.Monetary(string='Tax Discount',
        store=True, readonly=True, compute='_compute_amount')
    #add field for tax reversal and dicount
    #account_tax_reversal_id = fields.Many2one('account.account', string='Tax Reversal Account',
        #required=True, help="The tax reversal account used for this invoice.")    
    #account_discount_id = fields.Many2one('account.account', string='Discount Account',
        #required=True, help="The discount account used for this invoice.")
    account_tax_reversal_id = fields.Integer()
    account_discount_id = fields.Integer()
    @api.one
    @api.depends(
        'state', 'currency_id', 'invoice_line_ids.price_subtotal',
        'move_id.line_ids.amount_residual',
        'move_id.line_ids.currency_id')
    def _compute_residual(self):
        residual = 0.0
        residual_company_signed = 0.0
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        for line in self.sudo().move_id.line_ids:
            if line.account_id.internal_type in ('receivable', 'payable'):
                residual_company_signed += line.amount_residual
                if line.currency_id == self.currency_id:
                    residual += line.amount_residual_currency if line.currency_id else line.amount_residual
                else:
                    from_currency = (line.currency_id and line.currency_id.with_context(date=line.date)) or line.company_id.currency_id.with_context(date=line.date)
                    residual += from_currency.compute(line.amount_residual, self.currency_id)
                    
        #Add discounts to computation of residual            
        #residual_company_signed = residual_company_signed - (self.amount_total_discount + self.amount_tax_discounted)
        #residual = residual - (self.amount_total_discount + self.amount_tax_discounted)
        
        self.residual_company_signed = abs(residual_company_signed) * sign
        self.residual_signed = abs(residual) * sign
        self.residual = abs(residual)
        digits_rounding_precision = self.currency_id.rounding
        if float_is_zero(self.residual, precision_rounding=digits_rounding_precision):
            self.reconciled = True
        else:
            self.reconciled = False    
            
    @api.one
    @api.depends('invoice_line_ids.price_subtotal', 'tax_line_ids.amount', 'currency_id', 'company_id', 'date_invoice', 'type')
    def _compute_amount(self):
        self.amount_untaxed = sum(line.price_subtotal for line in self.invoice_line_ids)
        self.amount_tax = sum(line.amount for line in self.tax_line_ids)
        self.amount_total = self.amount_untaxed + self.amount_tax

        amount_total_discounted = 0.0
        amount_untaxed_temp = self.amount_untaxed
        
        for line in self.invoice_line_ids:
            self.amt_total_discount += line.price_subtotal - ( line.price_subtotal * (1 - (line.discount or 0.0) / 100.0))       
        
        amount_total_discounted = self.amount_untaxed - self.amt_total_discount
        
        if self.amount_untaxed:
            self.amt_tax_with_discount = self.amount_tax - (self.amount_tax * amount_total_discounted)/self.amount_untaxed
        
        amount_total_company_signed = self.amount_total
        amount_untaxed_signed = self.amount_untaxed
        
        if self.currency_id and self.company_id and self.currency_id != self.company_id.currency_id:
            currency_id = self.currency_id.with_context(date=self.date_invoice)
            amount_total_company_signed = currency_id.compute(self.amount_total, self.company_id.currency_id)
            amount_untaxed_signed = currency_id.compute(self.amount_untaxed, self.company_id.currency_id)
        
        sign = self.type in ['in_refund', 'out_refund'] and -1 or 1
        self.amount_total_company_signed = amount_total_company_signed * sign
        self.amount_total_signed = self.amount_total * sign
        self.amount_untaxed_signed = amount_untaxed_signed * sign
    
    @api.multi
    def get_taxes_values(self):
        tax_grouped = {}
        for line in self.invoice_line_ids:
            #price_unit = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            price_unit = line.price_unit
            taxes = line.invoice_line_tax_ids.compute_all(price_unit, self.currency_id, line.quantity, line.product_id, self.partner_id)['taxes']
            for tax in taxes:
                val = self._prepare_tax_line_vals(line, tax)
                key = self.env['account.tax'].browse(tax['id']).get_grouping_key(val)

                if key not in tax_grouped:
                    tax_grouped[key] = val
                else:
                    tax_grouped[key]['amount'] += val['amount']
                    tax_grouped[key]['base'] += val['base']
        return tax_grouped
      
    '''New function to get the account codes from Sales Orders'''
    @api.one
    def get_account_code_discount(self, vals):
        acc_code_disc = vals.get('account_discount_id')
        acc_code_tax_rev = vals.get('account_tax_reversal_id')
        self.discount_account_code = acc_code_disc
        self.tax_reversal_account_code = acc_code_tax_rev


class AccountInvoiceLine(models.Model):
    _inherit = 'account.invoice.line'
    #_order = 'invoice_id, layout_category_id, sequence, id'

    @api.one
    @api.depends('price_unit', 'discount', 'invoice_line_tax_ids', 'quantity',
        'product_id', 'invoice_id.partner_id', 'invoice_id.currency_id', 'invoice_id.company_id',
        'invoice_id.date_invoice')
    def _compute_price(self):
        currency = self.invoice_id and self.invoice_id.currency_id or None
        #price = self.price_unit * (1 - (self.discount or 0.0) / 100.0)
        price = self.price_unit
        taxes = False
        if self.invoice_line_tax_ids:
            taxes = self.invoice_line_tax_ids.compute_all(price, currency, self.quantity, product=self.product_id, partner=self.invoice_id.partner_id)
        self.price_subtotal = price_subtotal_signed = taxes['total_excluded'] if taxes else self.quantity * price
        if self.invoice_id.currency_id and self.invoice_id.company_id and self.invoice_id.currency_id != self.invoice_id.company_id.currency_id:
            price_subtotal_signed = self.invoice_id.currency_id.with_context(date=self.invoice_id.date_invoice).compute(price_subtotal_signed, self.invoice_id.company_id.currency_id)
        sign = self.invoice_id.type in ['in_refund', 'out_refund'] and -1 or 1
        self.price_subtotal_signed = price_subtotal_signed * sign
        
        
