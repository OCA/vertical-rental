# Part of rental-vertical See LICENSE file for full copyright and licensing details.

{
    "name": "Rental Off-Day",
    "version": "12.0.1.0.0",
    "category": "Rental",
    "summary": "Manage off-days in rentals on daily basis",
    "description": """
During short-term rentals over several days or weeks, the customer and the salesman
agree on so called off-days. On these days the customer still have the rented products
but usually doesn't use them and, therefore, does not pay the daily price. This is often
the case for weekends and holidays, since there might be some legal limitations in using
the products on these days.
In order to meet this requirement, the salesman can add off-days on sale order lines for
products that are rentable in days. These days will not be included in price calculation.
""",
    "usage": """
The off-days can only be used for products rentable in days.

Create a rentable product and its rental service for daily rentals:
 * Go to Rentals > Configuration > Settings.
 * Please activate the checkbox for using 'Product Variants'.
 * Go to Rentals > Products > Products.
 * Create a new storable product.
 * Active the checkbox 'Can be Rented'.
 * Go to page 'Rental Price'.
 * Activate the boolean fields for daily rental.
 * Add a usual price for one day.
 * Save the product, which creates the related rental service.
 * Add bulk prices as desired, e.g. one day costs 300 €, 7 days 290 €, 21 days 250 €, and so on.
 * Adjust its stock in location 'Rental In'.

Create a rental order:
 * Go to Rentals > Customer > Rental Quotations.
 * Create a new order and choose the type 'Rental Order'.
 * Add the rental service as an order line.
 * Set the quantity to rent out one or several storable rentable products.
 * Choose start and end date, e.g. for 3 weeks.
 * On the order line you will see a page 'Off-Days' at the bottom.
 * Choose the type 'Weekend' in order to create 'Fixed Off-Days' and you get a list with all saturdays and sundays within the rental period.
 * Add some additional off-days as needed.
 * The number of off-days reduces the rental quantity and is therefore not included in price calculation.
 * Confirm the order.
""",
    "author": "elego Software Solutions GmbH, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/vertical-rental",
    "depends": [
        "rental_pricelist",
    ],
    "data": [
        "security/ir.model.access.csv",
        "views/sale_view.xml",
    ],
    "demo": [],
    "qweb": [],
    "auto_install": False,
    "license": "AGPL-3",
}
