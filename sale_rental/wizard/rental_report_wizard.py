# models/rental_kpi_wizard.py
from odoo import fields, models


class RentalReportWizard(models.TransientModel):
    _name = "rental.report.wizard"
    _description = "Rental Report Period Wizard"

    date_from = fields.Date(required=True, default=fields.Date.today)
    date_to = fields.Date(required=True, default=fields.Date.today)

    def action_view_dashboard(self):
        return {
            "name": "Rental Dashboard",
            "type": "ir.actions.act_window",
            "res_model": "rental.report.dashboard",
            "view_mode": "form",
            "target": "current",
            "context": {
                "default_date_from": self.date_from.isoformat(),
                "default_date_to": self.date_to.isoformat(),
            },
        }
