
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

class AccountPayment(models.Model):
    _inherit = 'account.payment'  
    
        
    def _get_discount_move_line(self, debit2, credit2, amount_currency, move_id, name, account_id, invoice_id=False):
        """ dict for discount move line
        """
        return {
            'partner_id': self.payment_type in ('inbound', 'outbound') and self.env['res.partner']._find_accounting_partner(self.partner_id).id or False,
            'invoice_id': invoice_id and invoice_id.id or False,
            'move_id': move_id,
            'debit': debit2,
            'amount_currency': amount_currency or False,
            'name': name,
            'account_id': account_id,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
            'payment_id': self.id,
        }     
    def _get_tax_reversal_move_line(self, debit2, credit2, amount_currency, move_id, name, account_id, invoice_id=False):
        """ dict for tax reversal line
        """
        return {
            'partner_id': self.payment_type in ('inbound', 'outbound') and self.env['res.partner']._find_accounting_partner(self.partner_id).id or False,
            'invoice_id': invoice_id and invoice_id.id or False,
            'move_id': move_id,
            'debit': debit2,
            'amount_currency': amount_currency or False,
            'name': name,
            'account_id': account_id,
            'journal_id': self.journal_id.id,
            'currency_id': self.currency_id != self.company_id.currency_id and self.currency_id.id or False,
            'payment_id': self.id,
        }
      
    def get_discount_account_codes():
      """Get Accounting Codes tied up to Invoice to be paid."""
      
     
    def _create_payment_entry(self, amount):
        """ Modified Move Lines for Liquidity, A/R, and add for Discounts + Tax Reversal
            to check: Super() cannot be called on this method since return value is from account.move -> _create()
        """
        aml_obj = self.env['account.move.line'].with_context(check_move_validity=False)
        invoice_currency = False
        
        total_invoices_discounts = sum(invoice.amt_total_discount for invoice in self.invoice_ids)
        total_invoices_tax_discounts = sum(invoice.amt_tax_with_discount for invoice in self.invoice_ids)
        
        discount_account_id = self.invoice_ids[0].account_discount_id
        tax_reversal_account_id = self.invoice_ids[0].account_tax_reversal_id
        
        
        if self.invoice_ids and all([x.currency_id == self.invoice_ids[0].currency_id for x in self.invoice_ids]):
            #if all the invoices selected share the same currency, record the payment in that currency too
            invoice_currency = self.invoice_ids[0].currency_id
        debit, credit, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(amount, self.currency_id, self.company_id.currency_id, invoice_currency)
        
        move = self.env['account.move'].create(self._get_move_vals())

        #Write line corresponding to invoice payment
        
        counterpart_aml_dict = self._get_shared_move_line_vals(debit, credit, amount_currency, move.id, False)
        counterpart_aml_dict.update(self._get_counterpart_move_line_vals(self.invoice_ids))
        counterpart_aml_dict.update({'currency_id': currency_id})
        counterpart_aml = aml_obj.create(counterpart_aml_dict)
        
        #Add discount move line
        amount_discount = total_invoices_discounts #to change new function
        
        #format values base on amount (negative is credit positive is debit)
        debit_discount = amount_discount > 0 and amount_discount or 0.0
        credit_discount = amount_discount < 0 and -amount_discount or 0.0
        
        disc_aml_dict = self._get_discount_move_line(debit_discount, credit_discount, amount_currency, move.id, 'Sales Discounts', discount_account_id, False)
        disc_aml_dict.update({'currency_id': currency_id})
        disc_aml_dict = aml_obj.create(disc_aml_dict)
        
        #Add tax reversal move line
        tax_discount = total_invoices_tax_discounts #to change new function
        
        #format values base on amount (negative is credit positive is debit)
        debit_tax_reversal = tax_discount > 0 and tax_discount or 0.0
        credit_tax_reversal = tax_discount < 0 and -tax_discount or 0.0
        
        tax_r_aml_dict = self._get_tax_reversal_move_line(debit_tax_reversal, credit_tax_reversal, amount_currency, move.id, 'Tax Discounts', tax_reversal_account_id, False)
        tax_r_aml_dict.update({'currency_id': currency_id})
        tax_r_aml_dict = aml_obj.create(tax_r_aml_dict)
        
        
        #Reconcile with the invoices
        if self.payment_difference_handling == 'reconcile' and self.payment_difference:
            writeoff_line = self._get_shared_move_line_vals(0, 0, 0, move.id, False)
            amount_currency_wo, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(self.payment_difference, self.currency_id, self.company_id.currency_id, invoice_currency)[2:]
            # the writeoff debit and credit must be computed from the invoice residual in company currency
            # minus the payment amount in company currency, and not from the payment difference in the payment currency
            # to avoid loss of precision during the currency rate computations. See revision 20935462a0cabeb45480ce70114ff2f4e91eaf79 for a detailed example.
            total_residual_company_signed = sum(invoice.residual_company_signed for invoice in self.invoice_ids)
            total_payment_company_signed = self.currency_id.with_context(date=self.payment_date).compute(self.amount, self.company_id.currency_id)
            if self.invoice_ids[0].type in ['in_invoice', 'out_refund']:
                amount_wo = total_payment_company_signed - total_residual_company_signed
            else:
                amount_wo = total_residual_company_signed - total_payment_company_signed
            debit_wo = amount_wo > 0 and amount_wo or 0.0
            credit_wo = amount_wo < 0 and -amount_wo or 0.0
            writeoff_line['name'] = _('Counterpart')
            writeoff_line['account_id'] = self.writeoff_account_id.id
            writeoff_line['debit'] = debit_wo
            writeoff_line['credit'] = credit_wo
            writeoff_line['amount_currency'] = amount_currency_wo
            writeoff_line['currency_id'] = currency_id
            writeoff_line = aml_obj.create(writeoff_line)
            if counterpart_aml['debit']:
                counterpart_aml['debit'] += credit_wo - debit_wo
            if counterpart_aml['credit']:
                counterpart_aml['credit'] += debit_wo - credit_wo
            counterpart_aml['amount_currency'] -= amount_currency_wo
        self.invoice_ids.register_payment(counterpart_aml)

        #Write counterpart lines
        if not self.currency_id != self.company_id.currency_id:
            amount_currency = 0

        '''get invoices discount and tax discount, deduct to liquidity account CASH'''
        amount_full = amount + (total_invoices_discounts + total_invoices_tax_discounts)

        #Compute new amounts for Cash/Liquidity Move Line
        debit_cash, credit_cash, amount_currency, currency_id = aml_obj.with_context(date=self.payment_date).compute_amount_fields(amount_full, self.currency_id, self.company_id.currency_id, invoice_currency)
  
        liquidity_aml_dict = self._get_shared_move_line_vals(credit_cash, debit_cash, -amount_currency, move.id, False)
        liquidity_aml_dict.update(self._get_liquidity_move_line_vals(-amount))
        aml_obj.create(liquidity_aml_dict)

        move.post()
        return move
