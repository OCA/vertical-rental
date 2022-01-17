# Part of rental-vertical See LICENSE file for full copyright and licensing details.

from odoo import _, api, exceptions, fields, models


class UpdateSaleLineDateLine(models.TransientModel):
    _name = "update.sale.line.date.line"
    _description = "Details for updating sale order line dates"

    wizard_id = fields.Many2one(
        comodel_name="update.sale.line.date",
        required=True,
    )

    sequence = fields.Integer(
        string="Sequence",
    )

    order_line_id = fields.Many2one(
        comodel_name="sale.order.line",
        required=True,
    )

    date_start = fields.Date(
        string="Date Start",
    )

    date_end = fields.Date(
        string="Date End",
    )

    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
    )

    change = fields.Boolean(
        string="Change",
    )


class UpdateSaleLineDate(models.TransientModel):
    _name = "update.sale.line.date"
    _description = "Wizard for updating sale order line dates"

    date_start = fields.Date(
        string="Date Start",
        required=True,
    )

    date_end = fields.Date(
        string="Date End",
        required=True,
    )

    order_id = fields.Many2one(
        comodel_name="sale.order",
        string="Sale Order",
    )

    date_in_line = fields.Boolean(
        string="Date in Lines",
        help="If set, you can set an individual date in " "every selected position.",
    )

    all_line = fields.Boolean(
        string="All Lines",
        help="If set, all order lines of this order are "
        "updated with the given dates.",
    )

    from_line = fields.Integer(
        string="From",
        help="In order to update one or several order lines, "
        "please set a number referring to the first order "
        "line that should to be changed.",
    )

    to_line = fields.Integer(
        string="To",
        help="In order to update one or several order lines, "
        "please set a number referring to the last order "
        "line that should to be changed.",
    )

    line_ids = fields.One2many(
        comodel_name="update.sale.line.date.line",
        inverse_name="wizard_id",
        string="Positions",
    )

    @api.onchange("date_in_line")
    def onchange_date_in_line(self):
        if self.date_in_line:
            self.all_line = True

    @api.onchange("from_line", "to_line", "all_line")
    def onchange_line(self):
        if self.all_line:
            for line in self.line_ids:
                line.change = True
        elif self.from_line and self.to_line:
            for line in self.line_ids:
                if line.sequence >= self.from_line and line.sequence <= self.to_line:
                    line.change = True
                else:
                    line.change = False

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        active_id = self.env.context.get("active_id")
        order = self.env["sale.order"].browse(active_id)
        seq = 1
        line_ids_value = []
        for line in order.order_line:
            if not line.start_date or not line.end_date:
                continue
            line_ids_value.append(
                (
                    0,
                    0,
                    {
                        "sequence": seq,
                        "order_line_id": line.id,
                        "change": False,
                        "date_start": line.start_date,
                        "date_end": line.end_date,
                        "product_id": line.product_id.id,
                    },
                )
            )
            seq += 1
        res.update(
            {
                "order_id": order.id,
                "date_start": order.default_start_date,
                "date_end": order.default_end_date,
                "date_in_line": False,
                "all_line": True,
                "from_line": 1,
                "to_line": len(line_ids_value),
                "line_ids": line_ids_value,
            }
        )
        return res

    def action_confirm(self):
        self.ensure_one()
        subject = _("Update Date of Sale Order Lines<lu>")
        message_body = ""
        message_body += subject
        if self.all_line:
            if self.date_in_line:
                for line in self.line_ids:
                    message_body += _("<li>%s: %s - %s -> %s - %s</li>") % (
                        line.order_line_id.product_id.name,
                        line.order_line_id.start_date,
                        line.order_line_id.end_date,
                        line.date_start,
                        line.date_end,
                    )
                    line.order_line_id.update_start_end_date(
                        line.date_start, line.date_end
                    )
            else:
                message_body += _("<li>(All lines): %s - %s -> %s - %s</li>") % (
                    self.order_id.default_start_date,
                    self.order_id.default_end_date,
                    self.date_start,
                    self.date_end,
                )
                self.order_id.order_line.filtered(
                    lambda x: x.start_date and x.end_date
                ).update_start_end_date(self.date_start, self.date_end)
        else:
            if self.from_line > self.to_line:
                raise exceptions.UserError(
                    _("The value in 'To' is less then the value in 'From'.")
                )
            if self.date_in_line:
                for line in self.line_ids:
                    if self.from_line <= line.sequence <= self.to_line:
                        message_body += _("<li>%s: %s - %s -> %s - %s</li>") % (
                            line.order_line_id.product_id.name,
                            line.order_line_id.start_date,
                            line.order_line_id.end_date,
                            line.date_start,
                            line.date_end,
                        )
                        line.order_line_id.update_start_end_date(
                            line.date_start, line.date_end
                        )
            else:
                message_body += _("<li>(Lines: %s - %s): %s - %s -> %s - %s</li>") % (
                    self.from_line,
                    self.to_line,
                    self.order_id.default_start_date,
                    self.order_id.default_end_date,
                    self.date_start,
                    self.date_end,
                )
                for line in self.line_ids:
                    if self.from_line <= line.sequence <= self.to_line:
                        line.order_line_id.update_start_end_date(
                            self.date_start, self.date_end
                        )
        message_body += "</lu>"
        self.order_id.message_post(
            body=message_body, subject=subject, message_type="comment"
        )
