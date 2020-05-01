# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    email_broker = fields.Char(string='Email Alias', readonly=False,
                               config_parameter='louet_stock.default_broker_email',
                               help='Set this email as alias for Shipping Broker.')

    ftp_host_broker = fields.Char(string='Host', default='',
                                  config_parameter='louet_stock.ftp_host_broker')
    ftp_port_broker = fields.Integer(string='Port', required=True, default=21,
                                     config_parameter='louet_stock.ftp_port_broker')
    # ftp_protocol_broker = fields.Selection(selection=[('ftp', 'FTP - File Transfer Protocol'),
    #                                                    ('sftp', 'SFTP - SSH File Transfer Protocol')],
    #                                         config_parameter='louet_stock.ftp_protocol_broker',
    #                                         string='Protocol', required=True, default='ftp')
    ftp_login_broker = fields.Char(string='Username', required=True, default='',
                                   config_parameter='louet_stock.ftp_login_broker')
    ftp_password_broker = fields.Char(string='Password', required=True, default='',
                                      config_parameter='louet_stock.ftp_password_broker')
    ftp_public_key_broker = fields.Char(string='Public Key', required=True, default='',
                                        config_parameter='louet_stock.ftp_public_key_broker')

    # export to Broker, import from Broker
    ftp_dir_export = fields.Char(string='Export Directory',
                                 config_parameter='louet_stock.ftp_dir_export',
                                 help='Directory where export of Transfer information from Odoo to Broker')
    ftp_dir_import = fields.Char(string='Import Directory',
                                 config_parameter='louet_stock.ftp_dir_import',
                                 help='Directory where import of Broker information from Broker to Odoo')
