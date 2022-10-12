# Part of rental-vertical See LICENSE file for full copyright and licensing details.

from odoo import fields, models

from .ir_view import RENTAL_TIMELINE_VIEW


class IrActionsActWindowView(models.Model):
    _inherit = "ir.actions.act_window.view"

    view_mode = fields.Selection(selection_add=[RENTAL_TIMELINE_VIEW])
