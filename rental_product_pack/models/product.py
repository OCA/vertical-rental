# Part of rental-vertical See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    used_pack_line_count = fields.Integer(
        string="# Used Pack Line Count",
        compute="_compute_used_pack_line_count",
    )

    @api.depends("pack_line_ids")
    def _compute_used_pack_line_count(self):
        for rec in self:
            rec.used_pack_line_count = len(rec.used_in_pack_line_ids)


class ProductProduct(models.Model):
    _inherit = "product.product"

    used_pack_line_count = fields.Integer(
        string="# Used Pack Line Count",
        related="product_tmpl_id.used_pack_line_count",
    )
