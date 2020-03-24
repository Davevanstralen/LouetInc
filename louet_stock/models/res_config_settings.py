# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    email_broker = fields.Char(string='Email Alias', readonly=False,
                               config_parameter='louet_stock.default_broker_email',
                               help='Set this email as alias for Shipping Broker.')
