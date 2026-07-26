from datetime import datetime

from odoo.tests import Form

from odoo.addons.quality_control_oca.tests.test_quality_control import (
    TestQualityControlOcaBase,
)


class TestRentalQualityControlOca(TestQualityControlOcaBase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.qc_trigger_model = cls.env["qc.trigger"]

        cls.picking_type = cls.env.ref("stock.picking_type_out")

        cls.trigger = cls.qc_trigger_model.search(
            [("picking_type_id", "=", cls.picking_type.id)]
        )

        cls.test_rental_prod = cls.env.ref("sale_rental.rent_product_product_25")
        cls.test_partner = cls.env["res.partner"].create({"name": "Foo"})

        warehouse = cls.env.ref("stock.warehouse0")
        cls.rental_in_loc = warehouse.rental_in_location_id
        cls.rental_out_loc = warehouse.rental_out_location_id

        cls.period_day = cls.env.ref("sale_rental.rental_period_day")

        cls.test_rental_prod.rented_product_id.qc_triggers = [
            (
                0,
                0,
                {"trigger": cls.trigger.id, "test": cls.test.id, "timing": "before"},
            )
        ]

    def test_rental_has_qc_inspection(self):
        so_form = Form(self.env["sale.order"])
        so_form.partner_id = self.test_partner
        so = so_form.save()

        line_vals = {
            "product_id": self.test_rental_prod.id,
            "start_date": "2022-01-01",
            "end_date": "2022-01-10",
            "rental_qty": 1,
            "rental": True,
            "rental_type": "new_rental",
            "price_unit": 60,
            "product_uom_qty": 10,
            "rental_period_id": self.period_day.id,
            "start_datetime": datetime(2022, 1, 1, 0, 0, 0),
            "end_datetime": datetime(2022, 1, 11, 0, 0, 0),
        }
        so.write({"order_line": [(0, 0, line_vals)]})
        so.action_confirm()

        self.assertEqual(len(so.picking_ids), 2)
        rental_out_pick = so.picking_ids.filtered(
            lambda p: p.location_id == self.rental_in_loc
            and p.location_dest_id == self.rental_out_loc
        )
        self.assertTrue(rental_out_pick)

        rental_out_pick.move_ids.write({"quantity_done": 1})
        rental_out_pick.action_confirm()

        sol = so.order_line[0]
        rental = self.env["sale.rental"].search([("start_order_line_id", "=", sol.id)])
        self.assertTrue(rental)

        inspections = rental.qc_inspections_ids.filtered(lambda i: i.test == self.test)

        self.assertTrue(
            inspections, "Inspection from our configured test should be created"
        )

        inspection = inspections[0]
        self.assertEqual(inspection.state, "ready")
        self.assertEqual(inspection.qty, rental_out_pick.move_ids.quantity_done)
        self.assertEqual(
            inspection.test, self.test, "Wrong test picked when creating inspection."
        )
