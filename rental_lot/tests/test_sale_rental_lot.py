# Copyright 2023 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import Form
from odoo.tests.common import TransactionCase


class TestSaleRentalLot(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.rental_prod = cls.env.ref("sale_rental.rent_product_product_25")
        cls.rented_prod = cls.env.ref("product.product_product_25")
        cls.rented_prod.tracking = "serial"

        cls.serial = cls.env["stock.lot"].create(
            {
                "product_id": cls.rented_prod.id,
                "product_uom_id": cls.rented_prod.uom_id.id,
                "company_id": cls.env.ref("base.main_company").id,
            }
        )
        cls.warehouse = cls.env.ref("stock.warehouse0")
        quant = cls.env["stock.quant"].create(
            {
                "product_id": cls.rented_prod.id,
                "location_id": cls.warehouse.lot_stock_id.id,
                "lot_id": cls.serial.id,
                "inventory_quantity": 1,
            }
        )
        quant.action_apply_inventory()

    def test_rented_serial_number(self):
        so_form = Form(self.env["sale.order"])
        so_form.partner_id = self.env.ref("base.res_partner_1")
        with so_form.order_line.new() as line:
            line.product_id = self.rental_prod
            line.start_date = "2049-01-01"
            line.end_date = "2049-01-10"
            line.rental_qty = 1
            line.rented_lot_id = self.serial
        so = so_form.save()
        so.action_confirm()
        so.picking_ids.action_assign()

        rental = self.env["sale.rental"].search(
            [("start_order_line_id", "=", so.order_line[0].id)]
        )
        self.assertEqual(rental.rented_lot_id, self.serial)
        self.assertEqual(so.picking_ids.move_ids.restrict_lot_id, self.serial)
