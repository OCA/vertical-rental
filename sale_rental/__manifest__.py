# Copyright 2014-2021 Akretion France (http://www.akretion.com)
# @author Alexis de Lattre <alexis.delattre@akretion.com>
# Copyright 2016-2021 Sodexis (http://sodexis.com)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Sale Rental",
    "version": "16.0.1.0.5",
    "category": "Sales",
    "license": "AGPL-3",
    "summary": "Manage Rental of Products",
    "author": "Akretion, Sodexis, Odoo Community Association (OCA)",
    "maintainers": ["alexis-via"],
    "website": "https://github.com/OCA/vertical-rental",
    "depends": ["sale_start_end_dates", "sale_stock", "sales_team"],
    "data": [
        "security/ir.model.access.csv",
        "security/sale_rental_security.xml",
        "data/ir_crons.xml",
        "data/mail_template_data.xml",
        "data/rental_data.xml",
        "data/rental_period.xml",
        "views/stock_warehouse.xml",
        "views/rental_pricing.xml",
        "views/rental_period.xml",
        "views/sale_rental.xml",
        "wizard/create_rental_product_view.xml",
        "views/product.xml",
        "views/res_config_settings_views.xml",
        "views/sale_order.xml",
    ],
    "demo": ["demo/rental_demo.xml"],
    "installable": True,
}
