# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class RentalSignTemplateItem(models.Model):
    _name = "rental.sign.template.item"
    _description = "Rental Signature Template Item"

    description = fields.Char(
        help="Optional description to identify this signature slot.",
    )

    company_id = fields.Many2one(
        "res.company",
        default=lambda self: self.env.company,
        required=True,
    )

    report_id = fields.Many2one(
        "ir.actions.report",
        string="Report",
        required=True,
    )

    role_id = fields.Many2one(
        "sign.oca.role",
        string="Sign Role",
        required=True,
        help="Role that will sign (Customer, Employee...).",
    )

    page = fields.Integer(
        default=1,
        required=True,
    )

    position_x = fields.Float(required=True)

    position_y = fields.Float(required=True)

    width = fields.Float()

    height = fields.Float()
