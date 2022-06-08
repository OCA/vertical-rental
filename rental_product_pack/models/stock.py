# Part of rental-vertical See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class StockMove(models.Model):
    _inherit = "stock.move"

    #TODO Delete field rental_pack_move_id
    rental_pack_move_id = fields.Many2one(
        string="Rental Main Pack Move",
        comodel_name="stock.move",
    )

    @api.multi
    def _create_pack_products(self):
        self.ensure_one()
        if self.product_id and not self.product_id.pack_ok:
            return
        else:
            for line in self.product_id.pack_line_ids:
               qty = self.product_uom_qty * line.quantity
               move = self.search(
                   [
                       ('picking_id', '=', self.picking_id.id),
                       ('product_id', '=', line.product_id.id),
                   ]
               )
               if move and not line.product_id.pack_ok:
                   move.product_uom_qty += qty
               else:
                   new_move = self.copy(
                       {
                           "product_id": line.product_id.id,
                           "product_uom_qty": qty,
                           "rental_pack_move_id": self.id,
                           "picking_id": self.picking_id.id,
                       }
                   )
                   new_move._create_pack_products()
