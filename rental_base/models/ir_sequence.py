# Part of rental-vertical See LICENSE file for full copyright and licensing details.

from odoo import _, fields, api, models
from odoo.exceptions import ValidationError, UserError


class IrSequence(models.Model):
    _inherit = "ir.sequence"

    @api.model
    def next_by_code(self, sequence_code):
        if sequence_code == "sale.order" and self.env.context.get(
            "default_type_id", False
        ):
            order_type = self.env["sale.order.type"].browse(
                self.env.context.get("default_type_id")
            )
            if order_type.sequence_id:
                return order_type.sequence_id._next()
        return super().next_by_code(sequence_code)
