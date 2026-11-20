# Part of rental-vertical See LICENSE file for full copyright and licensing details.

import datetime
from math import ceil

from odoo import api, exceptions, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare, float_round


class SaleOrder(models.Model):
    _inherit = "sale.order"

    default_start_date = fields.Date(
        compute="_compute_default_start_date",
        readonly=False,
        store=True,
    )

    default_end_date = fields.Date(
        compute="_compute_default_end_date",
        readonly=False,
        store=True,
    )

    is_rental_order = fields.Boolean(
        compute="_compute_is_rental_order",
        store=True,
    )

    @api.depends("order_line.start_date")
    def _compute_default_start_date(self):
        for order in self:
            dates = []
            so_lines = order.order_line
            if so_lines:
                for line in so_lines:
                    if line.start_date:
                        dates.append(line.start_date)
            if dates:
                order.update(
                    {
                        "default_start_date": min(dates),
                    }
                )

    @api.depends("order_line.end_date")
    def _compute_default_end_date(self):
        for order in self:
            dates = []
            so_lines = order.order_line
            if so_lines:
                for line in so_lines:
                    if line.end_date:
                        dates.append(line.end_date)
            if dates:
                order.update(
                    {
                        "default_end_date": max(dates),
                    }
                )

    @api.depends("partner_id", "company_id")
    @api.depends_context("partner_id", "company_id", "company")
    def _compute_sale_type_id(self):
        """Keep the order type sticky when dependencies change.

        sale_order_type recomputes ``type_id`` from ``partner_id`` /
        ``company_id`` and always assigns a value, which silently replaces
        the type set by the menu action (``default_type_id``) or a manual
        selection as soon as the customer is entered or changed. Restore
        the v12 behavior: the type is only determined while it is not set
        yet (action context default first, then partner sale type, then
        the first configured type) and is not overwritten afterwards.
        """
        for record in self:
            if record.type_id:
                continue
            sale_type = record.default_get(["type_id"]).get("type_id", False)
            if not sale_type:
                sale_type = (
                    record.partner_id.with_company(record.company_id).sale_type
                    or record.partner_id.commercial_partner_id.with_company(
                        record.company_id
                    ).sale_type
                )
            if not sale_type:
                sale_type = record._default_type_id()
            record.type_id = sale_type

    @api.depends("type_id", "type_id.is_rental_type")
    def _compute_is_rental_order(self):
        rental_type = self.sudo().env.ref(
            "rental_base.rental_sale_type", raise_if_not_found=False
        )
        for order in self:
            order.is_rental_order = bool(
                order.type_id.is_rental_type
                or (rental_type and order.type_id.id == rental_type.id)
            )

    is_rental_line = fields.Boolean(
        compute="_compute_is_rental_line",
        store=False,
    )
    is_of_rental_type = fields.Selection(
        [("new_rental", "New Rental"), ("rental_extension", "Rental Extension")],
        string="Rental Type (Mirror)",
        compute="_compute_is_of_rental_type",
        store=False,
    )
    is_can_sell_rental = fields.Boolean(
        compute="_compute_is_can_sell_rental",
        store=False,
    )

    @api.depends("order_line.rental")
    def _compute_is_rental_line(self):
        for order in self:
            order.is_rental_line = any(line.rental for line in order.order_line)

    @api.depends("order_line.rental_type", "order_line.rental")
    def _compute_is_of_rental_type(self):
        for order in self:
            rental_line = next(
                (line for line in order.order_line if line.rental and line.rental_type),
                False,
            )
            order.is_of_rental_type = rental_line.rental_type if rental_line else False

    @api.depends("order_line.can_sell_rental")
    def _compute_is_can_sell_rental(self):
        for order in self:
            order.is_can_sell_rental = any(
                line.can_sell_rental for line in order.order_line
            )

    def unlink(self):
        for rec in self:
            rentals = self.env["sale.rental"].search(
                [
                    ("start_order_line_id", "in", rec.order_line.ids),
                ]
            )
            rentals.unlink()
        return super().unlink()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    rental_qty_uom = fields.Many2one(
        string="Product Unit of Measure",
        related="product_id.rented_product_id.uom_id",
    )

    start_date = fields.Date()

    end_date = fields.Date()

    @api.constrains(
        "rental_type",
        "extension_rental_id",
        "start_date",
        "end_date",
        "rental_qty",
        "product_uom_qty",
        "product_id",
    )
    def _check_sale_line_rental(self):
        for line in self:
            if line.rental_type == "rental_extension":
                if not line.extension_rental_id:
                    raise ValidationError(
                        self.env._(
                            'Missing "Rental to Extend" on the sale order line '
                            "with rental service %s."
                        )
                        % line.product_id.name
                    )

                if line.rental_qty != line.extension_rental_id.rental_qty:
                    raise ValidationError(
                        self.env._(
                            "On the sale order line with rental service %s, "
                            "you are trying to extend a rental with a rental "
                            "quantity (%s) that is different from the quantity "
                            "of the original rental (%s). This is not supported."
                        )
                        % (
                            line.product_id.name,
                            line.rental_qty,
                            line.extension_rental_id.rental_qty,
                        )
                    )
            if line.rental_type in ("new_rental", "rental_extension"):
                if not line.product_id.rented_product_id:
                    raise ValidationError(
                        self.env._(
                            'On the "new rental" sale order line with product '
                            '"%s", we should have a rental service product!'
                        )
                        % (line.product_id.name)
                    )
                if (
                    not self._context.get("allow_write", False)
                    and line.start_date
                    and line.end_date
                    and line.start_date <= line.end_date
                ):
                    number_of_time_unit = line._get_number_of_time_unit()
                    if (
                        number_of_time_unit
                        and line.product_uom_qty
                        != line.rental_qty * number_of_time_unit
                    ):
                        raise ValidationError(
                            self.env._(
                                "On the sale order line with product '%s' "
                                "the Product Quantity (%s) should be the "
                                "number of time units (%s) "
                                "multiplied by the Rental Quantity (%s)."
                            )
                            % (
                                line.product_id.name,
                                line.product_uom_qty,
                                number_of_time_unit,
                                line.rental_qty,
                            )
                        )
            elif line.sell_rental_id:
                if line.product_uom_qty != line.sell_rental_id.rental_qty:
                    raise ValidationError(
                        self.env._(
                            "On the sale order line with product %s "
                            "you are trying to sell a rented product with a "
                            "quantity (%s) that is different from the rented "
                            "quantity (%s). This is not supported."
                        )
                        % (
                            line.product_id.name,
                            line.product_uom_qty,
                            line.sell_rental_id.rental_qty,
                        )
                    )

    # use this field to show the widget radio for field rental
    order_type = fields.Selection(
        selection=[("normal", "Normal"), ("rental", "Rental")],
        compute="_compute_order_type",
        inverse="_inverse_order_type",
    )

    @api.depends("rental")
    def _compute_order_type(self):
        for rec in self:
            rec.order_type = "rental" if rec.rental else "normal"

    def _inverse_order_type(self):
        for rec in self:
            rec.rental = rec.order_type == "rental"

    @api.onchange("order_type")
    def _onchange_order_type(self):
        self.rental = self.order_type == "rental"

    @api.model
    def _search_time_uom(self, factor_low, factor_high):
        """Fallback when this module's own Month/Week uoM records are not present
        (deployment dedupes them against migrated customer uoMs). The migrated
        uoMs keep the same factor windows; smallest id wins to prefer first-created."""
        return self.env["uom.uom"].search(
            [
                ("category_id", "=", self.env.ref("uom.uom_categ_wtime").id),
                ("uom_type", "=", "bigger"),
                ("factor", ">", factor_low),
                ("factor", "<", factor_high),
            ],
            order="id",
            limit=1,
        )

    @api.model
    def _get_time_uom(self):
        def _time_uom_by_factor(factor_low, factor_high):
            return self.env["uom.uom"].search(
                [
                    ("category_id", "=", self.env.ref("uom.uom_categ_wtime").id),
                    ("uom_type", "=", "bigger"),
                    ("factor", ">", factor_low),
                    ("factor", "<", factor_high),
                ],
                order="id",
                limit=1,
            )

        # The deployment may keep migrated customer UoMs (same factor, different
        # id) instead of this module's records. Resolve by factor within the
        # expected window so the migrated UoMs are found; fall back to the
        # module's own records. (issue #7190, staging data check 2026-10-27)
        uom_month = self._search_time_uom(0.02, 0.05) or self.env.ref(
            "rental_base.product_uom_month", raise_if_not_found=False
        )
        uom_week = self._search_time_uom(0.1, 0.2) or self.env.ref(
            "rental_base.product_uom_week", raise_if_not_found=False
        )
        uom_day = self.env.ref("uom.product_uom_day")
        uom_hour = self.env.ref("uom.product_uom_hour")
        return {
            "month": uom_month,
            "week": uom_week,
            "day": uom_day,
            "hour": uom_hour,
        }

    def _get_number_of_time_unit(self):
        self.ensure_one()
        number = False
        if not self.start_date or not self.end_date:
            return number
        time_uoms = self._get_time_uom()
        # Compare by factor instead of record id: deployments may keep migrated
        # customer UoMs (same factor, different id) next to this module's records.
        # (issue #7190, staging data check 2026-10-27)
        if (
            float_compare(
                self.product_uom.factor, time_uoms["day"].factor, precision_digits=2
            )
            == 0
        ):
            number = (self.end_date - self.start_date).days + 1
        elif (
            float_compare(
                self.product_uom.factor, time_uoms["hour"].factor, precision_digits=2
            )
            == 0
        ):
            number = ((self.end_date - self.start_date).days + 1) * 8
        elif (
            float_compare(
                self.product_uom.factor, time_uoms["month"].factor, precision_digits=2
            )
            == 0
        ):
            number = ((self.end_date - self.start_date).days + 1) / 30.4167
            number = float_round(number, precision_rounding=1)
        elif (
            float_compare(
                self.product_uom.factor, time_uoms["week"].factor, precision_digits=2
            )
            == 0
        ):
            number = ceil(((self.end_date - self.start_date).days + 1) / 7)
        return number

    def update_start_end_date(self, date_start, date_end):
        for line in self:
            # update sale order lines
            update_date_start_later = False
            if date_start > line.end_date:
                update_date_start_later = True
            else:
                line.with_context(allow_write=True).start_date = date_start
            line.with_context(allow_write=True).end_date = date_end
            if update_date_start_later:
                line.with_context(allow_write=True).start_date = date_start
            datetime_start = fields.Datetime.to_datetime(date_start)
            datetime_end = fields.Datetime.to_datetime(date_end)
            # update rental
            if line.rental:
                rentals = self.env["sale.rental"].search(
                    [
                        ("start_order_line_id", "=", line.id),
                        ("state", "!=", "cancel"),
                        ("out_move_id.state", "!=", "cancel"),
                        ("in_move_id.state", "!=", "cancel"),
                    ]
                )
                if rentals and date_start:
                    rental = rentals[0]
                    date_move_out = fields.Date.to_date(rental.out_move_id.date)
                    if date_start != date_move_out:
                        if rental.out_move_id.state not in [
                            "draft",
                            "confirmed",
                            "waiting",
                            "assigned",
                        ]:
                            raise exceptions.UserError(
                                self.env._(
                                    "Outgoing shipment is in state %s. You "
                                    "cannot change the start date anymore."
                                )
                                % rental.out_move_id.state
                            )
                        rental.out_move_id.date = datetime_start
                if rentals and date_end:
                    rental = rentals[0]
                    date_move_in = fields.Date.to_date(rental.in_move_id.date)
                    if date_end != date_move_in:
                        if rental.in_move_id.state not in [
                            "draft",
                            "confirmed",
                            "waiting",
                            "assigned",
                        ]:
                            raise exceptions.UserError(
                                self.env._(
                                    "Incoming shipment is in state %s. You "
                                    "cannot change the end date anymore."
                                )
                                % rental.in_move_id.state
                            )
                        rental.in_move_id.date = datetime_end

    def write(self, values):
        """
        Both fields start_date and end_date were made editable in state draft,
        sent and sale, in order to allow the creation of new sale order lines
        with start and end dates.
        However, it is forbidden to write the dates of already existing sale
        order lines.
        To update these existing lines, the method 'update_start_end_date'
        should be called.
        :param values: dictionary
        :return: Boolean
        """
        for sol in self:
            if sol.order_id.state not in ("draft", "sent"):
                messages = []
                if "start_date" in values and not self._context.get(
                    "allow_write", False
                ):
                    if (
                        isinstance(values["start_date"], str)
                        and sol.start_date
                        != datetime.datetime.strptime(
                            values["start_date"], "%Y-%m-%d"
                        ).date()
                    ) or (
                        isinstance(values["start_date"], datetime.date)
                        and sol.start_date != values["start_date"]
                    ):
                        messages.append(
                            self.env._(
                                "You are not allowed to change the 'start date' "
                                "in an order line of a confirmed order."
                            )
                        )
                if "end_date" in values and not self._context.get("allow_write", False):
                    if (
                        isinstance(values["end_date"], str)
                        and sol.end_date
                        != datetime.datetime.strptime(
                            values["end_date"], "%Y-%m-%d"
                        ).date()
                    ) or (
                        isinstance(values["end_date"], datetime.date)
                        and sol.end_date != values["end_date"]
                    ):
                        messages.append(
                            self.env._(
                                "You are not allowed to change the 'end date' "
                                "in an order line of a confirmed order."
                            )
                        )
                if messages:
                    messages.append(
                        self.env._(
                            "\nOrder: %s\n"
                            "Line with product: '%s'\n\n"
                            "Please use instead the button 'Update Times' "
                            "in the order to correctly update the order "
                            "line's times, its timeline entry, contract and "
                            "its stock moves and pickings as required."
                        )
                        % (sol.order_id.name, sol.product_id.display_name)
                    )
                    raise exceptions.UserError("\n".join(messages))
        return super().write(values)
