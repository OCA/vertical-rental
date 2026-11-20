from odoo import fields
from odoo.exceptions import UserError, ValidationError

from .stock_common import RentalStockCommon


class TestSaleRentalExt(RentalStockCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.date_0101 = fields.Date.to_date("2021-01-01")
        cls.date_0110 = fields.Date.to_date("2021-01-10")
        cls.date_0120 = fields.Date.to_date("2021-01-20")
        cls.product_rental = cls.env["product.product"].create(
            {
                "name": "Hardware Product",
                "type": "consu",
                "categ_id": cls.category_all.id,
                "uom_id": cls.uom_unit.id,
                "uom_po_id": cls.uom_unit.id,
            }
        )
        cls.service_rental = cls._create_rental_service_day(cls.product_rental)

    def _create_rental_order(self, partner_id, date_start, date_end, qty=1):
        date_qty = (date_end - date_start).days + 1
        pricelist = self.env["product.pricelist"].search([], limit=1)
        if not pricelist:
            pricelist = self.env["product.pricelist"].create(
                {
                    "name": "Test Pricelist",
                    "currency_id": self.env.ref("base.USD").id,
                }
            )
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
        return rental_order

    def test_10_check_rental_product_must_be_service(self):
        with self.assertRaises(ValidationError):
            self.env["product.product"].create(
                {
                    "name": "Not a service",
                    "type": "consu",
                    "uom_id": self.uom_day.id,
                    "must_have_dates": True,
                    "rented_product_id": self.product_rental.id,
                }
            )

    def test_11_check_rental_product_must_have_dates(self):
        with self.assertRaises(ValidationError):
            self.env["product.product"].create(
                {
                    "name": "No dates service",
                    "type": "service",
                    "uom_id": self.uom_day.id,
                    "must_have_dates": False,
                    "rented_product_id": self.product_rental.id,
                }
            )

    def test_12_check_rental_product_must_use_day_uom(self):
        with self.assertRaises(ValidationError):
            self.env["product.product"].create(
                {
                    "name": "Wrong UoM service",
                    "type": "service",
                    "uom_id": self.uom_unit.id,
                    "must_have_dates": True,
                    "rented_product_id": self.product_rental.id,
                }
            )

    def test_20_is_rental_line(self):
        rental_order = self._create_rental_order(
            self.partnerA.id,
            self.date_0101,
            self.date_0110,
        )
        self.assertTrue(rental_order.is_rental_line)

    def test_21_is_of_rental_type_new(self):
        rental_order = self._create_rental_order(
            self.partnerA.id,
            self.date_0101,
            self.date_0110,
        )
        self.assertEqual(rental_order.is_of_rental_type, "new_rental")

    def test_22_is_can_sell_rental_false(self):
        rental_order = self._create_rental_order(
            self.partnerA.id,
            self.date_0101,
            self.date_0110,
        )
        self.assertFalse(rental_order.is_can_sell_rental)

    def test_30_check_extension_without_extension_rental_id(self):
        rental_order = self._create_rental_order(
            self.partnerA.id,
            self.date_0101,
            self.date_0110,
        )
        with self.assertRaises(ValidationError):
            rental_order.order_line[0].write(
                {
                    "rental_type": "rental_extension",
                    "extension_rental_id": False,
                }
            )

    def test_40_check_new_rental_product_not_rental_service(self):
        normal_product = self.env["product.product"].create(
            {
                "name": "Normal Service",
                "type": "service",
                "uom_id": self.uom_day.id,
                "must_have_dates": True,
            }
        )
        date_start = self.date_0101
        date_end = self.date_0110
        date_qty = (date_end - date_start).days + 1
        with self.assertRaises(ValidationError):
            self.env["sale.order"].create(
                {
                    "type_id": self.rental_sale_type.id,
                    "partner_id": self.partnerA.id,
                    "partner_invoice_id": self.partnerA.id,
                    "partner_shipping_id": self.partnerA.id,
                    "pricelist_id": self.env["product.pricelist"]
                    .search([], limit=1)
                    .id,
                    "picking_policy": "direct",
                    "warehouse_id": self.warehouse0.id,
                    "order_line": [
                        (
                            0,
                            0,
                            {
                                "name": "Not a rental service",
                                "product_id": normal_product.id,
                                "rental": True,
                                "rental_type": "new_rental",
                                "rental_qty": 1,
                                "product_uom_qty": date_qty,
                                "start_date": date_start,
                                "end_date": date_end,
                                "price_unit": 100,
                                "product_uom": self.uom_day.id,
                            },
                        )
                    ],
                }
            )

    def test_50_check_qty_mismatch(self):
        date_start = self.date_0101
        date_end = self.date_0110
        rental_order = self._create_rental_order(
            self.partnerA.id, date_start, date_end, qty=1
        )
        line = rental_order.order_line[0]
        with self.assertRaises(ValidationError):
            line.write({"product_uom_qty": 999})

    def test_60_rental_type_change_clears_extension(self):
        rental_order = self._create_rental_order(
            self.partnerA.id,
            self.date_0101,
            self.date_0110,
        )
        line = rental_order.order_line[0]
        with self.assertRaises(ValidationError):
            line.write({"rental_type": "rental_extension"})
        self.assertEqual(line.rental_type, "new_rental")
        self.assertFalse(line.extension_rental_id)

    def test_70_sell_rental_not_delivered(self):
        date_start = self.date_0101
        date_end = self.date_0110
        rental_order = self._create_rental_order(self.partnerA.id, date_start, date_end)
        rental_order.action_confirm()
        rental = self.env["sale.rental"].search(
            [("start_order_line_id", "=", rental_order.order_line[0].id)]
        )
        self.assertTrue(rental)
        sell_order = self.env["sale.order"].create(
            {
                "partner_id": self.partnerA.id,
                "partner_invoice_id": self.partnerA.id,
                "partner_shipping_id": self.partnerA.id,
                "pricelist_id": self.env["product.pricelist"].search([], limit=1).id,
                "picking_policy": "direct",
                "warehouse_id": self.warehouse0.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "Sell rental",
                            "product_id": self.product_rental.id,
                            "product_uom_qty": 1,
                            "product_uom": self.uom_unit.id,
                            "sell_rental_id": rental.id,
                            "price_unit": 50,
                        },
                    )
                ],
            }
        )
        with self.assertRaises(UserError):
            sell_order.action_confirm()

    def test_80_rental_state_ordered(self):
        rental_order = self._create_rental_order(
            self.partnerA.id,
            self.date_0101,
            self.date_0110,
        )
        rental_order.action_confirm()
        rental = self.env["sale.rental"].search(
            [("start_order_line_id", "=", rental_order.order_line[0].id)]
        )
        self.assertEqual(rental.state, "ordered")

    def test_81_rental_state_out(self):
        rental_order = self._create_rental_order(
            self.partnerA.id,
            self.date_0101,
            self.date_0110,
        )
        rental_order.action_confirm()
        rental = self.env["sale.rental"].search(
            [("start_order_line_id", "=", rental_order.order_line[0].id)]
        )
        out_pick = rental_order.picking_ids.filtered(
            lambda p: p.location_dest_id == self.warehouse0.rental_out_location_id
        )
        out_pick.action_assign()
        out_pick.move_ids.picked = True
        out_pick.button_validate()
        self.assertEqual(rental.state, "out")

    def test_82_rental_state_in(self):
        rental_order = self._create_rental_order(
            self.partnerA.id,
            self.date_0101,
            self.date_0110,
        )
        rental_order.action_confirm()
        rental = self.env["sale.rental"].search(
            [("start_order_line_id", "=", rental_order.order_line[0].id)]
        )
        out_pick = rental_order.picking_ids.filtered(
            lambda p: p.location_dest_id == self.warehouse0.rental_out_location_id
        )
        out_pick.action_assign()
        out_pick.move_ids.picked = True
        out_pick.button_validate()
        in_pick = rental_order.picking_ids.filtered(
            lambda p: p.location_dest_id == self.warehouse0.rental_in_location_id
        )
        in_pick.action_assign()
        in_pick.move_ids.picked = True
        in_pick.button_validate()
        self.assertEqual(rental.state, "in")

    def test_90_compute_display_name(self):
        rental_order = self._create_rental_order(
            self.partnerA.id,
            self.date_0101,
            self.date_0110,
        )
        rental_order.action_confirm()
        rental = self.env["sale.rental"].search(
            [("start_order_line_id", "=", rental_order.order_line[0].id)]
        )
        self.assertIn(self.partnerA.display_name, rental.display_name)
        self.assertIn(self.product_rental.display_name, rental.display_name)

    def test_100_rental_end_date_no_extension(self):
        date_start = self.date_0101
        date_end = self.date_0110
        rental_order = self._create_rental_order(self.partnerA.id, date_start, date_end)
        rental_order.action_confirm()
        rental = self.env["sale.rental"].search(
            [("start_order_line_id", "=", rental_order.order_line[0].id)]
        )
        self.assertEqual(rental.end_date, date_end)

    def test_110_prepare_procurement_values_sell_route(self):
        date_start = self.date_0101
        date_end = self.date_0110
        rental_order = self._create_rental_order(self.partnerA.id, date_start, date_end)
        rental_order.action_confirm()
        rental = self.env["sale.rental"].search(
            [("start_order_line_id", "=", rental_order.order_line[0].id)]
        )
        out_pick = rental_order.picking_ids.filtered(
            lambda p: p.location_dest_id == self.warehouse0.rental_out_location_id
        )
        out_pick.action_assign()
        out_pick.move_ids.picked = True
        out_pick.button_validate()
        sell_order = self.env["sale.order"].create(
            {
                "partner_id": self.partnerA.id,
                "partner_invoice_id": self.partnerA.id,
                "partner_shipping_id": self.partnerA.id,
                "pricelist_id": self.env["product.pricelist"].search([], limit=1).id,
                "picking_policy": "direct",
                "warehouse_id": self.warehouse0.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "Sell rental",
                            "product_id": self.product_rental.id,
                            "product_uom_qty": 1,
                            "product_uom": self.uom_unit.id,
                            "sell_rental_id": rental.id,
                            "price_unit": 50,
                        },
                    )
                ],
            }
        )
        sell_order.action_confirm()
        line = sell_order.order_line[0]
        vals = line._prepare_procurement_values(group_id=False)
        self.assertIn(
            self.warehouse0.sell_rented_product_route_id,
            vals.get("route_ids", []),
        )

    def test_120_warehouse_write_disable_rental(self):
        wh = self.warehouse0
        wh.write({"rental_allowed": False})
        self.assertFalse(wh.rental_route_id)
        self.assertFalse(wh.sell_rented_product_route_id)

    def test_121_warehouse_write_enable_rental(self):
        wh = self.warehouse0
        wh.write({"rental_allowed": False})
        wh.write({"rental_allowed": True})
        self.assertTrue(wh.rental_route_id)
        self.assertTrue(wh.sell_rented_product_route_id)
        self.assertTrue(wh.rental_in_location_id)
        self.assertTrue(wh.rental_out_location_id)
