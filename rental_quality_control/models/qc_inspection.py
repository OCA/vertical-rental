# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class QcInspection(models.Model):
    _inherit = "qc.inspection"

    rental_id = fields.Many2one(
        "sale.rental",
        string="Rental",
        ondelete="set null",
    )
