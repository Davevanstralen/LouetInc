# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import csv
import xlrd
import base64
import logging
import os
import paramiko
import pysftp

from base64 import decodebytes
from tempfile import TemporaryDirectory

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.tools.float_utils import float_round

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _prepare_procurement_values(self):
        # Calling super, sale_line_id does not get set for procurements that are run from another procurement
        res = super(StockMove, self)._prepare_procurement_values()
        res.update({'sale_line_id': self.sale_line_id.id})
        return res


class PickingType(models.Model):
    _inherit = 'stock.picking.type'

    send_email = fields.Boolean(string='Send Broker File',
                                help='Check to enable sending broker File over SFTP at validation of transfer with this operation type')
    set_carrier = fields.Boolean(string='Set Broker Carrier Info',
                                 help='Check to enable setting Tracking Number and Carrier Name from the Broker File once synced.')


class Picking(models.Model):
    _inherit = 'stock.picking'

    carrier_name = fields.Char(string='Carrier Name',
                               help='Carrier Name from Shipping Broker')
    broker_received = fields.Boolean(string='Broker Shipping Received',
                                     help='Will be set to True when file is read from Broker stating shipping information.')

    def check_if_production(self):
        """
        Function that Check for both production db name and enterprise code set

        @param self: model self

        @return string: 'Production' or 'Test'
        """
        if self.env.cr.dbname == 'davevanstralen-louetinc-production-770941' and \
                self.env['ir.config_parameter'].sudo().get_param('database.enterprise_code'):
            return 'Production'
        return 'Test'

    def create_csv_data(self):
        """
        Function that creates csv based on move lines on a picking

        @param self: model self

        @return list: rows
        """
        sale_id = self.group_id.sale_id
        rows = []
        for line in self.move_line_ids_without_package:
            rows.append({
                'number': self.name or '',
                'date': '',
                'sales_order_number': '',
                'purchase_order_number': '',
                'freight_billing': '',
                'carrier_account_number': '',
                'ship_via': '',
                'carrierserviceid': '',
                'currency': sale_id.currency_id.name or '',
                'sales_person_code': '',
                'backorders_accepted': '',
                'warehouse': '',
                'identity': '',
                'soldto_company': sale_id.partner_id.name or '',
                'soldto_address1': sale_id.partner_id.street or '',
                'soldto_address2': '',
                'soldto_city': sale_id.partner_id.city or '',
                'soldto_state_province': sale_id.partner_invoice_id.state_id.code or '',
                'soldto_postal_code': sale_id.partner_id.zip or '',
                'soldto_country': sale_id.partner_id.country_id.code or '',
                'soldto_contact_name': '',
                'soldto_contact_telephone': '',
                'soldto_contact_email': '',
                'soldto_tax_id': sale_id.partner_id.vat or '',
                'soldto_reference_number': '',
                'shipto_company': sale_id.partner_shipping_id.name or '',
                'shipto_address1': sale_id.partner_shipping_id.street or '',
                'shipto_address2': '',
                'shipto_city': sale_id.partner_shipping_id.city or '',
                'shipto_state_province': sale_id.partner_shipping_id.state_id.code or '',
                'shipto_postal_code': sale_id.partner_shipping_id.zip or '',
                'shipto_country': sale_id.partner_shipping_id.country_id.code or '',
                'shipto_contact_name': '',
                'shipto_contact_telephone': '',
                'shipto_contact_email': '',
                'shipto_tax_id': sale_id.partner_shipping_id.vat or '',
                'bill_freight_to_company': sale_id.partner_invoice_id.name or '',
                'bill_freight_to_address1': sale_id.partner_invoice_id.street or '',
                'bill_freight_to_address2': '',
                'bill_freight_to_city': sale_id.partner_invoice_id.city or '',
                'bill_freight_to_state_province': sale_id.partner_invoice_id.state_id.code or '',
                'bill_freight_to_postal_code': sale_id.partner_invoice_id.zip or '',
                'bill_freight_to_country': sale_id.partner_invoice_id.country_id.code or '',
                # 'shipto_company': sale_id.partner_invoice_id.name or '',
                # 'shipto_address1': sale_id.partner_invoice_id.street or '',
                # 'shipto_address2': '',
                # 'shipto_city': sale_id.partner_invoice_id.city or '',
                # 'shipto_state_province': sale_id.partner_invoice_id.state_id.code or '',
                # 'shipto_postal_code': sale_id.partner_invoice_id.zip or '',
                # 'shipto_country': sale_id.partner_invoice_id.country_id.code or '',
                # 'shipto_contact_name': '',
                # 'shipto_contact_telephone': '',
                # 'shipto_contact_email': '',
                # 'shipto_tax_id': sale_id.partner_invoice_id.vat or '',
                # 'bill_freight_to_company': sale_id.partner_shipping_id.name or '',
                # 'bill_freight_to_address1': sale_id.partner_shipping_id.street or '',
                # 'bill_freight_to_address2': '',
                # 'bill_freight_to_city': sale_id.partner_shipping_id.city or '',
                # 'bill_freight_to_state_province': sale_id.partner_shipping_id.state_id.code or '',
                # 'bill_freight_to_postal_code': sale_id.partner_shipping_id.zip or '',
                # 'bill_freight_to_country': sale_id.partner_shipping_id.country_id.code or '',
                'ship_by_date': '',
                'deliver_by_date': sale_id.commitment_date or '',
                'cancel_by_date': '',
                'bill_duties_and_taxes_to': '',
                'seller_and_buyer_are_related': '',
                'comment': '',
                'terms_of_sale': '',
                'commercial_payment_terms': '',
                'freight_amount': '',
                'cod_amount': '',
                'commercial_paid_amount': '',
                'line_number': line.id or '',
                'part_number': line.product_id.default_code or '',
                'part_description': line.product_id.name or '',
                'quantity_ordered': line.qty_done,
                'quantity_shipped': line.qty_done,
                'unit_price': line.move_id.sale_line_id.price_unit,
                'extended_price': '',
                'lineitem_comment': self.check_if_production(),
                'lineitem_country_origin': '',
                'serial_number': ''
            })
        return rows

    def create_broker_report(self):
        """
        Generate xls file for broker report and create attachment

        @param self: model self

        @return record: attachment
        """
        report_name = '{company}_{transfer}_shipping_{date}'.format(company=self.company_id.name.replace(' ', ''),
                                                                    transfer=self.name.replace('/', ''),
                                                                    date=datetime.now().strftime("%Y_%m_%d"))
        filename = "%s.%s" % (report_name, "csv")

        with open(filename, mode='w') as broker_file:
            # fieldnames = ['number', 'date', 'sales_order_number', 'currency', 'soldto_company', 'soldto_address1', 'soldto_address2', 'soldto_city', 'soldto_state_province', 'soldto_postal_code', 'soldto_country', 'soldto_telephone', 'soldto_contact_email', 'soldto_tax_id', 'shipto_company', 'shipto_address1', 'shipto_address2', 'shipto_city', 'shipto_state_province', 'shipto_postal_code', 'shipto_country', 'shipto_contact_telephone', 'shipto_contact_email', 'shipto_tax_id', 'ship_by_date', 'deliver_by_date', 'line_number', 'part_number', 'part_description', 'quantity_ordered', 'quantity_shiped', 'unit_price', 'database_type']
            fieldnames = ['number', 'date', 'sales_order_number', 'purchase_order_number', 'freight_billing',
                          'carrier_account_number', 'ship_via', 'carrierserviceid', 'currency', 'sales_person_code',
                          'backorders_accepted', 'warehouse', 'identity', 'soldto_company', 'soldto_address1',
                          'soldto_address2', 'soldto_city', 'soldto_state_province', 'soldto_postal_code',
                          'soldto_country', 'soldto_contact_name', 'soldto_contact_telephone', 'soldto_contact_email',
                          'soldto_tax_id', 'soldto_reference_number', 'shipto_company', 'shipto_address1',
                          'shipto_address2', 'shipto_city', 'shipto_state_province', 'shipto_postal_code',
                          'shipto_country', 'shipto_contact_name', 'shipto_contact_telephone', 'shipto_contact_email',
                          'shipto_tax_id', 'bill_freight_to_company', 'bill_freight_to_address1',
                          'bill_freight_to_address2', 'bill_freight_to_city', 'bill_freight_to_state_province',
                          'bill_freight_to_postal_code', 'bill_freight_to_country', 'ship_by_date', 'deliver_by_date',
                          'cancel_by_date', 'bill_duties_and_taxes_to', 'seller_and_buyer_are_related', 'comment',
                          'terms_of_sale', 'commercial_payment_terms', 'freight_amount', 'cod_amount',
                          'commercial_paid_amount', 'line_number', 'part_number', 'part_description', 'quantity_ordered',
                          'quantity_shipped', 'unit_price', 'extended_price', 'lineitem_comment', 'lineitem_country_origin',
                          'serial_number']
            writer = csv.DictWriter(broker_file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.create_csv_data())

        with open(filename, mode='rb') as broker_file:
            file_base64 = base64.b64encode(broker_file.read())

        attachment = self.env['ir.attachment'].create({
            'name': filename,
            'datas': file_base64,
            'res_model': 'stock.picking',
            'res_id': self.id,
            'type': 'binary',  # override default_type from context, possibly meant for another model!
        })

        try:
            os.remove(filename)
        except Exception:
            _logger.warn("Failed to remove '%s' from directory but '%s' attachment is still created.",
                         filename, attachment.name_get())
        return attachment

    def get_ftp_config(self):
        """
        Return the ftp configuration from config param

        @param self: model self

        @return dict: config info from settings
        """
        return {'host': self.env['ir.config_parameter'].sudo().get_param('louet_stock.ftp_host_broker'),
                'port': int(self.env['ir.config_parameter'].sudo().get_param('louet_stock.ftp_port_broker')),
                'login': self.env['ir.config_parameter'].sudo().get_param('louet_stock.ftp_login_broker'),
                'password': self.env['ir.config_parameter'].sudo().get_param('louet_stock.ftp_password_broker'),
                'repin': '/',
                'public_key': self.env['ir.config_parameter'].sudo().get_param('louet_stock.ftp_public_key_broker'),
                }

    def export_ftp_report(self, attachment_id):
        """
        Export the created shipping csv through sftp

        @param self: model self
        @param attachment_id: csv attachment record

        @return boolean: True if export success
        """
        target_path = self.env['ir.config_parameter'].sudo().get_param('louet_stock.ftp_dir_export')
        config = self.get_ftp_config()

        myHostname = config.get('host')
        myUsername = config.get('login')
        myPassword = config.get('password')
        keydata = config.get('public_key').encode()

        # Add hostkey if not already there
        key = paramiko.RSAKey(data=decodebytes(keydata))
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys.add(myHostname, 'ssh-rsa', key)

        with pysftp.Connection(myHostname, username=myUsername, password=myPassword, cnopts=cnopts) as sftp:
            sftp.cwd(target_path)

            if attachment_id:
                # get attachment name
                filename = attachment_id.name

                with open(str(filename), "wb") as fh:
                    fh.write(base64.b64decode(attachment_id.datas))
                try:
                    sftp.put(filename, preserve_mtime=True)
                except Exception:
                    _logger.warn("Failed to export '%s' from transfer '%s' but is still validated.",
                                 attachment_id.name, self.id)
        return True

    def action_done(self):
        """
        Call super on action done to send the csv

        @param self: model self

        @return res: result of the action_done super call
        """
        res = super(Picking, self).action_done()
        for pick in self:
            if pick.picking_type_id.send_email:
                attachment_id = pick.create_broker_report()
                if attachment_id:
                    pick.export_ftp_report(attachment_id)
        return res

    def create_shipping_cost_line(self, sale_order_id, product_id, shipping_cost, delivery_order_id):
        """
        Create shipping cost sol based on broker's shipping cost

        @param self: model self
        @param sale_order_id: sale order id
        @param product_id: product id of product with is_broker_ship true
        @param shipping_cost: shipping cost from broker
        @param delivery_order_id: DO id

        @return None
        """
        rounding = self.env.company.currency_id.decimal_places

        amount_untaxed = amount_tax = 0.0
        for line in sale_order_id.order_line.filtered(lambda l: l.product_id != product_id):
            amount_untaxed += line.price_subtotal
            amount_tax += line.price_tax

        no_ship_total = amount_untaxed + amount_tax

        order_line_id = self.env['sale.order.line'].create([{
            "order_id": sale_order_id.id,
            "product_id": product_id.id,
            # Shipping Cost Line item =  Cost Returned by Shipping Broker + $3.00 (fixed)  + (0.01 * order value without shipping)
            "price_unit": float_round(shipping_cost + 3.00 + (0.01 * no_ship_total), precision_rounding=rounding)
        }])
        if order_line_id:
            # after successful shipping charge and read, change boolean to true to avoid duplicates
            delivery_order_id.broker_received = True
            delivery_order_id.message_post(body=_('Your shipment request has been successfully received.'))

    def process_broker_order(self, data):
        """
        Use broker data to find equivalent DO in db and update information

        @param self: model self
        @param data: data from broker read file

        @return None
        """
        for do in data:
            do_name = do.get('Order', False)
            if do_name:
                # Only get DO which match name and have not been read
                delivery_order_id = self.env['stock.picking'].search(
                    [['name', '=', str(do_name)], ['broker_received', '=', False]], limit=1)
                if delivery_order_id:
                    delivery_order_id.carrier_tracking_ref = str(int(do.get('Shipment_ID', '')))
                    delivery_order_id.carrier_name = str(do.get('Carrier', ''))

                    sale_order_id = delivery_order_id.sale_id
                    product_id = self.env['product.product'].search([['is_broker_ship', '=', True]], limit=1)
                    shipping_cost = do.get('Published_Cost', 0.0)

                    if sale_order_id:
                        # Find if there is another picking to update carrier info
                        do_out = sale_order_id.picking_ids.filtered(
                            lambda p: p.picking_type_id.set_carrier and p.state not in ['done', 'cancel'])
                        for out in do_out:
                            out.carrier_tracking_ref = str(int(do.get('Shipment_ID', '')))
                            out.carrier_name = str(do.get('Carrier', ''))
                        # if there is a product that has is_broker_ship create SOL
                        if product_id:
                            self.create_shipping_cost_line(sale_order_id, product_id, shipping_cost, delivery_order_id)
                    else:
                        _logger.warning(_(
                            'No Sale Order Line with additional shipping cost added to %s from Broker Shipping Import because no Sale Order or product associated.'),
                            delivery_order_id.name)
                else:
                    _logger.warning(
                        _('No Delivery Order with Name,%s, found. Shipping Broker information not imported'), do_name)

    @api.model
    def get_broker_files(self):
        """
        Sync the broker data over sftp

        @param self: model self

        @return boolean: True if files read successfully
        """
        target_path = self.env['ir.config_parameter'].sudo().get_param('louet_stock.ftp_dir_import')
        config = self.get_ftp_config()

        myHostname = config.get('host')
        myUsername = config.get('login')
        myPassword = config.get('password')
        keydata = config.get('public_key').encode()

        # Add hostkey if not already there
        key = paramiko.RSAKey(data=decodebytes(keydata))
        cnopts = pysftp.CnOpts()
        cnopts.hostkeys.add(myHostname, 'ssh-rsa', key)

        with TemporaryDirectory() as temp_dir:
            try:
                with pysftp.Connection(myHostname, username=myUsername, password=myPassword, cnopts=cnopts) as sftp:
                    sftp.get_d(target_path, temp_dir, preserve_mtime=True)
            except Exception:
                _logger.warning(_('Connection failed to %s with User, %s,from Broker Shipping SFTP.'), myHostname,
                                myUsername)
            # Check all files that were read
            for filename in os.listdir(temp_dir):
                workbook = xlrd.open_workbook(os.path.join(temp_dir, filename))
                sheet = workbook.sheet_by_index(0)

                header_row = []
                for col in range(sheet.ncols):
                    header_row.append(sheet.cell_value(0, col))

                # list of 'rows' data, dictionary with keys as header values
                data = []
                for row in range(1, sheet.nrows):
                    value = {}
                    for col in range(sheet.ncols):
                        value[header_row[col]] = sheet.cell_value(row, col)
                    data.append(value)
                self.process_broker_order(data)
        return True
