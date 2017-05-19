# -*- coding: utf-8 -*-
from odoo import http

# class ForexPublishRate(http.Controller):
#     @http.route('/forex_publish_rate/forex_publish_rate/', auth='public')
#     def index(self, **kw):
#         return "Hello, world"

#     @http.route('/forex_publish_rate/forex_publish_rate/objects/', auth='public')
#     def list(self, **kw):
#         return http.request.render('forex_publish_rate.listing', {
#             'root': '/forex_publish_rate/forex_publish_rate',
#             'objects': http.request.env['forex_publish_rate.forex_publish_rate'].search([]),
#         })

#     @http.route('/forex_publish_rate/forex_publish_rate/objects/<model("forex_publish_rate.forex_publish_rate"):obj>/', auth='public')
#     def object(self, obj, **kw):
#         return http.request.render('forex_publish_rate.object', {
#             'object': obj
#         })