# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    is_broker_ship = fields.Boolean(string='Use For Broker Shipping',
                                    help='Check field for it to be used as the product for Shipping Cost for Shipping Broker')
