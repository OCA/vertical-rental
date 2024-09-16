# Part of rental-vertical See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    rental = fields.Boolean("Can be Rent")


class ProductProduct(models.Model):
    _inherit = "product.product"

    rental = fields.Boolean(
        "Can be Rent", compute="_compute_rental", inverse="_inverse_rental", store=True
    )

    @api.depends("product_tmpl_id.rental")
    def _compute_rental(self):
        for product in self:
            product.rental = product.product_tmpl_id.rental

    def _inverse_rental(self):
        for product in self:
            product.product_tmpl_id.rental = product.rental
