# -*- coding: utf-8 -*-
# Mark Justin Henry I. Talingdan
#Modify Sales Order to show discount amount and discount total

from odoo import fields, models, api
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT

class SaleOrder(models.Model):
    _inherit = 'sale.order'
    
    #add total discount field and undiscounted amount to SO
    amount_total_discount = fields.Monetary(string='Total Discount', store=True, readonly=True, compute='_amount_all', track_visibility='always')
    amount_total_base = fields.Monetary(string='Base Amount', store=True, readonly=True, compute='_amount_all', track_visibility='always')
    
    @api.depends('order_line.price_total')
    def _amount_all(self):
        """
        Compute the total amounts of the SO.
        """
        #add amount_undiscounted, amount_discount
        for order in self:
            amount_untaxed = amount_tax = 0.0
            amount_discount = 0.0
            amount_undiscounted = 0.0
            for line in order.order_line:
                amount_untaxed += line.price_subtotal 
                amount_undiscounted += line.price_unit * line.product_uom_qty
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
                'amount_total_discount': order.pricelist_id.currency_id.round(amount_discount),
                'amount_total_base' : order.pricelist_id.currency_id.round(amount_undiscounted)
            })
            
    '''@api.multi
    def _prepare_invoice(self):
        """
        Override dict of values for invoice creation. Add 
        """  
        rec = super(SaleOrder, self)._prepare_invoice()
        inv_obj = self.env['account.invoice']
        discount_account = self.pricelist_id.acc_code_ids,
        tax_rev_account = self.pricelist_id.tax_reversal_code_ids
        inv_obj.get_account_code_discount(discount_account, tax_rev_account)
        return rec'''
    
    @api.multi
    def action_invoice_create(self, grouped=False, final=False):
        """
        Create the invoice associated to the SO.
        :param grouped: if True, invoices are grouped by SO id. If False, invoices are grouped by
                        (partner_invoice_id, currency)
        :param final: if True, refunds will be generated if necessary
        :returns: list of created invoices
        """
        inv_obj = self.env['account.invoice']
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        invoices = {}
        references = {}
        for order in self:
            group_key = order.id if grouped else (order.partner_invoice_id.id, order.currency_id.id)
            for line in order.order_line.sorted(key=lambda l: l.qty_to_invoice < 0):
                if float_is_zero(line.qty_to_invoice, precision_digits=precision):
                    continue
                if group_key not in invoices:
                    inv_data = order._prepare_invoice()
                    #update dict of invoice data
                    inv_data.update({
                        'account_discount_id': self.pricelist_id.acc_code_ids,
                        'account_tax_reversal_id': self.pricelist_id.tax_reversal_code_ids
                    })
                    accounts = inv_obj.get_account_code_discount(inv_data)
                    invoice = inv_obj.create(inv_data)
                    references[invoice] = order
                    invoices[group_key] = invoice
                elif group_key in invoices:
                    vals = {}
                    if order.name not in invoices[group_key].origin.split(', '):
                        vals['origin'] = invoices[group_key].origin + ', ' + order.name
                    if order.client_order_ref and order.client_order_ref not in invoices[group_key].name.split(', '):
                        vals['name'] = invoices[group_key].name + ', ' + order.client_order_ref
                    invoices[group_key].write(vals)
                if line.qty_to_invoice > 0:
                    line.invoice_line_create(invoices[group_key].id, line.qty_to_invoice)
                elif line.qty_to_invoice < 0 and final:
                    line.invoice_line_create(invoices[group_key].id, line.qty_to_invoice)

            if references.get(invoices.get(group_key)):
                if order not in references[invoices[group_key]]:
                    references[invoice] = references[invoice] | order

        if not invoices:
            raise UserError(_('There is no invoicable line.'))

        for invoice in invoices.values():
            if not invoice.invoice_line_ids:
                raise UserError(_('There is no invoicable line.'))
            # If invoice is negative, do a refund invoice instead
            if invoice.amount_untaxed < 0:
                invoice.type = 'out_refund'
                for line in invoice.invoice_line_ids:
                    line.quantity = -line.quantity
            # Use additional field helper function (for account extensions)
            for line in invoice.invoice_line_ids:
                line._set_additional_fields(invoice)
            # Necessary to force computation of taxes. In account_invoice, they are triggered
            # by onchanges, which are not triggered when doing a create.
            invoice.compute_taxes()
            invoice.message_post_with_view('mail.message_origin_link',
                values={'self': invoice, 'origin': references[invoice]},
                subtype_id=self.env.ref('mail.mt_note').id)
        return [inv.id for inv in invoices.values()]
      
class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    @api.depends('product_uom_qty', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):

        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.product_uom_qty, product=line.product_id, partner=line.order_id.partner_id)
            #add discount amount in array Line
            line.update({
                'price_tax': taxes['total_included'] - taxes['total_excluded'],
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
                'price_discountsubtotal': (line.price_unit - line.price_reduce) * (line.product_uom_qty)
            })

    #new field for discount subtotal
    price_discountsubtotal = fields.Float(compute='_compute_amount', string='Discount Amount', require=True, readonly=True, store=True)
 