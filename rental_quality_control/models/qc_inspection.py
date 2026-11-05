# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class QcInspection(models.Model):
    _inherit = "qc.inspection"

    rental_id = fields.Many2one(
        "sale.rental",
        string="Rental",
        ondelete="set null",
    )

    def _find_rental_from_object_ref(self, object_ref):
        if not object_ref or object_ref._name != "stock.move":
            return self.env["sale.rental"]
        sale_line = getattr(object_ref, "sale_line_id", False)
        if not sale_line:
            return self.env["sale.rental"]

        return (
            self.env["sale.rental"]
            .sudo()
            .search(
                [
                    "|",
                    "|",
                    ("start_order_line_id", "=", sale_line.id),
                    ("extension_order_line_ids", "in", sale_line.id),
                    ("sell_order_line_ids", "in", sale_line.id),
                ],
                limit=1,
            )
        )

    def _prepare_inspection_header(self, object_ref, trigger_line):
        vals = super()._prepare_inspection_header(object_ref, trigger_line)

        rental = self._find_rental_from_object_ref(object_ref)

        if rental:
            vals["rental_id"] = rental.id

        return vals
