# -*- coding: utf-8 -*-
{
    'name': "Louet Inc.: Shipping Broker Files",

    'summary': """
        Louet Inc. ships all its products through a shipping broker. They need Request pickup of a shipment and Receive back cost and tracking information related to a shipment.""",

    'description': """
CIC - [2178896]
    
1.1. On validation of a picking (as specified in 1.2), an email is sent out to an email alias of the broker with a CSV file containing the fields highlighted in the attached file "Odoo Mapping.xlsl". I have mapped the broker's system's fields to Odoo's fields. The alias will be provided at a future date.

1.2. Louet will use a two-step shipping process consisting of a "pick" or "picking" and a "delivery" or "shipment". The picking must always precede the delivery and moves goods from WH/Stock to WH/Output. The delivery moves goods from WH/Output to Partner Locations/Customers. For the purposes of this document, picking means the second to last transfer in the chain of transfers related to a sales order. If there is only one transfer (which moves stock from WH/Stock to Virtual locations/Customers directly, that single transfer should be considered the picking.. 

2. The CSV should also contain a field stating whether it was sent from a production database or a test database as a way to indicate the broker to only process legitimate deliveries.  

3. The broker's system will report when an email was received successfully. This message should be shown in the chatter of the final delivery order as a message" Your shipment request has been successfully received".

New requests:
Sending Information: 

Initially, the plan was to send the CSV file containing the information to a specific email alias. However, now due to a system change, we will need to upload this file to an FTP server ( FSTP ) of Ebridge. The trigger point is the same as above  -  When a picking slip to transfer products to WH/Output is validated. 

Ebridge website - http://www.ebridge.com

Receiving Information:- Extra 8 hours
When the delivery is made in the real world, Ebridge will upload the information on a file with the Delivery Order Number ( Primary Key), Tracking Number, Carrier Name and Shipping cost will be read A shipping cost line item will be added on that specific SO. I am still waiting on the file type information. Refer to the below Technical Support ticket for this information: 

Currently, the " Tracking Number" and " Carrier Name" field is being populated on the Pick Slip. This requires to be populated on the Delivery Warehouse Slip ( WH/OUT/ ****) so that the shipping email that gets sent automatically upon validation contains the information. 

    """,

    'author': "PS-US Odoo",
    'website': "http://www.odoo.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Custom Development',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['stock', 'sale'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/res_config_settings_views.xml',
        'views/stock_views.xml',
        'views/product_views.xml',
        'data/actions.xml',
    ],
    'license': 'OEEL-1',
}
