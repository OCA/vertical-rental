# Part of rental-vertical See LICENSE file for full copyright and licensing details.

from odoo import fields, models


class SaleOrderType(models.Model):
    _inherit = "sale.order.type"

    is_rental_type = fields.Boolean(
        string="Rental Type",
        help="Orders of this type are considered rental orders.",
    )
