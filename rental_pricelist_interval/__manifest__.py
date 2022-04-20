# Part of rental-vertical See LICENSE file for full copyright and licensing details.

{
    "name": "Rental Pricelist (Interval)",
    "summary": "Enables the user to define different rental prices "
    "time uom (Month, Day and Hour).",
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
        "security/ir.model.access.csv",
        "data/product_uom_data.xml",
        "data/product_pricelist_data.xml",
        "views/product_pricelist_view.xml",
        "views/product_view.xml",
        "views/res_company_view.xml",
    ],
    "demo": [],
    "qweb": [],
    "post_init_hook": "set_product_def_interval_pricelist_id",
    "application": False,
    "installable": True,
    "license": "AGPL-3",
}
