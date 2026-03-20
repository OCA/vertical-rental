from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    reminder_days = fields.Integer(
        string="Rental Reminder Days",
        config_parameter="sale_rental.reminder_days",
        default=3.0,
    )
