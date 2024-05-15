# Copyright 2023 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>

from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    rental_product_id = fields.Many2one(
        "product.product",
    )

    def get_rented_product_id(self):
        if len(self.rented_product_tmpl_id.product_variant_ids) == 1:
            return self.rented_product_tmpl_id.product_variant_ids
        product = self.rented_product_tmpl_id.product_variant_ids.filtered_domain(
            [
                (
                    "product_template_attribute_value_ids",
                    "=",
                    self.product_template_attribute_value_ids.ids,
                )
            ]
        )
        if product:
            if len(product) == 1:
                return product
            else:
                return product.filtered(
                    lambda x, self: len(self.product_template_attribute_value_ids)
                    == len(x.product_template_attribute_value_ids)
                )
        else:
            return None
