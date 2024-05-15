# Copyright 2023 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_confirm(self):
        rentals = [line for line in self.order_line if line.is_rental]
        for rental in rentals:
            rented = (
                rental.product_id.rented_product_id.id or rental.set_rented_product_id()
            )
            if not isinstance(rented, int):
                rented = rented.id
            rented_product = self.env["product.product"].browse(rented)
            rented_product.rental_product_id = rental.product_id
            rental.product_id.rented_product_id = rented_product
            rental.rental_product_id_change()
        return super().action_confirm()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    rental_id = fields.Many2one(
        comodel_name="sale.rental",
        string="Rental",
        compute="_compute_rental_id",
        store=True,
    )
    is_rental = fields.Boolean(
        string="Is Rental Variant Exist",
        compute="_compute_is_rental",
    )

    @api.depends("product_id.product_tmpl_id")
    def _compute_is_rental(self):
        for rec in self:
            rec.is_rental = bool(rec.product_id.product_tmpl_id.rented_product_tmpl_id)

    @api.depends("order_id.state")
    def _compute_rental_id(self):
        for rec in self:
            rec.rental_id = self.env["sale.rental"].search(
                [("start_order_line_id", "=", rec.id)], limit=1
            )

    def set_rented_product_id(self):
        if not self.product_id.rented_product_id:
            rented_product_tmpl = self.product_id.product_tmpl_id.rented_product_tmpl_id
            rented = rented_product_tmpl.product_variant_ids.filtered(
                lambda x, s=self: (
                    s.product_id.product_template_variant_value_ids.product_attribute_value_id
                    == x.product_template_variant_value_ids.product_attribute_value_id
                )
            ).id
            if not rented:
                ptavs = self.product_template_attribute_value_ids
                rented_ptav = self.env["product.template.attribute.value"].search(
                    [
                        ("product_tmpl_id", "=", rented_product_tmpl.id),
                        (
                            "product_attribute_value_id",
                            "in",
                            ptavs.product_attribute_value_id.ids,
                        ),
                    ]
                )

                rented = rented_product_tmpl.create_product_variant(rented_ptav.ids)
            if not rented:
                raise ValidationError(
                    _("Physical rent product " "can not be found / created.")
                )
            else:
                return rented

    def rental_product_id_change(self):
        if (
            not self.product_id.rented_product_id
            and self.product_id.product_tmpl_id.rented_product_tmpl_id
        ):
            return
        else:
            return super().rental_product_id_change()

    def _check_sale_line_rental(self):
        lines = [
            line
            for line in self
            if line.rental_type == "new_rental"
            and not line.product_id.rented_product_id
            and line.product_id.product_tmpl_id.rented_product_tmpl_id
        ]
        return super(SaleOrderLine, self - lines).rental_product_id_change()

    @api.constrains("is_rental")
    def _check_start_end_dates(self):
        for line in self:
            if line.is_rental and not line.start_date and not line.end_date:
                return
            else:
                return super()._check_start_end_dates()

    def open_rental_line_wizard(self):
        view_id = self.env.ref("rental_variant.sale_rental_line_wizard_view").id
        wizard = self.env["sale.rental.line.wizard"].create(
            {
                "rental_line_id": self.id,
                "rental_type": self.rental_type,
                "extension_rental_id": self.extension_rental_id.id,
                "rental_qty": self.rental_qty,
                "sell_rental_id": self.sell_rental_id.id,
                "start_date": self.start_date,
                "end_date": self.end_date,
            }
        )
        return {
            "type": "ir.actions.act_window",
            "res_model": "sale.rental.line.wizard",
            "res_id": wizard.id,
            "view_mode": "form",
            "view_id": view_id,
            "target": "new",
        }
