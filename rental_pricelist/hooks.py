# Part of rental-vertical See LICENSE file for full copyright and licensing details.

from odoo import SUPERUSER_ID
from odoo.api import Environment


def set_multi_sales_price(cr, registry):
    env = Environment(cr, SUPERUSER_ID, {})
    conf_page = env["res.config.settings"].create({})
    conf_page.group_uom = True
    conf_page.multi_sales_price = True
    conf_page.multi_sales_price_method = "formula"
    conf_page.execute()
