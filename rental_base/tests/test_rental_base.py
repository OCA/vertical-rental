# Part of rental-vertical See LICENSE file for full copyright and licensing details.

from odoo import fields
from odoo.exceptions import UserError, ValidationError

from odoo.addons.rental_base.tests.stock_common import RentalStockCommon


class TestRentalBase(RentalStockCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        ProductObj = cls.env["product.product"]
        cls.product_rental = ProductObj.create(
            {
                "name": "Rental Product",
                "type": "consu",
                "categ_id": cls.category_all.id,
            }
        )
        cls.service_rental = cls._create_rental_service_day(cls.product_rental)
        cls.date_0101 = fields.Date.to_date("2021-01-01")
        cls.date_0110 = fields.Date.to_date("2021-01-10")
        cls.date_0115 = fields.Date.to_date("2021-01-15")
        cls.date_0120 = fields.Date.to_date("2021-01-20")

    def test_10_is_rental_order(self):
        """Test that is_rental_order is computed based on type_id."""
        rental_order = self._create_rental_order(
            self.partnerA.id, self.date_0101, self.date_0110
        )
        self.assertTrue(rental_order.is_rental_order)
        self.assertEqual(rental_order.type_id, self.rental_sale_type)

    def test_11_is_rental_order_normal(self):
        """Test that normal orders are not rental orders."""
        normal_type = self.env.ref("sale_order_type.normal_sale_type")
        order = self.env["sale.order"].create(
            {
                "type_id": normal_type.id,
                "partner_id": self.partnerA.id,
                "partner_invoice_id": self.partnerA.id,
                "partner_shipping_id": self.partnerA.id,
                "pricelist_id": self.test_pricelist.id,
                "warehouse_id": self.warehouse0.id,
            }
        )
        self.assertFalse(order.is_rental_order)

    def test_12_is_rental_order_no_type(self):
        """Test is_rental_order when no type_id set."""
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partnerA.id,
                "partner_invoice_id": self.partnerA.id,
                "partner_shipping_id": self.partnerA.id,
                "pricelist_id": self.test_pricelist.id,
                "warehouse_id": self.warehouse0.id,
            }
        )
        self.assertFalse(order.is_rental_order)

    def test_20_default_dates(self):
        """Test default_start_date and default_end_date computed from lines."""
        rental_order = self._create_rental_order(
            self.partnerA.id, self.date_0101, self.date_0110
        )
        self.assertEqual(rental_order.default_start_date, self.date_0101)
        self.assertEqual(rental_order.default_end_date, self.date_0110)

    def test_21_default_dates_multiple_lines(self):
        """Test default dates with multiple order lines."""
        pricelist = self.env["product.pricelist"].search([], limit=1)
        date_qty = (self.date_0115 - self.date_0101).days + 1
        order = self.env["sale.order"].create(
            {
                "type_id": self.rental_sale_type.id,
                "partner_id": self.partnerA.id,
                "partner_invoice_id": self.partnerA.id,
                "partner_shipping_id": self.partnerA.id,
                "pricelist_id": pricelist.id,
                "warehouse_id": self.warehouse0.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.service_rental.id,
                            "rental": True,
                            "rental_type": "new_rental",
                            "rental_qty": 1,
                            "product_uom_qty": 10,
                            "start_date": self.date_0101,
                            "end_date": self.date_0110,
                            "price_unit": 100,
                            "product_uom": self.uom_day.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "product_id": self.service_rental.id,
                            "rental": True,
                            "rental_type": "new_rental",
                            "rental_qty": 1,
                            "product_uom_qty": date_qty,
                            "start_date": self.date_0101,
                            "end_date": self.date_0115,
                            "price_unit": 100,
                            "product_uom": self.uom_day.id,
                        },
                    ),
                ],
            }
        )
        self.assertEqual(order.default_start_date, self.date_0101)
        self.assertEqual(order.default_end_date, self.date_0115)

    def test_22_default_dates_no_lines(self):
        """Test default dates when no order lines."""
        order = self.env["sale.order"].create(
            {
                "type_id": self.rental_sale_type.id,
                "partner_id": self.partnerA.id,
                "partner_invoice_id": self.partnerA.id,
                "partner_shipping_id": self.partnerA.id,
                "pricelist_id": self.test_pricelist.id,
                "warehouse_id": self.warehouse0.id,
            }
        )
        self.assertFalse(order.default_start_date)
        self.assertFalse(order.default_end_date)

    def test_30_rental_qty_uom(self):
        """Test rental_qty_uom related field."""
        rental_order = self._create_rental_order(
            self.partnerA.id, self.date_0101, self.date_0110
        )
        line = rental_order.order_line[0]
        self.assertEqual(line.rental_qty_uom, self.product_rental.uom_id)

    def test_40_order_type_compute_inverse(self):
        """Test order_type compute and inverse on sale.order.line."""
        rental_order = self._create_rental_order(
            self.partnerA.id, self.date_0101, self.date_0110
        )
        line = rental_order.order_line[0]
        self.assertEqual(line.order_type, "rental")
        self.assertTrue(line.rental)

        line.order_type = "normal"
        self.assertFalse(line.rental)

        line.order_type = "rental"
        self.assertTrue(line.rental)

    def test_50_check_sale_line_rental_missing_extension(self):
        """Test constraint: rental_extension without extension_rental_id raises."""
        with self.assertRaises(ValidationError):
            self.env["sale.order.line"].create(
                {
                    "product_id": self.service_rental.id,
                    "rental": True,
                    "rental_type": "rental_extension",
                    "rental_qty": 1,
                    "product_uom_qty": 10,
                    "start_date": self.date_0101,
                    "end_date": self.date_0110,
                    "price_unit": 100,
                    "product_uom": self.uom_day.id,
                    "order_id": self._create_rental_order(
                        self.partnerA.id, self.date_0101, self.date_0110
                    ).id,
                }
            )

    def test_51_check_sale_line_rental_no_rented_product(self):
        """Test constraint: new_rental with non-service product raises."""
        with self.assertRaises(ValidationError):
            self.env["sale.order.line"].create(
                {
                    "product_id": self.product_rental.id,
                    "rental": True,
                    "rental_type": "new_rental",
                    "rental_qty": 1,
                    "product_uom_qty": 10,
                    "start_date": self.date_0101,
                    "end_date": self.date_0110,
                    "price_unit": 100,
                    "product_uom": self.uom_day.id,
                    "order_id": self._create_rental_order(
                        self.partnerA.id, self.date_0101, self.date_0110
                    ).id,
                }
            )

    def test_60_get_number_of_time_unit_day(self):
        """Test _get_number_of_time_unit for day UoM."""
        rental_order = self._create_rental_order(
            self.partnerA.id, self.date_0101, self.date_0110
        )
        line = rental_order.order_line[0]
        number = line._get_number_of_time_unit()
        self.assertEqual(number, 10)

    def test_61_get_number_of_time_unit_hour(self):
        """Test _get_number_of_time_unit for hour UoM."""
        order = self.env["sale.order"].create(
            {
                "type_id": self.rental_sale_type.id,
                "partner_id": self.partnerA.id,
                "partner_invoice_id": self.partnerA.id,
                "partner_shipping_id": self.partnerA.id,
                "pricelist_id": self.test_pricelist.id,
                "warehouse_id": self.warehouse0.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.service_rental.id,
                            "rental": True,
                            "rental_type": "new_rental",
                            "rental_qty": 1,
                            "product_uom_qty": 80,
                            "start_date": self.date_0101,
                            "end_date": self.date_0110,
                            "price_unit": 100,
                            "product_uom": self.uom_hour.id,
                        },
                    )
                ],
            }
        )
        line = order.order_line[0]
        number = line._get_number_of_time_unit()
        self.assertEqual(number, 80)

    def test_62_get_number_of_time_unit_month(self):
        """Test _get_number_of_time_unit for month UoM."""
        order = self.env["sale.order"].create(
            {
                "type_id": self.rental_sale_type.id,
                "partner_id": self.partnerA.id,
                "partner_invoice_id": self.partnerA.id,
                "partner_shipping_id": self.partnerA.id,
                "pricelist_id": self.test_pricelist.id,
                "warehouse_id": self.warehouse0.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.service_rental.id,
                            "rental": True,
                            "rental_type": "new_rental",
                            "rental_qty": 1,
                            "product_uom_qty": 1,
                            "start_date": self.date_0101,
                            "end_date": self.date_0120,
                            "price_unit": 100,
                            "product_uom": self.uom_month.id,
                        },
                    )
                ],
            }
        )
        line = order.order_line[0]
        number = line._get_number_of_time_unit()
        self.assertEqual(number, 1)

    def test_63_get_number_of_time_unit_week(self):
        """Test _get_number_of_time_unit for week UoM."""
        order = self.env["sale.order"].create(
            {
                "type_id": self.rental_sale_type.id,
                "partner_id": self.partnerA.id,
                "partner_invoice_id": self.partnerA.id,
                "partner_shipping_id": self.partnerA.id,
                "pricelist_id": self.test_pricelist.id,
                "warehouse_id": self.warehouse0.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.service_rental.id,
                            "rental": True,
                            "rental_type": "new_rental",
                            "rental_qty": 1,
                            "product_uom_qty": 3,
                            "start_date": self.date_0101,
                            "end_date": self.date_0120,
                            "price_unit": 100,
                            "product_uom": self.uom_week.id,
                        },
                    )
                ],
            }
        )
        line = order.order_line[0]
        number = line._get_number_of_time_unit()
        self.assertEqual(number, 3)

    def test_70_ir_sequence_rental_order(self):
        """Test that rental orders get the custom sequence RO prefix."""
        rental_order = self._create_rental_order(
            self.partnerA.id, self.date_0101, self.date_0110
        )
        self.assertTrue(rental_order.name.startswith("RO"))

    def test_71_ir_sequence_normal_order(self):
        """Test that normal orders don't use the rental sequence."""
        normal_type = self.env.ref("sale_order_type.normal_sale_type")
        order = self.env["sale.order"].create(
            {
                "type_id": normal_type.id,
                "partner_id": self.partnerA.id,
                "partner_invoice_id": self.partnerA.id,
                "partner_shipping_id": self.partnerA.id,
                "pricelist_id": self.test_pricelist.id,
                "warehouse_id": self.warehouse0.id,
            }
        )
        self.assertFalse(order.name.startswith("RO"))

    def test_80_product_rental_field(self):
        """Test that rental Boolean can be set on product template."""
        self.product_rental.product_tmpl_id.rental = True
        self.assertTrue(self.product_rental.product_tmpl_id.rental)

    def test_81_product_rental_filter(self):
        """Test that rental product can be searched by rental filter."""
        self.product_rental.product_tmpl_id.rental = True
        products = self.env["product.product"].search(
            [("rental", "=", True), ("type", "=", "consu")]
        )
        self.assertIn(self.product_rental, products)

    def test_90_unlink_rental_order(self):
        """Test that unlinking a rental order also unlinks related sale.rental."""
        rental_order = self._create_rental_order(
            self.partnerA.id, self.date_0101, self.date_0110
        )
        rental_order.action_confirm()
        line = rental_order.order_line[0]
        rentals = self.env["sale.rental"].search(
            [("start_order_line_id", "=", line.id)]
        )
        self.assertEqual(len(rentals), 1)
        rental_order._action_cancel()
        rentals = self.env["sale.rental"].search(
            [("start_order_line_id", "=", line.id)]
        )
        self.assertEqual(len(rentals), 1)
        rental_order.unlink()
        rentals = self.env["sale.rental"].search(
            [("start_order_line_id", "=", line.id)]
        )
        self.assertEqual(len(rentals), 0)

    def test_100_write_start_date_confirmed_order(self):
        """Test that writing start_date on confirmed order line raises."""
        rental_order = self._create_rental_order(
            self.partnerA.id, self.date_0101, self.date_0110
        )
        rental_order.action_confirm()
        line = rental_order.order_line[0]
        with self.assertRaises(UserError):
            line.write({"start_date": self.date_0115})

    def test_101_write_start_date_with_allow_write(self):
        """Test that writing start_date with allow_write context works."""
        rental_order = self._create_rental_order(
            self.partnerA.id, self.date_0101, self.date_0110
        )
        rental_order.action_confirm()
        line = rental_order.order_line[0]
        line.with_context(allow_write=True).write({"start_date": self.date_0115})
        self.assertEqual(line.start_date, self.date_0115)
