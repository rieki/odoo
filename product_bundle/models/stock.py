# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models
from odoo.tools import float_round

class ReportDelivery(models.AbstractModels):
    name = "report.stock.report_deliveryslip"


    @api.model
    def render_html(self, docids, data=None):
        #stock = self.env['stock.picking'].browse(docids)
        data = dict(data or {})
        #stock.orogin = 'Hello'
        docs.update(self.origin('hello'))
        report_obj = self.env['report']
        report = report_obj._get_report_from_name('stock.report_deliveryslip')
        docargs = {
            'doc_ids': data.get('ids', data.get('active_ids')),
            'doc_model': 'stock.picking',
            'docs': stock,
        }
    
        return report_obj.render('stock.report_deliveryslip', docargs)

