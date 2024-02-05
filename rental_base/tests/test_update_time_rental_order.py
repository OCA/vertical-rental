# Part of rental-vertical See LICENSE file for full copyright and licensing details.

from odoo import fields

from .stock_common import RentalStockCommon


class TestUpdateTimeRentalOrder(RentalStockCommon):
    def setUp(self):
        super().setUp()
        ProductObj = self.env["product.product"]
        self.product_rental = ProductObj.create(
            {
                "name": "Rental Product",
                "type": "product",
                "categ_id": self.category_all.id,
            }
        )
        # rental service product
        self.service_rental = self._create_rental_service_day(self.product_rental)
        # dates
        self.date_0101 = fields.Date.from_string("2021-01-01")
        self.date_0110 = fields.Date.from_string("2021-01-10")
        self.date_0102 = fields.Date.from_string("2021-01-02")
        self.date_0111 = fields.Date.from_string("2021-01-11")
        self.date_0103 = fields.Date.from_string("2021-01-03")
        self.date_0112 = fields.Date.from_string("2021-01-12")
        self.date_0131 = fields.Date.from_string("2021-01-31")

    def test_00_update_time_rental_order(self):
        # rental order
        rental_order_1 = self._create_rental_order(
            self.partnerA.id, self.date_0101, self.date_0110
        )
        rental_order_1.action_confirm()
        self.assertEqual(rental_order_1.delivery_count, 2)
        self.assertEqual(len(rental_order_1.order_line), 1)
        line = rental_order_1.order_line[0]
        # 1. change date, date_in_lines = False
        line_ids_value_1 = []
        line_ids_value_1.append(
            (
                0,
                0,
                {
                    "sequence": 1,
                    "order_line_id": line.id,
                    "change": False,
                    "date_start": line.start_date,
                    "date_end": line.end_date,
                    "product_id": line.product_id.id,
                },
            )
        )
        wizard_1 = (
            self.env["update.sale.line.date"]
            .with_context(
                {
                    "active_model": "sale.order",
                    "active_ids": rental_order_1.ids,
                }
            )
            .create(
                {
                    "order_id": rental_order_1.id,
                    "date_start": self.date_0102,
                    "date_end": self.date_0111,
                    "date_in_line": False,
                    "all_line": True,
                    "line_ids": line_ids_value_1,
                }
            )
        )
        wizard_1.action_confirm()
        self.assertEqual(line.start_date, self.date_0102)
        self.assertEqual(line.end_date, self.date_0111)
        rental_1 = self.env["sale.rental"].search(
            [
                ("start_order_line_id", "=", line.id),
                ("state", "!=", "cancel"),
                ("out_move_id.state", "!=", "cancel"),
                ("in_move_id.state", "!=", "cancel"),
            ]
        )
        self.assertEqual(len(rental_1), 1)
        # disable checks for out_picking
        # self.assertEqual(
        #     rental_1.out_picking_id.scheduled_date,
        #     fields.Datetime.to_datetime(self.date_0102),
        # )
        self.assertEqual(
            rental_1.in_picking_id.scheduled_date,
            fields.Datetime.to_datetime(self.date_0111),
        )
        # disable checks for out_move
        # self.assertEqual(
        #     rental_1.out_move_id.date_expected,
        #     fields.Datetime.to_datetime(self.date_0102),
        # )
        self.assertEqual(
            rental_1.in_move_id.date_expected,
            fields.Datetime.to_datetime(self.date_0111),
        )
        # 2. change date, date_in_lines = True
        line_ids_value_2 = []
        line_ids_value_2.append(
            (
                0,
                0,
                {
                    "sequence": 1,
                    "order_line_id": line.id,
                    "change": False,
                    "date_start": self.date_0103,
                    "date_end": self.date_0112,
                    "product_id": line.product_id.id,
                },
            )
        )
        wizard_2 = (
            self.env["update.sale.line.date"]
            .with_context(
                {
                    "active_model": "sale.order",
                    "active_ids": rental_order_1.ids,
                }
            )
            .create(
                {
                    "order_id": rental_order_1.id,
                    "date_start": line.start_date,
                    "date_end": line.end_date,
                    "date_in_line": True,
                    "all_line": True,
                    "line_ids": line_ids_value_2,
                }
            )
        )
        self.assertEqual(len(wizard_2.line_ids), 1)
        wizard_2.action_confirm()
        self.assertEqual(line.start_date, self.date_0103)
        self.assertEqual(line.end_date, self.date_0112)
        rental_2 = self.env["sale.rental"].search(
            [
                ("start_order_line_id", "=", line.id),
                ("state", "!=", "cancel"),
                ("out_move_id.state", "!=", "cancel"),
                ("in_move_id.state", "!=", "cancel"),
            ]
        )
        self.assertEqual(len(rental_2), 1)
        # disable checks for out_picking
        # self.assertEqual(
        #     rental_2.out_picking_id.scheduled_date,
        #     fields.Datetime.to_datetime(self.date_0103),
        # )
        self.assertEqual(
            rental_2.in_picking_id.scheduled_date,
            fields.Datetime.to_datetime(self.date_0112),
        )
        # disable checks for out_move
        # self.assertEqual(
        #     rental_2.out_move_id.date_expected,
        #     fields.Datetime.to_datetime(self.date_0103),
        # )
        self.assertEqual(
            rental_2.in_move_id.date_expected,
            fields.Datetime.to_datetime(self.date_0112),
        )

    def test_00_get_time_unit(self):
        rental_order = self._create_rental_order(
            self.partnerA.id, self.date_0101, self.date_0131
        )
        days = rental_order.order_line._get_number_of_time_unit()
        rental_order.order_line.product_uom = self.uom_week
        weeks = rental_order.order_line._get_number_of_time_unit()
        rental_order.order_line.product_uom = self.uom_month
        months = rental_order.order_line._get_number_of_time_unit()
        self.assertEqual(days, 31)
        self.assertEqual(weeks, 5)
        self.assertEqual(months, 1)
