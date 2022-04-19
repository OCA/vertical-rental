# Part of rental-vertical See LICENSE file for full copyright and licensing details.

{
    "name": "Rental Product Pack",
    "version": "14.0.1.0.1",
    "category": "Rental",
    "summary": "Manage rentals with product packs",
    "author": "elego Software Solutions GmbH, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/vertical-rental",
    "depends": [
        "rental_base",
        "product_pack",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/product_view.xml",
        "views/product_pack_line_view.xml",
    ],
    "demo": [],
    "qweb": [],
    "application": False,
    "installable": True,
    "license": "AGPL-3",
}
