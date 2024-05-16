# Copyright 2023 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    rented_lot_id = fields.Many2one(
        "stock.lot",
        string="Rented Serial Number",
        copy=False,
        domain="[('product_id', '=', rented_product_id)]",
    )

    rented_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Rented Product",
        related="product_id.rented_product_id",
    )

    def _prepare_new_rental_procurement_values(self, group=False):
        vals = super()._prepare_new_rental_procurement_values(group=group)
        if self.rented_lot_id:
            vals["restrict_lot_id"] = self.rented_lot_id.id
        return vals
