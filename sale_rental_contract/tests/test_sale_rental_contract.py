# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import fields
from odoo.tests import TransactionCase, tagged


@tagged("post_install", "-at_install")
class TestSaleRentalContract(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.env = cls.env(context=dict(cls.env.context, tracking_disable=True))
        cls.company = cls.env.company
        cls.warehouse = cls.env["stock.warehouse"].search(
            [("company_id", "=", cls.company.id)], limit=1
        )
        cls.warehouse.rental_allowed = True
        cls.partner = cls.env["res.partner"].create({"name": "Exam Printing Ltd"})
        cls.printer = cls.env["product.product"].create(
            {"name": "Production printer", "detailed_type": "product"}
        )
        cls.env["stock.quant"].with_context(inventory_mode=True).create(
            {
                "product_id": cls.printer.id,
                "location_id": cls.warehouse.rental_in_location_id.id,
                "inventory_quantity": 5,
            }
        )._apply_inventory()
        wizard = (
            cls.env["create.rental.product"]
            .with_context(active_model="product.product", active_id=cls.printer.id)
            .create(
                {
                    "sale_price_per_day": 30.0,
                    "categ_id": cls.env.ref("product.product_category_all").id,
                }
            )
        )
        cls.rental_service = cls.env["product.product"].browse(
            wizard.create_rental_product()["res_id"]
        )
        template = cls.env["contract.template"].create(
            {"name": "Monthly rental", "contract_type": "sale"}
        )
        cls.rental_service.product_tmpl_id.write(
            {
                "is_contract": True,
                "recurring_rule_type": "monthly",
                "recurring_invoicing_type": "pre-paid",
                "property_contract_template_id": template.id,
                "rental_contract_price": 1000.0,
            }
        )
        cls.month = cls.env.ref("sale_rental_contract.product_uom_month")

    def _create_order(self, rental_qty=2, start=None, end=None, extend=None):
        # starts today: the contract line is due now
        start = start or fields.Date.today()
        end = end or start + relativedelta(years=1, days=-1)
        days = (end - start).days + 1
        return self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "warehouse_id": self.warehouse.id,
                "default_start_date": start,
                "default_end_date": end,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.rental_service.id,
                            "rental_type": "rental_extension"
                            if extend
                            else "new_rental",
                            "extension_rental_id": extend.id if extend else False,
                            "rental_qty": rental_qty,
                            "start_date": start,
                            "end_date": end,
                            # as in sale_rental tests
                            "number_of_days": days,
                            "product_uom_qty": rental_qty * days,
                            "price_unit": 30.0,
                        },
                    )
                ],
            }
        )

    def test_contract_from_rental(self):
        order = self._create_order()
        order.action_confirm()
        line = order.order_line
        contract_line = line.contract_id.contract_line_ids
        self.assertEqual(len(contract_line), 1)
        self.assertEqual(contract_line.quantity, 2)
        self.assertEqual(contract_line.uom_id, self.month)
        self.assertEqual(contract_line.price_unit, 1000.0)
        self.assertEqual(contract_line.date_start, line.start_date)
        self.assertEqual(contract_line.date_end, line.end_date)
        self.assertEqual(contract_line.recurring_next_date, line.start_date)
        # the rent is invoiced by the contract, not by the order
        self.assertFalse(line.qty_to_invoice)
        # sale_rental still moves the goods
        self.assertEqual(order.picking_ids.move_ids.product_id, self.printer)

    def test_monthly_invoice(self):
        order = self._create_order()
        order.action_confirm()
        invoice = order.order_line.contract_id.recurring_create_invoice()
        self.assertEqual(invoice.invoice_line_ids.quantity, 2)
        self.assertEqual(invoice.invoice_line_ids.product_uom_id, self.month)
        self.assertAlmostEqual(invoice.amount_untaxed, 2000.0)
        # the rental service must have dates: the invoice carries the period
        line = invoice.invoice_line_ids
        self.assertEqual(line.start_date, order.order_line.start_date)
        self.assertTrue(line.end_date)
        invoice.action_post()
        self.assertEqual(invoice.state, "posted")

    def test_price_from_order_amount(self):
        self.rental_service.rental_contract_price = 0.0
        order = self._create_order(rental_qty=1)
        order.action_confirm()
        line = order.order_line
        contract_line = line.contract_id.contract_line_ids
        # 30 a day for the whole year, spread over 12 months
        self.assertAlmostEqual(
            contract_line.price_unit, 30.0 * line.number_of_days / 12, places=2
        )

    def _rental(self, order):
        return self.env["sale.rental"].search(
            [("start_order_line_id", "=", order.order_line.id)]
        )

    def _done(self, picking):
        picking.action_assign()
        for move in picking.move_ids:
            move.quantity_done = move.product_uom_qty
        picking._action_done()

    def test_extension(self):
        order = self._create_order()
        order.action_confirm()
        rental = self._rental(order)
        start = rental.end_date + relativedelta(days=1)
        extension = self._create_order(
            start=start, end=start + relativedelta(months=6, days=-1), extend=rental
        )
        extension.action_confirm()
        contract = order.order_line.contract_id
        # same contract, the extension follows the first line
        self.assertEqual(extension.order_line.contract_id, contract)
        first, second = contract.contract_line_ids.sorted("date_start")
        self.assertEqual(second.date_start, start)
        self.assertEqual(second.quantity, 2)
        self.assertEqual(first.successor_contract_line_id, second)

    def test_sell_rented_product(self):
        order = self._create_order()
        order.action_confirm()
        self._done(
            order.picking_ids.filtered(lambda p: p.picking_type_code == "outgoing")
        )
        rental = self._rental(order)
        sale = self.env["sale.order"].create(
            {
                "partner_id": self.partner.id,
                "warehouse_id": self.warehouse.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.printer.id,
                            "sell_rental_id": rental.id,
                            "product_uom_qty": 2,
                            "price_unit": 5000.0,
                        },
                    )
                ],
            }
        )
        sale.action_confirm()
        contract_line = order.order_line.contract_id.contract_line_ids
        self.assertEqual(contract_line.date_end, sale.date_order.date())

    def test_early_return(self):
        order = self._create_order()
        order.action_confirm()
        out = order.picking_ids.filtered(lambda p: p.picking_type_code == "outgoing")
        self._done(out)
        back = order.picking_ids - out
        self._done(back)
        contract_line = order.order_line.contract_id.contract_line_ids
        # returned 11 months earlier: the contract stops on the return day
        self.assertEqual(contract_line.date_end, back.date_done.date())
