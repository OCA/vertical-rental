from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class RentalPeriod(models.Model):
    _name = "rental.period"
    _description = "Rental Period"
    _order = "sequence, id"

    name = fields.Char(required=True, translate=True)
    code = fields.Char(required=True, help="Short code like HOUR, DAY, WEEK, etc.")
    sequence = fields.Integer(default=10)
    active = fields.Boolean(default=True)

    # Standard unit used to convert duration -> hours
    # Example: hour=1, day=24, week=168, month=730 (approximately), year=8760 (approximately)
    hours_per_unit = fields.Float(required=True, default=1.0)

    _sql_constraints = [
        ("code_unique", "unique(code)", "Rental Period code must be unique."),
        (
            "hours_gt_zero",
            "CHECK(hours_per_unit>0)",
            "Hours per unit must be positive.",
        ),
    ]

    @api.constrains("code")
    def _check_code(self):
        for r in self:
            if not r.code.isupper():
                raise ValidationError(_("Period code must be UPPERCASE."))
