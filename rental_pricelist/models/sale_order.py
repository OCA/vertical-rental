from odoo import _, models
from odoo.exceptions import UserError


class SaleOrder(models.Model):
    _inherit = "sale.order"

    def _check_rental_order_line(self):
        for order in self:
            for line in order.order_line:
                if line.rental and line.product_id:
                    if line.product_id.type != "service":
                        raise UserError(
                            _("The product %(name)s is not correctly configured.")
                            % {"name": line.product_id.name}
                        )

    def action_confirm(self):
        self._check_rental_order_line()
        return super().action_confirm()
