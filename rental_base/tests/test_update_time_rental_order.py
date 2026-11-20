# Part of rental-vertical See LICENSE file for full copyright and licensing details.

from odoo import fields
from odoo.tests import tagged

from odoo.addons.rental_base.tests.stock_common import RentalStockCommon


# The confirm-time push machinery lives in rental_routing, which is not in
# the dependency tree of rental_base. Run after the full registry is loaded.
@tagged("post_install", "-at_install", "standard")
class TestUpdateTimeRentalOrder(RentalStockCommon):
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
        cls.date_0102 = fields.Date.to_date("2021-01-02")
        cls.date_0111 = fields.Date.to_date("2021-01-11")
        cls.date_0103 = fields.Date.to_date("2021-01-03")
        cls.date_0112 = fields.Date.to_date("2021-01-12")

    def _rental_confirm_push_active(self):
        """True if rental_routing's confirm-time push is loaded.

        The return picking at SO-confirm is created by machinery in
        rental_routing (post-#458). In per-repo test DBs without
        rental_routing the push does not exist and only one picking is
        created at confirm; skip rather than fail in that environment.
        """
        modules = self.env["ir.module.module"].search_count(
            [("name", "=", "rental_routing"), ("state", "=", "installed")]
        )
        return bool(modules) and bool(
            self.env["ir.model.fields"]
            .sudo()
            .search_count(
                [("model", "=", "stock.move"), ("name", "=", "rental_out_id")]
            )
        )

    def test_00_update_time_rental_order(self):
        if not self._rental_confirm_push_active():
            self.skipTest("rental_routing confirm-push machinery not loaded")
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
                active_model="sale.order",
                active_ids=rental_order_1.ids,
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
        self.assertEqual(
            rental_1.out_picking_id.scheduled_date,
            fields.Datetime.to_datetime(self.date_0102),
        )
        self.assertEqual(
            rental_1.in_picking_id.scheduled_date,
            fields.Datetime.to_datetime(self.date_0111),
        )
        self.assertEqual(
            rental_1.out_move_id.date, fields.Datetime.to_datetime(self.date_0102)
        )
        self.assertEqual(
            rental_1.in_move_id.date, fields.Datetime.to_datetime(self.date_0111)
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
                active_model="sale.order",
                active_ids=rental_order_1.ids,
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
        self.assertEqual(
            rental_2.out_picking_id.scheduled_date,
            fields.Datetime.to_datetime(self.date_0103),
        )
        self.assertEqual(
            rental_2.in_picking_id.scheduled_date,
            fields.Datetime.to_datetime(self.date_0112),
        )
        self.assertEqual(
            rental_2.out_move_id.date, fields.Datetime.to_datetime(self.date_0103)
        )
        self.assertEqual(
            rental_2.in_move_id.date, fields.Datetime.to_datetime(self.date_0112)
        )

    def test_10_update_sale_line_date_line_model_direct(self):
        """Directly test the update.sale.line.date.line TransientModel."""
        rental_order = self._create_rental_order(
            self.partnerA.id, self.date_0101, self.date_0110
        )
        rental_order.action_confirm()
        line = rental_order.order_line[0]
        # create parent wizard first (required M2one on line)
        wizard = self.env["update.sale.line.date"].create(
            {
                "date_start": self.date_0102,
                "date_end": self.date_0111,
            }
        )
        Line = self.env["update.sale.line.date.line"]
        date_line = Line.create(
            {
                "wizard_id": wizard.id,
                "sequence": 1,
                "order_line_id": line.id,
                "date_start": self.date_0102,
                "date_end": self.date_0111,
                "product_id": line.product_id.id,
                "change": False,
            }
        )
        self.assertEqual(date_line.wizard_id, wizard)
        self.assertEqual(date_line.sequence, 1)
        self.assertEqual(date_line.order_line_id, line)
        self.assertEqual(date_line.date_start, self.date_0102)
        self.assertEqual(date_line.date_end, self.date_0111)
        self.assertFalse(date_line.change)
        self.assertEqual(wizard.line_ids, date_line)

    def test_11_update_sale_line_date_default_get_lines(self):
        """Test that default_get creates line_ids for order lines."""
        rental_order = self._create_rental_order(
            self.partnerA.id, self.date_0101, self.date_0110
        )
        rental_order.action_confirm()
        Wizard = self.env["update.sale.line.date"].with_context(
            active_model="sale.order",
            active_ids=rental_order.ids,
            active_id=rental_order.id,
        )
        defaults = Wizard.default_get(
            [
                "order_id",
                "date_start",
                "date_end",
                "date_in_line",
                "all_line",
                "from_line",
                "to_line",
                "line_ids",
            ]
        )
        self.assertIn("line_ids", defaults)
        self.assertEqual(len(defaults["line_ids"]), 1)
        self.assertEqual(defaults["order_id"], rental_order.id)
        self.assertTrue(defaults["all_line"])
        self.assertEqual(defaults["from_line"], 1)
        wizard = Wizard.create(defaults)
        date_line = wizard.line_ids[0]
        self.assertEqual(date_line.order_line_id, rental_order.order_line[0])
        self.assertEqual(date_line.sequence, 1)
        self.assertTrue(date_line.product_id)
        # onchange_line with all_line=True sets change=True on all lines
        wizard.all_line = True
        wizard.onchange_line()
        self.assertTrue(date_line.change)
        # set all_line=False and use from_line/to_line
        wizard.all_line = False
        wizard.from_line = 1
        wizard.to_line = 1
        wizard.onchange_line()
        self.assertTrue(date_line.change)
        # line with sequence=1 is outside [2, 2] -> change=False
        wizard.from_line = 2
        wizard.to_line = 2
        wizard.onchange_line()
        self.assertFalse(date_line.change)

    def test_12_update_sale_line_date_onchange_date_in_line(self):
        """Test onchange_date_in_line sets all_line=True."""
        rental_order = self._create_rental_order(
            self.partnerA.id, self.date_0101, self.date_0110
        )
        rental_order.action_confirm()
        Wizard = self.env["update.sale.line.date"].with_context(
            active_model="sale.order",
            active_ids=rental_order.ids,
            active_id=rental_order.id,
        )
        defaults = Wizard.default_get(
            [
                "order_id",
                "date_start",
                "date_end",
                "date_in_line",
                "all_line",
                "from_line",
                "to_line",
                "line_ids",
            ]
        )
        wizard = Wizard.create(defaults)
        self.assertFalse(wizard.date_in_line)
        wizard.date_in_line = True
        wizard.onchange_date_in_line()
        self.assertTrue(wizard.all_line)
