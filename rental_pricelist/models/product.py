# Part of rental-vertical See LICENSE file for full copyright and licensing details.

from odoo import _, api, exceptions, fields, models
from odoo.exceptions import ValidationError


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _default_pricelist(self):
        # TODO change default pricelist if country group exist
        return self.env.ref("product.list0").id

    rental_of_month = fields.Boolean(
        string="Rented in months",
        copy=False,
    )

    rental_of_day = fields.Boolean(
        string="Rented in days",
        copy=False,
    )

    rental_of_hour = fields.Boolean(
        string="Rented in hours",
        copy=False,
    )

    product_rental_month_id = fields.Many2one(
        comodel_name="product.product",
        string="Rental Service (Month)",
        ondelete="set null",
        copy=False,
    )

    product_rental_day_id = fields.Many2one(
        comodel_name="product.product",
        string="Rental Service (Day)",
        ondelete="set null",
        copy=False,
    )

    product_rental_hour_id = fields.Many2one(
        comodel_name="product.product",
        string="Rental Service (Hour)",
        ondelete="set null",
        copy=False,
    )

    rental_price_month = fields.Float(
        string="Price / Month",
        store=True,
        copy=False,
        readonly=False,
        related="product_rental_month_id.list_price",
    )

    rental_price_day = fields.Float(
        string="Price / Day",
        store=True,
        copy=False,
        readonly=False,
        related="product_rental_day_id.list_price",
    )

    rental_price_hour = fields.Float(
        string="Price / Hour",
        store=True,
        copy=False,
        readonly=False,
        related="product_rental_hour_id.list_price",
    )

    day_scale_pricelist_item_ids = fields.One2many(
        comodel_name="product.pricelist.item",
        inverse_name="day_item_id",
        string="Day Scale Pricelist Items",
        copy=False,
    )

    month_scale_pricelist_item_ids = fields.One2many(
        comodel_name="product.pricelist.item",
        inverse_name="month_item_id",
        string="Month Scale Pricelist Items",
        copy=False,
    )

    hour_scale_pricelist_item_ids = fields.One2many(
        comodel_name="product.pricelist.item",
        inverse_name="hour_item_id",
        string="Hour Scale Pricelist Items",
        copy=False,
    )

    def_pricelist_id = fields.Many2one(
        comodel_name="product.pricelist",
        string="Default Pricelist",
        default=lambda self: self._default_pricelist(),
    )

    # override from sale_rental, to remove Uom constrain
    @api.constrains("rented_product_id", "must_have_dates", "type", "uom_id")
    def _check_rental(self):
        self.env.ref("uom.product_uom_day")
        for product in self:
            if product.rented_product_id:
                if product.type != "service":
                    raise ValidationError(
                        _("The rental product '%s' must be of type 'Service'.")
                        % product.name
                    )
                if not product.must_have_dates:
                    raise ValidationError(
                        _(
                            "The rental product '%s' must have the option "
                            "'Must Have Start and End Dates' checked."
                        )
                        % product.name
                    )

    @api.model
    def _get_rental_service_prefix_suffix(self, field, str_type, rental_type):
        field_name = "rental_service_%s_%s_%s" % (field, str_type, rental_type)
        res = getattr(self.env.user.company_id, field_name)
        return res

    def _get_rental_service(self, rental_type):
        self.ensure_one()
        if rental_type == "month" and self.product_rental_month_id:
            return self.product_rental_month_id
        elif rental_type == "day" and self.product_rental_day_id:
            return self.product_rental_day_id
        elif rental_type == "hour" and self.product_rental_hour_id:
            return self.product_rental_hour_id
        else:
            raise exceptions.ValidationError(
                _("The product has no related rental services.")
            )

    def _get_rental_service_list(self):
        self.ensure_one()
        rental_services = []
        if self.product_rental_month_id:
            rental_services.append(self.product_rental_month_id)
        if self.product_rental_day_id:
            rental_services.append(self.product_rental_day_id)
        if self.product_rental_hour_id:
            rental_services.append(self.product_rental_hour_id)
        return rental_services

    @api.model
    def _get_rental_service_uom(self, rental_type):
        time_uoms = self.env["sale.order.line"]._get_time_uom()
        uom = False
        if rental_type == "month":
            uom = time_uoms["month"]
        elif rental_type == "day":
            uom = time_uoms["day"]
        elif rental_type == "hour":
            uom = time_uoms["hour"]
        else:
            raise exceptions.ValidationError(
                _("No expected rental type (rental unit of measure) is found.")
            )
        return uom

    @api.model
    def _get_rental_service_type(self, uom):
        time_uoms = self.env["sale.order.line"]._get_time_uom()
        rental_type = False
        for key, val in time_uoms.items():
            if uom.id == val.id:
                rental_type = key
        if not rental_type:
            raise exceptions.ValidationError(
                _("No expected rental type (rental unit of measure) is found.")
            )
        return rental_type

    def _get_rental_service_name(self, rental_type, sp_name):
        self.ensure_one()
        prefix = self._get_rental_service_prefix_suffix("name", "prefix", rental_type)
        suffix = self._get_rental_service_prefix_suffix("name", "suffix", rental_type)
        name = sp_name
        if prefix:
            name = "%s %s" % (prefix, name)
        if suffix:
            name = "%s %s" % (name, suffix)
        return name

    def _get_rental_service_default_code(self, rental_type, sp_code):
        self.ensure_one()
        prefix = self._get_rental_service_prefix_suffix(
            "default_code", "prefix", rental_type
        )
        suffix = self._get_rental_service_prefix_suffix(
            "default_code", "suffix", rental_type
        )
        default_code = sp_code
        if default_code:
            if prefix:
                default_code = "%s-%s" % (prefix, default_code)
            if suffix:
                default_code = "%s-%s" % (default_code, suffix)
        else:
            default_code = ""
        return default_code

    @api.model
    def _create_rental_service(self, rental_type, product, price=0):
        uom = self._get_rental_service_uom(rental_type)
        values = {
            "hw_product_id": product.id,
            "name": _("Rental of %s (%s)") % (product.name, uom.name),
            "categ_id": product.categ_id.id,
            "copy_image": True,
            "default_code": "RENT-%s-%s" % (rental_type.upper(), product.default_code),
        }
        res = (
            self.env["create.rental.product"]
            .with_context(active_model="product.product", active_id=product.id)
            .create(values)
            .create_rental_product()
        )
        rental_service = self.browse(res["res_id"])
        name = rental_service._get_rental_service_name(
            rental_type,
            product.name,
        )
        default_code = rental_service._get_rental_service_default_code(
            rental_type,
            product.default_code,
        )
        rental_service.sudo().uom_id = uom.id
        rental_service.sudo().uom_po_id = uom.id
        rental_service.write(
            {
                "uom_id": uom.id,
                "uom_po_id": uom.id,
                "rental": True,
                "income_analytic_account_id": product.income_analytic_account_id.id,
                "expense_analytic_account_id": product.expense_analytic_account_id.id,
                "list_price": price,
                "name": name,
                "default_code": default_code,
            }
        )
        return rental_service

    def _update_rental_service_analytic_account(self, vals):
        self.ensure_one()
        analytic_vals = {}
        if "income_analytic_account_id" in vals:
            analytic_vals["income_analytic_account_id"] = vals.get(
                "income_analytic_account_id", False
            )
        if "expense_analytic_account_id" in vals:
            analytic_vals["expense_analytic_account_id"] = vals.get(
                "expense_analytic_account_id", False
            )
        self.rental_service_ids.write(analytic_vals)

    def _update_rental_service_default_code(self, vals):
        self.ensure_one()
        if "default_code" in vals:
            default_code = vals.get("default_code", False)
            for rental_service in self.rental_service_ids:
                rental_type = self._get_rental_service_type(rental_service.uom_id)
                rental_service_dc = rental_service._get_rental_service_default_code(
                    rental_type,
                    default_code,
                )
                rental_service.default_code = rental_service_dc

    def _update_rental_service_name(self, vals):
        self.ensure_one()
        if "name" in vals:
            name = vals.get("name", False)
            for rental_service in self.rental_service_ids:
                rental_type = self._get_rental_service_type(rental_service.uom_id)
                service_name = rental_service._get_rental_service_name(
                    rental_type,
                    name,
                )
                rental_service.name = service_name

    def _update_rental_service_fields(self, vals, fields, rental_services):
        self.ensure_one()
        service_vals = {}
        for field in fields:
            if field in vals:
                service_vals[field] = vals.get(field, False)
        # check 'active' becomes True from False
        check_rental_services = (
            service_vals.get("active", False)
            and not self.rental_service_ids
            and rental_services
        )
        if check_rental_services:
            for p in rental_services:
                p.write(service_vals)
        self.rental_service_ids.write(service_vals)

    def write(self, vals):
        res = super(ProductProduct, self).write(vals)
        for p in self:
            # Create service product automatically
            if vals.get("rental_of_month", False):
                if not p.product_rental_month_id:
                    service_product = self._create_rental_service(
                        "month", p, p.rental_price_month
                    )
                    p.product_rental_month_id = service_product
            if vals.get("rental_of_day", False):
                if not p.product_rental_day_id:
                    service_product = self._create_rental_service(
                        "day", p, p.rental_price_day
                    )
                    p.product_rental_day_id = service_product
            if vals.get("rental_of_hour", False):
                if not p.product_rental_hour_id:
                    service_product = self._create_rental_service(
                        "hour", p, p.rental_price_hour
                    )
                    p.product_rental_hour_id = service_product
            # update analytic account for service product
            if (
                "income_analytic_account_id" in vals
                or "expense_analytic_account_id" in vals
            ):
                p._update_rental_service_analytic_account(vals)
            # update defaul_code of related rental services
            if vals.get("default_code", False) and p.rental_service_ids:
                p._update_rental_service_default_code(vals)
            # update name for service product
            if vals.get("name", False) and p.rental_service_ids:
                p._update_rental_service_name(vals)
            # update image and description for service product
            update_fields = [
                "image_medium",
                "description_sale",
                "categ_id",
                "rental",
                "active",
            ]
            # when 'active' set to True from False,
            # then 'rental_service_ids' set to Null,
            # need to find rental service products from main product
            rental_services = []
            if vals.get("active", False):
                rental_services = p._get_rental_service_list()
            if (vals.keys() & update_fields) and (
                p.rental_service_ids or rental_services
            ):
                p._update_rental_service_fields(vals, update_fields, rental_services)
        return res

    @api.model_create_multi
    def create(self, vals_list):
        ext_vals = {}
        for vals in vals_list:
            if vals.get("rental_of_month", False):
                ext_vals["rental_of_month"] = True
                ext_vals["rental_price_month"] = vals.get("rental_price_month")
                del vals["rental_of_month"]
                if "rental_price_month" in vals:
                    del vals["rental_price_month"]
            if vals.get("rental_of_day", False):
                ext_vals["rental_of_day"] = True
                ext_vals["rental_price_day"] = vals.get("rental_price_day")
                del vals["rental_of_day"]
                if "rental_price_day" in vals:
                    del vals["rental_price_day"]
            if vals.get("rental_of_hour", False):
                ext_vals["rental_of_hour"] = True
                ext_vals["rental_price_hour"] = vals.get("rental_price_hour")
                del vals["rental_of_hour"]
                if "rental_price_hour" in vals:
                    del vals["rental_price_hour"]
        res = super().create(vals_list)
        for vals in vals_list:
            if "income_analytic_account_id" in vals:
                ext_vals["income_analytic_account_id"] = vals.get(
                    "income_analytic_account_id", False
                )
            else:
                ext_vals[
                    "income_analytic_account_id"
                ] = res.income_analytic_account_id.id
            if "expense_analytic_account_id" in vals:
                ext_vals["expense_analytic_account_id"] = vals.get(
                    "expense_analytic_account_id", False
                )
            else:
                ext_vals[
                    "expense_analytic_account_id"
                ] = res.expense_analytic_account_id.id
        res.write(ext_vals)
        return res
