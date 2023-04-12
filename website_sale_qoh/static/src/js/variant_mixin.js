odoo.define('website_sale_qoh.VariantMixin', function (require) {
    'use strict';
    
    const {Markup} = require('web.utils');
    var website_sale_stock_VariantMixin = require('website_sale_stock.VariantMixin')
    var core = require('web.core');
    var QWeb = core.qweb;
    
    website_sale_stock_VariantMixin._onChangeCombinationStock = function (ev, $parent, combination) {
        let product_id = 0;
        if ($parent.find('input.product_id:checked').length) {
            product_id = $parent.find('input.product_id:checked').val();
        } else {
            product_id = $parent.find('.product_id').val();
        }
        const isMainProduct = combination.product_id &&
            ($parent.is('.js_main_product') || $parent.is('.main_product')) &&
            combination.product_id === parseInt(product_id);
    
        if (!this.isWebsite || !isMainProduct){
            return;
        }
    
        const $addQtyInput = $parent.find('input[name="add_qty"]');
        let qty = $addQtyInput.val();
        let ctaWrapper = $parent[0].querySelector('#o_wsale_cta_wrapper');
        ctaWrapper.classList.replace('d-none', 'd-flex');
        ctaWrapper.classList.remove('out_of_stock');
    
        if (combination.product_type === 'product' && !combination.allow_out_of_stock_order) {
            combination.free_qty -= parseInt(combination.cart_qty);
            $addQtyInput.data('max', combination.free_qty || 1);
            if (combination.free_qty < 0) {
                combination.free_qty = 0;
            }
            if (qty > combination.free_qty) {
                qty = combination.free_qty || 1;
                $addQtyInput.val(qty);
            }
            if (combination.free_qty < 1) {
                ctaWrapper.classList.replace('d-flex', 'd-none');
                ctaWrapper.classList.add('out_of_stock');
            }
        }
    
        if (combination.product_type === 'product' && combination.allow_out_of_stock_order) {
            combination.free_qty -= parseInt(combination.cart_qty);
        }
    
        $('.oe_website_sale')
            .find('.availability_message_' + combination.product_template)
            .remove();
        combination.has_out_of_stock_message = $(combination.out_of_stock_message).text() !== '';
        combination.out_of_stock_message = Markup(combination.out_of_stock_message);
        const $message = $(QWeb.render(
            'website_sale_stock.product_availability',
            combination
        ));
        $('div.availability_messages').html($message);
    };
});
    