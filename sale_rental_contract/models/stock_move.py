# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _action_done(self, cancel_backorder=False):
        moves = super()._action_done(cancel_backorder=cancel_backorder)
        # rented goods back before the end: the contract stops billing
        for move in moves.filtered(
            lambda m: m.state == "done"
            and m.sale_line_id.contract_id
            and m.location_id
            == m.sale_line_id.order_id.warehouse_id.rental_out_location_id
        ):
            rental = self.env["sale.rental"].search(
                [("start_order_line_id", "=", move.sale_line_id.id)], limit=1
            )
            if rental.state == "in" and rental.end_date > move.date.date():
                rental._stop_rental_contract(move.date.date())
        return moves
