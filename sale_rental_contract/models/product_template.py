# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    rental_contract_price = fields.Float(
        string="Monthly Rental Price",
        digits="Product Price",
        help="Price per rented unit and month invoiced by the contract of a"
        " rental service. Empty: the rental order amount divided by the"
        " number of months of the rental.",
    )
