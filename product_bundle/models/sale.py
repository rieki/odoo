# -*- coding: utf-8 -*-
from itertools import groupby
from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import float_is_zero, float_compare, DEFAULT_SERVER_DATETIME_FORMAT
from odoo.tools.misc import formatLang

class SaleOrders(models.Model):
    _inherit = 'sale.order.line'
    
    @api.multi
    def _action_procurement_create(self):
        """
        Create procurements based on quantity ordered. If the quantity is increased, new
        procurements are created. If the quantity is decreased, no automated action is taken.
        """
        precision = self.env['decimal.precision'].precision_get('Product Unit of Measure')
        new_procs = self.env['procurement.order']  # Empty recordset
        for line in self:
            if line.state != 'sale' or not line.product_id._need_procurement():
                continue
            qty = 0.0
            for proc in line.procurement_ids:
                qty += proc.product_qty
            if float_compare(qty, line.product_uom_qty, precision_digits=precision) >= 0:
                continue

            if not line.order_id.procurement_group_id:
                vals = line.order_id._prepare_procurement_group()
                line.order_id.procurement_group_id = self.env["procurement.group"].create(vals)
            if line.product_id.bundle_okay == True: 
                for bundle in line.product_id.product_bundle_list:
                    vals = line._prepare_order_line_procurement(group_id=line.order_id.procurement_group_id.id)
                    vals['product_id'] = bundle.product_id.id
                    vals['product_qty'] = (bundle.product_uom_qty - qty) * line.product_uom_qty
                    vals['product_uom'] = bundle.product_uom.id
                    new_proc = self.env["procurement.order"].with_context(procurement_autorun_defer=True).create(vals)
                    new_proc.message_post_with_view('mail.message_origin_link',
                        values={'self': new_proc, 'origin': line.order_id},
                        subtype_id=self.env.ref('mail.mt_note').id)
                    new_procs += new_proc
            else:
                vals = line._prepare_order_line_procurement(group_id=line.order_id.procurement_group_id.id)
                vals['product_qty'] = line.product_uom_qty - qty
                new_proc = self.env["procurement.order"].with_context(procurement_autorun_defer=True).create(vals)
                new_proc.message_post_with_view('mail.message_origin_link',
                    values={'self': new_proc, 'origin': line.order_id},
                    subtype_id=self.env.ref('mail.mt_note').id)
                new_procs += new_proc
        new_procs.run()
        return new_procs

    @api.onchange('product_uom_qty', 'product_uom', 'route_id')
    def _onchange_product_id_check_availability(self):
        err = 0
        message_store = []
        message ="Insufficient stock for the following: \n"
        if not self.product_id or not self.product_uom_qty or not self.product_uom:
            self.product_packaging = False
            return {}
        if self.product_id.bundle_okay == True:
            for line in self.product_id.product_bundle_list:
                precision = line.env['decimal.precision'].precision_get('Product Unit of Measure')
                product_qty = line.product_uom._compute_quantity(self.product_uom_qty, self.product_id.uom_id)
                if float_compare(line.product_id.virtual_available, product_qty, precision_digits=precision) == -1:
                    is_available = self._check_routing()
                    if not is_available:
                        err = err + 1
                        title = _('Not enough inventory!')
                        message_store = _('-Bundle contains %s %s of %s but you only have %s %s available!') % \
                                (line.product_uom_qty, line.product_uom.name, line.product_id.name,line.product_id.virtual_available, line.product_id.uom_id.name)
                        message += message_store + "\n"

            if err != 0:
                warning_mess={
                'title': title,
                'message': message
                }
                return {'warning': warning_mess}
            else:
                return{}
        else:
            return super(SaleOrders, self)._onchange_product_id_check_availability()  









