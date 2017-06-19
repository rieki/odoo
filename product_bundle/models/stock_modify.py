# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

import odoo.addons.decimal_precision as dp

class StockModify(models.Model):
    _inherit='procurement.order'
    

    def _get_stock_move_values(self):

        if self.product_id:
            for line in self.product_id.product_bundle_list:
                return {
                'product_id': line.product_id.id,
                'product_uom': line.product_uom.id,
                'product_uom_qty': qty_left,
                }
        return super(StockModify, self)._get_stock_move_values()
