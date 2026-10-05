# Part of rental-vertical See LICENSE file for full copyright and licensing details.
from odoo import fields, models


class ResCompany(models.Model):
    _inherit = "res.company"

    rental_service_name_prefix_day = fields.Char(
        string="Prefix of Rental Service Name (Day)",
        default="Rental of",
        help="Define the name of the daily rental service "
        "by setting a prefix. The entire name is built "
        "by adding the prefix, the product's name and "
        "the suffix.",
        translate=True,
    )

    rental_service_name_prefix_month = fields.Char(
        string="Prefix of Rental Service Name (Month)",
        default="Rental of",
        help="Define the name of the monthly rental service "
        "by setting a prefix. The entire name is built "
        "by adding the prefix, the product's name and "
        "the suffix.",
        translate=True,
    )

    rental_service_name_prefix_hour = fields.Char(
        string="Prefix of Rental Service Name (Hour)",
        default="Rental of",
        help="Define the name of the hourly rental service "
        "by setting a prefix. The entire name is built "
        "by adding the prefix, the product's name and "
        "the suffix.",
        translate=True,
    )

    rental_service_name_suffix_day = fields.Char(
        string="Suffix of Rental Service Name (Day)",
        default="(Day(s))",
        help="Define the name of the daily rental service "
        "by setting a suffix. The entire name is built "
        "by adding the prefix, the product's name and "
        "the suffix.",
        translate=True,
    )

    rental_service_name_suffix_month = fields.Char(
        string="Suffix of Rental Service Name (Month)",
        default="(Month(s))",
        help="Define the name of the monthly rental service "
        "by setting a suffix. The entire name is built "
        "by adding the prefix, the product's name and "
        "the suffix.",
        translate=True,
    )

    rental_service_name_suffix_hour = fields.Char(
        string="Suffix of Rental Service Name (Hour)",
        default="(Hour(s))",
        help="Define the name of the hourly rental service "
        "by setting a suffix. The entire name is built "
        "by adding the prefix, the product's name and "
        "the suffix.",
        translate=True,
    )

    rental_service_default_code_prefix_day = fields.Char(
        string="Prefix of Rental Service Internal Reference (Day)",
        default="RENT-D",
        help="Define the default code of the daily rental "
        "service by setting a prefix code. The entire "
        "default code is built by adding the prefix code, "
        "the product's default code and the suffix code.",
    )

    rental_service_default_code_prefix_month = fields.Char(
        string="Prefix of Rental Service Internal Reference (Month)",
        default="RENT-M",
        help="Define the default code of the monthly rental "
        "service by setting a prefix code. The entire "
        "default code is built by adding the prefix code, "
        "the product's default code and the suffix code.",
    )

    rental_service_default_code_prefix_hour = fields.Char(
        string="Prefix of Rental Service Internal Reference (Hour)",
        default="RENT-H",
        help="Define the default code of the hourly rental "
        "service by setting a prefix code. The entire "
        "default code is built by adding the prefix code, "
        "the product's default code and the suffix code.",
    )

    rental_service_default_code_suffix_day = fields.Char(
        string="Suffix of Rental Service Internal Reference (Day)",
        help="Define the default code of the daily rental "
        "service by setting a suffix code. The entire "
        "default code is built by adding the prefix code, "
        "the product's default code and the suffix code.",
    )

    rental_service_default_code_suffix_month = fields.Char(
        string="Suffix of Rental Service Internal Reference (Month)",
        help="Define the default code of the monthly rental "
        "service by setting a suffix code. The entire "
        "default code is built by adding the prefix code, "
        "the product's default code and the suffix code.",
    )

    rental_service_default_code_suffix_hour = fields.Char(
        string="Suffix of Rental Service Internal Reference (Hour)",
        help="Define the default code of the hourly rental "
        "service by setting a suffix code. The entire "
        "default code is built by adding the prefix code, "
        "the product's default code and the suffix code.",
    )
