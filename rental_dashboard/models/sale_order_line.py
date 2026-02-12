from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    rental_display_name = fields.Char(
        string="Rental Display",
        compute="_compute_rental_display_name",
        store=True,
    )

    @api.depends(
        "product_id", "order_partner_id", "rental", "order_id.warehouse_id.rental_in_location_id",
    )
    def _compute_rental_display_name(self):
        for line in self:
            if line.rental and line.product_id:
                parts = []
                parts.append("\U0001F3D7 %s" % line.product_id.display_name)
                if line.order_id.warehouse_id and line.order_id.warehouse_id.rental_in_location_id:
                    parts.append("\U0001F4CD %s" % line.order_id.warehouse_id.rental_in_location_id.name)
                if line.order_partner_id:
                    parts.append("\U0001F464 %s" % line.order_partner_id.name)
                line.rental_display_name = " | ".join(parts)
            else:
                line.rental_display_name = line.name or ""

