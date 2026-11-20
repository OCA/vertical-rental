# Part of rental-vertical See LICENSE file for full copyright and licensing details.

from odoo.tests import TransactionCase, tagged


@tagged("post_install", "standard", "-at_install")
class TestSaleOrderTypeSticky(TransactionCase):
    """The sale order type must not be reassigned when the customer changes.

    sale_order_type computes type_id from partner_id and always assigns a
    value, which replaced the type coming from the menu action context
    (default_type_id) as soon as a customer was entered — e.g. rental or
    service quotations flipping to the sale type.
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.rental_type = cls.env.ref("rental_base.rental_sale_type")
        cls.normal_type = cls.env.ref("sale_order_type.normal_sale_type")
        cls.partner = cls.env["res.partner"].create({"name": "Sticky Customer"})
        cls.other_partner = cls.env["res.partner"].create(
            {"name": "Other Sticky Customer"}
        )

    def _new_order(self, values=None, **context):
        return self.env["sale.order"].with_context(**context).new(values or {})

    def test_type_survives_partner_change(self):
        order = self._new_order(default_type_id=self.rental_type.id)
        self.assertEqual(order.type_id, self.rental_type)
        order.partner_id = self.partner
        self.assertEqual(order.type_id, self.rental_type)

    def test_context_default_wins_over_partner_sale_type(self):
        self.partner.sale_type = self.normal_type
        order = self._new_order(
            {"partner_id": self.partner.id}, default_type_id=self.rental_type.id
        )
        self.assertEqual(order.type_id, self.rental_type)

    def test_partner_sale_type_applies_without_context_default(self):
        self.partner.sale_type = self.normal_type
        order = self._new_order({"partner_id": self.partner.id})
        self.assertEqual(order.type_id, self.normal_type)

    def test_manual_type_choice_sticks(self):
        order = self._new_order(default_type_id=self.rental_type.id)
        order.partner_id = self.partner
        order.type_id = self.normal_type
        order.partner_id = self.other_partner
        self.assertEqual(order.type_id, self.normal_type)
