# Copyright 2014-2021 Akretion France (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2016-2021 Sodexis (http://sodexis.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models


class StockMove(models.Model):
    _inherit = "stock.move"

    def _skip_push(self):
        # Up to Odoo 12, push rules were only applied when moves were
        # confirmed. Since Odoo 13 they are applied a second time when the
        # move is validated, unless _skip_push() says otherwise. The return
        # (in) move of a rental is already created by the push rule when the
        # rental order is confirmed (see _action_confirm below and
        # rental_routing), so the out move must not be pushed again at
        # validation time, or a duplicate return move would be created.
        # The product must match, too: pack components share the sale line
        # and the rental out location but are pushed individually, and each
        # of their return moves copies the product of its own out move.
        res = super()._skip_push()
        if (
            not res
            and self.sale_line_id.rental_type == "new_rental"
            and self.picking_id.picking_type_id.code == "outgoing"
            and self.sale_line_id.move_ids.filtered(
                lambda m: m.picking_id.picking_type_id.code == "incoming"
                and m.location_id == self.location_dest_id
                and m.product_id == self.product_id
                and m.state != "cancel"
            )
        ):
            return True
        return res

    def _action_confirm(self, merge=True, merge_into=False):
        moves = super()._action_confirm(merge=merge, merge_into=merge_into)
        # In Odoo 18, push rules for positive moves are only applied in
        # _action_done. The rental flow expects the return (in) picking to be
        # created at SO confirmation time, so we apply the push rule
        # (rental_out -> rental_in) here for rental out moves.
        rental_out_moves = moves.filtered(
            lambda m: m.sale_line_id.rental_type == "new_rental"
            and m.warehouse_id
            and m.warehouse_id.rental_out_location_id
            and m.location_dest_id == m.warehouse_id.rental_out_location_id
            and not m._skip_push()
        )
        if rental_out_moves:
            rental_out_moves._push_apply()
        return moves
