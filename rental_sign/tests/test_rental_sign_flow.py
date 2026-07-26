# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
from datetime import datetime
from io import BytesIO

from PIL import Image

from odoo.exceptions import UserError
from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestRentalSignFlow(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.test_rental_prod = cls.env.ref("sale_rental.rent_product_product_25")
        cls.test_partner = cls.env["res.partner"].create({"name": "Foo"})
        warehouse = cls.env.ref("stock.warehouse0")
        cls.rental_in_loc = warehouse.rental_in_location_id
        cls.rental_out_loc = warehouse.rental_out_location_id
        cls.period_day = cls.env.ref("sale_rental.rental_period_day")

        cls.delivery_report = cls.env.ref("stock.action_report_delivery")

        icp = cls.env["ir.config_parameter"].sudo()
        icp.set_param("rental_sign.delivery_report_id", str(cls.delivery_report.id))
        icp.set_param("rental_sign.return_report_id", str(cls.delivery_report.id))

        TemplateItem = cls.env["rental.sign.template.item"]
        role_employee = cls.env.ref("sign_oca.sign_role_employee")
        role_customer = cls.env.ref("sign_oca.sign_role_customer")

        # Delivery – Employee
        TemplateItem.create(
            {
                "description": "Deliver Slip Employee",
                "company_id": cls.env.company.id,
                "report_id": cls.delivery_report.id,
                "role_id": role_employee.id,
                "page": 1,
                "position_x": 6.94,
                "position_y": 58.22,
                "width": 24.95,
                "height": 8.48,
            }
        )
        # Delivery – Customer
        TemplateItem.create(
            {
                "description": "Deliver Slip Customer",
                "company_id": cls.env.company.id,
                "report_id": cls.delivery_report.id,
                "role_id": role_customer.id,
                "page": 1,
                "position_x": 65.80,
                "position_y": 58.52,
                "width": 24.95,
                "height": 8.48,
            }
        )
        # Return – Employee
        TemplateItem.create(
            {
                "description": "Return Slip Employee",
                "company_id": cls.env.company.id,
                "report_id": cls.delivery_report.id,
                "role_id": role_employee.id,
                "page": 1,
                "position_x": 6.94,
                "position_y": 58.22,
                "width": 24.95,
                "height": 8.48,
            }
        )

    def _create_fake_signature_base64(self):
        """Create a fake signature image as base64 for testing"""
        # Create a simple image (e.g., 200x100 white image with black text)
        img = Image.new("RGB", (200, 100), color="white")

        # Save to BytesIO
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)

        # Convert to base64
        return base64.b64encode(buffer.read()).decode("utf-8")

    def _build_sign_data(self, signer):
        sign_items = signer.get_info()["items"]
        data = {}

        fake_signature = self._create_fake_signature_base64()

        for key, val in sign_items.items():
            item = val.copy()
            item["value"] = fake_signature
            data[key] = item
        return data

    def test_full_rental_sign_flow(self):
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
            "product_uom_qty": 10,
            "rental_period_id": self.period_day.id,
            "start_datetime": datetime(2022, 1, 1, 0, 0, 0),
            "end_datetime": datetime(2022, 1, 11, 0, 0, 0),
        }
        so.write({"order_line": [(0, 0, line_vals)]})
        sol = so.order_line[0]
        sol._compute_pricing()
        self.assertEqual(sol.price_subtotal, 600)

        so.action_confirm()
        self.assertEqual(len(so.picking_ids), 2)

        rental_out_pick = so.picking_ids.filtered(
            lambda p: p.location_id == self.rental_in_loc
            and p.location_dest_id == self.rental_out_loc
        )
        self.assertTrue(rental_out_pick)

        rental_out_pick.move_ids.write({"quantity_done": 1})
        rental_out_pick.action_confirm()

        with self.assertRaises(UserError):
            rental_out_pick.button_validate()

        action = rental_out_pick.with_context(
            force_report_rendering=True
        ).action_staff_sign_delivery()
        self.assertTrue(action)

        req = rental_out_pick.delivery_sign_request_id
        self.assertTrue(req)
        self.assertEqual(req.state, "0_sent")
        self.assertEqual(req.record_ref, rental_out_pick)

        staff_signer = req.signer_id
        self.assertTrue(staff_signer)
        self.assertEqual(
            staff_signer.role_id, self.env.ref("sign_oca.sign_role_employee")
        )

        data = self._build_sign_data(staff_signer)
        res = staff_signer.action_sign(data)
        self.assertEqual(res["type"], "ir.actions.act_url")
        self.assertTrue(rental_out_pick.delivery_staff_signed)

        rental_out_pick.button_validate()
        self.assertEqual(rental_out_pick.state, "done")

        self.assertEqual(len(so.picking_ids), 2)
        rental_in_pick = so.picking_ids.filtered(
            lambda p: p.location_id == self.rental_out_loc
            and p.location_dest_id == self.rental_in_loc
        )
        self.assertTrue(rental_in_pick)

        rental = self.env["sale.rental"].search([("start_order_line_id", "=", sol.id)])
        self.assertTrue(rental)

        customer_role = self.env.ref("sign_oca.sign_role_customer")
        customer_signer = req.signer_ids.filtered(lambda s: s.role_id == customer_role)
        self.assertTrue(customer_signer)
        data_customer = self._build_sign_data(customer_signer)
        customer_signer.action_sign(data_customer)
        req.invalidate_recordset()
        self.assertEqual(req.state, "2_signed")

        Attachment = self.env["ir.attachment"]

        picking_atts = Attachment.search(
            [
                ("res_model", "=", "stock.picking"),
                ("res_id", "=", rental_out_pick.id),
            ]
        )
        self.assertTrue(
            picking_atts,
            "Signed PDF should be attached to the outgoing rental picking.",
        )

        rental_atts = Attachment.search(
            [
                ("res_model", "=", "sale.rental"),
                ("res_id", "=", rental.id),
            ]
        )
        self.assertTrue(
            rental_atts,
            "Signed PDF should also be attached to the related sale.rental.",
        )

        rental_in_pick.action_confirm()
        rental_in_pick.action_assign()

        rental_in_pick.move_ids.write({"quantity_done": 1})

        with self.assertRaises(UserError):
            rental_in_pick.button_validate()

        action_ret = rental_in_pick.with_context(
            force_report_rendering=True
        ).action_staff_sign_receipt()
        self.assertTrue(action_ret)

        return_request = rental_in_pick.return_sign_request_id
        self.assertTrue(return_request)
        self.assertEqual(return_request.state, "0_sent")

        ret_signer = return_request.signer_id
        self.assertTrue(ret_signer)
        data_ret = self._build_sign_data(ret_signer)
        ret_signer.action_sign(data_ret)
        self.assertTrue(rental_in_pick.return_staff_signed)

        rental_in_pick.button_validate()
        self.assertEqual(rental_in_pick.state, "done")
