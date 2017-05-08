# -*- coding: utf-8 -*-
from odoo import http

# class SaleCreditLimit(http.Controller):
#     @http.route('/sale_credit_limit/sale_credit_limit/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/sale_credit_limit/sale_credit_limit/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('sale_credit_limit.listing', {
#             'root': '/sale_credit_limit/sale_credit_limit',
#             'objects': http.request.env['sale_credit_limit.sale_credit_limit'].search([]),
#         })

#     @http.route('/sale_credit_limit/sale_credit_limit/objects/<model("sale_credit_limit.sale_credit_limit"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('sale_credit_limit.object', {
#             'object': obj
#         })