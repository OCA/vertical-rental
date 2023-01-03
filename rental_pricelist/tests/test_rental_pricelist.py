# Part of rental-vertical See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta

from odoo import exceptions, fields
from odoo.exceptions import ValidationError

from odoo.addons.rental_base.tests.stock_common import RentalStockCommon


def _run_sol_onchange_display_product_id(line):
    line.onchange_display_product_id()  # product_id, rental changed
    line.product_id_change()
    line.onchange_rental()  # product_id changed again
    line.product_id_change()  # product_uom changed
    line.product_uom_change()
    line.rental_product_id_change()  # set start end date manually


def _run_sol_onchange_date(line, start_date=False, end_date=False):
    if start_date:
        line.start_date = start_date
    if end_date:
        line.end_date = end_date
    line.onchange_start_end_date()  # number_of_time_unit changed
    line.rental_qty_number_of_days_change()  # product_uom_qty changed
    line.product_uom_change()


def _run_sol_onchange_product_uom(line, product_uom):
    line.product_uom = product_uom
    line.product_uom_change()
    line.product_id_change()
    line.onchange_start_end_date()
    line.rental_qty_number_of_days_change()
    line.product_uom_change()


def _run_sol_onchange_can_sell_rental(line, can_sell_rental):
    line.can_sell_rental = can_sell_rental
    line.onchange_can_sell_rental()
    line.onchange_rental()
    line.product_id_change()
    line.product_uom_change()


def _run_sol_onchange_rental(line, rental):
    line.rental = rental
    line.onchange_rental()
    line.onchange_can_sell_rental()
    line.rental_product_id_change()
    line.product_id_change()
    line.product_uom_change()


