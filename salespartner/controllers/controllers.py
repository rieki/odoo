# -*- coding: utf-8 -*-
from odoo import http

# class Salespartner(http.Controller):
#     @http.route('/salespartner/salespartner/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/salespartner/salespartner/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('salespartner.listing', {
#             'root': '/salespartner/salespartner',
#             'objects': http.request.env['salespartner.salespartner'].search([]),
#         })

#     @http.route('/salespartner/salespartner/objects/<model("salespartner.salespartner"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('salespartner.object', {
#             'object': obj
#         })