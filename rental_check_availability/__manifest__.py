# Part of rental-vertical See LICENSE file for full copyright and licensing details.

{
    "name": "Rental Check Availability",
    "summary": "Extends the sale_rental module for checking availability"
    "of the rented product.",
    "version": "14.0.1.0.0",
    "category": "Rental",
    "author": "elego Software Solutions GmbH, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/vertical-rental",
    "contributors": [
        "Ben Brich <b.brich@humanilog.org> (www.humanilog.org)",
        "Yu Weng <yweng@elegosoft.com> (www.elegosoft.com)",
    ],
    "depends": [
        "rental_pricelist",
    ],
    "data": [
        "views/sale_view.xml",
    ],
    "demo": [],
    "qweb": [],
    "application": False,
    "installable": True,
    "license": "AGPL-3",
}
