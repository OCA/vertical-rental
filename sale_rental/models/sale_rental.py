# Copyright 2014-2021 Akretion France (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2016-2021 Sodexis (http://sodexis.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from datetime import datetime, time

from dateutil.relativedelta import relativedelta

from odoo import api, fields, models

logger = logging.getLogger(__name__)


class SaleRental(models.Model):
    _name = "sale.rental"
    _description = "Rental"
    _order = "id desc"

    @api.depends(
        "start_order_line_id",
        "extension_order_line_ids.end_date",
        "extension_order_line_ids.state",
        "start_order_line_id.end_date",
    )
    def name_get(self):
        res = []
        for rental in self:
            name = "[{}] {} - {} > {} ({})".format(
                rental.partner_id.display_name,
                rental.rented_product_id.display_name,
                rental.start_datetime or "",
                rental.end_datetime or "",
                rental._fields["state"].convert_to_export(rental.state, rental),
            )
            res.append((rental.id, name))
        return res

    @api.depends(
        "sell_order_line_ids.move_ids.state",
        "start_order_line_id.order_id.state",
        "start_order_line_id.move_ids.state",
        "start_order_line_id.move_ids.move_dest_ids.state",
    )
    def _compute_move_and_state(self):
        for rental in self:
            in_move = False
            out_move = False
            sell_move = False
            state = False
            if rental.start_order_line_id:
                for move in rental.start_order_line_id.move_ids:
                    if move.state != "cancel" and move.picking_code == "outgoing":
                        out_move = move
                    if move.move_dest_ids:
                        out_move = move
                        in_move = move.move_dest_ids[0]
                if (
                    rental.sell_order_line_ids
                    and rental.sell_order_line_ids[0].move_ids
                ):
                    sell_move = rental.sell_order_line_ids[0].move_ids[-1]
                state = "ordered"
                if out_move and out_move.state == "done":
                    state = "out"
                    if in_move:
                        if in_move.state == "done":
                            state = "in"
                        elif in_move.state == "cancel" and sell_move:
                            state = "sell_progress"
                            if sell_move.state == "done":
                                state = "sold"
                    elif sell_move:
                        state = "sell_progress"
                        if sell_move.state == "done":
                            state = "sold"
                        elif sell_move.state == "cancel":
                            state = "out"
                if rental.start_order_line_id.state == "cancel":
                    state = "cancel"
            rental.in_move_id = in_move
            rental.out_move_id = out_move
            rental.state = state
            rental.sell_move_id = sell_move

    @api.depends(
        "extension_order_line_ids.end_datetime",
        "extension_order_line_ids.state",
        "start_order_line_id.end_datetime",
    )
    def _compute_end_datetime(self):
        for rental in self:
            end_datetime = False
            if rental.start_order_line_id:
                end_datetime = rental.start_order_line_id.end_datetime
            for extension in rental.extension_order_line_ids:
                if (
                    extension.state in ("sale", "done")
                    and extension.end_datetime
                    and (not end_datetime or extension.end_datetime > end_datetime)
                ):
                    end_datetime = extension.end_datetime
            rental.end_datetime = end_datetime

    start_order_line_id = fields.Many2one(
        "sale.order.line", string="Rental SO Line", readonly=True
    )
    start_datetime = fields.Datetime(
        string="From",
        related="start_order_line_id.start_datetime",
        readonly=True,
        store=True,
    )
    rental_product_id = fields.Many2one(
        "product.product",
        related="start_order_line_id.product_id",
        string="Rental Service",
        readonly=True,
        store=True,
    )
    rented_product_id = fields.Many2one(
        "product.product",
        related="start_order_line_id.product_id.rented_product_id",
        string="Rented Product",
        readonly=True,
        store=True,
    )
    rental_qty = fields.Float(
        related="start_order_line_id.rental_qty", readonly=True, store=True
    )
    start_order_id = fields.Many2one(
        "sale.order",
        related="start_order_line_id.order_id",
        string="Rental SO",
        readonly=True,
        store=True,
    )
    company_id = fields.Many2one(
        "res.company",
        related="start_order_line_id.company_id",
        string="Company",
        readonly=True,
        store=True,
    )
    partner_id = fields.Many2one(
        "res.partner",
        related="start_order_line_id.order_id.partner_id",
        string="Customer",
        readonly=True,
        store=True,
    )
    out_move_id = fields.Many2one(
        "stock.move",
        compute="_compute_move_and_state",
        string="Outgoing Move",
        readonly=True,
        store=True,
    )
    in_move_id = fields.Many2one(
        "stock.move",
        compute="_compute_move_and_state",
        string="Incoming Move",
        readonly=True,
        store=True,
    )
    out_state = fields.Selection(
        related="out_move_id.state", string="Out Move State", readonly=True
    )
    in_state = fields.Selection(
        related="in_move_id.state", string="In Move State", readonly=True
    )
    out_picking_id = fields.Many2one(
        "stock.picking",
        related="out_move_id.picking_id",
        string="Delivery Order",
        readonly=True,
    )
    in_picking_id = fields.Many2one(
        "stock.picking",
        related="in_move_id.picking_id",
        string="Receipt",
        readonly=True,
    )
    extension_order_line_ids = fields.One2many(
        "sale.order.line",
        "extension_rental_id",
        string="Rental Extensions",
        readonly=True,
    )
    sell_order_line_ids = fields.One2many(
        "sale.order.line", "sell_rental_id", string="Sell Rented Product", readonly=True
    )
    sell_move_id = fields.Many2one(
        "stock.move",
        compute="_compute_move_and_state",
        string="Selling Move",
        readonly=True,
        store=True,
    )
    sell_state = fields.Selection(
        related="sell_move_id.state", string="Sell Move State", readonly=True
    )
    sell_picking_id = fields.Many2one(
        "stock.picking",
        related="sell_move_id.picking_id",
        string="Sell Delivery Order",
        readonly=True,
    )
    end_datetime = fields.Datetime(
        string="To",
        compute="_compute_end_datetime",
        store=True,
        help="End Date of the Rental (extensions included), \
        taking into account all the extensions sold to the customer.",
    )
    state = fields.Selection(
        [
            ("ordered", "Ordered"),
            ("out", "Out"),
            ("sell_progress", "Sell in progress"),
            ("sold", "Sold"),
            ("in", "Back In"),
            ("cancel", "Cancelled"),
        ],
        compute="_compute_move_and_state",
        readonly=True,
        store=True,
    )

    in_stock = fields.Float(
        related="rented_product_id.qty_available",
        string="In Stock",
        readonly=True,
        store=True,
    )

    company_currency_id = fields.Many2one(
        "res.currency",
        related="company_id.currency_id",
        string="Currency",
        readonly=True,
    )

    revenue = fields.Monetary(
        related="start_order_line_id.price_subtotal",
        currency_field="company_currency_id",
        string="Revenue",
        readonly=True,
        store=True,
    )

    def _get_reminder_days(self):
        try:
            reminder_days = (
                self.env["ir.config_parameter"]
                .sudo()
                .get_param("sale_rental.reminder_days")
            )
            return int(reminder_days or 0)
        except (TypeError, ValueError, OverflowError):
            return 0

    @api.model
    def cron_send_return_reminders(self):
        """Send reminder emails X days before end_date."""
        reminder_days = self._get_reminder_days()

        today = fields.Date.today()
        target_date = today + relativedelta(days=reminder_days)

        target_dt_start = datetime.combine(target_date, time.min)
        target_dt_end = datetime.combine(target_date, time.max)

        domain = [
            ("state", "in", ["out", "sell_progress"]),
            ("end_datetime", ">=", target_dt_start),
            ("end_datetime", "<=", target_dt_end),
            ("partner_id", "!=", False),
        ]

        rentals = self.search(domain)
        if not rentals:
            return

        template = self.env.ref(
            "sale_rental.mail_template_rental_return_reminder",
            raise_if_not_found=False,
        )
        if not template:
            logger.warning(
                "Email template your_module.mail_template_rental_return_reminder not found."
            )
            return

        for rental in rentals:
            try:
                template.send_mail(rental.id, force_send=True)
            except Exception as e:
                logger.exception(
                    "Failed to send return reminder for rental %s: %s", rental.id, e
                )

    @api.depends("out_move_id.date", "in_move_id.date")
    def _compute_actual_rental_hours(self):
        for rental in self:
            if rental.out_move_id and rental.out_move_id.date:
                start = fields.Datetime.from_string(rental.out_move_id.date)
                if rental.in_move_id and rental.in_move_id.date:
                    end = fields.Datetime.from_string(rental.in_move_id.date)
                else:
                    end = fields.Datetime.now()
                rental.actual_rental_hours = (end - start).total_seconds() / 3600
            else:
                rental.actual_rental_hours = 0.0

    actual_rental_hours = fields.Float(
        compute="_compute_actual_rental_hours",
        store=True,
    )

    @api.depends("start_datetime", "end_datetime")
    def _compute_available_hours(self):
        for rental in self:
            if rental.start_datetime and rental.end_datetime:
                start = fields.Datetime.from_string(rental.start_datetime)
                end = fields.Datetime.from_string(rental.end_datetime)
                rental.available_hours = (end - start).total_seconds() / 3600
            else:
                rental.available_hours = 0.0

    available_hours = fields.Float(
        compute="_compute_available_hours",
        store=True,
    )

    @api.depends("actual_rental_hours", "available_hours")
    def _compute_utilization_rate(self):
        for rental in self:
            if rental.available_hours > 0:
                rental.utilization_rate = (
                    rental.actual_rental_hours / rental.available_hours
                ) * 100
            else:
                rental.utilization_rate = 0

    utilization_rate = fields.Float(
        compute="_compute_utilization_rate", string="Utilization Rate (%)", store=True
    )
