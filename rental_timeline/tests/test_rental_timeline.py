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
        self.service_rental = self.env["product.product"]

    def get_related_timeline_from_rental_order(self, line):
        domain = [
            ("res_model", "=", "sale.order.line"),
            ("res_id", "in", line.ids),
        ]
        TimelineObj = self.env["product.timeline"]
        timeline = TimelineObj.search(domain)
        return timeline
