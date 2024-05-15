# Copyright 2023 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>

from odoo.tests.common import TransactionCase


class TestSaleRentalVariant(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.rented_template = cls.env.ref("product.product_product_4_product_template")
        cls.rented_template.copy_for_rental()
        cls.rental_template = cls.rented_template.rental_product_tmpl_id
        cls.rental_product = cls.rental_template.product_variant_ids[0]
        cls.sale = cls.env["sale.order"].create(
            {
                "partner_id": cls.env.ref("base.res_partner_1").id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.rental_product.id,
                            "product_uom_qty": 10,
                            "start_date": "2049-01-01",
                            "end_date": "2049-01-10",
                            "rental_qty": 1,
                        },
                    )
                ],
            }
        )

        cls.rented_dynamic_template = cls.env["product.template"].create(
            {
                "name": "screw",
                "detailed_type": "product",
            }
        )
        cls.size_attr = cls.env["product.attribute"].create(
            {
                "name": "Size",
                "create_variant": "dynamic",
            }
        )
        cls.value_small = cls.env["product.attribute.value"].create(
            {"name": "Small", "attribute_id": cls.size_attr.id}
        )
        cls.value_medium = cls.env["product.attribute.value"].create(
            {"name": "Medium", "attribute_id": cls.size_attr.id}
        )
        cls.env["product.template.attribute.line"].create(
            [
                {
                    "product_tmpl_id": cls.rented_dynamic_template.id,
                    "attribute_id": cls.size_attr.id,
                    "value_ids": [(6, 0, cls.size_attr.value_ids.ids)],
                }
            ]
        )
        cls.rented_dynamic_template.copy_for_rental()
        cls.rental_dynamic_template = cls.rented_dynamic_template.rental_product_tmpl_id
        cls.value = cls.env["product.template.attribute.value"].search(
            [
                ("product_attribute_value_id", "=", cls.value_medium.id),
                ("attribute_id", "=", cls.size_attr.id),
                ("product_tmpl_id", "=", cls.rental_dynamic_template.id),
            ],
            limit=1,
        )
        cls.env["product.product"].create(
            {
                "product_tmpl_id": cls.rental_dynamic_template.id,
                "product_template_attribute_value_ids": [(6, 0, cls.value.ids)],
            }
        )
        cls.rental_dynamic_product = cls.rental_dynamic_template.product_variant_ids[0]
        cls.sale_dynamic = cls.env["sale.order"].create(
            {
                "partner_id": cls.env.ref("base.res_partner_1").id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": cls.rental_dynamic_product.id,
                            "product_uom_qty": 10,
                            "start_date": "2049-01-01",
                            "end_date": "2049-01-10",
                            "rental_qty": 1,
                        },
                    )
                ],
            }
        )

    def test_copy_for_rental(self):
        self.assertEqual(
            self.rental_template, self.rented_template.rental_product_tmpl_id
        )
        self.assertEqual(self.rental_template.detailed_type, "service")
        self.assertEqual(
            self.rental_template.attribute_line_ids.value_ids,
            self.rented_template.attribute_line_ids.value_ids,
        )

    def test_update_rental_attributes_values(self):
        self.assertFalse(self.rental_template.rental_attributes_values_need_update)
        self.env["product.template.attribute.line"].create(
            {
                "product_tmpl_id": self.rented_template.id,
                "attribute_id": self.env.ref("product.product_attribute_3").id,
                "value_ids": [
                    (
                        6,
                        0,
                        [
                            self.env.ref("product.product_attribute_value_5").id,
                            self.env.ref("product.product_attribute_value_6").id,
                        ],
                    )
                ],
            }
        )
        self.assertTrue(self.rental_template.rental_attributes_values_need_update)
        self.rental_template.update_rental_attributes_values()
        self.assertFalse(self.rental_template.rental_attributes_values_need_update)
        self.assertTrue(self.rental_template.attribute_line_ids.value_ids)
        self.assertEqual(
            self.rental_template.attribute_line_ids.value_ids,
            self.rented_template.attribute_line_ids.value_ids,
        )

    def test_link_to_rented_variant_in_sale(self):
        self.sale.action_confirm()
        rental = self.env["sale.rental"].search(
            [("start_order_line_id", "=", self.sale.order_line[0].id)]
        )
        self.assertEqual(rental.rental_product_id, self.rental_product)
        self.assertEqual(rental.rented_product_id.product_tmpl_id, self.rented_template)

    def test_link_to_dynamic_rented_variant_in_sale(self):
        self.assertFalse(self.rented_dynamic_template.product_variant_ids)
        self.sale_dynamic.action_confirm()
        rental = self.env["sale.rental"].search(
            [("start_order_line_id", "=", self.sale_dynamic.order_line[0].id)]
        )
        self.assertEqual(rental.rental_product_id, self.rental_dynamic_product)
        self.assertEqual(
            rental.rented_product_id.product_tmpl_id, self.rented_dynamic_template
        )

    def test_sale_rental_wizard(self):
        sale = self.env["sale.order"].create(
            {
                "partner_id": self.env.ref("base.res_partner_1").id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "product_id": self.rental_product.id,
                        },
                    )
                ],
            }
        )

        wizard_model = self.env["sale.rental.line.wizard"]
        wiz = wizard_model.create(
            {
                "rental_line_id": sale.order_line.id,
            }
        )
        wiz.rental_type = "new_rental"
        wiz.start_date = "2049-01-01"
        wiz.end_date = "2049-01-10"
        wiz.rental_qty = 1
        wiz.confirm_rental_config()
        self.assertEqual(sale.order_line.product_uom_qty, 10)

        sale.action_confirm()
        rental = self.env["sale.rental"].search(
            [("start_order_line_id", "=", sale.order_line.id)]
        )
        self.assertEqual(rental.rental_product_id, self.rental_product)
        self.assertEqual(rental.rented_product_id.product_tmpl_id, self.rented_template)
