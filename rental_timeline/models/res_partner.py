# Part of rental-vertical See LICENSE file for full copyright and licensing details.

from odoo import api, models


class ResPartner(models.Model):
    _inherit = "res.partner"

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        address_fields = self._address_fields()
        address_fields.append("name")
        if any(field in vals for field in address_fields):
            keys = set(self.env["product.timeline"]._get_partner_fields())
            domain = [(field, "in", self.ids) for field in keys]
            i = 1
            while i < len(keys):
                domain.insert(0, "|")
                i += 1
            timelines = self.env["product.timeline"].search(domain)
            timelines._compute_fields()
        return res
