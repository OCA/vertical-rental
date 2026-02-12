from odoo import fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    rental_color = fields.Integer(string="Rental Color Index", default=0)
