# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import csv
import xlrd
import base64
import logging
import os
import pysftp
from tempfile import TemporaryDirectory

from odoo import api, fields, models, _
from datetime import datetime, timedelta
from odoo.tools.float_utils import float_round

_logger = logging.getLogger(__name__)


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _prepare_procurement_values(self):
        res = super(StockMove, self)._prepare_procurement_values()
        res.update({'sale_line_id': self.sale_line_id.id})
        return res


class PickingType(models.Model):
    _inherit = 'stock.picking.type'

    send_email = fields.Boolean(string='Send Broker File',
                                help='Check to enable sending broker File over SFTP at validation of transfer with this operation type')


class Picking(models.Model):
    _inherit = 'stock.picking'

    carrier_name = fields.Char(string='Carrier Name',
                               help='Carrier Name from Shipping Broker')
    broker_received = fields.Boolean(string='Broker Shipping Received',
                                     help='Will be set to True when file is read from Broker stating shipping information.')

    def check_if_production(self):
        # Check for both production db name and enterprise code set
        if self.env.cr.dbname == 'davevanstralen-louetinc-production-770941' and \
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
                         'line_number': line.id or '',
                         'part_number': line.product_id.name or '',
                         'part_description': line.product_id.default_code or '',
                         'quantity_ordered': line.qty_done,
                         # 'quantity_shiped': '',
                         'unit_price': line.move_id.sale_line_id.price_unit,
                         'database_type': self.check_if_production()})
        return rows

    # Create xls file for broker report
    def create_broker_report(self):
        report_name = '{company}_{transfer}_shipping_{date}'.format(company=self.company_id.name,
                                                                    transfer=self.name.replace('/', ''),
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
            'res_model': 'stock.picking',
            'res_id': self.id,
            'type': 'binary',  # override default_type from context, possibly meant for another model!
        })
        print(attachment)
        return attachment

    def get_ftp_config(self):
        return {'host': self.env['ir.config_parameter'].sudo().get_param('louet_stock.ftp_host_broker'),
                'port': int(self.env['ir.config_parameter'].sudo().get_param('louet_stock.ftp_port_broker')),
                'login': self.env['ir.config_parameter'].sudo().get_param('louet_stock.ftp_login_broker'),
                'password': self.env['ir.config_parameter'].sudo().get_param('louet_stock.ftp_password_broker'),
                'repin': '/',
                }

    def export_ftp_report(self, attachment_id):
        target_path = self.env['ir.config_parameter'].sudo().get_param('louet_stock.ftp_dir_export')
        config = self.get_ftp_config()

        cnopts = pysftp.CnOpts()

        hostkeys = None

        myHostname = config.get('host')
        myUsername = config.get('login')
        myPassword = config.get('password')

        if cnopts.hostkeys.lookup(myHostname) == None:
            print("New host - will accept any host key")
            # Backup loaded .ssh/known_hosts file
            hostkeys = cnopts.hostkeys
            # And do not verify host key of the new host
            cnopts.hostkeys = None

        with pysftp.Connection(myHostname, username=myUsername, password=myPassword, cnopts=cnopts) as sftp:
            if hostkeys is not None:
                print("Connected to new host, caching its hostkey")
                hostkeys.add(myHostname, sftp.remote_server_key.get_name(), sftp.remote_server_key)
                hostkeys.save(pysftp.helpers.known_hosts())

        try:
            with pysftp.Connection(myHostname, username=myUsername, password=myPassword) as sftp:
                directory_structure = sftp.listdir_attr()
                for attr in directory_structure:
                    print(attr.filename, attr)
                print(sftp.pwd)
                sftp.cwd(target_path)
                print(sftp.pwd)
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
        except Exception:
            _logger.warn("Unable to connect to SFTP Server at '%s' with user '%s'. Transfer still validated.",
                         myHostname, myUsername)
        return True

    def action_done(self):
        # TODO: new picking will be created when Shipping cost is add, how to handle this case for TOD
        res = super(Picking, self).action_done()
        for pick in self:
            if pick.picking_type_id.send_email:
                attachment_id = pick.create_broker_report()
                if attachment_id:
                    pick.export_ftp_report(attachment_id)
        return res

    def create_shipping_cost_SOL(self, sale_order_id, product_id, shipping_cost, delivery_order_id):
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
        for do in data:
            do_name = do.get('Order', False)
            if do_name:
                # Only get DO which match name and have not been read
                delivery_order_id = self.env['stock.picking'].search(
                    [['name', '=', str(do_name)], ['broker_received', '=', False]], limit=1)
                if delivery_order_id:
                    delivery_order_id.carrier_tracking_ref = str(do.get('Shipment_ID', ''))
                    delivery_order_id.carrier_name = str(do.get('Carrier', ''))

                    sale_order_id = delivery_order_id.sale_id
                    product_id = self.env['product.product'].search([['is_broker_ship', '=', True]], limit=1)
                    shipping_cost = do.get('Published_Cost', 0.0)

                    if sale_order_id and product_id:
                        self.create_shipping_cost_SOL(sale_order_id, product_id, shipping_cost, delivery_order_id)
                    else:
                        _logger.warning(_(
                            'No Sale Order Line with additional shipping cost added to %s from Broker Shipping Import because no Sale Order or product associated.'),
                            delivery_order_id.name)
                else:
                    _logger.warning(
                        _('No Delivery Order with Name,%s, found. Shipping Broker information not imported'), do_name)

    @api.model
    def get_broker_files(self):
        target_path = self.env['ir.config_parameter'].sudo().get_param('louet_stock.ftp_dir_import')
        config = self.get_ftp_config()

        myHostname = config.get('host')
        myUsername = config.get('login')
        myPassword = config.get('password')
        with TemporaryDirectory() as temp_dir:
            try:
                with pysftp.Connection(myHostname, username=myUsername, password=myPassword) as sftp:
                    print(sftp.pwd)
                    sftp.get_d(target_path, temp_dir, preserve_mtime=True)
            except Exception:
                _logger.warning(_('Connection failed to %s with User, %s,from Broker Shipping SFTP.'), myHostname,
                                myUsername)

            print(os.listdir(temp_dir))
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
