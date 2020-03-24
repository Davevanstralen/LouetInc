# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import csv
import base64

from odoo import api, fields, models, _
from datetime import datetime, timedelta


class PickingType(models.Model):
    _inherit = 'stock.picking.type'

    send_email = fields.Boolean(string='Send Broker Email',
                                help='Check to enable sending broker email at validation of transfer with this operation type')


class Picking(models.Model):
    _inherit = 'stock.picking'

    def create_csv_data(self):
        sale_id = self.group_id.sale_id
        lines = [{'number': self.name,
                  'date': sale_id.date_order,
                  'sales_order_number': sale_id.name,
                  'currency': sale_id.currency_id,
                  'soldto_company': '',
                  'soldto_address': '',
                  'soldto_address2': '',
                  'soldto_city': '',
                  'soldto_state_province': '',
                  'soldto_postal_code': '',
                  'soldto_country': '',
                  'soldto_telephone': '',
                  'soldto_contact_email': '',
                  'soldto_tax_id': '',
                  'shipto_company': '',
                  'shipto_address1': '',
                  'shipto_address2': '',
                  'shipto_city': '',
                  'shipto_state_provice': '',
                  'shipto_postal_code': '',
                  'shipto_country': '',
                  'shipto_contact_telephone': '',
                  'shipto_contact_email': '',
                  'shipto_tax_id': '',
                  'ship_by_date': '',
                  'deliver_by_date': '',
                  'line_number': '',
                  'part_number': '',
                  'part_description': '',
                  'quantity_ordered': '',
                  'quantity_shiped': '',
                  'unit_price': '',
                  'database_type': ''}]

    # Create xls file for broker report
    def create_broker_report(self):
        report_name = '{company}_shipping_{date}'.format(company=self.company_id.name,
                                                         date=datetime.now().strftime("%Y_%m_%d"))
        filename = "%s.%s" % (report_name, "csv")
        print(filename)

        with open(filename, mode='w') as broker_file:
            fieldnames = ['number', 'date', 'sales_order_number', 'currency', 'soldto_company', 'soldto_address',
                          'soldto_address2', 'soldto_city', 'soldto_state_province', 'soldto_postal_code',
                          'soldto_country',
                          'soldto_telephone', 'soldto_contact_email', 'soldto_tax_id', 'shipto_company',
                          'shipto_address1',
                          'shipto_address2', 'shipto_city', 'shipto_state_provice', 'shipto_postal_code',
                          'shipto_country',
                          'shipto_contact_telephone', 'shipto_contact_email', 'shipto_tax_id', 'ship_by_date',
                          'deliver_by_date', 'line_number', 'part_number', 'part_description', 'quantity_ordered',
                          'quantity_shiped', 'unit_price', 'database_type']
            print(len(fieldnames))
            writer = csv.DictWriter(broker_file, fieldnames=fieldnames)
            writer.writeheader()

        with open(filename, mode='rb') as broker_file:
            file_base64 = base64.b64encode(broker_file.read())
        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'datas': file_base64,
            'store_fname': filename,
            'res_model': 'stock.picking',
            'res_id': self.id,
            'type': 'binary',  # override default_type from context, possibly meant for another model!
        })
        print(attachment)
