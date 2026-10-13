# Part of rental-vertical See LICENSE file for full copyright and licensing details.

from odoo import fields
from odoo.exceptions import UserError
from odoo.tools import mute_logger

from odoo.addons.rental_base.tests.stock_common import RentalStockCommon


class TestRentalTimeline(RentalStockCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        ProductObj = cls.env["product.product"]
        cls.partnerA = cls.PartnerObj.create(
            {
                "name": "Timeline Partner A",
                "country_id": cls.env.ref("base.de").id,
            }
        )
        cls.product_rental_1 = ProductObj.create(
            {
                "name": "Rental Product Timeline 1",
                "type": "product",
                "categ_id": cls.category_all.id,
            }
        )
        cls.product_rental_2 = ProductObj.create(
            {
                "name": "Rental Product Timeline 2",
                "type": "product",
                "categ_id": cls.category_all.id,
            }
        )
        cls.product_rental_3 = ProductObj.create(
            {
                "name": "Rental Product Timeline 3",
                "type": "product",
                "categ_id": cls.category_all.id,
            }
        )
        # dates
        cls.date_0101 = fields.Date.from_string("2022-01-01")
        cls.date_0110 = fields.Date.from_string("2022-01-10")
        cls.date_0102 = fields.Date.from_string("2022-01-02")
        cls.date_0111 = fields.Date.from_string("2022-01-11")
        cls.partnerB = cls.PartnerObj.create({"name": "Timeline Partner B"})
        cls.lang = cls.env["res.lang"].search(
            [("code", "=", cls.env.user.company_id.partner_id.lang)]
        )

    def _create_quotation(self, product):
        service_rental = self._create_rental_service_day(product)
        return self._create_rental_order(
            self.partnerA.id, self.date_0101, self.date_0110, product=service_rental
        )

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
        service_rental = self._create_rental_service_day(self.product_rental_1)
        # rental order
        rental_order_1 = self._create_rental_order(
            self.partnerA.id, self.date_0101, self.date_0110, product=service_rental
        )
        rental_order_1.action_confirm()
        self.assertEqual(len(rental_order_1.order_line), 1)
        line = rental_order_1.order_line[0]
        self.assertEqual(line.product_id, service_rental)
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
        self.assertEqual(timeline.name, self.partnerA.name)

    def test_01_update_start_end_date(self):
        # rental service product
        service_rental = self._create_rental_service_day(self.product_rental_2)
        # rental order
        rental_order_2 = self._create_rental_order(
            self.partnerA.id, self.date_0101, self.date_0110, product=service_rental
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
                **{
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
        service_rental = self._create_rental_service_day(self.product_rental_3)
        # rental order
        rental_order_3 = self._create_rental_order(
            self.partnerA.id, self.date_0101, self.date_0110, product=service_rental
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

    def test_03_timeline_of_quotation(self):
        order = self._create_quotation(self.product_rental_1)
        timeline = order.order_line.timeline_ids
        self.assertEqual(len(timeline), 1)
        self.assertEqual(timeline.type, "reserved")
        self.assertEqual(timeline.type_formated, "Quotation")
        self.assertEqual(timeline.order_name, order.name)
        self.assertEqual(timeline.product_name, self.product_rental_1.display_name)
        self.assertEqual(timeline.product_categ_name, self.category_all.display_name)
        self.assertEqual(timeline.warehouse_name, self.warehouse0.display_name)
        self.assertEqual(
            timeline.date_start_formated,
            timeline.date_start.strftime(self.lang.date_format),
        )
        self.assertEqual(
            timeline.date_end_formated,
            timeline.date_end.strftime(self.lang.date_format),
        )

    def test_04_hour_uom_shows_time(self):
        order = self._create_quotation(self.product_rental_1)
        line = order.order_line
        line.product_uom = self.uom_hour
        timeline = line.timeline_ids
        self.assertEqual(timeline.time_uom, self.uom_hour)
        datetime_format = f"{self.lang.date_format} {self.lang.time_format}"
        self.assertEqual(
            timeline.date_start_formated, timeline.date_start.strftime(datetime_format)
        )
        self.assertEqual(
            timeline.date_end_formated, timeline.date_end.strftime(datetime_format)
        )

    def test_05_write_dates_on_quotation_line(self):
        order = self._create_quotation(self.product_rental_1)
        line = order.order_line
        timeline = line.timeline_ids
        line.write({"start_date": "2022-01-02", "end_date": "2022-01-11"})
        self.assertEqual(timeline.date_start.date(), self.date_0102)
        self.assertEqual(timeline.date_end.date(), self.date_0111)
        # the new start date is after the current end date of the timeline
        line.write({"start_date": "2022-02-01", "end_date": "2022-02-10"})
        self.assertEqual(
            timeline.date_start.date(), fields.Date.from_string("2022-02-01")
        )
        self.assertEqual(
            timeline.date_end.date(), fields.Date.from_string("2022-02-10")
        )

    def test_06_reset_timeline_product_and_name(self):
        order = self._create_quotation(self.product_rental_1)
        line = order.order_line
        timeline = line.timeline_ids
        service_rental_2 = self._create_rental_service_day(self.product_rental_2)
        line._reset_timeline({"product_id": service_rental_2.id, "name": "SO-RESET"})
        self.assertEqual(timeline.product_id, self.product_rental_2)
        self.assertEqual(timeline.order_name, "SO-RESET")

    def test_07_write_rental_recreates_timeline(self):
        order = self._create_quotation(self.product_rental_1)
        line = order.order_line
        line.timeline_ids.unlink()
        self.assertFalse(self.get_related_timeline_from_rental_order(line))
        line.write({"rental": True, "name": "Rental again"})
        self.assertEqual(len(self.get_related_timeline_from_rental_order(line)), 1)

    def test_08_write_dates_without_timeline(self):
        order = self._create_quotation(self.product_rental_1)
        line = order.order_line
        line.timeline_ids.unlink()
        with self.assertRaisesRegex(UserError, "does not have timeline objects"):
            line.write({"start_date": "2022-01-02", "end_date": "2022-01-11"})

    def test_09_write_dates_on_line_without_rental_product(self):
        order = self._create_quotation(self.product_rental_1)
        line = order.order_line.create(
            {
                "order_id": order.id,
                "product_id": self.product_rental_3.id,
                "product_uom_qty": 1,
            }
        )
        # a line that is not a rental is skipped
        line.write({"start_date": "2022-01-02", "end_date": "2022-01-11"})
        self.assertFalse(self.get_related_timeline_from_rental_order(line))
        with self.assertRaisesRegex(UserError, "does not have a rental product"):
            line.write(
                {"rental": True, "start_date": "2022-01-03", "end_date": "2022-01-12"}
            )

    def test_10_change_rental_type_on_confirmed_order(self):
        order = self._create_quotation(self.product_rental_1)
        order.action_confirm()
        with self.assertRaisesRegex(
            UserError, "not allowed to change the 'rental type'"
        ):
            order.order_line.write({"rental_type": "new_rental", "name": "Changed"})

    def test_11_write_order_updates_timeline(self):
        order = self._create_quotation(self.product_rental_1)
        timeline = order.order_line.timeline_ids
        order.write(
            {
                "name": "SO-TIMELINE",
                "partner_id": self.partnerB.id,
                "partner_shipping_id": self.partnerB.id,
            }
        )
        self.assertEqual(timeline.order_name, "SO-TIMELINE")
        self.assertEqual(timeline.partner_id, self.partnerB)
        self.assertEqual(timeline.partner_shipping_id, self.partnerB)
        self.assertEqual(timeline.name, self.partnerB.name)

    def test_12_unlink_line_and_order(self):
        order_1 = self._create_quotation(self.product_rental_1)
        line_1 = order_1.order_line
        line_1.unlink()
        self.assertFalse(self.get_related_timeline_from_rental_order(line_1))
        order_2 = self._create_quotation(self.product_rental_2)
        line_2 = order_2.order_line
        order_2.unlink()
        self.assertFalse(self.get_related_timeline_from_rental_order(line_2))

    def test_13_timeline_without_sale_order_line(self):
        with mute_logger("odoo.addons.rental_timeline.models.product_timeline"):
            timeline = self.env["product.timeline"].create(
                {
                    "res_model": "res.partner",
                    "res_id": self.partnerA.id,
                    "click_res_model": "res.partner",
                    "click_res_id": self.partnerA.id,
                    "date_start": "2022-01-01 00:00:00",
                    "date_end": "2022-01-10 00:00:00",
                    "product_id": self.product_rental_1.id,
                    "order_name": "No order",
                }
            )
            self.assertEqual(timeline.type_formated, "False")
        self.assertFalse(timeline.warehouse_name)

    def test_14_archived_product_deactivates_timeline(self):
        order = self._create_quotation(self.product_rental_1)
        timeline = order.order_line.timeline_ids
        self.assertTrue(timeline.active)
        self.product_rental_1.active = False
        self.assertFalse(timeline.active)
