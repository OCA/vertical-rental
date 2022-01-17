# Part of rental-vertical See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta

from odoo.addons.rental_base.tests.stock_common import RentalStockCommon
from odoo import fields, exceptions


class TestRentalPricelist(RentalStockCommon):
    def setUp(self):
        super().setUp()

        # Product Created A, B, C
        ProductObj = self.env["product.product"]
        self.productA = ProductObj.create(
            {
                "name": "Product A",
                "type": "product",
                "rental": True,
                "rental_of_month": True,
                "rental_of_day": True,
                "rental_of_hour": True,
                "rental_price_month": 1000,
                "rental_price_day": 100,
                "rental_price_hour": 10,
            }
        )
        self.productB = ProductObj.create(
            {
                "name": "Product B",
                "type": "product",
                "rental": True,
            }
        )
        self.productC = ProductObj.create(
            {
                "name": "Product C",
                "type": "product",
                "rental": True,
            }
        )
        self.productD = ProductObj.create(
            {
                "name": "Product D",
                "type": "product",
                "rental": True,
            }
        )
        self.today = fields.Date.from_string(fields.Date.today())
        self.tomorrow = self.today + relativedelta(days=1)
        self.date_28_day_later = self.today + relativedelta(days=28)
        self.date_63_day_later = self.today + relativedelta(days=63)
        self.date_one_month_later = self.today + relativedelta(months=1)
        self.date_two_month_later = self.today + relativedelta(months=2)
        self.date_three_month_later = self.today + relativedelta(months=3)
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
                    "pricelist_id": self.env.ref("product.list0").id,
                }
            )
        )

    def _run_sol_onchange_display_product_id(self, line):
        line.onchange_display_product_id()  # product_id, rental changed
        line.product_id_change()
        line.onchange_rental()  # product_id changed again
        line.product_id_change()  # product_uom changed
        line.product_uom_change()
        line.rental_product_id_change()  # set start end date manually

    def _run_sol_onchange_date(self, line, start_date=False, end_date=False):
        if start_date:
            line.start_date = start_date
        if end_date:
            line.end_date = end_date
        line.onchange_start_end_date()  # number_of_time_unit changed
        line.rental_qty_number_of_days_change()  # product_uom_qty changed
        line.product_uom_change()

    def _run_sol_onchange_product_uom(self, line, product_uom):
        line.product_uom = product_uom
        line.product_uom_change()
        line.product_id_change()
        line.onchange_start_end_date()
        line.rental_qty_number_of_days_change()
        line.product_uom_change()

    def _run_sol_onchange_can_sell_rental(self, line, can_sell_rental):
        line.can_sell_rental = can_sell_rental
        line.onchange_can_sell_rental()
        line.onchange_rental()
        line.product_id_change()
        line.product_uom_change()

    def _run_sol_onchange_rental(self, line, rental):
        line.rental = rental
        line.onchange_rental()
        line.onchange_can_sell_rental()
        line.rental_product_id_change()
        line.product_id_change()
        line.product_uom_change()

    def test_00_auto_create_service_product(self):
        """
        check functions that create the rental service automatically.
        services of productA was created by using function create()
        services of productB will be created by using function write()
        """
        self.productB.write(
            {
                "rental_of_month": True,
                "rental_of_day": True,
                "rental_of_hour": True,
                "rental_price_month": 2000,
                "rental_price_day": 200,
                "rental_price_hour": 20,
            }
        )
        # check service products of product A
        check_hour = check_day = check_month = False
        self.assertEqual(len(self.productA.rental_service_ids), 3)
        for p in self.productA.rental_service_ids:
            if p.uom_id == self.uom_month:
                self.assertEqual(p.lst_price, 1000)
                check_month = True
            if p.uom_id == self.uom_day:
                self.assertEqual(p.lst_price, 100)
                check_day = True
            if p.uom_id == self.uom_hour:
                self.assertEqual(p.lst_price, 10)
                check_hour = True

        # check service products of product B
        check_hour = check_day = check_month = False
        self.assertEqual(len(self.productB.rental_service_ids), 3)
        for p in self.productB.rental_service_ids:
            if p.uom_id == self.uom_month:
                self.assertEqual(p.lst_price, 2000)
                check_month = True
            if p.uom_id == self.uom_day:
                self.assertEqual(p.lst_price, 200)
                check_day = True
            if p.uom_id == self.uom_hour:
                self.assertEqual(p.lst_price, 20)
                check_hour = True

    def test_01_rental_onchange_productA(self):
        """
        check onchange functions by setting of display_product_id
        check onchange functions by changing of product_uom
        """
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
                    "end_date": self.date_three_month_later,
                }
            )
        )
        line.onchange_display_product_id()
        res = line.product_id_change()
        # check uom domain
        check_uom_domain = False
        if "domain" in res and "product_uom" in res["domain"]:
            self.assertEqual(len(res["domain"]["product_uom"][0][2]), 3)
            check_uom_domain = True
        self.assertTrue(check_uom_domain)
        line.onchange_rental()
        line.product_uom_change()
        line.rental_product_id_change()
        self._run_sol_onchange_date(line)
        # self._print_sol(line)
        self.assertEqual(line.rental, True)
        self.assertEqual(line.rental_type, "new_rental")
        self.assertEqual(line.can_sell_rental, False)
        self.assertEqual(line.product_id, self.productA.product_rental_day_id)
        self.assertEqual(line.display_product_id, self.productA)
        self.assertEqual(line.product_uom, self.uom_day)
        self.assertEqual(line.product_uom_qty > 80, True)
        self.assertEqual(line.rental_qty, 1)
        self.assertEqual(line.number_of_time_unit > 80, True)

        # Change product_uom manually
        self._run_sol_onchange_product_uom(line, self.uom_month)
        # self._print_sol(line)
        self.assertEqual(line.product_id, self.productA.product_rental_month_id)
        self.assertEqual(line.display_product_id, self.productA)
        self.assertEqual(line.product_uom, self.uom_month)
        self.assertEqual(line.product_uom_qty, 3)
        self.assertEqual(line.rental_qty, 1)
        self.assertEqual(line.number_of_time_unit, 3)

    def test_02_rental_onchange_productC(self):
        """
        check auto detect time_uom "Month"
        check onchange functions by changing of can_sell_rental
        check onchange functions by changing of rental
        """
        self.productC.write(
            {
                "rental_of_month": True,
            }
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
                    "order_id": self.rental_order.id,
                    "display_product_id": self.productC.id,
                    "start_date": self.today,
                    "end_date": self.date_three_month_later,
                }
            )
        )
        line.onchange_display_product_id()
        res = line.product_id_change()
        # check uom domain
        check_uom_domain = False
        if "domain" in res and "product_uom" in res["domain"]:
            self.assertEqual(res["domain"]["product_uom"][0][2][0], self.uom_month.id)
            check_uom_domain = True
        self.assertTrue(check_uom_domain)
        line.onchange_rental()
        line.product_uom_change()
        line.rental_product_id_change()
        self._run_sol_onchange_date(line)
        # self._print_sol(line)
        self.assertEqual(line.rental, True)
        self.assertEqual(line.rental_type, "new_rental")
        self.assertEqual(line.can_sell_rental, False)
        self.assertEqual(line.product_id, self.productC.product_rental_month_id)
        self.assertEqual(line.display_product_id, self.productC)
        self.assertEqual(line.product_uom, self.uom_month)
        self.assertEqual(line.product_uom_qty, 3)
        self.assertEqual(line.rental_qty, 1)
        self.assertEqual(line.number_of_time_unit, 3)

        # Change can_sell_rental -> True manually
        self._run_sol_onchange_can_sell_rental(line, True)
        # self._print_sol(line)
        self.assertEqual(line.rental, False)
        self.assertEqual(line.rental_type, False)
        self.assertEqual(line.can_sell_rental, True)
        self.assertEqual(line.product_id, self.productC)
        self.assertEqual(line.display_product_id, self.productC)
        self.assertEqual(line.product_uom, self.uom_unit)
        self.assertEqual(line.rental_qty, 0)

        # Change rental -> True manually
        self._run_sol_onchange_rental(line, True)
        # self._print_sol(line)
        self.assertEqual(line.rental, True)
        self.assertEqual(line.rental_type, "new_rental")
        self.assertEqual(line.can_sell_rental, False)
        self.assertEqual(line.product_id, self.productC.product_rental_month_id)
        self.assertEqual(line.display_product_id, self.productC)
        self.assertEqual(line.product_uom, self.uom_month)
        self.assertEqual(line.rental_qty, 1)

    def test_03_rental_pricelist_items(self):
        # add scale price of product A
        #    Day     Price
        #      1     100
        #     20      90
        #     45      80
        #     80      70
        #
        #    Month   Price
        #      1     1000
        #      2      900
        #      3      800
        #
        # add item from product form view
        self.productA.write(
            {
                "day_scale_pricelist_item_ids": [
                    (
                        0,
                        0,
                        {
                            "min_quantity": 20,
                            "fixed_price": 90,
                            "applied_on": "0_product_variant",
                            "compute_price": "fixed",
                            "product_id": self.productA.product_rental_day_id.id,
                            "pricelist_id": self.productA.def_pricelist_id.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "min_quantity": 45,
                            "fixed_price": 80,
                            "applied_on": "0_product_variant",
                            "compute_price": "fixed",
                            "product_id": self.productA.product_rental_day_id.id,
                            "pricelist_id": self.productA.def_pricelist_id.id,
                        },
                    ),
                ],
            }
        )
        self.productA.write(
            {
                "month_scale_pricelist_item_ids": [
                    (
                        0,
                        0,
                        {
                            "min_quantity": 2,
                            "fixed_price": 900,
                            "applied_on": "0_product_variant",
                            "compute_price": "fixed",
                            "product_id": self.productA.product_rental_month_id.id,
                            "pricelist_id": self.productA.def_pricelist_id.id,
                        },
                    ),
                ],
            }
        )

        # add item from pricelist
        item1 = self.env["product.pricelist.item"].create(
            {
                "applied_on": "0_product_variant",
                "compute_price": "fixed",
                "product_id": self.productA.product_rental_day_id.id,
                "pricelist_id": self.productA.def_pricelist_id.id,
                "min_quantity": 80,
                "fixed_price": 70,
            }
        )
        item1._onchange_product_id()
        self.assertEqual(item1.day_item_id, self.productA)
        item2 = self.env["product.pricelist.item"].create(
            {
                "applied_on": "0_product_variant",
                "compute_price": "fixed",
                "product_id": self.productA.product_rental_month_id.id,
                "pricelist_id": self.productA.def_pricelist_id.id,
                "min_quantity": 3,
                "fixed_price": 800,
            }
        )
        item2._onchange_product_id()
        self.assertEqual(item2.month_item_id, self.productA)

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
                    "end_date": self.date_three_month_later,
                }
            )
        )
        self._run_sol_onchange_display_product_id(line)
        # check price of days
        self._run_sol_onchange_date(line)
        self.assertEqual(line.product_uom_qty > 80, True)
        self.assertEqual(line.price_unit, 70)
        self._run_sol_onchange_date(line, end_date=self.date_two_month_later)
        self.assertEqual(line.product_uom_qty > 45, True)
        self.assertEqual(line.price_unit, 80)
        self._run_sol_onchange_date(line, end_date=self.date_one_month_later)
        self.assertEqual(line.product_uom_qty > 20, True)
        self.assertEqual(line.price_unit, 90)
        self._run_sol_onchange_date(line, end_date=self.tomorrow)
        self.assertEqual(line.product_uom_qty, 2)
        self.assertEqual(line.price_unit, 100)

        # check price of months
        self._run_sol_onchange_product_uom(line, self.uom_month)
        self._run_sol_onchange_date(
            line, end_date=self.date_28_day_later
        )  # check round
        self.assertEqual(line.product_uom_qty, 1)
        self.assertEqual(line.price_unit, 1000)
        self._run_sol_onchange_date(
            line, end_date=self.date_63_day_later
        )  # check round
        self.assertEqual(line.product_uom_qty, 2)
        self.assertEqual(line.price_unit, 900)
        self._run_sol_onchange_date(line, end_date=self.date_three_month_later)
        self.assertEqual(line.product_uom_qty, 3)
        self.assertEqual(line.price_unit, 800)

    def test_04_check_rental_order_line_productD(self):
        """
        check function check_rental_order_line()
        """
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
                    "display_product_id": self.productD.id,
                }
            )
        )
        line.onchange_display_product_id()
        line.product_id_change()
        line.rental = True
        vals = line._convert_to_write(line._cache)
        self.env["sale.order.line"].create(vals)
        with self.assertRaises(exceptions.UserError) as e:
            self.rental_order.action_confirm()
        self.assertEqual("Product D is not correctly configured.", e.exception.name)
