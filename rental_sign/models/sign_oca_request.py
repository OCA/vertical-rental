# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class SignOcaRequest(models.Model):
    _inherit = "sign.oca.request"

    def _attach_signed_pdf_to_record_ref(self):
        self.ensure_one()

        if not self.record_ref or not self.data:
            return

        record = self.record_ref
        if not record or not record.exists():
            return

        if record._name != "stock.picking":
            return

        filename = self.filename or (self.name + ".pdf")

        attachment_vals = {
            "name": filename,
            "datas": self.data,
            "res_model": record._name,
            "res_id": record.id,
            "type": "binary",
            "mimetype": "application/pdf",
        }
        picking_attachment = self.env["ir.attachment"].create(attachment_vals)

        if hasattr(record, "message_post"):
            record.message_post(
                body=self.env._(
                    "Signed document from signature request <b>%s</b> "
                    "has been attached.",
                    self.name,
                ),
                attachment_ids=[picking_attachment.id],
            )

        sale_lines = record.move_ids.mapped("sale_line_id")
        rentals = self.env["sale.rental"].search(
            [("start_order_line_id", "in", sale_lines.ids)]
        )

        for rental in rentals:
            rental_attachment = self.env["ir.attachment"].create(
                {
                    "name": filename,
                    "datas": self.data,
                    "res_model": rental._name,
                    "res_id": rental.id,
                    "type": "binary",
                    "mimetype": "application/pdf",
                }
            )
            if hasattr(rental, "message_post"):
                rental.message_post(
                    body=self.env._(
                        "Signed document from signature request <b>%s</b> "
                        "has been attached (via picking %s).",
                        self.name,
                        record.name,
                    ),
                    attachment_ids=[rental_attachment.id],
                )

    def _check_signed(self):
        res = super()._check_signed()
        for req in self:
            if req.state == "2_signed":
                req._attach_signed_pdf_to_record_ref()
        return res
