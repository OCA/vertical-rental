# Copyright 2024 OCA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tests.common import TransactionCase


class RentalDashboardCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.partner = cls.env["res.partner"].create({"name": "Test Dashboard Partner"})
        cls.warehouse = cls.env.ref("stock.warehouse0")
        cls.warehouse.write({"rental_allowed": True})
        cls.rental_in_loc = cls.warehouse.rental_in_location_id

        cls.physical = cls.env["product.product"].create(
            {"name": "Dashboard Physical Product", "type": "product"}
        )
        cls.service = cls.env["product.product"].create(
            {
                "name": "Dashboard Rental Service",
                "type": "service",
                "must_have_dates": True,
                "rented_product_id": cls.physical.id,
            }
        )
        # rental field lives on product.template (from rental_base).
        # Set it there so the stored compute on sale.order.line picks it up.
        if "rental" in cls.env["product.template"]._fields:
            cls.service.product_tmpl_id.write({"rental": True})
        cls.env["stock.quant"].create(
            {
                "product_id": cls.physical.id,
                "location_id": cls.rental_in_loc.id,
                "quantity": 10.0,
            }
        )
        cls.rental_period = cls.env["rental.period"].search([], limit=1)
        if not cls.rental_period:
            cls.rental_period = cls.env["rental.period"].create(
                {"name": "Day", "code": "day", "hours_per_unit": 24}
            )

    def _rental_order_vals(self, **line_overrides):
        line = {
            "product_id": self.service.id,
            "rental_type": "new_rental",
            "rental_qty": 1.0,
            "rental_period_id": self.rental_period.id,
            "start_datetime": "2024-01-01 08:00:00",
            "end_datetime": "2024-01-10 08:00:00",
            "product_uom_qty": 9.0,
            "price_unit": 100.0,
        }
        line.update(line_overrides)
        return {
            "partner_id": self.partner.id,
            "warehouse_id": self.warehouse.id,
            "lines": [line],
        }


class TestRentalDashboardSaleOrderLine(RentalDashboardCommon):
    def test_compute_rental_display_name_non_rental(self):
        """Non-rental line (plain service product) falls back to line.name."""
        # Use a plain service product with no rental setup so line.rental=False
        plain_product = self.env["product.product"].create(
            {"name": "Plain Service", "type": "service"}
        )
        order = self.env["sale.order"].create({"partner_id": self.partner.id})
        line = self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": plain_product.id,
                "name": "Plain line",
                "price_unit": 0,
                "product_uom_qty": 1,
            }
        )
        self.assertEqual(line.rental_display_name, "Plain line")

    def test_compute_rental_display_name_rental(self):
        """Rental line includes the product display name."""
        order = self.env["sale.order"].create({"partner_id": self.partner.id})
        line = self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": self.service.id,
                "name": "Rental line",
                "price_unit": 100,
                "product_uom_qty": 1,
                "rental": True,
                "rental_qty": 1.0,
                "rental_period_id": self.rental_period.id,
                "start_datetime": "2024-01-01 08:00:00",
                "end_datetime": "2024-01-02 08:00:00",
            }
        )
        self.assertIn(self.service.display_name, line.rental_display_name)

    def test_compute_rental_display_name_with_location(self):
        """Rental line with warehouse location includes location name."""
        order = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "warehouse_id": self.warehouse.id,
            }
        )
        line = self.env["sale.order.line"].create(
            {
                "order_id": order.id,
                "product_id": self.service.id,
                "name": "Rental line",
                "price_unit": 100,
                "product_uom_qty": 1,
                "rental": True,
                "rental_qty": 1.0,
                "rental_period_id": self.rental_period.id,
                "start_datetime": "2024-01-01 08:00:00",
                "end_datetime": "2024-01-02 08:00:00",
            }
        )
        if self.rental_in_loc:
            self.assertIn(self.rental_in_loc.name, line.rental_display_name)

    def test_create_rental_order(self):
        """create_rental_order creates a sale order with one rental line."""
        SolEnv = self.env["sale.order.line"]
        order_id = SolEnv.create_rental_order(self._rental_order_vals())

        self.assertIsInstance(order_id, int)
        order = self.env["sale.order"].browse(order_id)
        self.assertEqual(order.partner_id, self.partner)
        self.assertEqual(order.warehouse_id, self.warehouse)
        self.assertEqual(len(order.order_line), 1)

        line = order.order_line[0]
        self.assertTrue(line.rental)
        self.assertEqual(line.product_id, self.service)
        self.assertEqual(line.rental_qty, 1.0)

    def test_create_rental_order_no_lines(self):
        """create_rental_order with empty lines creates an order without lines."""
        order_id = self.env["sale.order.line"].create_rental_order(
            {
                "partner_id": self.partner.id,
                "warehouse_id": self.warehouse.id,
                "lines": [],
            }
        )
        order = self.env["sale.order"].browse(order_id)
        self.assertFalse(order.order_line)

    def test_update_rental_order(self):
        """update_rental_order replaces rental lines on the order."""
        SolEnv = self.env["sale.order.line"]
        order_id = SolEnv.create_rental_order(self._rental_order_vals())

        new_service = self.env["product.product"].create(
            {
                "name": "Second Rental Service",
                "type": "service",
                "must_have_dates": True,
                "rented_product_id": self.physical.id,
            }
        )
        SolEnv.update_rental_order(
            order_id,
            self._rental_order_vals(
                product_id=new_service.id,
                rental_qty=2.0,
                start_datetime="2024-02-01 08:00:00",
                end_datetime="2024-02-05 08:00:00",
                product_uom_qty=8.0,
            ),
        )

        order = self.env["sale.order"].browse(order_id)
        self.assertEqual(len(order.order_line), 1)
        self.assertEqual(order.order_line[0].product_id, new_service)
        self.assertEqual(order.order_line[0].rental_qty, 2.0)

    def test_get_rental_order_edit_data(self):
        """get_rental_order_edit_data returns structured data for editing."""
        SolEnv = self.env["sale.order.line"]
        order_id = SolEnv.create_rental_order(self._rental_order_vals())
        line_id = self.env["sale.order"].browse(order_id).order_line[0].id

        result = SolEnv.get_rental_order_edit_data(line_id)

        self.assertIsNotNone(result)
        self.assertIn("order", result)
        self.assertIn("lines", result)
        self.assertIn("location_id", result)
        self.assertIn("modal_products", result)
        self.assertEqual(result["order"]["id"], order_id)
        self.assertEqual(len(result["lines"]), 1)

    def test_get_rental_order_edit_data_nonexistent(self):
        """get_rental_order_edit_data returns None for a non-existent line ID."""
        result = self.env["sale.order.line"].get_rental_order_edit_data(999999999)
        self.assertIsNone(result)


