# -*- coding: utf-8 -*-

from odoo import SUPERUSER_ID
from odoo.api import Environment


def migrate(cr, version):
    env = Environment(cr, SUPERUSER_ID, {})
    interval_price_id = env.ref("rental_pricelist_interval.pricelist_interval").id
    env["product.product"].search([]).write(
        {
            "def_interval_pricelist_id": interval_price_id,
        }
    )
