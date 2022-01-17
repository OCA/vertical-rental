# Part of rental-vertical See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta

from odoo import fields

from odoo.addons.rental_base.tests.stock_common import RentalStockCommon


class TestRentalProductPack(RentalStockCommon):
    def setUp(self):
        super().setUp()

        # Product Created A, B, C
        ProductObj = self.env["product.product"]
        self.productA = ProductObj.create({"name": "Product A", "type": "product"})
        self.productB = ProductObj.create({"name": "Product B", "type": "product"})
        self.productC = ProductObj.create({"name": "Product C", "type": "product"})
        self.productA.write(
            {
                "pack_ok": True,
                "pack_type": "non_detailed",
                "pack_line_ids": [
                    (0, 0, {"product_id": self.productB.id, "quantity": 1}),
                    (0, 0, {"product_id": self.productC.id, "quantity": 2}),
                ],
            }
        )
        # Rental Service (Day) of Product A
        self.rental_service_day = self._create_rental_service_day(self.productA)

        self.date_start = fields.Date.from_string(fields.Date.today())
        self.date_end = self.date_start + relativedelta(days=1)

        self.rental_order = self.env["sale.order"].create(
            {
                "type_id": self.rental_sale_type.id,
                "partner_id": self.partnerA.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.rental_service_day.id,
                            "name": self.rental_service_day.name,
                            "rental_type": "new_rental",
                            "rental_qty": 1.0,
                            "product_uom": self.rental_service_day.uom_id.id,
                            "start_date": self.date_start,
                            "end_date": self.date_end,
                            "product_uom_qty": 2.0,
                        },
                    )
                ],
            }
        )

    def test_00_rental_product_pack(self):
        self.rental_order.action_confirm()
        self.assertEqual(len(self.rental_order.picking_ids), 2)
        for picking in self.rental_order.picking_ids:
            if picking.picking_type_id == self.picking_type_out:
                self.picking_out = picking
                self.assertEqual(len(picking.move_lines), 3)
            if picking.picking_type_id == self.picking_type_in:
                self.picking_in = picking
                self.assertEqual(len(picking.move_lines), 3)
        for move in self.picking_out.move_lines:
            if move.product_id == self.productA:
                self.assertEqual(move.product_qty, 1)
                self.moveDestId_A = move.move_dest_ids[0]
            elif move.product_id == self.productB:
                self.assertEqual(move.product_qty, 1)
                self.moveDestId_B = move.move_dest_ids[0]
            elif move.product_id == self.productC:
                self.assertEqual(move.product_qty, 2)
                self.moveDestId_C = move.move_dest_ids[0]
        for move in self.picking_in.move_lines:
            if move.product_id == self.productA:
                self.assertEqual(move.product_qty, 1)
                self.assertEqual(self.moveDestId_A, move)
            elif move.product_id == self.productB:
                self.assertEqual(move.product_qty, 1)
                self.assertEqual(self.moveDestId_B, move)
            elif move.product_id == self.productC:
                self.assertEqual(move.product_qty, 2)
                self.assertEqual(self.moveDestId_C, move)
