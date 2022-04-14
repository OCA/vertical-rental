# Part of rental-vertical See LICENSE file for full copyright and licensing details.

{
    "name": "Rental Pricelist",
    "summary": "Enables the user to define different rental prices with "
    "time uom (Month, Day and Hour).",
    "version": "14.0.1.0.1",
    "category": "Rental",
    "author": "elego Software Solutions GmbH, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/vertical-rental",
    "depends": [
        "rental_base",
    ],
    "data": [
        "views/sale_view.xml",
        "views/product_view.xml",
        "views/res_company_view.xml",
    ],
    "demo": [],
    "qweb": [],
    "post_init_hook": "set_multi_sales_price",
    "application": False,
    "installable": True,
    "license": "AGPL-3",
}
