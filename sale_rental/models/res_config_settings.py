from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    send_return_reminder = fields.Boolean(
        string="Send Return Reminders",
        config_parameter="sale_rental.send_return_reminder",
    )

    reminder_days = fields.Integer(
        string="Rental Reminder Days",
        config_parameter="sale_rental.reminder_days",
        default=3.0,
    )
