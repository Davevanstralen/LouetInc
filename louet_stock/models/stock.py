# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import csv
import base64
import logging

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from .ftp_connection import FTPConnection

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _prepare_procurement_values(self):
        res = super(StockMove, self)._prepare_procurement_values()
        res.update({'sale_line_id': self.sale_line_id.id})
        return res


class PickingType(models.Model):
    _inherit = 'stock.picking.type'

    send_email = fields.Boolean(string='Send Broker Email',
                                help='Check to enable sending broker email at validation of transfer with this operation type')


class Picking(models.Model):
    _inherit = 'stock.picking'

    delivery_number = fields.Char(string='Delivery number',
                                  help='Delivery Number from Shipping Broker')
    carrier_name = fields.Char(string='Carrier Name',
                               help='Carrier Name from Shipping Broker')

    def check_if_production(self):
        # Check for both production db name and enterprise code set
        if self.env.cr.dbname == 'davevanstralen-louetinc-production-770941' and\
                self.env['ir.config_parameter'].sudo().get_param('database.enterprise_code'):
            # if self.env.cr.dbname == 'louet_v13' and self.env['ir.config_parameter'].sudo().get_param('database.enterprise_code'):
            return 'Production'
        return 'Test'

    def create_csv_data(self):
        sale_id = self.group_id.sale_id
        rows = []
        for line in self.move_line_ids_without_package:
            rows.append({'number': self.name or '',
                         # 'date': sale_id.date_order,
                         # 'sales_order_number': sale_id.name,
                         'currency': sale_id.currency_id.name or '',
                         'soldto_company': sale_id.partner_id.name or '',
                         'soldto_address': sale_id.partner_id.street or '',
                         # 'soldto_address2': '',
                         'soldto_city': sale_id.partner_id.city or '',
                         'soldto_state_province': sale_id.partner_id.state_id.name or '',
                         'soldto_postal_code': sale_id.partner_id.zip or '',
                         'soldto_country': sale_id.partner_id.country_id.name or '',
                         # 'soldto_contact_name': '',
                         # 'soldto_telephone': '',
                         # 'soldto_contact_email': '',
                         'soldto_tax_id': sale_id.partner_id.vat or '',
                         'shipto_company': sale_id.partner_invoice_id.name or '',
                         'shipto_address1': sale_id.partner_invoice_id.street or '',
                         # 'shipto_address2': '',
                         'shipto_city': sale_id.partner_invoice_id.city or '',
                         'shipto_state_provice': sale_id.partner_invoice_id.state_id.name or '',
                         'shipto_postal_code': sale_id.partner_invoice_id.zip or '',
                         'shipto_country': sale_id.partner_invoice_id.country_id.name or '',
                         # 'soldto_contact_name': '',
                         # 'shipto_contact_telephone': '',
                         # 'shipto_contact_email': '',
                         'shipto_tax_id': sale_id.partner_invoice_id.vat or '',
                         'bill_freight_to_company': sale_id.partner_shipping_id.name or '',
                         'bill_freight_to_address1': sale_id.partner_shipping_id.street or '',
                         # 'bill_freight_to_address2': '',
                         'bill_freight_to_city': sale_id.partner_shipping_id.city or '',
                         'bill_freight_to_state_province': sale_id.partner_shipping_id.state_id.name or '',
                         'bill_freight_to_postal_code': sale_id.partner_shipping_id.zip or '',
                         'bill_freight_to_country': sale_id.partner_shipping_id.country_id.name or '',
                         # 'ship_by_date': '',
                         'deliver_by_date': sale_id.commitment_date or '',
                         'line_number': lincorrespondinge.id or '',
                         'part_number': line.product_id.name or '',
                         'part_description': line.product_id.default_code or '',
                         'quantity_ordered': line.qty_done,
                         # 'quantity_shiped': '',
                         'unit_price': line.move_id.sale_line_id.price_unit,
                         'database_type': self.check_if_production()})
        return rows

    # Create xls file for broker report
    def create_broker_report(self):
        report_name = '{company}_shipping_{date}'.format(company=self.company_id.name,
                                                         date=datetime.now().strftime("%Y_%m_%d"))
        filename = "%s.%s" % (report_name, "csv")
        print(filename)

        with open(filename, mode='w') as broker_file:
            # fieldnames = ['number', 'date', 'sales_order_number', 'currency', 'soldto_company', 'soldto_address', 'soldto_address2', 'soldto_city', 'soldto_state_province', 'soldto_postal_code', 'soldto_country', 'soldto_telephone', 'soldto_contact_email', 'soldto_tax_id', 'shipto_company', 'shipto_address1', 'shipto_address2', 'shipto_city', 'shipto_state_provice', 'shipto_postal_code', 'shipto_country', 'shipto_contact_telephone', 'shipto_contact_email', 'shipto_tax_id', 'ship_by_date', 'deliver_by_date', 'line_number', 'part_number', 'part_description', 'quantity_ordered', 'quantity_shiped', 'unit_price', 'database_type']
            fieldnames = ['number', 'currency', 'soldto_company', 'soldto_address', 'soldto_city',
                          'soldto_state_province', 'soldto_postal_code', 'soldto_country', 'soldto_tax_id',
                          'shipto_company', 'shipto_address1', 'shipto_city', 'shipto_state_provice',
                          'shipto_postal_code', 'shipto_country', 'shipto_tax_id', 'bill_freight_to_company',
                          'bill_freight_to_address1', 'bill_freight_to_city', 'bill_freight_to_state_province',
                          'bill_freight_to_postal_code', 'bill_freight_to_country', 'deliver_by_date', 'line_number',
                          'part_number', 'part_description', 'quantity_ordered', 'unit_price', 'database_type']
            print(len(fieldnames))
            writer = csv.DictWriter(broker_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.create_csv_data())

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
        return attachment

    def export_ftp_report(self, attachment_id):
        host = self.env['ir.config_parameter'].sudo().get_param('louet_stock.ftp_host_broker')
        port = self.env['ir.config_parameter'].sudo().get_param('louet_stock.ftp_port_broker')
        login = self.env['ir.config_parameter'].sudo().get_param('louet_stock.ftp_login_broker')
        password = self.env['ir.config_parameter'].sudo().get_param('louet_stock.ftp_password_broker')

        #TODO: get target dir from TOD
        traget_path = 'SOME FOLDER'

        config = {'host': host,
                  'port': port,
                  'login': login,
                  'password': password,
                  'repin': '/',
                  }

        conn = FTPConnection(config)

        conn._connect()
        conn.cd(traget_path)
        if attachment_id:
            # get attachment name
            filename = attachment_id.datas_fname

            with open(str(filename), "w") as fh:
                fh.write(base64.b64decode(attachment_id.datas))
            conn._conn.put(filename, traget_path + '/' + filename)
        conn._disconnect()
        return True

    def action_done(self):
        res = super(Picking, self).action_done()
        for pick in self:
            if pick.picking_type_id.send_email:
                attachment_id = pick.create_broker_report()
                # email_sub = '{company} Shipping CSV {date}'.format(company=self.company_id.name,
                #                                                           date=datetime.now().strftime("%Y-%m-%d"))
                # vals = {'email_to': self.env['ir.config_parameter'].sudo().get_param('louet_stock.default_broker_email'),
                #         'body_html': 'Broker Shipping Report CSV',
                #         'subject': email_sub,
                #         'attachment_ids': [(6, 0, [report_id.id])]
                #         }
                # print(vals)
                # try:
                #     report_email = self.env['mail.mail'].create(vals)
                #     report_email.send()
                # except Exception:
                #     _logger.warn("Failed to send email'%s' (email id %d) but picking(id %d) still validated.",
                #                  email_sub, report_email.id, self.id)
                # if attachment_id:
                #     pick.export_ftp_report(attachment_id)

        return res
