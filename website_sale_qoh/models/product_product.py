# -*- coding: utf-8 -*-

from odoo import models
from odoo.http import request


class ProductProduct(models.Model):
    _inherit = 'product.product'

    def _get_cart_qty(self, website=None):
        website = website or self.env['website'].get_current_website()
        cart = website and request and hasattr(request, 'website') and website.sale_get_order() or None
        if cart:
            return sum(
                cart._get_common_product_lines(product=self).mapped('product_uom_qty')
            )
        else:
            return 0