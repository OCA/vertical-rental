# Copyright (C) 2023 Akretion (<http://www.akretion.com>).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleRentalLineWizard(models.TransientModel):
    _name = "sale.rental.line.wizard"
    _description = "Sale Rental Line Wizard"

    rental_line_id = fields.Many2one(
        comodel_name="sale.order.line",
        string="Rental Line",
    )

    rental_type = fields.Selection(
        [("new_rental", "New Rental"), ("rental_extension", "Rental Extension")],
        default="new_rental",
    )
    extension_rental_id = fields.Many2one(
        "sale.rental",
        string="Rental to Extend",
    )
    rental_qty = fields.Float(
        default=1.0,
        digits="Product Unit of Measure",
    )
    sell_rental_id = fields.Many2one(
        "sale.rental",
        string="Rental to Sell",
    )

    start_date = fields.Date()
    end_date = fields.Date()

    def confirm_rental_config(self):
        line = self.rental_line_id
        line.write(
            {
                "rental_type": self.rental_type,
                "extension_rental_id": self.extension_rental_id.id,
                "rental_qty": self.rental_qty,
                "sell_rental_id": self.sell_rental_id.id,
                "start_date": self.start_date,
                "end_date": self.end_date,
            }
        )
        line.product_uom_qty = line.rental_qty * line.number_of_days
