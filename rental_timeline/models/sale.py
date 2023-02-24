# Part of rental-vertical See LICENSE file for full copyright and licensing details.

import functools
import operator

from odoo import _, api, exceptions, fields, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    timeline_ids = fields.One2many(
        string="Timeline Objects",
        comodel_name="product.timeline",
        compute="_compute_timeline_ids",
    )

    rental_type = fields.Selection(
        states={
            "draft": [("readonly", False)],
            "sent": [("readonly", False)],
            "sale": [("readonly", False)],
        }
    )

    @api.multi
    def _compute_timeline_ids(self):
        for line in self:
            domain = [
                ("res_model", "=", line._name),
                ("res_id", "=", line.id),
            ]
            line.timeline_ids = self.env["product.timeline"].search(domain)

    @api.multi
    def _prepare_timeline_vals(self):
        self.ensure_one()
        return {
            "type": "rental" if self.state == "sale" else "reserved",
            "date_start": self.start_date,
            "date_end": self.end_date,
            "product_id": self.product_id.rented_product_id.id,
            "order_name": self.order_id.name,
            "res_model": self._name,
            "res_id": self.id,
            "click_res_model": self.order_id._name,
            "click_res_id": self.order_id.id,
        }

    @api.multi
    def _create_product_timeline(self):
        self.ensure_one()
        if self.product_id.rented_product_id:
            if self.rental_type in ["new_rental", "rental_extension"]:
                vals = self._prepare_timeline_vals()
                self.env["product.timeline"].create(vals)

    @api.multi
    def _reset_timeline(self, vals):
        for line in self:
            if not line.rental:
                continue
            if line.product_id.rented_product_id:
                if not line.timeline_ids:
                    raise exceptions.UserError(
                        _(
                            "The order line with rental product '%s' "
                            "does not have timeline objects."
                        )
                        % line.product_id.rented_product_id
                    )
                update_date_start_later = False
                start_timelines = sorted(line.timeline_ids, key=lambda l: l.date_start)
                end_timelines = sorted(
                    line.timeline_ids, key=lambda l: l.date_end, reverse=True
                )
                if vals.get("start_date", False) and start_timelines:
                    if start_timelines[0].date_end < fields.Datetime.to_datetime(
                        vals.get("start_date")
                    ):
                        update_date_start_later = True
                    else:
                        start_timelines[0].date_start = vals["start_date"]
                if vals.get("end_date", False):
                    end_timelines[0].date_end = vals["end_date"]
                if update_date_start_later:
                    start_timelines[0].date_start = vals["start_date"]
                if vals.get("product_id", False):
                    timelines = sorted(line.timeline_ids, key=lambda l: l.product_id)
                    product = self.env["product.product"].browse(vals["product_id"])
                    timelines[0].product_id = product.rented_product_id.id
                if vals.get("name", False):
                    timelines = sorted(line.timeline_ids, key=lambda l: l.name)
                    timelines[0].order_name = vals["name"]
            else:
                raise exceptions.UserError(
                    _(
                        "The order line with ID '%s' of order '%s' "
                        "does not have a rental product."
                    )
                    % (line.id, line.order_id.name)
                )

    @api.multi
    def _timeline_recompute_fields(self):
        for line in self:
            line.timeline_ids._compute_fields()

    @api.model
    def create(self, vals):
        res = super().create(vals)
        res._create_product_timeline()
        return res

    @api.multi
    def write(self, vals):
        res = super(SaleOrderLine, self).write(vals)
        keys = {"start_date", "end_date", "product_id", "name"}
        if keys.intersection(vals.keys()):
            rental = vals.get("rental", False)
            reset_lines = self.browse([])
            start_date = vals.get("start_date", False)
            end_Date = vals.get("end_date", False)
            product_id = vals.get("product_id", False)
            name = vals.get("name", False)
            for line in self:
                if rental:
                    search = [
                        ("res_model", "=", self._name),
                        ("res_id", "=", self.id),
                    ]
                    if not self.env["product.timeline"].search(search):
                        line._create_product_timeline()
                if start_date and line.start_date != start_date:
                    reset_lines |= line
                if end_Date and line.end_date != end_Date:
                    reset_lines |= line
                if product_id and line.product_id.id != product_id:
                    reset_lines |= line
                if name and line.name != name:
                    reset_lines |= line
                # Since rental_type needed to be editable in state 'sent' and 'sale'
                # to create new order lines in these states it is here forbidden to
                # change it on existing sale order lines.
                if (
                    line.order_id.state not in ("draft", "sent")
                    and "rental_type" in vals
                ):
                    raise exceptions.UserError(
                        _(
                            "You are not allowed to change the 'rental type' "
                            "in an order line of a confirmed order.\n\n"
                            "Order: %s\n"
                            "Line with product: '%s'"
                        )
                        % (line.order_id.name, line.product_id.display_name)
                    )
            reset_lines._reset_timeline(vals)
        keys = set(self.env["product.timeline"]._get_depends_fields("sale.order.line"))
        if keys.intersection(vals.keys()):
            self._timeline_recompute_fields()
        return res

    @api.multi
    def unlink(self):
        res = super(SaleOrderLine, self).unlink()
        domain = [
            ("res_model", "=", self._name),
            ("res_id", "in", self.ids),
        ]
        self.env["product.timeline"].search(domain).unlink()
        return res

    @api.multi
    def update_start_end_date(self, date_start, date_end):
        # update dates
        super(SaleOrderLine, self).update_start_end_date(date_start, date_end)
        for line in self:
            line._reset_timeline(
                {
                    "start_date": fields.Datetime.to_datetime(date_start),
                    "end_date": fields.Datetime.to_datetime(date_end),
                }
            )


class SaleOrder(models.Model):
    _inherit = "sale.order"

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        keys = {"partner_id", "partner_shipping_id", "name"}
        if keys.intersection(vals.keys()):
            for order in self:
                for line in order.order_line:
                    line._timeline_recompute_fields()
        return res

    @api.multi
    def action_cancel(self):
        """
        Delete all timeline objects when cancelling sale order.
        """
        for order in self:
            for line in order.order_line.filtered(
                lambda l: l.rental_type == "rental_extension"
                or l.rental_type == "new_rental"
            ):
                line.timeline_ids.unlink()
        res = super(SaleOrder, self).action_cancel()
        return res

    @api.multi
    def action_draft(self):
        """
        Recreate the timeline objects when setting sale order to draft state.
        """
        res = super(SaleOrder, self).action_draft()
        for order in self:
            for line in order.order_line:
                line._create_product_timeline()
        return res

    @api.multi
    def action_confirm(self):
        """
        Update timeline type of timeline objects when confirming the sale order.
        """
        values = {
            "type": "rental",
        }
        for order in self:
            for line in order.order_line.filtered(
                lambda l: l.rental_type == "rental_extension"
                or l.rental_type == "new_rental"
            ):
                line.timeline_ids.write(values)
                line.timeline_ids._compute_fields()
        res = super(SaleOrder, self).action_confirm()
        return res

    @api.multi
    def unlink(self):
        ids = functools.reduce(operator.iconcat, [i.order_line.ids for i in self], [])
        if ids:
            domain = [
                ("res_model", "=", "sale.order.line"),
                ("res_id", "in", ids),
            ]
            self.env["product.timeline"].search(domain).unlink()
        return super(SaleOrder, self).unlink()