class TestRentalDashboardProduct(RentalDashboardCommon):
    def test_get_rental_dashboard_data_keys(self):
        """get_rental_dashboard_data returns all expected top-level keys."""
        result = self.env["product.product"].get_rental_dashboard_data()
        self.assertIn("locations", result)
        self.assertIn("warehouses", result)
        self.assertIn("rental_periods", result)
        self.assertIn("products", result)

    def test_get_rental_dashboard_data_with_location(self):
        """get_rental_dashboard_data accepts a location_id filter."""
        result = self.env["product.product"].get_rental_dashboard_data(
            location_id=self.rental_in_loc.id
        )
        self.assertIsInstance(result["products"], list)

    def test_get_rental_dashboard_data_with_dates(self):
        """get_rental_dashboard_data accepts date filters."""
        result = self.env["product.product"].get_rental_dashboard_data(
            date_from="2024-01-01", date_to="2024-01-31"
        )
        self.assertIsInstance(result["products"], list)

    def test_get_rental_products(self):
        """get_rental_products returns a list."""
        result = self.env["product.product"].get_rental_products()
        self.assertIsInstance(result, list)

    def test_get_rental_products_with_location(self):
        """get_rental_products filtered by location returns a list."""
        result = self.env["product.product"].get_rental_products(
            location_id=self.rental_in_loc.id
        )
        self.assertIsInstance(result, list)

    def test_get_rental_modal_products(self):
        """get_rental_modal_products returns a list."""
        result = self.env["product.product"].get_rental_modal_products()
        self.assertIsInstance(result, list)

    def test_get_rental_modal_products_with_location(self):
        """get_rental_modal_products filtered by location returns a list."""
        result = self.env["product.product"].get_rental_modal_products(
            location_id=self.rental_in_loc.id
        )
        self.assertIsInstance(result, list)

    def test_get_rental_modal_products_with_dates(self):
        """get_rental_modal_products with date range filters committed rentals."""
        result = self.env["product.product"].get_rental_modal_products(
            location_id=self.rental_in_loc.id,
            date_from="2024-01-01",
            date_to="2024-01-31",
        )
        self.assertIsInstance(result, list)

    def test_check_rental_availability_sufficient_stock(self):
        """check_rental_availability returns no errors when stock is sufficient."""
        errors = self.env["product.product"].check_rental_availability(
            location_id=self.rental_in_loc.id,
            start_date="2024-03-01",
            end_date="2024-03-10",
            lines=[{"product_id": self.service.id, "rental_qty": 2.0}],
        )
        self.assertEqual(errors, [])

    def test_check_rental_availability_insufficient_stock(self):
        """check_rental_availability returns an error when qty exceeds stock."""
        errors = self.env["product.product"].check_rental_availability(
            location_id=self.rental_in_loc.id,
            start_date="2024-03-01",
            end_date="2024-03-10",
            lines=[{"product_id": self.service.id, "rental_qty": 100.0}],
        )
        self.assertTrue(errors)
        self.assertIn(self.physical.display_name, errors[0])

    def test_check_rental_availability_empty_lines(self):
        """check_rental_availability with no lines returns no errors."""
        errors = self.env["product.product"].check_rental_availability(
            location_id=self.rental_in_loc.id,
            start_date="2024-03-01",
            end_date="2024-03-10",
            lines=[],
        )
        self.assertEqual(errors, [])

    def test_rental_color_field_default(self):
        """rental_color defaults to 0."""
        self.assertEqual(self.physical.rental_color, 0)

    def test_rental_color_field_write(self):
        """rental_color can be updated."""
        self.physical.write({"rental_color": 5})
        self.assertEqual(self.physical.rental_color, 5)
