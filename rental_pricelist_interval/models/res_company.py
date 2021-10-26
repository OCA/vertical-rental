# Part of rental-vertical See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    rental_price_interval_rule_ids = fields.One2many(
        "rental.price.interval.rule",
        "company_id",
        string="Rental Interval Price Rules",
    )
    rental_service_name_prefix_interval = fields.Char(
        "Prefix of Rental Service Name (Interval)",
        default="Rental of",
        translate=True,
    )
    rental_service_name_suffix_interval = fields.Char(
        "Suffix of Rental Service Name (Interval)",
        default="(Interval(s))",
        translate=True,
    )
    rental_service_default_code_prefix_interval = fields.Char(
        "Prefix of Rental Service Internal Reference (Interval)",
        default="RENT-I",
    )
    rental_service_default_code_suffix_interval = fields.Char(
        "Suffix of Rental Service Internal Reference (Interval)",
    )


class RentalPriceIntervalRule(models.Model):
    _name = "rental.price.interval.rule"
    _description = "Rental Price Interval Rule"

    name = fields.Char(
        "Name",
    )

    factor = fields.Float(
        "Factor",
    )

    min_quantity = fields.Integer(
        "Interval (days)",
    )

    company_id = fields.Many2one(
        "res.company",
        "Company",
    )
