# Part of rental-vertical See LICENSE file for full copyright and licensing details.
from odoo import _, api, exceptions, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def action_check_rental_availability(self):
        for order in self:
            for line in order.order_line:
                line._check_rental_availability()


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    concurrent_orders = fields.Selection(
        selection=[
            ("none", "None"),
            ("quotation", "Quotation"),
            ("order", "Order"),
        ],
        default="none",
    )

    # (override) from module rental_pricelist
    def _check_rental_availability(self):
        self.ensure_one()
        res = {}
        if not self.start_date or not self.end_date or not self.rental_qty:
            return {}
        total_qty = self.product_id.rented_product_id.with_context(
            {"location": self.order_id.warehouse_id.rental_view_location_id.id}
        ).qty_available
        max_ol_qty = self._get_max_overlapping_rental_qty()
        avail_qty = total_qty - max_ol_qty
        if self.rental_qty > avail_qty:
            res = self._get_concurrent_orders()
            if total_qty == 0:
                self.concurrent_orders = "none"
            elif res["quotation"] and not res["order"]:
                self.concurrent_orders = "quotation"
            else:
                self.concurrent_orders = "order"
            res["warning"] = {
                "title": _("Not enough stock!"),
                "message": _(
                    "You want to rent %.2f %s but you only "
                    "have %.2f %s available in the selected period."
                )
                % (
                    self.rental_qty,
                    self.product_id.rented_product_id.uom_id.name,
                    avail_qty,
                    self.product_id.rented_product_id.uom_id.name,
                ),
            }
        else:
            self.concurrent_orders = "none"
        return res

    # (override) from module rental_pricelist
    @api.onchange("start_date", "end_date", "product_uom")
    def onchange_start_end_date(self):
        res = {}
        if self.start_date and self.end_date:
            number = self._get_number_of_time_unit()
            self.number_of_time_unit = number
            res = self._check_rental_availability()
        return res

    def _get_concurrent_order_lines(self):
        self.ensure_one()
        domain = []
        if self.id:
            domain = [("id", "!=", self.id)]
        domain += [
            ("state", "!=", "cancel"),
            ("display_product_id", "=", self.display_product_id.id),
            "|",
            "&",
            ("start_date", "<=", self.start_date),
            ("end_date", ">=", self.start_date),
            "&",
            ("start_date", "<=", self.end_date),
            ("end_date", ">=", self.end_date),
        ]
        res = self.search(domain)
        return res

    def _get_concurrent_orders(self):
        self.ensure_one()
        sols = self._get_concurrent_order_lines()
        sos = sols.mapped("order_id")
        quotations = sos.filtered(lambda o: o.state in ["draft", "sent"])
        orders = sos.filtered(lambda o: o.state in ["sale"])
        return {
            "quotation": quotations,
            "order": orders,
            "sale_order_ids": quotations.ids + orders.ids,
        }

    def action_view_concurrent_orders(self):
        self.ensure_one()
        record_ids = self._get_concurrent_orders()["sale_order_ids"]
        if record_ids:
            action = self.env.ref("rental_base.action_rental_orders").read([])[0]
            action["domain"] = [("id", "in", record_ids)]
            return action
        raise exceptions.UserError(_("No found concurrent Rental Order/Quotation(s)."))

    def _get_max_overlapping_rental_qty(self):
        self.ensure_one()
        lines = self._get_concurrent_order_lines()
        max_qty = 0
        for line in lines:
            ol_lines = self.search(
                [
                    ("id", "in", lines.ids),
                    ("start_date", "<=", line.start_date),
                    ("end_date", ">=", line.start_date),
                ]
            )
            tmp_qty = sum(line.rental_qty for line in ol_lines)
            if tmp_qty > max_qty:
                max_qty = tmp_qty
            ol_lines = self.search(
                [
                    ("id", "in", lines.ids),
                    ("start_date", "<=", line.end_date),
                    ("end_date", ">=", line.end_date),
                ]
            )
            tmp_qty = sum(line.rental_qty for line in ol_lines)
            if tmp_qty > max_qty:
                max_qty = tmp_qty
        return max_qty
