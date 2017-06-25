# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models
from odoo.tools import float_round

class StockMove(models.Model):
    _inherit = "stock.move"

    @api.multi
    def action_done(self):
        result = super(StockMove, self).action_done()

        # Update delivered quantities on sale order lines
        sale_order_lines = self.filtered(lambda move: move.procurement_id.sale_line_id and move.product_id.expense_policy == 'no').mapped('procurement_id.sale_line_id')
        for line in sale_order_lines:
            if sale_order_lines.product_id.bundle_okay == True:
            line.qty_delivered = line._get_delivered_qty()
        return result
