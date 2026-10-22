# Copyright 2023 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    rented_lot_id = fields.Many2one(
        "stock.lot",
        string="Rented Serial Number",
        copy=False,
        compute="_compute_rented_lot_id",
        store=True,
        readonly=False,
    )

    @api.depends("rented_product_id")
    def _compute_rented_lot_id(self):
        for sol in self:
            if sol.rented_product_id != sol.rented_lot_id.product_id:
                sol.rented_lot_id = False

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

    def write(self, vals):
        res = super().write(vals)
        allow_to_change_lot = self.env.company.allow_to_change_lot_on_confirmed_so
        if "rented_lot_id" in vals and (
            allow_to_change_lot or self.order_id.state not in ["sale", "done"]
        ):
            self.move_ids.write({"restrict_lot_id": vals.get("rented_lot_id")})
        elif "rented_lot_id" in vals and not allow_to_change_lot:
            raise UserError(_("You can't change the lot on confirmed sale order."))
        return res
