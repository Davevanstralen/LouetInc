# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    def _get_combination_info(self, combination=False, product_id=False, add_qty=1, pricelist=False, parent_combination=False, only_template=False):
        combination_info = super()._get_combination_info(
            combination=combination, product_id=product_id, add_qty=add_qty, pricelist=pricelist,
            parent_combination=parent_combination, only_template=only_template)
        if combination_info['product_id']:
            product = self.env['product.product'].sudo().browse(combination_info['product_id'])
            website = self.env['website'].get_current_website()
            combination_info.update({
                'free_qty': product.with_context(warehouse=website.warehouse_id.id).qty_available - product.with_context(warehouse=website.warehouse_id.id).outgoing_qty
            })
        return combination_info
