# Copyright 2023 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>

from odoo import _, api, fields, models
from odoo.exceptions import UserError


class ProductTemplate(models.Model):
    _inherit = "product.template"

    rental_product_tmpl_id = fields.Many2one(
        comodel_name="product.template",
        string="Related Rental Product Template",
    )

    rental_attributes_values_need_update = fields.Boolean(
        compute="_compute_rental_attributes_values_need_update",
        store=True,
        readonly=True,
    )
    show_rental_attributes_values_need_update = fields.Boolean(
        related="rental_product_tmpl_id.rental_attributes_values_need_update",
    )

    @api.depends("rental_product_tmpl_id")
    def _compute_rented_product_tmpl_id(self):
        with_variants = self.filtered(lambda template: template.attribute_line_ids)
        for template in with_variants:
            template.rental_product_tmpl_id.rented_product_tmpl_id = template.id
        return super(
            ProductTemplate, self - with_variants
        )._compute_rented_product_tmpl_id()

    def copy_for_rental(self):
        self.ensure_one()
        rental_template = self.with_context(copy_for_rental=True).copy()
        active_langs = self.env["res.lang"].get_installed()
        for lang_code, _lang_name in active_langs:
            new_name = "[RENT] %s" % self.with_context(lang=lang_code).name
            rental_template.with_context(lang=lang_code).name = new_name
        self.rental_product_tmpl_id = rental_template.id

    def write(self, vals):
        for rec in self:
            if "attribute_line_ids" in vals and rec.rented_product_tmpl_id:
                raise UserError(
                    _(
                        "You can not change the attributes of a rental "
                        "product. Instead, please update the rented one."
                    )
                )
        return super().write(vals)

    @api.model_create_multi
    def create(self, values):
        templates = super().create(values)
        if self.env.context.get("copy_for_rental"):
            for template in templates:
                template.must_have_dates = True
                template.type = "service"
                template.tracking = "none"
                template.uom_id = self.env.ref("uom.product_uom_day").id
        return templates

    @api.depends(
        "rented_product_tmpl_id.attribute_line_ids",
        "rented_product_tmpl_id.attribute_line_ids.value_ids",
    )
    def _compute_rental_attributes_values_need_update(self):
        for rec in self:
            rec.rental_attributes_values_need_update = False
            if (
                rec.type == "service"
                and rec.rented_product_tmpl_id
                and rec.rented_product_tmpl_id.attribute_line_ids.value_ids
                != rec.attribute_line_ids.value_ids
            ):
                rec.rental_attributes_values_need_update = True

    def update_rental_attributes_values(self):
        rented_attributes = self.rented_product_tmpl_id.attribute_line_ids.attribute_id
        rental_attributes = self.attribute_line_ids.attribute_id
        attributes_to_add = rented_attributes - rental_attributes
        attributes_to_delete = rental_attributes - rented_attributes
        attributes_to_update = (
            rental_attributes - attributes_to_delete + attributes_to_add
        )

        for attribute in attributes_to_add:
            self.env["product.template.attribute.line"].create(
                {
                    "product_tmpl_id": self.id,
                    "attribute_id": attribute.id,
                    "value_ids": [(6, 0, attribute.value_ids.ids)],
                }
            )
        for attribute in attributes_to_update:
            domain = [("attribute_id", "=", attribute.id)]
            line = self.attribute_line_ids.filtered_domain(domain)
            rented_line = (
                self.rented_product_tmpl_id.attribute_line_ids.filtered_domain(domain)
            )
            if line.value_ids != rented_line.value_ids:
                line.write(
                    {
                        "value_ids": [(6, 0, rented_line.value_ids.ids)],
                    }
                )
        for attribute in attributes_to_delete:
            domain = [
                ("attribute_id", "=", attribute.id),
                ("product_tmpl_id", "=", self.id),
            ]
            self.attribute_line_ids.filtered_domain(domain).unlink()

    def cron_update_rental_attributes_values(self):
        templates = self.search([("rental_attributes_values_need_update", "=", True)])
        for template in templates:
            template.update_rental_attributes_values()
