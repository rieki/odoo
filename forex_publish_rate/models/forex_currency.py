# -*- coding: utf-8 -*-

from odoo import fields, api, models

class ResCurrencyRate(models.Model):
    _inherit = "res.currency.rate"
    
    publish_rate = fields.Float(string='Published Rate', digits=(12, 6),readonly=True, help='The published rate of currency')