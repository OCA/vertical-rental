# Copyright 2025 Kencove (https://www.kencove.com/)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Rental sign (OCA)",
    "version": "16.0.1.0.0",
    "category": "Sales",
    "license": "AGPL-3",
    "author": "Kencove, Trobz, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/vertical-rental",
    "depends": ["sale_rental", "sign_oca"],
    "data": [
        "security/ir.model.access.csv",
        "views/rental_sign_template_item.xml",
        "views/res_config_settings_views.xml",
        "views/stock_picking_views.xml",
    ],
    "demo": [
        "demo/rental_sign_demo.xml",
    ],
    "installable": True,
}
