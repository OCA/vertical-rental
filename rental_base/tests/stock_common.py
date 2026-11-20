# Part of rental-vertical See LICENSE file for full copyright and licensing details.

from odoo.addons.base.tests.common import BaseCommon


class RentalStockCommon(BaseCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(
            context=dict(
                cls.env.context,
                allowed_company_ids=[cls.env.company.id],
                tracking_disable=True,
            )
        )

        # Rental Type, Picking Type, Locations and Uoms
        cls.category_all = cls.env.ref("product.product_category_all")
        cls.rental_sale_type = cls.env.ref("rental_base.rental_sale_type")
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.uom_hour = cls.env.ref("uom.product_uom_hour")
        cls.uom_day = cls.env.ref("uom.product_uom_day")
        cls.uom_month = cls.env.ref("rental_base.product_uom_month")
        cls.uom_week = cls.env.ref("rental_base.product_uom_week")
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.uom_kgm = cls.env.ref("uom.product_uom_kgm")
        cls.warehouse0 = cls.env.ref("stock.warehouse0")
        cls.PartnerObj = cls.env["res.partner"]
        cls.partnerA = cls.PartnerObj.create(
            {
                "name": "Partner A",
                "country_id": cls.env.ref("base.de").id,
            }
        )
        usd = cls.env.ref("base.USD")
        if not usd.active:
            usd.active = True
        PricelistObj = cls.env["product.pricelist"]
        cls.test_pricelist = PricelistObj.create(
            {
                "name": "Test Pricelist",
                "currency_id": usd.id,
            }
        )

    @classmethod
    def _create_rental_service_day(cls, product):
        values = {
            "hw_product_id": product.id,
            "name": f"Rental of {product.name} (Day)",
            "categ_id": product.categ_id.id,
            "copy_image": True,
        }
        company_id = cls.env.company.id
        res = (
            cls.env["create.rental.product"]
            .with_context(
                active_model="product.product",
                active_id=product.id,
                allowed_company_ids=[company_id],
            )
            .create(values)
            .create_rental_product()
        )

        rental_service = cls.env["product.product"].browse(res["res_id"])
        rental_service_values = {
            "uom_id": cls.uom_day.id,
            "uom_po_id": cls.uom_day.id,
            "list_price": 100,
        }
        rental_service.write(rental_service_values)

        return rental_service

    def _create_move(self, product, src_location, dst_location, **values):
        Move = self.env["stock.move"]
        move = Move.new(
            {
                "product_id": product.id,
                "product_uom": product.uom_id.id,
                "name": product.display_name,
                "location_id": src_location.id,
                "location_dest_id": dst_location.id,
            }
        )

        move._onchange_product_id()
        move_values = move._convert_to_write(move._cache)
        move_values.update(**values)
        return Move.create(move_values)

    def _create_rental_order(self, partner_id, date_start, date_end, qty=1):
        """
        Create a Rental Order with Product (self.service_rental)
        """
        date_qty = (date_end - date_start).days + 1
        pricelist = self.test_pricelist
        rental_order = self.env["sale.order"].create(
            {
                "type_id": self.rental_sale_type.id,
                "partner_id": partner_id,
                "partner_invoice_id": partner_id,
                "partner_shipping_id": partner_id,
                "pricelist_id": pricelist.id,
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
