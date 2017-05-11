# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Order(models.Model):
  _inherit = 'sale.order'
  credit_raised = fields.Char(string='Credit Status',default='None',track_visibility='onchange')
  credit_limit = fields.Monetary(related='partner_id.credit_limit', string='Credit Limit',track_visibility='onchange')
  credit = fields.Monetary(related='partner_id.credit', string='Credit',track_visibility='onchange')
  credit_exceed = fields.Monetary(string='Credit Exceed',compute="_credit_exceed",track_visibility='onchange')

  state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('exception','Credit Exception'),
        ('sale', 'Sales Order'),
        ('done', 'Locked'),
        ('cancel', 'Cancelled'),
        ], string='Status', readonly=True, copy=False, index=True, track_visibility='onchange', default='draft')

  @api.multi
  def action_confirm(self):
    for order in self:
      if order.credit_limit == 0 or order.amount_total + order.credit < order.credit_limit or order.state == 'exception':
          if order.state == 'exception' or order.credit_raised == 'Denied':
            order.credit_raised = 'Approved'
          return super(Order, self).action_confirm()  
      else:
        self.credit_raised = 'For Approval'
        self.state = 'exception'

  @api.multi
  def action_exception(self):
     self.credit_raised = 'Denied'
     self.write({'state': 'draft'})

  @api.depends('credit_limit','amount_total','credit')
  def _credit_exceed(self):
        for r in self:
            if r.credit_limit == 0:
                r.credit_exceed = 0
            else:
                r.credit_exceed = (r.amount_total + r.credit ) - r.credit_limit



Order()
class Orders(models.Model):
  _inherit = 'sale.order.line'

  state = fields.Selection([
        ('draft', 'Quotation'),
        ('sent', 'Quotation Sent'),
        ('sale', 'Sale Order'),
        ('done', 'Done'),
        ('cancel', 'Cancelled'),
        ], related='order_id.state', string='Order Status', readonly=True, copy=False, store=True, default='draft')



