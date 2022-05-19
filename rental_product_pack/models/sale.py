# Part of rental-vertical See LICENSE file for full copyright and licensing details.

from odoo import models, api


class SaleOrder(models.Model):
    _inherit = "sale.order"


    @api.multi
    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        for order in self:
            out_pickings = order.picking_ids.filtered(
                lambda x: x.picking_type_id.code == "outgoing" and x.state != "cancel"
            )
            in_pickings = order.picking_ids.filtered(
                lambda x: x.picking_type_id.code == "incoming" and x.state != "cancel"
            )
            for picking in out_pickings:
                for move in picking.move_ids_without_package:
                    move._create_pack_products()
            out_pickings.action_confirm()
            in_pickings.action_confirm()
        return res
