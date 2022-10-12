# Part of rental-vertical See LICENSE file for full copyright and licensing details.

from odoo import fields

from odoo.addons.rental_base.tests.stock_common import RentalStockCommon


class TestRentalTimeline(RentalStockCommon):
    def setUp(self):
        super().setUp()
        ProductObj = self.env["product.product"]
        self.partnerA = self.PartnerObj.create(
            {
                "name": "Timeline Partner A",
                "customer": True,
                "supplier": True,
                "country_id": self.env.ref("base.de").id,
            }
        )
        self.product_rental_1 = ProductObj.create(
            {
                "name": "Rental Product Timeline 1",
                "type": "product",
                "categ_id": self.category_all.id,
            }
        )
        self.product_rental_2 = ProductObj.create(
            {
                "name": "Rental Product Timeline 2",
                "type": "product",
                "categ_id": self.category_all.id,
            }
        )
        self.product_rental_3 = ProductObj.create(
            {
                "name": "Rental Product Timeline 3",
                "type": "product",
                "categ_id": self.category_all.id,
            }
        )
        # dates
        self.date_0101 = fields.Date.from_string("2022-01-01")
        self.date_0110 = fields.Date.from_string("2022-01-10")
        self.date_0102 = fields.Date.from_string("2022-01-02")
        self.date_0111 = fields.Date.from_string("2022-01-11")

    def get_related_timeline_from_rental_order(self, line):
        domain = [
            ("res_model", "=", "sale.order.line"),
            ("res_id", "in", line.ids),
        ]
        TimelineObj = self.env["product.timeline"]
        timeline = TimelineObj.search(domain)
        return timeline

    def test_00_update_partner_rental_order(self):
        # rental service product
        self.service_rental = self._create_rental_service_day(self.product_rental_1)
        # rental order
        rental_order_1 = self._create_rental_order(
            self.partnerA.id, self.date_0101, self.date_0110
        )
        rental_order_1.action_confirm()
        self.assertEqual(len(rental_order_1.order_line), 1)
        line = rental_order_1.order_line[0]
        self.assertEqual(line.product_id, self.service_rental)
        self.assertEqual(rental_order_1.partner_id.name, self.partnerA.name)
        # get related timeline object
        timeline = self.get_related_timeline_from_rental_order(line)
        self.assertEqual(len(timeline), 1)
        self.assertEqual(timeline.partner_id.name, self.partnerA.name)
        # update Partner A name
        self.partnerA.name = "Timeline Partner A Update"
        # check partner name on Rental Order and Rental Timeline
        self.assertEqual(rental_order_1.partner_id.name, self.partnerA.name)
        self.assertEqual(timeline.partner_id.name, self.partnerA.name)

    def test_01_update_start_end_date(self):
        # rental service product
        self.service_rental = self._create_rental_service_day(self.product_rental_2)
        # rental order
        rental_order_2 = self._create_rental_order(
            self.partnerA.id, self.date_0101, self.date_0110
        )
        rental_order_2.action_confirm()
        self.assertEqual(len(rental_order_2.order_line), 1)
        line = rental_order_2.order_line[0]
        # get related timeline object
        timeline = self.get_related_timeline_from_rental_order(line)
        # check start and end date before update
        self.assertEqual(timeline.date_start.date(), self.date_0101)
        self.assertEqual(timeline.date_end.date(), self.date_0110)
        # update start and end date
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
                    "active_ids": rental_order_2.ids,
                }
            )
            .create(
                {
                    "order_id": rental_order_2.id,
                    "date_start": self.date_0102,
                    "date_end": self.date_0111,
                    "date_in_line": False,
                    "all_line": True,
                    "line_ids": line_ids_value_1,
                }
            )
        )
        wizard_1.action_confirm()
        # check start and end date after update
        self.assertEqual(line.start_date, self.date_0102)
        self.assertEqual(line.end_date, self.date_0111)
        self.assertEqual(timeline.date_start.date(), self.date_0102)
        self.assertEqual(timeline.date_end.date(), self.date_0111)

    def test_02_change_state_of_rental_order(self):
        # rental service product
        self.service_rental = self._create_rental_service_day(self.product_rental_3)
        # rental order
        rental_order_3 = self._create_rental_order(
            self.partnerA.id, self.date_0101, self.date_0110
        )
        rental_order_3.action_confirm()
        self.assertEqual(len(rental_order_3.order_line), 1)
        line = rental_order_3.order_line[0]
        # get related timeline object
        timeline = self.get_related_timeline_from_rental_order(line)
        # check values
        self.assertEqual(timeline.date_start.date(), self.date_0101)
        self.assertEqual(timeline.date_end.date(), self.date_0110)
        self.assertEqual(timeline.product_id, self.product_rental_3)
        self.assertEqual(timeline.type, "rental")
        # cancel order
        rental_order_3.action_cancel()
        # get related timeline object after canceling the order
        timeline = self.get_related_timeline_from_rental_order(line)
        self.assertFalse(timeline)
        # set to draft order
        rental_order_3.action_draft()
        # get related timeline object after set to draft the order
        timeline = self.get_related_timeline_from_rental_order(line)
        self.assertTrue(timeline)
