# Part of rental-vertical See LICENSE file for full copyright and licensing details.

{
    "name": "Rental Base",
    "version": "12.0.1.0.1",
    "category": "Rental",
    "summary": "Manage Rental of Products",
    "description": """Base Module for Rental Management

This module provides a new menu for rental management.
It is based on the sale_rental module that currently can be found in sale-workflow repository.
""",
    "usage": """
Create a rentable product and its rental service.
 * Go to Rentals > Configuration > Settings.
 * Please activate the checkbox for using 'Product Variants'.
 * Go to Rentals > Products > Products.
 * Create a new storable product.
 * Activate the checkbox 'Can be Rented'.
 * Go to page 'Sales & Purchase'.
 * Create the rental service and configure its name and price.

Create a rental order:
 * Go to Rentals > Customer > Rental Quotations.
 * Create a new order and choose the type 'Rental Order'.
 * Add the rental service as an order line.
 * Set the quantity to rent out one or several storable rentable products.
 * Choose start and end date.
 * Confirm the order.
 * Check out the two deliveries, one for outgoing and one for incoming delivery.

Please also see the usage section of sale_rental module.
""",

    "author": "elego Software Solutions GmbH, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/vertical-rental",
    "depends": [
        "account",
        "product_analytic",
        "sale",
        "sale_order_type",
        "sale_rental",
        "sale_start_end_dates",
        "sale_stock",
        "sales_team",
    ],
    "data": [
        "data/ir_sequence_data.xml",
        "data/order_type_data.xml",
        "data/product_uom_data.xml",
        "wizard/update_sale_line_date_view.xml",
        "views/res_config_settings_view.xml",
        "views/stock_picking_views.xml",
        "views/product_views.xml",
        "views/menu_view.xml",
        "views/sale_view.xml",
    ],
    "demo": [],
    "qweb": [],
    "application": True,
    "license": "AGPL-3",
}
