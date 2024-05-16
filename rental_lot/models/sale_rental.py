# Copyright 2023 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleRental(models.Model):
    _inherit = "sale.rental"

    rented_lot_id = fields.Many2one(
        "stock.lot",
        string="Rented Serial Number",
        related="start_order_line_id.rented_lot_id",
    )
