# Part of rental-vertical See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta

from odoo import fields

from odoo.addons.rental_base.tests.stock_common import RentalStockCommon
from odoo.addons.rental_pricelist.tests.test_rental_pricelist import (
    _run_sol_onchange_date,
    _run_sol_onchange_display_product_id,
)


class TestRentalCheckAvailability(RentalStockCommon):
    def setUp(self):
        super().setUp()

        # Product Created A
        ProductObj = self.env["product.product"]
        self.productA = ProductObj.create(
            {
                "name": "Product A",
                "type": "product",
                "rental": True,
                "rental_of_day": True,
                "rental_price_day": 100,
            }
        )
        self.today = fields.Date.from_string(fields.Date.today())
        self.date_2_day_later = self.today + relativedelta(days=2)
        self.date_5_day_later = self.today + relativedelta(days=5)
        self.date_10_day_later = self.today + relativedelta(days=10)
        self.date_15_day_later = self.today + relativedelta(days=15)
        self.date_20_day_later = self.today + relativedelta(days=20)
        self.date_25_day_later = self.today + relativedelta(days=25)
        self.date_27_day_later = self.today + relativedelta(days=27)
        self.date_30_day_later = self.today + relativedelta(days=30)

    def create_rental_order(self, start_date, end_date, qty):
        rental_order = (
            self.env["sale.order"]
            .with_context(
                {
                    "default_type_id": self.rental_sale_type.id,
                }
            )
            .create(
                {
                    "warehouse_id": self.warehouse0.id,
                    "partner_id": self.partnerA.id,
                    "pricelist_id": self.env.ref("product.list0").id,
                }
            )
        )
        line = (
            self.env["sale.order.line"]
            .with_context(
                {
                    "type_id": self.rental_sale_type.id,
                }
            )
            .new(
                {
                    "order_id": rental_order.id,
                    "display_product_id": self.productA.id,
                    "start_date": start_date,
                    "end_date": end_date,
                }
            )
        )
        _run_sol_onchange_display_product_id(line)
        line.rental_qty = qty
        _run_sol_onchange_date(line)
        values = line._convert_to_write(line._cache)
        self.env["sale.order.line"].create(values)
        return rental_order

    def test_00_check_availability(self):
        # Rental Orders Info
        # RO 1  (qty: 2)    today -------- 10 (none)
        # RO 2  (qty: 2)                                 20 ----------- 30 (none)
        # RO 3  (qty: 3)                                           27 - 30 (quotation)
        # RO 4  (qty: 1)              5 ----------------------- 25 (none)
        # RO 5  (qty: 3)    today - 2 (order)
        # RO 6  (qty: 1)              5 --------- 15 (none)
        expected_warning = {
            "title": "Not enough stock!",
            "message": "You want to rent 3.00 Units but you only "
            "have 2.00 Units available in the selected period.",
        }
        # create some quantity of productA (qty: 4)
        self.env["stock.quant"]._update_available_quantity(
            self.productA, self.warehouse0.rental_in_location_id, 4
        )
        # RO 1
        rental_order_1 = self.create_rental_order(self.today, self.date_10_day_later, 2)
        rental_order_1.action_confirm()
        self.assertEqual(rental_order_1.order_line.concurrent_orders, "none")

        # RO 2
        rental_order_2 = self.create_rental_order(
            self.date_20_day_later, self.date_30_day_later, 2
        )
        self.assertEqual(rental_order_2.order_line.concurrent_orders, "none")

        # RO 3
        rental_order_3 = self.create_rental_order(
            self.date_27_day_later, self.date_30_day_later, 3
        )
        res = rental_order_3.order_line.onchange_start_end_date()
        self.assertEqual(res.get("warning", False), expected_warning)
        self.assertEqual(rental_order_3.order_line.concurrent_orders, "quotation")
        action = rental_order_3.order_line.action_view_concurrent_orders()
        self.assertEqual(
            action.get("domain", False), [("id", "in", [rental_order_2.id])]
        )

        # RO 4
        rental_order_4 = self.create_rental_order(
            self.date_5_day_later, self.date_25_day_later, 1
        )
        self.assertEqual(rental_order_4.order_line.concurrent_orders, "none")

        # RO 5
        rental_order_5 = self.create_rental_order(self.today, self.date_2_day_later, 3)
        res = rental_order_5.order_line.onchange_start_end_date()
        self.assertEqual(res.get("warning", False), expected_warning)
        self.assertEqual(rental_order_5.order_line.concurrent_orders, "order")
        action = rental_order_5.order_line.action_view_concurrent_orders()
        self.assertEqual(
            action.get("domain", False), [("id", "in", [rental_order_1.id])]
        )

        # RO 6
        rental_order_6 = self.create_rental_order(
            self.date_5_day_later, self.date_15_day_later, 1
        )
        self.assertEqual(rental_order_6.order_line.concurrent_orders, "none")
