# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'eCommerce Qty On Hand',
    'summary': 'eCommerce Qty On Hand',
    'sequence': 100,
    'license': 'OPL-1',
    'website': 'https://www.odoo.com',
    'version': '1.3',
    'author': 'Odoo Inc',
    'description': """
eCommerce Qty On Hand
=====================
    """,
    'category': 'Custom Development',
    'depends': ['website_sale_stock'],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'assets': {
        'web.assets_frontend': [
            'website_sale_qoh/static/src/js/*',
            'website_sale_qoh/static/src/xml/*',
        ],
    },
}
