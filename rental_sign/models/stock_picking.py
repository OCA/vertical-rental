# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError


class StockPicking(models.Model):
    _inherit = "stock.picking"

    is_rental_invoice = fields.Boolean(
        string="Rental Invoice",
        compute="_compute_is_rental_invoice",
        store=True,
        readonly=True,
    )

    delivery_sign_request_id = fields.Many2one(
        "sign.oca.request",
        string="Delivery Sign Request",
        copy=False,
        readonly=True,
    )
    delivery_staff_signed = fields.Boolean(
        compute="_compute_delivery_staff_signed",
        store=True,
        readonly=True,
    )
    delivery_customer_signed = fields.Boolean(
        compute="_compute_delivery_customer_signed",
        store=True,
        readonly=True,
    )

    return_sign_request_id = fields.Many2one(
        "sign.oca.request",
        string="Return Sign Request",
        copy=False,
        readonly=True,
    )
    return_staff_signed = fields.Boolean(
        string="Return Signed",
        compute="_compute_return_staff_signed",
        store=True,
        readonly=True,
    )

    @api.depends("move_ids.sale_line_id.rental", "move_ids.sale_line_id.rental_type")
    def _compute_is_rental_invoice(self):
        for picking in self:
            sale_lines = picking.move_ids.mapped("sale_line_id")
            picking.is_rental_invoice = any(
                line.rental and line.rental_type in ("new_rental", "rental_extension")
                for line in sale_lines
            )

    @api.depends(
        "delivery_sign_request_id.state",
        "delivery_sign_request_id.signer_ids.signed_on",
    )
    def _compute_delivery_staff_signed(self):
        for picking in self:
            picking.delivery_staff_signed = False
            req = picking.delivery_sign_request_id
            if not req:
                continue

            role_employee = picking.env.ref(
                "sign_oca.sign_role_employee", raise_if_not_found=False
            )
            if not role_employee:
                continue

            items = req.signer_ids.filtered(
                lambda r, role=role_employee: r.role_id.id == role.id
            )
            if items and all(i.signed_on for i in items):
                picking.delivery_staff_signed = True

    @api.depends(
        "delivery_sign_request_id.state",
        "delivery_sign_request_id.signer_ids.signed_on",
    )
    def _compute_delivery_customer_signed(self):
        for picking in self:
            picking.delivery_customer_signed = False
            req = picking.delivery_sign_request_id
            if not req:
                continue

            role_customer = picking.env.ref(
                "sign_oca.sign_role_customer", raise_if_not_found=False
            )
            if not role_customer:
                continue

            items = req.signer_ids.filtered(
                lambda r, role=role_customer: r.role_id.id == role.id
            )
            if items and all(i.signed_on for i in items):
                picking.delivery_customer_signed = True

    @api.depends(
        "return_sign_request_id.state",
        "return_sign_request_id.signer_ids.signed_on",
    )
    def _compute_return_staff_signed(self):
        for picking in self:
            picking.return_staff_signed = False
            req = picking.return_sign_request_id
            if not req:
                continue

            role_employee = picking.env.ref(
                "sign_oca.sign_role_employee", raise_if_not_found=False
            )
            if not role_employee:
                continue

            items = req.signer_ids.filtered(
                lambda r, role=role_employee: r.role_id.id == role.id
            )
            if items and all(i.signed_on for i in items):
                picking.return_staff_signed = True

    def _get_employee_partner(self):
        self.ensure_one()
        partner = self.user_id.partner_id or self.env.user.partner_id
        if not partner:
            raise UserError(
                self.env._(
                    "No partner found for the responsible employee on picking %s.",
                    self.name,
                )
            )
        return partner

    def _get_rental_sign_report(self, kind):
        self.ensure_one()

        ICP = self.env["ir.config_parameter"]
        if kind == "delivery":
            report_id = ICP.get_param("rental_sign.delivery_report_id")
        elif kind == "return":
            report_id = ICP.get_param("rental_sign.return_report_id")
        else:
            report_id = False

        if not report_id:
            raise UserError(
                self.env._("No %s report configured in Rental Sign settings.", kind)
            )

        report = self.env["ir.actions.report"].browse(int(report_id))
        if not report or not report.exists():
            raise UserError(
                self.env._("Configured %s report could not be found.", kind)
            )
        return report

    def _get_signature_positions_by_role(self, report):
        self.ensure_one()

        positions = self.env["rental.sign.template.item"].search(
            [
                ("report_id", "=", report.id),
                ("company_id", "=", self.company_id.id),
            ]
        )
        if not positions:
            raise UserError(
                self.env._(
                    "No signature position configuration found for report '%s'.",
                    report.name,
                )
            )

        grouped = {}
        for pos in positions:
            role = pos.role_id
            if not role:
                raise ValidationError(
                    self.env._(
                        "Signature position on report '%(report)s' "
                        "(page %(page)s) has no role.",
                        report=report.name,
                        page=pos.page,
                    )
                )
            grouped.setdefault(role, self.env["rental.sign.template.item"])
            grouped[role] |= pos
        return grouped

    def _generate_template_from_report(self, report):
        self.ensure_one()
        pdf_content, _ = report._render_qweb_pdf(report.report_name, res_ids=self.ids)
        if not pdf_content:
            raise UserError(
                self.env._("Could not generate PDF for picking %s.", self.name)
            )

        filename = f"{report.name} - {self.name}.pdf"

        signature_field = self.env["sign.oca.field"].search(
            [("field_type", "=", "signature")], limit=1
        )
        if not signature_field:
            raise ValidationError(
                self.env._(
                    "No signature field configured in sign_oca "
                    "(field_type='signature')."
                )
            )

        picking_model = self.env["ir.model"]._get("stock.picking")

        template = self.env["sign.oca.template"].create(
            {
                "name": filename,
                "data": base64.b64encode(pdf_content),
                "filename": filename,
                "model_id": picking_model.id if picking_model else False,
            }
        )

        positions_by_role = self._get_signature_positions_by_role(report)

        for role, positions in positions_by_role.items():
            for pos in positions:
                self.env["sign.oca.template.item"].create(
                    {
                        "template_id": template.id,
                        "field_id": signature_field.id,
                        "role_id": role.id,
                        "page": pos.page,
                        "position_x": pos.position_x,
                        "position_y": pos.position_y,
                        "width": pos.width,
                        "height": pos.height,
                        "required": True,
                    }
                )

        return template, positions_by_role

    def _create_sign_request(self, template, signer_lines, subject_prefix):
        self.ensure_one()

        if not signer_lines:
            raise UserError(self.env._("No signers defined for picking %s.", self.name))

        vals = {
            "name": self.env._(
                "%(prefix)s signature for %(name)s",
                prefix=subject_prefix,
                name=self.name,
            ),
            "template_id": template.id,
            "record_ref": f"{self._name},{self.id}",
            "signatory_data": template._get_signatory_data(),
            "data": template.data,
            "signer_ids": signer_lines,
        }

        req = self.env["sign.oca.request"].create(vals)

        req._set_action_log("validate")
        req.state = "0_sent"

        return req

    def _get_or_create_delivery_sign_request(self):
        self.ensure_one()

        if self.picking_type_id.code != "outgoing" or not self.is_rental_invoice:
            raise UserError(self.env._("This action is only for delivery orders."))

        role_employee = self.env.ref(
            "sign_oca.sign_role_employee", raise_if_not_found=False
        )
        role_customer = self.env.ref(
            "sign_oca.sign_role_customer", raise_if_not_found=False
        )

        if not role_employee:
            raise UserError(self.env._("No Sign role found for Employee."))

        req = self.delivery_sign_request_id
        if req and req.state not in ("3_cancel",):
            return req, role_employee, role_customer

        report = self._get_rental_sign_report("delivery")
        template, slots_by_role = self._generate_template_from_report(report)

        signer_lines = []

        if role_employee and role_employee in slots_by_role:
            partner_emp = self._get_employee_partner()
            signer_lines.append(
                (
                    0,
                    0,
                    {
                        "partner_id": partner_emp.id,
                        "role_id": role_employee.id,
                    },
                )
            )

        if role_customer and role_customer in slots_by_role:
            if not self.partner_id:
                raise UserError(
                    self.env._(
                        "Picking %s has no customer to sign the document.", self.name
                    )
                )
            signer_lines.append(
                (
                    0,
                    0,
                    {
                        "partner_id": self.partner_id.id,
                        "role_id": role_customer.id,
                    },
                )
            )

        if not signer_lines:
            raise UserError(
                self.env._(
                    "No signers could be matched for the delivery "
                    "document of picking %s.\n"
                    "Check your signature slot configuration.",
                    self.name,
                )
            )

        req = self._create_sign_request(
            template=template,
            signer_lines=signer_lines,
            subject_prefix=self.env._("Delivery"),
        )
        self.delivery_sign_request_id = req

        return req, role_employee, role_customer

    def action_customer_sign_delivery(self):
        self.ensure_one()

        if self.delivery_customer_signed:
            raise UserError(
                self.env._(
                    "The delivery order %s has already been signed by the customer.",
                    self.name,
                )
            )

        req, _, role_customer = self._get_or_create_delivery_sign_request()

        if not role_customer:
            raise UserError(self.env._("No Sign role found for Customer."))

        signer = req.signer_ids.filtered(
            lambda s, rc=role_customer: s.role_id.id == rc.id
        )[:1]
        if not signer:
            raise UserError(self.env._("No customer signer found on this request."))

        return {
            "type": "ir.actions.act_url",
            "url": signer.access_url,
            "target": "new",
        }

    def action_staff_sign_delivery(self):
        self.ensure_one()

        if self.delivery_customer_signed:
            raise UserError(
                self.env._(
                    "The delivery order %s has already been signed by the customer.",
                    self.name,
                )
            )

        req, role_employee, _ = self._get_or_create_delivery_sign_request()

        if not role_employee:
            raise UserError(self.env._("No Sign role found for Staff."))

        signer = req.signer_ids.filtered(
            lambda s, rc=role_employee: s.role_id.id == rc.id
        )[:1]
        if not signer:
            raise UserError(self.env._("No staff signer found on this request."))

        return {
            "type": "ir.actions.act_url",
            "url": signer.access_url,
            "target": "new",
        }

    def action_staff_sign_receipt(self):
        self.ensure_one()

        if self.picking_type_id.code != "incoming" or not self.is_rental_invoice:
            raise UserError(
                self.env._("This action is only for rental receipt orders.")
            )

        role_employee = self.env.ref(
            "sign_oca.sign_role_employee", raise_if_not_found=False
        )
        if not role_employee:
            raise UserError(self.env._("No Sign role found for Employee."))

        if self.return_sign_request_id and self.return_sign_request_id.state not in (
            "3_cancel",
        ):
            return self.return_sign_request_id.sign()

        report = self._get_rental_sign_report("return")

        template, slots_by_role = self._generate_template_from_report(report)

        if role_employee not in slots_by_role:
            raise UserError(
                self.env._(
                    "No signature slot configured for Employee on the return report "
                    "'%s'.",
                    report.name,
                )
            )

        partner_emp = self._get_employee_partner()
        signer_lines = [
            (
                0,
                0,
                {
                    "partner_id": partner_emp.id,
                    "role_id": role_employee.id,
                },
            )
        ]

        req = self._create_sign_request(
            template=template,
            signer_lines=signer_lines,
            subject_prefix=self.env._("Return receipt"),
        )
        self.return_sign_request_id = req

        return req.sign()

    def button_validate(self):
        for picking in self:
            if picking.picking_type_id.code == "outgoing" and picking.is_rental_invoice:
                if not picking.delivery_staff_signed:
                    raise UserError(
                        self.env._(
                            "The delivery order %s must be signed by the delivery "
                            "staff before validation.",
                            picking.name,
                        )
                    )

            if picking.picking_type_id.code == "incoming" and picking.is_rental_invoice:
                if not picking.return_staff_signed:
                    raise UserError(
                        self.env._(
                            "The receipt %s must be signed by the staff "
                            "before validation.",
                            picking.name,
                        )
                    )

        return super().button_validate()
