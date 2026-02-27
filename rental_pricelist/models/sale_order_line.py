from odoo import _, api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_compare


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    number_of_time_unit = fields.Float(
        string="Number of TU",
        help="This is the time difference given by "
        "start and end date for this order line.",
    )

    display_product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        domain=lambda self: self._get_product_domain(),
    )

    rental_ok = fields.Boolean(
        string="Can be rented",
        related="display_product_id.rental",
    )

    @api.model_create_multi
    def create(self, vals_list):
        lines = super().create(vals_list)
        for line in lines:
            if (
                line.product_uom_qty > 0
                and line.order_id.type_id.id
                == self.env.ref("rental_base.rental_sale_type").id
                and line.rental_qty == 0
            ):
                line.rental_qty = line.product_uom_qty
        return lines

    @api.model
    def _get_product_domain(self):
        domain = [
            "|",
            "&",
            ("type", "=", "product"),
            "|",
            ("sale_ok", "=", True),
            ("rental", "=", True),
            "&",
            ("type", "=", "service"),
            "&",
            ("sale_ok", "=", True),
            ("rental", "=", False),
        ]
        return domain

    def _set_product_id(self):
        self.ensure_one()
        if self.rental and self.display_product_id:
            time_uoms = self._get_time_uom()
            if self.display_product_id.rental_of_day:
                self.product_uom = time_uoms["day"]
                self.product_id = self.display_product_id.product_rental_day_id
            elif self.display_product_id.rental_of_month:
                self.product_uom = time_uoms["month"]
                self.product_id = self.display_product_id.product_rental_month_id
            elif self.display_product_id.rental_of_hour:
                self.product_uom = time_uoms["hour"]
                self.product_id = self.display_product_id.product_rental_hour_id
            else:
                self.rental = False
                self.product_id = self.display_product_id
        elif not self.rental and self.display_product_id:
            self.product_id = self.display_product_id

    @api.onchange("display_product_id")
    def onchange_display_product_id(self):
        if self.display_product_id:
            self.product_id = self.display_product_id
            if self.display_product_id.rental:
                self.rental = True
            self.rental = False
            self.can_sell_rental = False
        rental_type_id = self.env.ref("rental_base.rental_sale_type").id
        if self.env.context.get("type_id", False) == rental_type_id:
            self.rental = True
        self._set_product_id()

    @api.onchange("rental")
    def onchange_rental(self):
        if self.rental:
            self.can_sell_rental = False
            self.sell_rental_id = False
            rental_type_id = self.env.ref("rental_base.rental_sale_type").id
            if self.env.context.get("type_id", False) == rental_type_id:
                self.rental_qty = 1
        else:
            self.rental_type = False
            self.rental_qty = 0
            self.extension_rental_id = False
        self._set_product_id()

    @api.onchange("can_sell_rental")
    def onchange_can_sell_rental(self):
        if self.can_sell_rental:
            self.rental = False
            self.rental_type = False
            self.rental_qty = 0
            self.extension_rental_id = False
            self.product_id = self.display_product_id
        else:
            self.sell_rental_id = False
            self._set_product_id()

    def _check_rental_availability(self):
        res = {}
        self.ensure_one()
        product_uom = self.product_id.rented_product_id.uom_id
        warehouse = self.order_id.warehouse_id
        rental_in_location = warehouse.rental_in_location_id
        rented_product_ctx = self.with_context(
            location=rental_in_location.id
        ).product_id.rented_product_id
        in_location_available_qty = (
            rented_product_ctx.qty_available - rented_product_ctx.outgoing_qty
        )
        compare_qty = float_compare(
            in_location_available_qty,
            self.rental_qty,
            precision_rounding=product_uom.rounding,
        )
        if compare_qty == -1:
            rental_uom_name = self.product_id.rented_product_id.uom_id.name
            res["warning"] = {
                "title": _("Not enough stock!"),
                "message": _(
                    f"You want to rent {self.rental_qty}.2f {rental_uom_name} "
                    f"but you only "
                    f"have {in_location_available_qty}.2f "
                    f"{rental_uom_name} currently available "
                    "on the "
                    f'stock location "{rental_in_location.name}"! Make sure that you '
                    "get some units back in the meantime or "
                    f're-supply the stock location "{rental_in_location.name}".'
                ),
            }
        return res

    # Override function in rental_sale
    @api.onchange("product_id", "rental_qty")
    def rental_product_id_change(self):
        res = {}
        if self.product_id:
            if self.product_id.rented_product_id:
                self.sell_rental_id = False
                if not self.rental_type:
                    self.rental_type = "new_rental"
                elif (
                    self.rental_type == "new_rental"
                    and self.rental_qty
                    and self.order_id.warehouse_id
                ):
                    avail = self._check_rental_availability()
                    if avail.get("warning", False):
                        res["warning"] = avail["warning"]
            elif self.product_id.rental_service_ids:
                self.rental_type = False
                self.rental_qty = 0
                self.extension_rental_id = False
            else:
                self.rental_type = False
                self.rental_qty = 0
                self.extension_rental_id = False
                self.sell_rental_id = False
        else:
            self.rental_type = False
            self.rental_qty = 0
            self.extension_rental_id = False
            self.sell_rental_id = False
        return res

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
                        _(
                            'Missing "Rental to Extend" on the sale order line '
                            "with rental service %(name)s."
                        )
                        % {"name": line.product_id.name}
                    )

                if line.rental_qty != line.extension_rental_id.rental_qty:
                    raise ValidationError(
                        _(
                            "On the sale order line with rental service %(name)s, "
                            "you are trying to extend a rental with a rental "
                            "quantity (%(rental_qty)s) that is different from "
                            "the quantity of the original rental "
                            "(%(ext_rental_qty)s). This is not supported."
                        )
                        % {
                            "name": line.product_id.name,
                            "rental_qty": line.rental_qty,
                            "ext_rental_qty": line.extension_rental_id.rental_qty,
                        }
                    )
            if line.rental_type in ("new_rental", "rental_extension"):
                if not line.product_id.rented_product_id:
                    raise ValidationError(
                        _(
                            'On the "new rental" sale order line with product '
                            '"%(name)s", we should have a rental service product!'
                        )
                        % {"name": line.product_id.name}
                    )
            elif line.sell_rental_id:
                if line.product_uom_qty != line.sell_rental_id.rental_qty:
                    raise ValidationError(
                        _(
                            "On the sale order line with product %(name)s "
                            "you are trying to sell a rented product with a "
                            "quantity (%(qty)s) that is different from the rented "
                            "quantity (%(rental_qty)s). This is not supported."
                        )
                        % {
                            "name": line.product_id.name,
                            "qty": line.product_uom_qty,
                            "rental_qty": line.sell_rental_id.rental_qty,
                        }
                    )

    @api.onchange("rental_qty", "number_of_time_unit", "product_id")
    def rental_qty_number_of_days_change(self):
        if self.product_id.rented_product_id:
            qty = self.rental_qty * self.number_of_time_unit
            self.product_uom_qty = qty

    def _get_product_rental_uom_ids(self):
        self.ensure_one()
        time_uoms = self._get_time_uom()
        uom_ids = []
        if self.display_product_id.rental_of_month:
            uom_ids.append(time_uoms["month"].id)
        if self.display_product_id.rental_of_day:
            uom_ids.append(time_uoms["day"].id)
        if self.display_product_id.rental_of_hour:
            uom_ids.append(time_uoms["hour"].id)
        return uom_ids

    @api.onchange("product_id")
    def _onchange_product_id(self):
        for line in self:
            if line.rental:
                if line.display_product_id.rental:
                    uom_ids = line._get_product_rental_uom_ids()
                    if line.product_uom.id not in uom_ids:
                        line.product_uom = uom_ids and uom_ids[0] or False

    @api.onchange("product_uom", "product_uom_qty")
    def _onchange_product_uom(self):
        for line in self:
            if line.rental and line.display_product_id:
                if line.product_uom.id != line.product_id.uom_id.id:
                    time_uoms = line._get_time_uom()
                    key = list(
                        filter(
                            lambda key: time_uoms[key].id == line.product_uom.id,
                            time_uoms.keys(),
                        )
                    )[-1]
                    line.product_id = line.display_product_id._get_rental_service(key)

    @api.onchange("start_date", "end_date", "product_uom")
    def _onchange_start_end_date(self):
        if self.start_date and self.end_date:
            number = self._get_number_of_time_unit()
            self.number_of_time_unit = number
