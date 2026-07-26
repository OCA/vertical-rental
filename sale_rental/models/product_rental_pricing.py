from odoo import api, fields, models


class ProductRentalPricing(models.Model):
    _name = "product.rental.pricing"
    _description = "Rental Pricing per Period"
    _order = "product_id, period_id, id"

    product_id = fields.Many2one("product.product", required=True, ondelete="cascade")
    period_id = fields.Many2one("rental.period", required=True, ondelete="restrict")
    price = fields.Monetary(required=True)
    currency_id = fields.Many2one(
        "res.currency",
        default=lambda self: self.env.company.currency_id.id,
        required=True,
    )

    company_id = fields.Many2one(
        "res.company", default=lambda self: self.env.company.id, required=True
    )

    @api.model
    def default_get(self, fields_list):
        res = super().default_get(fields_list)
        active_id = self.env.context.get("active_id")

        if active_id and "product_id" in fields_list and not res.get("product_id"):
            res["product_id"] = active_id

        return res
