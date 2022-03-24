# Part of rental-vertical See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProductPricelistItem(models.Model):
    _inherit = "product.pricelist.item"

    day_item_id = fields.Many2one(
        comodel_name="product.product",
        string="Rental Service (Day)",
    )

    month_item_id = fields.Many2one(
        comodel_name="product.product",
        string="Rental Service (Month)",
    )

    hour_item_id = fields.Many2one(
        comodel_name="product.product",
        string="Rental Service (Hour)",
    )

    @api.onchange("product_id")
    def _onchange_product_id(self):
        uom_month = self.env.ref("rental_base.product_uom_month")
        uom_day = self.env.ref("uom.product_uom_day")
        uom_hour = self.env.ref("uom.product_uom_hour")
        super()._onchange_product_id()
        if self.product_id.rented_product_id:
            if self.product_id.uom_id.id == uom_month.id:
                self.month_item_id = self.product_id.rented_product_id.id
            if self.product_id.uom_id.id == uom_day.id:
                self.day_item_id = self.product_id.rented_product_id.id
            if self.product_id.uom_id.id == uom_hour.id:
                self.hour_item_id = self.product_id.rented_product_id.id
