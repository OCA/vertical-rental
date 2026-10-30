# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SaleRental(models.Model):
    _inherit = "sale.rental"

    def _get_contract_lines(self):
        self.ensure_one()
        order_lines = self.start_order_line_id | self.extension_order_line_ids
        return self.env["contract.line"].search(
            [("sale_order_line_id", "in", order_lines.ids)]
        )

    def _stop_rental_contract(self, date_end):
        """End the rent on date_end (product returned or sold): contract lines
        go on until the last invoiced day; extensions not started yet and not
        invoiced are cancelled."""
        for rental in self:
            for line in rental._get_contract_lines():
                stop_date = max(date_end, line.last_date_invoiced or date_end)
                if line.date_start > stop_date:
                    if not line.last_date_invoiced and not line.is_canceled:
                        line.cancel()
                elif not line.date_end or line.date_end > stop_date:
                    line.stop(stop_date)
