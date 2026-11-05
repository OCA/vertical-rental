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

    @api.depends("qc_inspections_ids.state")
    def _compute_qc_counts(self):
        groups = self.env["qc.inspection"]._read_group(
            domain=[("rental_id", "in", self.ids)],
            groupby=["rental_id", "state"],
            aggregates=["id:count"],
        )
        mapping = {}
        for rental_rec, state, count in groups:
            if not rental_rec:
                continue
            rid = rental_rec.id
            mapping.setdefault(rid, {})
            mapping[rid][state] = mapping[rid].get(state, 0) + count

        for rental in self:
            count_data = mapping.get(rental.id, {})
            rental.created_inspections = sum(count_data.values())
            rental.passed_inspections = count_data.get("success", 0)
            rental.failed_inspections = count_data.get("failed", 0)
            rental.done_inspections = (
                rental.passed_inspections + rental.failed_inspections
            )
