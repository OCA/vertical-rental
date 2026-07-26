# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class SaleRental(models.Model):
    _inherit = "sale.rental"

    qc_inspections_ids = fields.One2many(
        "qc.inspection",
        "rental_id",
        string="Inspections",
    )

    created_inspections = fields.Integer(compute="_compute_qc_counts")
    done_inspections = fields.Integer(compute="_compute_qc_counts")
    passed_inspections = fields.Integer(
        compute="_compute_qc_counts", string="Inspections OK"
    )
    failed_inspections = fields.Integer(
        compute="_compute_qc_counts", string="Inspections failed"
    )

    @api.model_create_multi
    def create(self, vals_list):
        rentals = super().create(vals_list)

        for rental in rentals:
            sale_line = rental.start_order_line_id
            if not sale_line:
                continue

            moves = self.env["stock.move"].search([("sale_line_id", "=", sale_line.id)])

            for move in moves:
                self.env["qc.inspection"].search(
                    [
                        ("object_id", "=", f"stock.move,{move.id}"),  # noqa: E231
                        ("rental_id", "=", False),
                    ]
                ).write({"rental_id": rental.id})

        return rentals

    @api.depends("qc_inspections_ids", "qc_inspections_ids.state")
    def _compute_qc_counts(self):
        data = (
            self.env["qc.inspection"]
            .sudo()
            .read_group(
                [("rental_id", "in", self.ids)],
                ["rental_id", "state"],
                ["rental_id", "state"],
                lazy=False,
            )
        )
        rental_data = {}
        for d in data:
            rental_data.setdefault(d["rental_id"][0], {}).setdefault(d["state"], 0)
            rental_data[d["rental_id"][0]][d["state"]] += d["__count"]
        for rental in self:
            count_data = rental_data.get(rental.id, {})
            rental.created_inspections = sum(count_data.values())
            rental.passed_inspections = count_data.get("success", 0)
            rental.failed_inspections = count_data.get("failed", 0)
            rental.done_inspections = (
                rental.passed_inspections + rental.failed_inspections
            )
