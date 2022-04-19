# Part of rental-vertical See LICENSE file for full copyright and licensing details.

from odoo import models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        res = super().action_confirm()
        for order in self:
            out_pickings = order.picking_ids.filtered(
                lambda x: x.picking_type_id.code == "outgoing" and x.state != "cancel"
            )
            in_pickings = order.picking_ids.filtered(
                lambda x: x.picking_type_id.code == "incoming" and x.state != "cancel"
            )
            for picking in out_pickings:
                for move in picking.move_ids_without_package:
                    if move.product_id and move.product_id.pack_ok:
                        for line in move.product_id.pack_line_ids:
                            qty = move.product_uom_qty * line.quantity
                            move.copy(
                                {
                                    "product_id": line.product_id.id,
                                    "product_uom_qty": qty,
                                    "rental_pack_move_id": move.id,
                                    "picking_id": move.picking_id.id,
                                }
                            )
            out_pickings.action_confirm()
            in_pickings.action_confirm()
        return res
