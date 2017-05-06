# -*- coding: utf-8 -*-
from odoo import http

# class SaleDiscount2journal(http.Controller):
#     @http.route('/sale_discount2journal/sale_discount2journal/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_discount2journal/sale_discount2journal/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_discount2journal.listing', {
#             'root': '/sale_discount2journal/sale_discount2journal',
#             'objects': http.request.env['sale_discount2journal.sale_discount2journal'].search([]),
#         })

#     @http.route('/sale_discount2journal/sale_discount2journal/objects/<model("sale_discount2journal.sale_discount2journal"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_discount2journal.object', {
#             'object': obj
#         })