class TestRentalPricelist(RentalStockCommon):
    def setUp(self):
        super().setUp()

        self.analytic_account_A = self.env["account.analytic.account"].create(
            {
                "name": "Analytic Account A",
                "code": "100001",
            }
        )
        self.analytic_account_B = self.env["account.analytic.account"].create(
            {
                "name": "Analytic Account B",
                "code": "100002",
            }
        )

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
                "income_analytic_account_id": self.analytic_account_A.id,
                "expense_analytic_account_id": self.analytic_account_A.id,
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
        self.productE = ProductObj.create(
            {
                "name": "Product E",
                "type": "product",
                "rental": True,
                "rental_of_day": True,
                "rental_price_day": 500,
                "default_code": "PRD-E123",
            }
        )
        self.productF = ProductObj.create(
            {
                "name": "Product F",
                "type": "product",
                "rental": True,
                "rental_of_hour": True,
                "rental_price_hour": 1000,
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
                "income_analytic_account_id": self.analytic_account_B.id,
                "expense_analytic_account_id": self.analytic_account_B.id,
            }
        )
        # check service products of product A
        check_hour_A = check_day_A = check_month_A = False
        check_income_aa_A = check_expense_aa_A = False
        self.assertEqual(len(self.productA.rental_service_ids), 3)
        for p in self.productA.rental_service_ids:
            if p.uom_id == self.uom_month:
                self.assertEqual(p.lst_price, 1000)
                check_month_A = True
            if p.uom_id == self.uom_day:
                self.assertEqual(p.lst_price, 100)
                check_day_A = True
            if p.uom_id == self.uom_hour:
                self.assertEqual(p.lst_price, 10)
                check_hour_A = True
            if p.income_analytic_account_id == self.productA.income_analytic_account_id:
                check_income_aa_A = True
            if (
                p.expense_analytic_account_id
                == self.productA.expense_analytic_account_id
            ):
                check_expense_aa_A = True
        self.assertTrue(check_hour_A)
        self.assertTrue(check_day_A)
        self.assertTrue(check_month_A)
        self.assertTrue(check_income_aa_A)
        self.assertTrue(check_expense_aa_A)

        # check service products of product B
        check_hour_B = check_day_B = check_month_B = False
        check_income_aa_B = check_expense_aa_B = False
        self.assertEqual(len(self.productB.rental_service_ids), 3)
        for p in self.productB.rental_service_ids:
            if p.uom_id == self.uom_month:
                self.assertEqual(p.lst_price, 2000)
                check_month_B = True
            if p.uom_id == self.uom_day:
                self.assertEqual(p.lst_price, 200)
                check_day_B = True
            if p.uom_id == self.uom_hour:
                self.assertEqual(p.lst_price, 20)
                check_hour_B = True
            if p.income_analytic_account_id == self.productB.income_analytic_account_id:
                check_income_aa_B = True
            if (
                p.expense_analytic_account_id
                == self.productB.expense_analytic_account_id
            ):
                check_expense_aa_B = True
        self.assertTrue(check_hour_B)
        self.assertTrue(check_day_B)
        self.assertTrue(check_month_B)
        self.assertTrue(check_income_aa_B)
        self.assertTrue(check_expense_aa_B)

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
        line.product_id_change()
        # check uom domain
        # check_uom_domain = False
        # if "domain" in res and "product_uom" in res["domain"]:
        #     self.assertEqual(len(res["domain"]["product_uom"][0][2]), 3)
        #     check_uom_domain = True
        # self.assertTrue(check_uom_domain)
        line.onchange_rental()
        line.product_uom_change()
        line.rental_product_id_change()
        _run_sol_onchange_date(line)
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
        _run_sol_onchange_product_uom(line, self.uom_month)
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
        line.product_id_change()
        # check uom domain
        # check_uom_domain = False
        # if "domain" in res and "product_uom" in res["domain"]:
        #     self.assertEqual(res["domain"]["product_uom"][0][2][0], self.uom_month.id)
        #     check_uom_domain = True
        # self.assertTrue(check_uom_domain)
        line.onchange_rental()
        line.product_uom_change()
        line.rental_product_id_change()
        _run_sol_onchange_date(line)
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
        _run_sol_onchange_can_sell_rental(line, True)
        # self._print_sol(line)
        self.assertEqual(line.rental, False)
        self.assertEqual(line.rental_type, False)
        self.assertEqual(line.can_sell_rental, True)
        self.assertEqual(line.product_id, self.productC)
        self.assertEqual(line.display_product_id, self.productC)
        self.assertEqual(line.product_uom, self.uom_unit)
        self.assertEqual(line.rental_qty, 0)

        # Change rental -> True manually
        _run_sol_onchange_rental(line, True)
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
        _run_sol_onchange_display_product_id(line)
        # check price of days
        _run_sol_onchange_date(line)
        self.assertEqual(line.product_uom_qty > 80, True)
        self.assertEqual(line.price_unit, 70)
        _run_sol_onchange_date(line, end_date=self.date_two_month_later)
        self.assertEqual(line.product_uom_qty > 45, True)
        self.assertEqual(line.price_unit, 80)
        _run_sol_onchange_date(line, end_date=self.date_one_month_later)
        self.assertEqual(line.product_uom_qty > 20, True)
        self.assertEqual(line.price_unit, 90)
        _run_sol_onchange_date(line, end_date=self.tomorrow)
        self.assertEqual(line.product_uom_qty, 2)
        self.assertEqual(line.price_unit, 100)

        # check price of months
        _run_sol_onchange_product_uom(line, self.uom_month)
        _run_sol_onchange_date(line, end_date=self.date_28_day_later)  # check round
        self.assertEqual(line.product_uom_qty, 1)
        self.assertEqual(line.price_unit, 1000)
        _run_sol_onchange_date(line, end_date=self.date_63_day_later)  # check round
        self.assertEqual(line.product_uom_qty, 2)
        self.assertEqual(line.price_unit, 900)
        _run_sol_onchange_date(line, end_date=self.date_three_month_later)
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
        self.assertEqual(
            "The product Product D is not correctly configured.", str(e.exception)
        )

    def test_05_check_rental_productE(self):
        self.assertEqual(len(self.productE.rental_service_ids), 1)
        rental_serviceE = self.productE.rental_service_ids[0]
        # check type and must_have_dates of product
        self.assertEqual(rental_serviceE.type, "service")
        self.assertEqual(rental_serviceE.must_have_dates, True)
        with self.assertRaises(ValidationError) as e:
            rental_serviceE.type = "consu"
        self.assertEqual(
            "The rental product 'Rental of Product E (Day(s))' must be of type 'Service'.",
            str(e.exception),
        )
        with self.assertRaises(ValidationError) as e:
            rental_serviceE.must_have_dates = False
        self.assertEqual(
            "The rental product 'Rental of Product E (Day(s))'"
            " must have the option 'Must Have Start and End Dates' checked.",
            str(e.exception),
        )
        # check onchange method of product.pricelist.item
        self.productE.write(
            {
                "hour_scale_pricelist_item_ids": [
                    (
                        0,
                        0,
                        {
                            "min_quantity": 3,
                            "fixed_price": 600,
                            "applied_on": "0_product_variant",
                            "compute_price": "fixed",
                            "product_id": self.productE.product_rental_day_id.id,
                            "pricelist_id": self.productE.def_pricelist_id.id,
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
                "product_id": self.productE.product_rental_day_id.id,
                "pricelist_id": self.productE.def_pricelist_id.id,
                "min_quantity": 80,
                "fixed_price": 70,
            }
        )
        item1._onchange_product_id()
        self.assertEqual(item1.day_item_id, self.productE)
        # check default_code
        self.assertEqual(self.productE.default_code, "PRD-E123")
        self.assertEqual(rental_serviceE.default_code, "RENT-D-PRD-E123")
        # update and check default_code
        self.productE.default_code = "PRD-E110"
        self.assertEqual(self.productE.default_code, "PRD-E110")
        self.assertEqual(rental_serviceE.default_code, "RENT-D-PRD-E110")
        # update and check name
        self.productE.name = "Product E1"
        self.assertEqual(rental_serviceE.name, "Rental of Product E1 (Day(s))")
        # update active
        self.productE.active = False
        self.assertEqual(rental_serviceE.active, False)
        self.productE.active = True
        self.assertTrue(rental_serviceE.active)

    def test_06_check_start_end_dates_productF(self):
        rental_order = (
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
                    "display_product_id": self.productF.id,
                }
            )
        )
        line.onchange_display_product_id()
        line.product_id_change()
        line.onchange_rental()
        line.product_uom_change()
        line.rental_product_id_change()
        _run_sol_onchange_date(line)
        line.start_end_dates_product_id_change()
        # no dates avaiavlbe
        self.assertEqual(line.start_date, False)
        self.assertEqual(line.end_date, False)
        # set dates on rental order
        rental_order.update(
            {
                "default_start_date": self.today,
                "default_end_date": self.tomorrow,
            }
        )
        line.start_end_dates_product_id_change()
        self.assertEqual(line.start_date, self.today)
        self.assertEqual(line.end_date, self.tomorrow)
