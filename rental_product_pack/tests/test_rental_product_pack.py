# Part of rental-vertical See LICENSE file for full copyright and licensing details.

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests import new_test_user

from odoo.addons.rental_base.tests.stock_common import RentalStockCommon


class TestRentalProductPack(RentalStockCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_sale = new_test_user(
            cls.env,
            login="rental_pack_salesman",
            groups="sales_team.group_sale_salesman,stock.group_stock_user",
        )
        cls.user_internal = new_test_user(
            cls.env,
            login="rental_pack_internal",
            groups="base.group_user",
        )

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
                self.assertEqual(len(picking.move_ids), 3)
            if picking.picking_type_id == self.picking_type_in:
                self.picking_in = picking
                self.assertEqual(len(picking.move_ids), 3)
        for move in self.picking_out.move_ids:
            if move.product_id == self.productA:
                self.assertEqual(move.product_qty, 1)
                self.moveDestId_A = move.move_dest_ids[0]
            elif move.product_id == self.productB:
                self.assertEqual(move.product_qty, 1)
                self.moveDestId_B = move.move_dest_ids[0]
            elif move.product_id == self.productC:
                self.assertEqual(move.product_qty, 2)
                self.moveDestId_C = move.move_dest_ids[0]
        for move in self.picking_in.move_ids:
            if move.product_id == self.productA:
                self.assertEqual(move.product_qty, 1)
                self.assertEqual(self.moveDestId_A, move)
            elif move.product_id == self.productB:
                self.assertEqual(move.product_qty, 1)
                self.assertEqual(self.moveDestId_B, move)
            elif move.product_id == self.productC:
                self.assertEqual(move.product_qty, 2)
                self.assertEqual(self.moveDestId_C, move)

    def _create_salesman_rental_order(self, products):
        order_lines = []
        for product in products:
            service = self._create_rental_service_day(product)
            order_lines.append(
                (
                    0,
                    0,
                    {
                        "product_id": service.id,
                        "name": service.name,
                        "rental_type": "new_rental",
                        "rental_qty": 1.0,
                        "product_uom": service.uom_id.id,
                        "start_date": self.date_start,
                        "end_date": self.date_end,
                        "product_uom_qty": 2.0,
                    },
                )
            )
        return self.env["sale.order"].create(
            {
                "type_id": self.rental_sale_type.id,
                "partner_id": self.partnerA.id,
                "user_id": self.user_sale.id,
                "order_line": order_lines,
            }
        )

    def _get_out_picking(self, order):
        return order.picking_ids.filtered(
            lambda p: p.picking_type_id == self.picking_type_out
        )

    def test_01_component_already_in_picking_is_summed(self):
        order = self._create_salesman_rental_order(self.productA + self.productB)
        order.with_user(self.user_sale).action_confirm()
        picking_out = self._get_out_picking(order)
        self.assertEqual(len(picking_out.move_ids), 3)
        move_b = picking_out.move_ids.filtered(lambda m: m.product_id == self.productB)
        self.assertEqual(len(move_b), 1)
        self.assertEqual(move_b.product_uom_qty, 2)
        move_c = picking_out.move_ids.filtered(lambda m: m.product_id == self.productC)
        self.assertEqual(move_c.product_uom_qty, 2)

    def test_02_nested_pack_components_are_added(self):
        product_d = self.env["product.product"].create(
            {
                "name": "Product D",
                "type": "product",
                "pack_ok": True,
                "pack_type": "non_detailed",
                "pack_line_ids": [
                    (0, 0, {"product_id": self.productA.id, "quantity": 1}),
                ],
            }
        )
        order = self._create_salesman_rental_order(product_d)
        order.with_user(self.user_sale).action_confirm()
        picking_out = self._get_out_picking(order)
        self.assertEqual(
            picking_out.move_ids.product_id,
            product_d + self.productA + self.productB + self.productC,
        )
        move_c = picking_out.move_ids.filtered(lambda m: m.product_id == self.productC)
        self.assertEqual(move_c.product_uom_qty, 2)
        move_a = picking_out.move_ids.filtered(lambda m: m.product_id == self.productA)
        self.assertEqual(move_a.rental_pack_move_id.product_id, product_d)

    def test_03_used_pack_line_count_follows_pack_lines(self):
        self.assertEqual(self.productC.used_pack_line_count, 1)
        self.env["product.pack.line"].create(
            {
                "parent_product_id": self.productB.id,
                "product_id": self.productC.id,
                "quantity": 1,
            }
        )
        self.assertEqual(self.productC.used_pack_line_count, 2)
        self.assertEqual(self.productC.product_tmpl_id.used_pack_line_count, 2)

    def test_04_internal_user_manages_pack_lines(self):
        pack_line = self.productA.pack_line_ids.filtered(
            lambda line: line.product_id == self.productC
        )
        pack_line.with_user(self.user_internal).write({"quantity": 3})
        self.assertEqual(pack_line.quantity, 3)
        pack_line.with_user(self.user_internal).unlink()
        self.assertEqual(self.productA.pack_line_ids.product_id, self.productB)
        self.assertEqual(self.productC.used_pack_line_count, 0)
