# Part of rental-vertical See LICENSE file for full copyright and licensing details.

{
    "name": "Rental Product Pack",
    "version": "12.0.1.0.0",
    "category": "Rental",
    "summary": "Manage rentals with product packs",
    "description": """
This module allows to manage rentals with product packs.
You can define product packs as described in the module product_pack.
The components of the pack are added to both rental stock pickings after order confirmation.
""",
    "usage": """
Install the module.
No further configuration is needed.

Create at least one storable product that will be a component of a pack.
 * Go to Rentals > Configuration > Settings.
 * Please activate the checkbox for using 'Product Variants'.
 * Go to Rentals > Products > Products.
 * Create a new storable product.

Create a rentable pack product.
 * Create a new storable product.
 * Activate the checkbox 'Can be Rented' and 'Is Pack'.
 * Go to page 'Pack'.
 * Choose Pack Type (e.g. Non-detailled) and add the previously created storable products that are part of this pack.
 * Go to page 'Sales & Purchase'.
 * Create the rental service and configure its name and price.

Create a rental order:
 * Go to Rentals > Customer > Rental Quotations.
 * Create a new order and choose the type 'Rental Order'.
 * Add the rental service of the rentable pack product as an order line.
 * Set the quantity.
 * Choose start and end date.
 * Confirm the order.
 * Check out the two deliveries, one for outgoing and one for incoming delivery.
 * You can see all parts of the pack in both stock pickings.

Hint:
Refer to the usage information of the OCA module product_pack to learn how to
define product packs.
Please note, that this module does not include the behavior of the module sale_product_pack.
""",

    "author": "elego Software Solutions GmbH, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/vertical-rental",
    "depends": [
        "rental_base",
        "product_pack",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/product_view.xml",
    ],
    "demo": [],
    "qweb": [],
    "application": False,
    "license": "AGPL-3",
}
