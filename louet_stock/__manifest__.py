# -*- coding: utf-8 -*-
{
    'name': "Louet Inc.: Shipping Details CSV in Email",

    'summary': """
        Louet Inc. ships all its products through a shipping broker. They need Request pickup of a shipment and Receive back cost and tracking information related to a shipment.""",

    'description': """
CIC - 
    
1.1. On validation of a picking (as specified in 1.2), an email is sent out to an email alias of the broker with a CSV file containing the fields highlighted in the attached file "Odoo Mapping.xlsl". I have mapped the broker's system's fields to Odoo's fields. The alias will be provided at a future date.

1.2. Louet will use a two-step shipping process consisting of a "pick" or "picking" and a "delivery" or "shipment". The picking must always precede the delivery and moves goods from WH/Stock to WH/Output. The delivery moves goods from WH/Output to Partner Locations/Customers. For the purposes of this document, picking means the second to last transfer in the chain of transfers related to a sales order. If there is only one transfer (which moves stock from WH/Stock to Virtual locations/Customers directly, that single transfer should be considered the picking.. 

2. The CSV should also contain a field stating whether it was sent from a production database or a test database as a way to indicate the broker to only process legitimate deliveries.  

3. The broker's system will report when an email was received successfully. This message should be shown in the chatter of the final delivery order as a message" Your shipment request has been successfully received".



Shipping Contact Details:-  it-support@sfi.ca  

    """,

    'author': "PS-US Odoo",
    'website': "http://www.odoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Custom Development',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
    ],
    'license': 'OEEL-1',
}
