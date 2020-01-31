# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'eCommerce Qty On Hand',
    'summary': 'eCommerce Qty On Hand',
    'sequence': 100,
    'license': 'OEEL-1',
    'website': 'https://www.odoo.com',
    'version': '1.0',
    'author': 'Odoo Inc',
    'description': """
eCommerce Qty On Hand
=====================
    """,
    'category': 'Custom Development',
    'depends': ['sale', 'website_sale', 'website_sale_stock'],
    'data': [
        'views/website_sale_stock_template.xml',
    ],
    'demo': [],
    'qweb': ['static/src/xml/website_sale_stock_product_availability.xml'],
    'installable': True,
    'application': False,
    'auto_install': False,
}
