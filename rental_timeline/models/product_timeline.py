# Part of rental-vertical See LICENSE file for full copyright and licensing details.

import logging
from datetime import datetime

from odoo import api, fields, models

_logger = logging.getLogger(__name__)


class ProductTimeline(models.Model):
    _name = "product.timeline"
    _description = "Product Timeline"

    res_model = fields.Char(
        string="Origin Data Model",
        help="This is a technical field to know which kind "
        "of Odoo object this timeline item is about.",
        require=True,
    )

    res_id = fields.Integer(
        string="Origin Object ID",
        help="This is a technical field to know which exact "
        "Odoo object this timeline item is about.",
        require=True,
    )

    click_res_model = fields.Char(
        string="Clickable Data Model",
        help="This is a technical field to define which kind "
        "of Odoo object this timeline item opens, when "
        "double clicked.",
        require=True,
    )

    click_res_id = fields.Integer(
        string="Clickable Object ID",
        help="This is a technical field to define which exact "
        "Odoo object this timeline item opens, when double "
        "clicked.",
        require=True,
    )

    date_start = fields.Datetime(
        string="Date Start",
        require=True,
    )

    date_start_formated = fields.Char(
        string="Date Start (Formatted)",
        help="This field contains the start date as string "
        "without time to show it in rental timeline "
        "mouseover view.",
        compute="_compute_required_fields",
        store=True,
    )

    date_end = fields.Datetime(
        string="Date End",
        require=True,
    )

    date_end_formated = fields.Char(
        string="Date End (Formatted)",
        help="This field contains the end date as string "
        "without time to show it in rental timeline "
        "mouseover view.",
        compute="_compute_required_fields",
        store=True,
    )

    product_id = fields.Many2one(
        string="Product",
        comodel_name="product.product",
        ondelete="cascade",
        required=True,
    )

    active = fields.Boolean(
        compute="_compute_active",
        store=True,
    )

    product_name = fields.Char(
        string="Product Name",
        help="This field contains the product name as string "
        "to show it in rental timeline mouseover view.",
        compute="_compute_required_fields",
        store=True,
    )

    time_uom = fields.Many2one(
        string="Time UOM",
        comodel_name="uom.uom",
        compute="_compute_fields",
        store=True,
    )

    order_name = fields.Char(
        string="Order",
        help="This field contains the order name as string "
        "to show it in rental timeline mouseover view.",
        require=True,
    )

    type = fields.Selection(
        string="Type",
        selection=[
            ("rental", "Confirmed Order"),
            ("reserved", "Quotation"),
        ],
    )

    type_formated = fields.Char(
        string="Type (Formatted)",
        help="This field contains the timeline type as string "
        "to show it in rental timeline mouseover view.",
        compute="_compute_required_fields",
        store=True,
    )

    has_clues = fields.Char(
        "Has Clues",
        compute="_compute_fields",
        store=True,
    )

    product_tmpl_id = fields.Many2one(
        string="Product Template",
        related="product_id.product_tmpl_id",
        store=True,
    )

    product_categ_id = fields.Many2one(
        string="Product Category",
        related="product_id.categ_id",
        store=True,
    )

    product_categ_name = fields.Char(
        compute="_compute_required_fields",
        store=True,
    )

    name = fields.Char(
        string="Name",
        compute="_compute_fields",
        store=True,
    )

    partner_id = fields.Many2one(
        string="Partner",
        comodel_name="res.partner",
        ondelete="set null",
        compute="_compute_fields",
        store=True,
    )

    partner_shipping_id = fields.Many2one(
        string="Shipping Partner",
        comodel_name="res.partner",
        ondelete="set null",
        compute="_compute_fields",
        store=True,
    )

    partner_shipping_address = fields.Char(
        string="Shipping address",
        help="This field contains the shipping address as string "
        "to show it in rental timeline mouseover view.",
        compute="_compute_fields",
        store=True,
    )

    currency_id = fields.Many2one(
        string="Currency",
        comodel_name="res.currency",
        compute="_compute_fields",
        store=True,
    )

    price_subtotal = fields.Monetary(
        currency_field="currency_id",
        field_digits=True,
        compute="_compute_fields",
        store=True,
    )

    number_of_days = fields.Integer(
        string="Total days",
        compute="_compute_fields",
        store=True,
    )

    rental_period = fields.Char(
        string="Rental Duration",
        help="This field contains the rental duration as string "
        "to show it in rental timeline mouseover view.",
        compute="_compute_fields",
        store=True,
    )

    amount = fields.Char(
        string="Amount",
        compute="_compute_fields",
        store=True,
    )

    warehouse_id = fields.Many2one(
        string="Warehouse",
        comodel_name="stock.warehouse",
        compute="_compute_fields",
        store=True,
    )

    warehouse_name = fields.Char(
        string="Warehouse Name",
        help="This field contains the warehouse name as string "
        "to show it in rental timeline mouseover view.",
        compute="_compute_warehouse_name",
        store=True,
    )

    _sql_constraints = [
        (
            "date_check",
            "CHECK ((date_start <= date_end))",
            "The start date must be anterior to the end date.",
        ),
    ]

    @api.depends("res_id", "res_model")
    def _compute_fields(self):
        """This function calculates the computed fields for model sale.order.line
        Since It will only be triggered, if res_id or res_model is changed.
        For updating of further infos of the related model it should be called
        for example in _reset_timeline of the related res_model.
        """
        lang = self.env["res.lang"].search(
            [("code", "=", self.env.user.company_id.partner_id.lang)]
        )
        for line in self:
            if line.res_model == "sale.order.line":
                obj = (
                    self.env[line.res_model]
                    .browse(line.res_id)
                    .with_context(lang=lang.code)
                )
                order_obj = obj.order_id
                line.order_name = order_obj.name
                line.name = order_obj.partner_id.commercial_partner_id.name
                line.partner_id = order_obj.partner_id.id
                line.partner_shipping_id = order_obj.partner_shipping_id.id
                line.partner_shipping_address = (
                    order_obj.partner_shipping_id._display_address()
                )
                line.warehouse_id = order_obj.warehouse_id.id
                line.currency_id = obj.currency_id.id
                line.price_subtotal = obj.price_subtotal
                line.number_of_days = obj.number_of_days
                line.time_uom = obj.product_uom
                line.rental_period = "{product_uom_qty} {product_uom}".format(
                    product_uom_qty=int(obj.product_uom_qty),
                    product_uom=obj.product_uom.name,
                )
                currency = line.currency_id
                line.amount = "{price_subtotal} {currency}".format(
                    price_subtotal=lang.format(
                        "%.2f", line.price_subtotal, grouping=True
                    ),
                    currency=currency.symbol,
                )
                line.has_clues = False

    @api.model
    def _get_depends_fields(self, model):
        """
        This function returns the "api.depends"-fields of related model.
        The function _compute_fields should be called if these fields
        of the related model are changed.
        """
        res = []
        if model == "sale.order.line":
            res += [
                "order_id",
                "currency_id",
                "price_subtotal",
                "number_of_days",
                "product_uom_qty",
                "product_uom",
            ]
        return res

    @api.model
    def _get_partner_fields(self):
        """
        This function returns all "Many2one"-fields that are related
        to res.partner. It can be used for triggering the _compute_fields
        to update the partner or address information.
        """
        res = [
            "partner_id",
            "partner_shipping_id",
        ]
        return res

    @api.depends("warehouse_id", "warehouse_id.name")
    def _compute_warehouse_name(self):
        for line in self:
            if line.warehouse_id:
                line.warehouse_name = line.warehouse_id.display_name

    @api.depends(
        "date_start",
        "date_end",
        "product_id",
        "product_id.name",
        "type",
        "product_categ_id",
        "product_categ_id.name",
        "time_uom",
    )
    def _compute_required_fields(self):
        lang = self.env["res.lang"].search(
            [("code", "=", self.env.user.company_id.partner_id.lang)]
        )
        for line in self:
            date_with_time = False
            line.product_name = line.product_id.display_name
            line.product_categ_name = line.product_categ_id.display_name
            try:
                selections = self.with_context(lang=lang.code).fields_get()["type"][
                    "selection"
                ]
                selection = [s for s in selections if s[0] == line.type][0]
                line.type_formated = selection[1]
            except Exception as e:
                _logger.exception(e)
                line.type_formated = str(line.type)

            if line.res_model == "sale.order.line":
                if line.time_uom == self.env.ref("uom.product_uom_hour"):
                    date_with_time = True
            datetime_format = lang.date_format
            if date_with_time:
                datetime_format += " " + lang.time_format
            if isinstance(line.date_start, datetime):
                line.date_start_formated = line.date_start.strftime(datetime_format)
            else:
                line.date_start_formated = str(line.date_start)
            if isinstance(line.date_end, datetime):
                line.date_end_formated = line.date_end.strftime(datetime_format)
            else:
                line.date_end_formated = str(line.date_end)

    @api.depends("product_id", "product_id.active")
    def _compute_active(self):
        for line in self:
            line.active = False
            if line.product_id and line.product_id.active:
                line.active = True
