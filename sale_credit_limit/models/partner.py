# -*- coding: utf-8 -*-

from odoo import models, fields, api

class Partner(models.Model):
   _inherit = 'res.partner'

   credit_limit = fields.Monetary(string="Credit Limit", default=0)
