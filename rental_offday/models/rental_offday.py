# Part of rental-vertical See LICENSE file for full copyright and licensing details.

from odoo import _, api, exceptions, fields, models


class RentalOffday(models.Model):
    _name = "rental.offday"
    _description = "Off-days for daily rentals"

    add_order_line_id = fields.Many2one(
        comodel_name="sale.order.line",
        string="Order Line (of additional off-day)",
        ondelete="set null",
    )

    fixed_order_line_id = fields.Many2one(
        comodel_name="sale.order.line",
        string="Order Line (of fixed off-day)",
        ondelete="set null",
    )

    name = fields.Char(
        string="Description",
    )

    date = fields.Date(
        string="Date",
        required=True,
    )

    @api.constrains("fixed_order_line_id", "date", "add_order_line_id")
    def _check_date(self):
        for line in self:
            domain = [
                ("date", "=", line.date),
                ("id", "!=", line.id),
                ("fixed_order_line_id", "=", line.fixed_order_line_id.id),
            ]
            if line.fixed_order_line_id:
                domain.append("|")
                domain.append(("fixed_order_line_id", "=", line.fixed_order_line_id.id))
                domain.append(("add_order_line_id", "=", line.fixed_order_line_id.id))
            if line.add_order_line_id:
                domain.append("|")
                domain.append(("fixed_order_line_id", "=", line.add_order_line_id.id))
                domain.append(("add_order_line_id", "=", line.add_order_line_id.id))
            lines = self.search_count(domain)
            if lines:
                raise exceptions.ValidationError(
                    _('You have already created the off-day "%s".') % line.date
                )
