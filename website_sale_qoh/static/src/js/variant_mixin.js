/** @odoo-module **/

import VariantMixin from "website_sale_stock.VariantMixin";
import "website_sale.website_sale";

const oldChangeCombinationStock = VariantMixin._onChangeCombinationStock;
/**
 * @override
 */
VariantMixin._onChangeCombinationStock = function (ev, $parent, combination) {
    if (combination.product_type === 'product' && combination.allow_out_of_stock_order) {
        combination.free_qty -= parseInt(combination.cart_qty);
    }
    oldChangeCombinationStock.apply(this, arguments);
}
