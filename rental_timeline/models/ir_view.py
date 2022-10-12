# Part of rental-vertical See LICENSE file for full copyright and licensing details.

from odoo import fields, models

RENTAL_TIMELINE_VIEW = ("rental_timeline", "Rental Timeline")


class IrUIView(models.Model):
    _inherit = "ir.ui.view"

    type = fields.Selection(selection_add=[RENTAL_TIMELINE_VIEW])
