# -*- coding: utf-8 -*-
from odoo import http

# class ProductBundle(http.Controller):
#     @http.route('/product_bundle/product_bundle/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/product_bundle/product_bundle/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('product_bundle.listing', {
#             'root': '/product_bundle/product_bundle',
#             'objects': http.request.env['product_bundle.product_bundle'].search([]),
#         })

#     @http.route('/product_bundle/product_bundle/objects/<model("product_bundle.product_bundle"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('product_bundle.object', {
#             'object': obj
#         })