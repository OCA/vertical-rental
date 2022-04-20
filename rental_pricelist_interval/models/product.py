# Part of rental-vertical See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    interval_item_id = fields.Many2one(
        "product.product",
        string="Rental Service (Interval)",
    )

    @api.onchange("product_id")
    def _onchange_product_id(self):
        uom_interval = self.env.ref("rental_pricelist_interval.product_uom_interval")
        super()._onchange_product_id()
        if self.product_id.rented_product_id:
            if self.product_id.uom_id.id == uom_interval.id:
                self.interval_item_id = self.product_id.rented_product_id.id


class ProductPricelist(models.Model):
    _inherit = "product.pricelist"

    is_interval_pricelist = fields.Boolean("Interval Pricelist")


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _default_interval_pricelist(self):
        try:
            res = self.env.ref("rental_pricelist_interval.pricelist_interval").id
        except Exception:
            return False
        return res

    rental_of_interval = fields.Boolean(
        "Rented in interval",
        copy=False,
    )

    product_rental_interval_id = fields.Many2one(
        "product.product",
        "Rental Service (Interval)",
        ondelete="set null",
        copy=False,
    )

    rental_interval_max = fields.Integer(
        "Interval days (Max)",
        copy=False,
    )

    rental_price_interval = fields.Float(
        string="Interval Price",
    )

    interval_scale_pricelist_item_ids = fields.One2many(
        "product.pricelist.item",
        "interval_item_id",
        string="Interval Scale Pricelist Items",
        copy=False,
    )

    def_interval_pricelist_id = fields.Many2one(
        "product.pricelist",
        "Default Interval Pricelist",
        default=lambda self: self._default_interval_pricelist(),
    )

    def _get_rental_service(self, rental_type):
        self.ensure_one()
        if rental_type == "interval" and self.product_rental_interval_id:
            return self.product_rental_interval_id
        return super()._get_rental_service(rental_type)

    @api.model
    def _get_rental_service_uom(self, rental_type):
        if rental_type == "interval":
            uom_interval = self.env.ref(
                "rental_pricelist_interval.product_uom_interval"
            )
            return uom_interval
        else:
            return super()._get_rental_service_uom(rental_type)

    def write(self, vals):
        res = super(ProductProduct, self).write(vals)
        for p in self:
            # Create service product automatically
            if vals.get("rental_of_interval", False):
                if not p.product_rental_interval_id:
                    service_product = self._create_rental_service(
                        "interval", p, p.rental_price_interval
                    )
                    p.product_rental_interval_id = service_product
            # update analytic account for service product
            if (
                "income_analytic_account_id" in vals
                or "expense_analytic_account_id" in vals
            ):
                p._update_rental_service_analytic_account(vals)
        return res

    @api.model_create_multi
    def create(self, vals_list):
        ext_vals = {}
        for vals in vals_list:
            if vals.get("rental_of_interval", False):
                ext_vals["rental_of_interval"] = True
                ext_vals["rental_price_interval"] = vals.get("rental_price_interval")
                del vals["rental_of_interval"]
                if "rental_price_interval" in vals:
                    del vals["rental_price_interval"]
        res = super().create(vals_list)
        res.write(ext_vals)
        return res

    def action_reset_rental_price_interval_items(self):
        self.ensure_one()
        company = self.company_id or self.env.user.company_id
        self.interval_scale_pricelist_item_ids.unlink()
        values = []
        for rule in company.rental_price_interval_rule_ids:
            values.append(
                (
                    0,
                    0,
                    {
                        "fixed_price": self.rental_price_interval * rule.factor,
                        "min_quantity": rule.min_quantity,
                        "compute_price": "fixed",
                        "applied_on": "0_product_variant",
                        "product_id": self.product_rental_interval_id.id,
                        "pricelist_id": self.def_interval_pricelist_id.id,
                    },
                )
            )
        self.interval_scale_pricelist_item_ids = values
