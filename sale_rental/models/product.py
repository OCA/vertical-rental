# Copyright 2014-2021 Akretion France (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2016-2021 Sodexis (http://sodexis.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = "product.product"

    # Link rental service -> rented HW product
    rented_product_id = fields.Many2one(
        "product.product",
        string="Related Rented Product",
        domain=[("type", "=", "consu")],
    )
    # Link rented HW product -> rental service
    rental_service_ids = fields.One2many(
        "product.product", "rented_product_id", string="Related Rental Services"
    )
    rental_pricing_ids = fields.One2many(
        "product.rental.pricing", "product_id", string="Rental Pricings"
    )

    def _get_rental_price_for_period(self, period, company=None, currency=None):
        self.ensure_one()
        if not period:
            return 0.0

        rec = self.rental_pricing_ids.filtered(lambda r: r.period_id.id == period.id)[
            :1
        ]
        if not rec:
            return 0.0
        price = rec.price
        from_currency = rec.currency_id

        to_currency = currency or (company or self.env.company).currency_id
        if from_currency != to_currency:
            price = from_currency._convert(
                from_amount=price,
                to_currency=to_currency,
                company=company or self.env.company,
                date=fields.Date.context_today(self),
            )
        return price

    def _get_rental_price_for_duration(
        self, period, duration, company=None, currency=None
    ):
        self.ensure_one()
        if not period or duration <= 0:
            return 0.0
        base = self._get_rental_price_for_period(
            period, company=company, currency=currency
        )
        if not base:
            return 0.0

        amount = base * duration
        return amount

    @api.constrains("rented_product_id", "must_have_dates", "type")
    def _check_rental(self):
        for product in self:
            if product.rented_product_id:
                if product.type != "service":
                    raise ValidationError(
                        self.env._(
                            "The rental product '%s' must be of type 'Service'.",
                            product.name,
                        )
                    )
                if not product.must_have_dates:
                    raise ValidationError(
                        self.env._(
                            "The rental product '%s' must have the option "
                            "'Must Have Start and End Dates' checked.",
                            product.name,
                        )
                    )

    def action_view_rental_pricing(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "sale_rental.action_product_rental_pricing"
        )

        ctx = dict(self.env.context or {})
        ctx.update(
            {
                "active_id": self.id,
                "active_model": "product.product",
                "search_default_this_product": 1,
            }
        )
        action["context"] = ctx

        return action


class ProductTemplate(models.Model):
    _inherit = "product.template"

    rented_product_tmpl_id = fields.Many2one(
        "product.template",
        compute="_compute_rented_product_tmpl_id",
        string="Rented Product",
        inverse="_inverse_rented_product_tmpl_id",
        store=True,
    )
    rental_service_tmpl_ids = fields.One2many(
        "product.template", "rented_product_tmpl_id", string="Rental Services"
    )

    @api.depends("product_variant_ids", "product_variant_ids.rented_product_id")
    def _compute_rented_product_tmpl_id(self):
        unique_variants = self.filtered(
            lambda template: len(template.product_variant_ids) == 1
        )
        for template in unique_variants:
            variant_id = template.product_variant_ids
            template.rented_product_tmpl_id = (
                variant_id.rented_product_id.product_tmpl_id.id
                if variant_id.rented_product_id
                else False
            )
        for template in self - unique_variants:
            template.rented_product_tmpl_id = False

    def _inverse_rented_product_tmpl_id(self):
        for template in self:
            if len(template.product_variant_ids) == 1:
                template.product_variant_ids.rented_product_id = (
                    template.rented_product_tmpl_id.product_variant_ids[0].id
                )

    def action_view_rental_pricing(self):
        self.ensure_one()
        action = self.env["ir.actions.actions"]._for_xml_id(
            "sale_rental.action_product_rental_pricing"
        )
        product_ids = self.product_variant_ids.ids
        action["domain"] = [("product_id", "in", product_ids)]

        ctx = dict(self.env.context or {})
        ctx.update(
            {
                "active_id": product_ids[0],
                "active_model": "product.product",
                "search_default_this_product": 1,
            }
        )
        action["context"] = ctx
        return action
