# Part of rental-vertical See LICENSE file for full copyright and licensing details.

from odoo import fields
from odoo.tests import Form, new_test_user

from odoo.addons.rental_base.tests.stock_common import RentalStockCommon


class TestCreateUnlinkRentalOrder(RentalStockCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        ProductObj = cls.env["product.product"]
        cls.SaleOrderObj = cls.env["sale.order"]
        cls.product_rental = ProductObj.create(
            {
                "name": "Rental Product",
                "type": "product",
                "categ_id": cls.category_all.id,
            }
        )
        # rental service product
        cls.service_rental = cls._create_rental_service_day(product=cls.product_rental)
        # dates
        cls.date_0101 = fields.Date.from_string("2021-01-01")
        cls.date_0110 = fields.Date.from_string("2021-01-10")
        cls.salesman = new_test_user(
            cls.env,
            login="rental_order_salesman",
            groups="sales_team.group_sale_salesman",
        )

    def test_01_unlink_rental_order(self):
        rental_order_1 = self._create_rental_order(
            self.partnerA.id, self.date_0101, self.date_0110
        )
        self.assertEqual(rental_order_1.is_rental_order, True)
        rental_order_1.action_confirm()
        self.assertEqual(rental_order_1.delivery_count, 2)
        self.assertEqual(len(rental_order_1.order_line), 1)
        line = rental_order_1.order_line[0]
        rental_1 = self.env["sale.rental"].search(
            [
                ("start_order_line_id", "=", line.id),
                ("state", "!=", "cancel"),
                ("out_move_id.state", "!=", "cancel"),
                ("in_move_id.state", "!=", "cancel"),
            ]
        )
        self.assertEqual(len(rental_1), 1)
        rental_order_1.with_context(disable_cancel_warning=True).action_cancel()
        rental_order_1.unlink()
        rental_1_after = self.env["sale.rental"].search(
            [
                ("start_order_line_id", "=", line.id),
                ("state", "!=", "cancel"),
                ("out_move_id.state", "!=", "cancel"),
                ("in_move_id.state", "!=", "cancel"),
            ]
        )
        self.assertEqual(len(rental_1_after), 0)

    def test_02_normal_line_creates_no_rental(self):
        order_form = Form(self.SaleOrderObj.with_user(self.salesman))
        order_form.type_id = self.rental_sale_type
        order_form.partner_id = self.partnerA
        with order_form.order_line.new() as line:
            line.product_id = self.service_rental
            line.start_date = self.date_0101
            line.end_date = self.date_0110
            self.assertEqual(line.rental_type, "new_rental")
            line.order_type = "normal"
            self.assertFalse(line.rental)
            self.assertFalse(line.rental_type)
        order = order_form.save()
        order.action_confirm()
        self.assertFalse(
            self.env["sale.rental"].search(
                [("start_order_line_id", "in", order.order_line.ids)]
            )
        )
