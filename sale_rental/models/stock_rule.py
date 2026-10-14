# Copyright 2014-2021 Akretion France (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2016-2021 Sodexis (http://sodexis.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.tools import float_compare


class StockRule(models.Model):
    _inherit = "stock.rule"

    def _push_prepare_move_copy_values(self, move_to_copy, new_date):
        """Inherit to write the end date of the rental on the return move.

        In Odoo 18, the upstream method uses move_to_copy.quantity (actual
        done/reserved quantity from move lines) for the new move's
        product_uom_qty.  When push rules are applied during _action_confirm
        (as we do for rental out moves in stock_move._action_confirm), the
        move is still draft and quantity is 0, which would create a return
        move with product_uom_qty=0.  Fix that by falling back to
        product_uom_qty (the demanded quantity) when quantity is 0.
        """
        res = super()._push_prepare_move_copy_values(move_to_copy, new_date)
        rounding = move_to_copy.product_uom.rounding
        if (
            float_compare(res.get("product_uom_qty", 0), 0, precision_rounding=rounding)
            == 0
            and float_compare(
                move_to_copy.product_uom_qty, 0, precision_rounding=rounding
            )
            > 0
        ):
            res["product_uom_qty"] = move_to_copy.product_uom_qty
        location_id = res.get("location_id", False)
        if (
            location_id
            and location_id == move_to_copy.warehouse_id.rental_out_location_id.id
            and move_to_copy.sale_line_id
            and move_to_copy.sale_line_id.rental_type == "new_rental"
        ):
            rental_end_date = move_to_copy.sale_line_id.end_date
            res["date"] = fields.Datetime.to_datetime(rental_end_date)
        return res
