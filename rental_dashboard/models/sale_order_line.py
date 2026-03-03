from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    rental_display_name = fields.Char(
        string="Rental Display",
        compute="_compute_rental_display_name",
        store=True,
    )

    @api.depends(
        "product_id",
        "order_partner_id",
        "rental",
        "order_id.warehouse_id.rental_in_location_id",
    )
    def _compute_rental_display_name(self):
        for line in self:
            if not (line.rental and line.product_id):
                line.rental_display_name = line.name or ""
                continue
            parts = ["\U0001F3D7 %s" % line.product_id.display_name]
            loc = line.order_id.warehouse_id.rental_in_location_id
            if loc:
                parts.append("\U0001F4CD %s" % loc.name)
            if line.order_partner_id:
                parts.append("\U0001F464 %s" % line.order_partner_id.name)
            line.rental_display_name = " | ".join(parts)

    @api.model
    def create_rental_order(self, vals):
        """Create a rental sale order with all lines in a single RPC call.

        :param vals: {
            'partner_id': int,
            'warehouse_id': int,
            'lines': [{
                'product_id': int,
                'rental_type': str,
                'rental_qty': float,
                'rental_period_id': int,
                'start_datetime': str,
                'end_datetime': str,
                'product_uom_qty': float,
                'price_unit': float,
            }]
        }
        :returns: order ID (int)
        """
        order = self.env["sale.order"].create(
            {
                "partner_id": vals["partner_id"],
                "warehouse_id": vals["warehouse_id"],
            }
        )

        line_vals = [
            {
                "order_id": order.id,
                "product_id": line["product_id"],
                "rental": True,
                "rental_type": line.get("rental_type", "new_rental"),
                "extension_rental_id": line.get("extension_rental_id") or False,
                "rental_qty": line["rental_qty"],
                "rental_period_id": line.get("rental_period_id"),
                "start_datetime": line["start_datetime"],
                "end_datetime": line["end_datetime"],
                "product_uom_qty": line.get("product_uom_qty", line["rental_qty"]),
                "price_unit": line.get("price_unit", 0),
            }
            for line in vals.get("lines", [])
        ]

        if line_vals:
            self.create(line_vals)

        return order.id

    @api.model
    def update_rental_order(self, order_id, vals):
        """Update a rental sale order and replace its lines in a single RPC.

        :param order_id: sale.order ID to update
        :param vals: same structure as create_rental_order
        """
        order = self.env["sale.order"].browse(order_id)
        order.write(
            {
                "partner_id": vals["partner_id"],
                "warehouse_id": vals["warehouse_id"],
            }
        )

        # Remove old rental lines
        old_lines = self.search([("order_id", "=", order_id), ("rental", "=", True)])
        if old_lines:
            old_lines.unlink()

        # Create new lines in batch
        line_vals = [
            {
                "order_id": order_id,
                "product_id": line["product_id"],
                "rental": True,
                "rental_type": line.get("rental_type", "new_rental"),
                "extension_rental_id": line.get("extension_rental_id") or False,
                "rental_qty": line["rental_qty"],
                "rental_period_id": line.get("rental_period_id"),
                "start_datetime": line["start_datetime"],
                "end_datetime": line["end_datetime"],
                "product_uom_qty": line.get("product_uom_qty", line["rental_qty"]),
                "price_unit": line.get("price_unit", 0),
            }
            for line in vals.get("lines", [])
        ]

        if line_vals:
            self.create(line_vals)

    @api.model
    def get_rental_order_edit_data(self, so_line_id):
        """Load all data needed to edit a rental order in a single RPC.

        Returns order header, all rental lines, location, and modal products.

        :param so_line_id: sale.order.line ID (the clicked calendar event)
        :returns: dict with order, location_id, modal_products
        """
        line = self.browse(so_line_id)
        if not line.exists():
            return None

        order = line.order_id

        # All rental lines for this order
        rental_lines = self.search_read(
            [("order_id", "=", order.id), ("rental", "=", True)],
            [
                "id",
                "product_id",
                "rental_type",
                "extension_rental_id",
                "rental_period_id",
                "rental_qty",
                "price_unit",
                "start_datetime",
                "end_datetime",
            ],
        )

        # Find rental_in location from warehouse
        warehouse = order.warehouse_id
        location_id = (
            warehouse.rental_in_location_id.id
            if warehouse.rental_in_location_id
            else None
        )

        # Get modal products with pricings for this location, filtered by order dates
        first_line = rental_lines[0] if rental_lines else None
        date_from = (
            str(first_line["start_datetime"]).split(" ")[0]
            if first_line and first_line.get("start_datetime")
            else None
        )
        date_to = (
            str(first_line["end_datetime"]).split(" ")[0]
            if first_line and first_line.get("end_datetime")
            else None
        )
        modal_products = self.env["product.product"].get_rental_modal_products(
            location_id, date_from=date_from, date_to=date_to
        )

        return {
            "order": {
                "id": order.id,
                "partner_id": [order.partner_id.id, order.partner_id.name],
                "warehouse_id": [
                    order.warehouse_id.id,
                    order.warehouse_id.name,
                ],
                "state": order.state,
            },
            "lines": rental_lines,
            "location_id": location_id,
            "modal_products": modal_products,
        }
