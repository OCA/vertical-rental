# Part of rental-vertical See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta

from odoo import exceptions, fields

from odoo.addons.rental_base.tests.stock_common import RentalStockCommon
from odoo.addons.rental_pricelist.tests.test_rental_pricelist import (
    _run_sol_onchange_date,
    _run_sol_onchange_display_product_id,
)


class TestRentalPricelist(RentalStockCommon):
    def setUp(self):
        super().setUp()

        self.uom_interval = self.env.ref(
            "rental_pricelist_interval.product_uom_interval"
        )
        self.pricelist0 = self.env.ref("product.list0")
        self.pricelist_interval = self.env.ref(
            "rental_pricelist_interval.pricelist_interval"
        )
        # Product Created A and B
        ProductObj = self.env["product.product"]
        self.productA = ProductObj.create(
            {
                "name": "Product A",
                "type": "product",
                "rental": True,
                "rental_of_day": True,
                "rental_price_day": 200,
                "rental_of_interval": True,
                "rental_price_interval": 1000,
                "rental_interval_max": 21,
            }
        )
        self.productB = ProductObj.create(
            {
                "name": "Product B",
                "type": "product",
                "rental": True,
                "rental_of_day": True,
                "rental_price_day": 200,
            }
        )
        self.today = fields.Date.from_string(fields.Date.today())
        self.date_4_day_later = self.today + relativedelta(days=4)
        self.date_12_day_later = self.today + relativedelta(days=12)
        self.date_17_day_later = self.today + relativedelta(days=17)
        self.date_24_day_later = self.today + relativedelta(days=24)
        self.rental_order = (
            self.env["sale.order"]
            .with_context(
                {
                    "default_type_id": self.rental_sale_type.id,
                }
            )
            .create(
                {
                    "partner_id": self.partnerA.id,
                    "pricelist_id": self.pricelist_interval.id,
                }
            )
        )

    def test_00_interval_price(self):
        """
        Create Interval Prices for productA
        Activate interval price in sale order line
        Change End Date and rental_qty
        Reset field rental_interval_price
        """
        self.assertEqual(self.productA.rental_price_interval, 1000)
        # Create Interval Prices for productA
        self.env.user.company_id.write(
            {
                "rental_price_interval_rule_ids": [
                    (0, 0, {"name": "0-7 interval", "factor": 1, "min_quantity": 0}),
                    (
                        0,
                        0,
                        {"name": "8-14 interval", "factor": 1.75, "min_quantity": 8},
                    ),
                    (
                        0,
                        0,
                        {"name": "15-21 interval", "factor": 2.25, "min_quantity": 15},
                    ),
                ]
            }
        )
        self.productA.action_reset_rental_price_interval_items()
        check_p1 = check_p2 = check_p3 = False
        for price in self.productA.interval_scale_pricelist_item_ids:
            # 0-7 interval
            if price.min_quantity == 0:
                self.assertEqual(price.fixed_price, 1000)
                check_p1 = True
            # 8-14 interval
            elif price.min_quantity == 8:
                self.assertEqual(price.fixed_price, 1750)
                check_p2 = True
            # 15-21 interval
            elif price.min_quantity == 15:
                self.assertEqual(price.fixed_price, 2250)
                check_p3 = True
        self.assertTrue(check_p1)
        self.assertTrue(check_p2)
        self.assertTrue(check_p3)
        # Activate interval price in sale order line
        line = (
            self.env["sale.order.line"]
            .with_context(
                {
                    "type_id": self.rental_sale_type.id,
                }
            )
            .new(
                {
                    "order_id": self.rental_order.id,
                    "display_product_id": self.productA.id,
                    "start_date": self.today,
                    "end_date": self.date_17_day_later,
                }
            )
        )
        _run_sol_onchange_display_product_id(line)
        _run_sol_onchange_date(line)
        self.assertEqual(line.rental, True)
        self.assertEqual(line.rental_type, "new_rental")
        self.assertEqual(line.can_sell_rental, False)
        self.assertEqual(line.product_id, self.productA.product_rental_interval_id)
        self.assertEqual(line.display_product_id, self.productA)
        self.assertEqual(line.product_uom, self.uom_interval)
        self.assertEqual(line.product_uom_qty, 1)
        self.assertEqual(line.rental_qty, 1)
        self.assertEqual(line.number_of_time_unit, 18)
        self.assertEqual(line.price_unit, 2250)
        self.assertEqual(line.price_subtotal, 2250)
        # Change End Date and rental_qty
        line.rental_qty = 2
        _run_sol_onchange_date(line, end_date=self.date_12_day_later)
        self.assertEqual(line.rental_qty, 2)
        self.assertEqual(line.product_uom_qty, 2)
        self.assertEqual(line.price_unit, 1750)
        self.assertEqual(line.price_subtotal, 3500)  # 2 * 1750
        # Change End Date again
        _run_sol_onchange_date(line, end_date=self.date_4_day_later)
        self.assertEqual(line.price_unit, 1000)
        self.assertEqual(line.price_subtotal, 2000)  # 2 * 1000
        # Change Pricelist
        self.rental_order.pricelist_id = self.pricelist0
        _run_sol_onchange_display_product_id(line)
        _run_sol_onchange_date(line, end_date=self.date_12_day_later)
        self.assertEqual(line.price_unit, 200)
        self.rental_order.pricelist_id = self.pricelist_interval
        _run_sol_onchange_display_product_id(line)
        _run_sol_onchange_date(line, end_date=self.date_12_day_later)
        self.assertEqual(line.price_unit, 1750)
        with self.assertRaises(exceptions.UserError) as e:
            _run_sol_onchange_date(line, end_date=self.date_24_day_later)
        self.assertEqual("Max rental interval (21 days) is exceeded.", str(e.exception))
