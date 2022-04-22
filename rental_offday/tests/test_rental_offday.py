import logging
from datetime import date, timedelta

from odoo import fields
from odoo.exceptions import UserError
from odoo.tests.common import TransactionCase
from odoo.tools.translate import _

_logger = logging.getLogger(__name__)


class TestRentalOffDay(TransactionCase):
    def setUp(self):
        super(TestRentalOffDay, self).setUp()

        product = self.env["product.product"].create(
            {
                "name": "Beamer",
                "default_code": "00123",
                "type": "product",
                "sale_ok": True,
                "rental": True,
                "rental_of_day": True,
                "rental_price_day": 200.00,
            }
        )

        rental_service_day = self.env["product.product"].search(
            [("rented_product_id", "=", product.id)]
        )

        self.date_start = date.today()
        self.date_end = self.date_start + timedelta(days=28)

        self.sale_order = self.env["sale.order"].create(
            {
                "partner_id": self.env.ref("base.res_partner_1").id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": rental_service_day.id,
                            "name": rental_service_day.name,
                            "rental": True,
                            "rental_type": "new_rental",
                            "rental_qty": 1.0,
                            "product_uom": rental_service_day.uom_id.id,
                            "start_date": self.date_start,
                            "end_date": self.date_end,
                        },
                    )
                ],
            }
        )

        self.sale_order_line = self.sale_order.order_line[0]
        self.sale_order_line.onchange_start_end_date()
        self.sale_order_line.rental_qty_number_of_days_change()

    def test_01_daily_rental_no_offdays(self):
        self.assertEqual(self.sale_order_line.number_of_time_unit, 29.0)
        self.assertEqual(self.sale_order_line.product_uom_qty, 29.0)
        self.assertEqual(len(self.sale_order_line.fixed_offday_ids), 0.0)
        self.assertEqual(len(self.sale_order_line.add_offday_ids), 0.0)

    def test_02_daily_rental_offdays(self):
        # Fixed Off-Days
        self.sale_order_line.write(
            {
                "fixed_offday_type": "weekend",
            }
        )
        self.sale_order_line.onchange_fixed_offday_type()
        self.sale_order_line.rental_qty_number_of_days_change()

        if self.date_start.isoweekday() in range(1, 6):
            self.assertEqual(self.sale_order_line.offday_number, 8.0)
            self.assertEqual(self.sale_order_line.product_uom_qty, 21.0)
            self.assertEqual(len(self.sale_order_line.fixed_offday_ids), 8.0)
        else:
            self.assertEqual(self.sale_order_line.offday_number, 9.0)
            self.assertEqual(self.sale_order_line.product_uom_qty, 20.0)
            self.assertEqual(len(self.sale_order_line.fixed_offday_ids), 9.0)

        self.assertEqual(self.sale_order_line.number_of_time_unit, 29.0)
        self.assertEqual(len(self.sale_order_line.add_offday_ids), 0.0)

        # Additional Off-Days
        # Add fixed off-day also as additional off-day
        date_fixed_offday = self.sale_order_line.fixed_offday_ids[0].date

        with self.assertRaises(UserError) as e:
            self.sale_order_line.write(
                {
                    "add_offday_ids": [
                        (
                            0,
                            0,
                            {
                                "date": date_fixed_offday,
                                "name": "Fixed off-day as additional off-day.",
                            },
                        )
                    ],
                }
            )
            self.sale_order_line.onchange_add_offday_ids()
        self.assertEqual(
            str(e.exception),
            _('The off-day "%s" was already created as fixed off-day.')
            % date_fixed_offday,
        )

        # Add additional off-day not in rental period
        date_before_start = self.date_start - timedelta(days=1)

        with self.assertRaises(UserError) as e:
            self.sale_order_line.write(
                {
                    "add_offday_ids": [
                        (
                            1,
                            self.sale_order_line.add_offday_ids[0].id,
                            {
                                "date": date_before_start,
                                "name": "Additional off-day before rental period.",
                            },
                        )
                    ],
                }
            )
            self.sale_order_line.onchange_add_offday_ids()
        self.assertEqual(
            str(e.exception),
            _('The off-day "%s" is not between %s and %s.')
            % (date_before_start, self.date_start, self.date_end),
        )

        # Add 'good' additional off-day
        date_additional_offday = date_fixed_offday + timedelta(days=2)
        self.sale_order_line.write(
            {
                "add_offday_ids": [
                    (
                        1,
                        self.sale_order_line.add_offday_ids[0].id,
                        {
                            "date": date_additional_offday,
                            "name": "Additional off-day.",
                        },
                    )
                ],
            }
        )

        self.sale_order_line.onchange_add_offday_ids()
        self.sale_order_line.rental_qty_number_of_days_change()

        if self.date_start.isoweekday() in range(1, 6):
            self.assertEqual(self.sale_order_line.offday_number, 9.0)
            self.assertEqual(self.sale_order_line.product_uom_qty, 20.0)
            self.assertEqual(len(self.sale_order_line.fixed_offday_ids), 8.0)
        else:
            self.assertEqual(self.sale_order_line.offday_number, 10.0)
            self.assertEqual(self.sale_order_line.product_uom_qty, 19.0)
            self.assertEqual(len(self.sale_order_line.fixed_offday_ids), 9.0)

        self.assertEqual(self.sale_order_line.number_of_time_unit, 29.0)
        self.assertEqual(len(self.sale_order_line.add_offday_ids), 1.0)

    def test_03_add_several_additional_offdays(self):
        date_start = fields.Date.from_string("2020-12-01")
        date_end = fields.Date.from_string("2020-12-31")
        self.sale_order_line.write(
            {
                "start_date": date_start,
                "end_date": date_end,
            }
        )
        self.sale_order_line.onchange_start_end_date()
        self.sale_order_line.write(
            {
                "fixed_offday_type": "weekend",
            }
        )
        self.sale_order_line.onchange_fixed_offday_type()
        self.sale_order_line.rental_qty_number_of_days_change()
        # Add additional off days
        self.sale_order_line.offday_date_start = fields.Date.from_string("2020-12-18")
        self.sale_order_line.offday_date_end = fields.Date.from_string("2020-12-28")
        self.sale_order_line.add_additional_offdays = True
        self.sale_order_line.onchange_add_additional_offdays()
        self.sale_order_line.rental_qty_number_of_days_change()
        # 31 - 8 - 7 = 16
        self.assertEqual(len(self.sale_order_line.fixed_offday_ids), 8)
        self.assertEqual(len(self.sale_order_line.add_offday_ids), 7)
        self.assertEqual(self.sale_order_line.product_uom_qty, 16)
