# -*- coding: utf-8 -*-
{
    'name': 'Louet Inc: Block E-commerce/ Shop Menu & its Sub-Menus from public users.',
    'summary': 'Restricting the website shop page access to public users',
    'sequence': 100,
    'license': 'OEEL-1',
    'website': 'https://www.odoo.com',
    'version': '1.1',
    'author': 'Odoo Inc',
    'description': """
    -  2308058
    """,
    'category': 'Custom Development',

    # any module necessary for this one to work correctly
    'depends': ['website','website_sale'],

    # always loaded
    'data': [],

    'installable': True,
    'application': True,
    'auto_install': False,
}