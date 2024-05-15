# Copyright 2023 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>

{
    "name": "Rental Variant",
    "version": "16.0.1.0.0",
    "category": "Rental",
    "website": "https://github.com/OCA/vertical-rental",
    "author": "Akretion, Odoo Community Association (OCA), , Groupe Voltaire SAS",
    "maintainers": ["Kev-Roche"],
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": [
        "sale_rental",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/data.xml",
        "views/product_template.xml",
        "views/sale_order.xml",
        "wizard/sale_rental_wizard.xml",
    ],
}
