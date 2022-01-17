# Part of rental-vertical See LICENSE file for full copyright and licensing details.

from odoo.tests import common


class RentalStockCommon(common.TransactionCase):
    def setUp(self):
        super().setUp()

        # Rental Type, Picking Type, Locations and Uoms
        self.category_all = self.env.ref("product.product_category_all")
        self.rental_sale_type = self.env.ref("rental_base.rental_sale_type")
        self.picking_type_in = self.env.ref("stock.picking_type_in")
        self.picking_type_out = self.env.ref("stock.picking_type_out")
        self.stock_location = self.env.ref("stock.stock_location_stock")
        self.supplier_location = self.env.ref("stock.stock_location_suppliers")
        self.customer_location = self.env.ref("stock.stock_location_customers")
        self.uom_hour = self.env.ref("uom.product_uom_hour")
        self.uom_day = self.env.ref("uom.product_uom_day")
        self.uom_month = self.env.ref("rental_base.product_uom_month")
        self.uom_unit = self.env.ref("uom.product_uom_unit")
        self.uom_kgm = self.env.ref("uom.product_uom_kgm")
        self.warehouse0 = self.env.ref("stock.warehouse0")
        self.PartnerObj = self.env["res.partner"]
        self.partnerA = self.PartnerObj.create(
            {
                "name": "Partner A",
                "country_id": self.env.ref("base.de").id,
            }
        )

    def _create_rental_service_day(self, product):
        values = {
            "hw_product_id": product.id,
            "name": "Rental of %s (Day)" % product.name,
            "categ_id": product.categ_id.id,
            "copy_image": True,
        }
        res = (
            self.env["create.rental.product"]
            .with_context(active_model="product.product", active_id=product.id)
            .create(values)
            .create_rental_product()
        )

        rental_service = self.env["product.product"].browse(res["res_id"])
        rental_service.write(
            {
                "uom_id": self.uom_day.id,
                "uom_po_id": self.uom_day.id,
                "income_analytic_account_id": product.income_analytic_account_id.id,
                "list_price": 100,
            }
        )

        return rental_service

    def _create_move(self, product, src_location, dst_location, **values):
        Move = self.env["stock.move"]
        move = Move.new(
            {
                "product_id": product.id,
                "location_id": src_location.id,
                "location_dest_id": dst_location.id,
            }
        )
        move.onchange_product_id()
        move_values = move._convert_to_write(move._cache)
        move_values.update(**values)
        return Move.create(move_values)

    def _create_rental_order(self, partner_id, date_start, date_end, qty=1):
        """
        Create a Rental Order with Product (self.service_rental)
        """
        date_qty = (date_end - date_start).days + 1
        rental_order = self.env["sale.order"].create(
            {
                "type_id": self.rental_sale_type.id,
                "partner_id": partner_id,
                "partner_invoice_id": partner_id,
                "partner_shipping_id": partner_id,
                "pricelist_id": self.env.ref("product.list0").id,
                "picking_policy": "direct",
                "warehouse_id": self.warehouse0.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "Service for Rental",
                            "product_id": self.service_rental.id,
                            "rental": True,
                            "rental_type": "new_rental",
                            "rental_qty": qty,
                            "product_uom_qty": date_qty * qty,
                            "start_date": date_start,
                            "end_date": date_end,
                            "price_unit": 100,
                            "product_uom": self.uom_day.id,
                        },
                    )
                ],
            }
        )
        self.assertEqual(rental_order.state, "draft")
        return rental_order
