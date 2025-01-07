# Part of rental-vertical See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models


class ProductTemplate(models.Model):
    _inherit = "product.template"

    rental_of_month = fields.Boolean(
        string="Rented in months",
        copy=False,
    )

    def_pricelist_id = fields.Many2one(
        comodel_name="product.pricelist",
        string="Default Pricelist",
        default=lambda self: self._default_pricelist(),
    )

    product_rental_month_id = fields.Many2one(
        comodel_name="product.product",
        string="Rental Service (Month)",
        ondelete="set null",
        copy=False,
    )

    rental_price_month = fields.Float(
        string="Price / Month",
        store=True,
        copy=False,
        readonly=False,
        related="product_rental_month_id.list_price",
    )

    rental_of_day = fields.Boolean(
        string="Rented in days",
        copy=False,
    )

    product_rental_day_id = fields.Many2one(
        comodel_name="product.product",
        string="Rental Service (Day)",
        ondelete="set null",
        copy=False,
    )

    rental_price_day = fields.Float(
        string="Price / Day",
        store=True,
        copy=False,
        readonly=False,
        related="product_rental_day_id.list_price",
    )

    rental_of_hour = fields.Boolean(
        string="Rented in hours",
        copy=False,
    )

    rental_price_hour = fields.Float(
        string="Price / Hour",
        store=True,
        copy=False,
        readonly=False,
        related="product_rental_hour_id.list_price",
    )

    product_rental_hour_id = fields.Many2one(
        comodel_name="product.product",
        string="Rental Service (Hour)",
        ondelete="set null",
        copy=False,
    )

    """
        This field defines which product.product is associated with the product.template
        and obtains the data necessary for Rental.
    """
    product_value_ids = fields.Many2many(
        "product.product", compute="_compute_product_value_ids", store=True
    )
    product_related_id = fields.Many2one(
        "product.product",
        domain="[('id','in',product_value_ids)]",
        help="Defines the product associated with the product template.",
    )

    month_scale_pricelist_item_ids = fields.One2many(
        comodel_name="product.pricelist.item",
        inverse_name="month_item_tmpl_id",
        compute="_compute_month_scale_pricelist_item_ids",
        inverse="_inverse_month_scale_pricelist_item_ids",
        store=True,
    )

    day_scale_pricelist_item_ids = fields.One2many(
        comodel_name="product.pricelist.item",
        inverse_name="day_item_tmpl_id",
        compute="_compute_day_scale_pricelist_item_ids",
        inverse="_inverse_day_scale_pricelist_item_ids",
        store=True,
    )

    hour_scale_pricelist_item_ids = fields.One2many(
        comodel_name="product.pricelist.item",
        inverse_name="hour_item_tmpl_id",
        string="Hour Scale Pricelist Items",
        compute="_compute_hour_scale_pricelist_item_ids",
        inverse="_inverse_hour_scale_pricelist_item_ids",
        copy=False,
    )

    def _default_pricelist(self):
        # TODO change default pricelist if country group exist
        return self.env.ref("product.list0").id

    def _get_product_by_template(self, limit=1000):
        product_ids = self.env["product.product"].search_read(
            domain=[["product_tmpl_id", "=", self.id]], fields=["id"], limit=limit
        )
        return product_ids

    def write(self, vals):
        if vals.get("rental", False):
            product_id = self._get_product_by_template(limit=1)
            if product_id:
                vals["product_related_id"] = product_id[0]["id"]
        return super().write(vals)

    @api.depends("product_related_id")
    def _compute_product_value_ids(self):
        for product_tmpl in self:
            self.product_value_ids = [
                (6, 0, [val["id"] for val in product_tmpl._get_product_by_template()])
            ]

    @api.depends("product_related_id.month_scale_pricelist_item_ids")
    def _compute_month_scale_pricelist_item_ids(self):
        for product_tmpl in self:
            product_tmpl.month_scale_pricelist_item_ids = (
                product_tmpl.product_related_id.month_scale_pricelist_item_ids
            )

    def _inverse_month_scale_pricelist_item_ids(self):
        for product_tmpl in self:
            product_tmpl.product_related_id.month_scale_pricelist_item_ids = (
                product_tmpl.month_scale_pricelist_item_ids
            )

    @api.depends("product_related_id.day_scale_pricelist_item_ids")
    def _compute_day_scale_pricelist_item_ids(self):
        for product_tmpl in self:
            product_tmpl.day_scale_pricelist_item_ids = (
                product_tmpl.product_related_id.day_scale_pricelist_item_ids
            )

    def _inverse_day_scale_pricelist_item_ids(self):
        for product_tmpl in self:
            product_tmpl.product_related_id.day_scale_pricelist_item_ids = (
                product_tmpl.day_scale_pricelist_item_ids
            )

    @api.depends("product_related_id.hour_scale_pricelist_item_ids")
    def _compute_hour_scale_pricelist_item_ids(self):
        for product_tmpl in self:
            product_tmpl.hour_scale_pricelist_item_ids = (
                product_tmpl.product_related_id.hour_scale_pricelist_item_ids
            )

    def _inverse_hour_scale_pricelist_item_ids(self):
        for product_tmpl in self:
            product_tmpl.product_related_id.hour_scale_pricelist_item_ids = (
                product_tmpl.hour_scale_pricelist_item_ids
            )
