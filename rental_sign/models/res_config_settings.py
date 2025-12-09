# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    rental_delivery_report_id = fields.Many2one(
        "ir.actions.report",
        string="Delivery Report for Signature",
        domain="[('model', '=', 'stock.picking'), ('report_type', '=', 'qweb-pdf')]",
        config_parameter="rental_sign.delivery_report_id",
        help="PDF report that will be rendered and sent for signature when delivering "
        "rented items.",
    )

    rental_return_report_id = fields.Many2one(
        "ir.actions.report",
        string="Return Report for Signature",
        domain="[('model', '=', 'stock.picking'), ('report_type', '=', 'qweb-pdf')]",
        config_parameter="rental_sign.return_report_id",
        help="PDF report that will be rendered and sent for signature when receiving "
        "returned items.",
    )
