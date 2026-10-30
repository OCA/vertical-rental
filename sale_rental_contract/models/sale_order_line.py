# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from dateutil.relativedelta import relativedelta

from odoo import api, models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _is_rental_contract_line(self):
        """New rental of a rental service that is also a contract product:
        sale_rental moves the goods, the contract invoices the rent."""
        self.ensure_one()
        return bool(
            self.rental_type in ("new_rental", "rental_extension")
            and self.product_id.rented_product_id
            and self.product_id.is_contract
            and self.start_date
            and self.end_date
        )

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        for line in lines:
            # a rental extension continues the contract of the extended rental
            if (
                line.rental_type == "rental_extension"
                and line.extension_rental_id
                and not line.contract_id
            ):
                origin = line.extension_rental_id.start_order_line_id
                if origin.contract_id:
                    line.contract_id = origin.contract_id
        return lines

    def create_contract_line(self, contract):
        contract_lines = super().create_contract_line(contract)
        for line in self.filtered(
            lambda sol: sol.rental_type == "rental_extension"
            and sol.extension_rental_id
        ):
            new = contract_lines.filtered(
                lambda cl, sol=line: cl.sale_order_line_id == sol
            )
            previous = line.extension_rental_id._get_contract_lines() - new
            previous = previous.filtered(lambda cl: not cl.successor_contract_line_id)
            if new and previous:
                last = previous.sorted("date_start")[-1:]
                last.successor_contract_line_id = new
                new.predecessor_contract_line_id = last
        return contract_lines

    def _action_launch_stock_rule(self, previous_product_uom_qty=False):
        res = super()._action_launch_stock_rule(
            previous_product_uom_qty=previous_product_uom_qty
        )
        # selling the rented product ends the rent
        for line in self.filtered("sell_rental_id"):
            line.sell_rental_id._stop_rental_contract(line.order_id.date_order.date())
        return res

    def _get_rental_contract_months(self):
        self.ensure_one()
        delta = relativedelta(self.end_date + relativedelta(days=1), self.start_date)
        months = delta.years * 12 + delta.months + (1 if delta.days else 0)
        return max(months, 1)

    def _get_rental_contract_price(self):
        self.ensure_one()
        price = self.product_id.rental_contract_price
        if not price:
            # the rental line is priced by day: spread its amount over months
            price = (
                self.price_unit
                * self.number_of_days
                / self._get_rental_contract_months()
            )
        return price

    def _get_contract_line_qty(self):
        if self._is_rental_contract_line():
            return self.rental_qty
        return super()._get_contract_line_qty()

    def _prepare_contract_line_values(
        self, contract, predecessor_contract_line_id=False
    ):
        values = super()._prepare_contract_line_values(
            contract, predecessor_contract_line_id
        )
        if self._is_rental_contract_line():
            values.update(
                {
                    "quantity": self.rental_qty,
                    "uom_id": self.env.ref("sale_rental_contract.product_uom_month").id,
                    "price_unit": self._get_rental_contract_price(),
                    "date_start": self.start_date,
                    "date_end": self.end_date,
                    "recurring_next_date": self.env[
                        "contract.line"
                    ]._compute_first_recurring_next_date(
                        self.start_date,
                        values["recurring_invoicing_type"],
                        values["recurring_rule_type"],
                        1,
                    ),
                }
            )
        return values
