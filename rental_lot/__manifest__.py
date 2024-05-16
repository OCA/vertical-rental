# Copyright 2023 Akretion (https://www.akretion.com).
# @author Kévin Roche <kevin.roche@akretion.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Rental Lot",
    "summary": "Add the lot number of the rented physical product on a rental",
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
        "stock_restrict_lot",
    ],
    "data": [
        "views/sale_order.xml",
        "views/sale_rental.xml",
    ],
}
