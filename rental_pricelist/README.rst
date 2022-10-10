Rental Pricelist
====================================================

*This file has been generated on 2022-05-04-12-21-41. Changes to it will be overwritten.*

Summary
-------

Enables the user to define different rental prices with time uom (Month, Day and Hour).

Description
-----------

Rental prices are usually scaled prices based on a time unit, typically day, sometimes months or hour.
This modules integrates the standard Odoo pricelists into rental use cases and allows the user an
easy way to specify the prices in a product tab as well as to use all the enhanced pricelist features.


Usage
-----

Create a rentable product:
 * Go to Rentals > Configuration > Settings.
 * Please activate the checkbox for using 'Product Variants'.
 * Go to Rentals > Products > Products.
 * Create a new storable product.
 * Active the checkbox 'Can be Rented'.

 Configure the naming of rental services:
 * Go to Settings > Users & Companies > Companies.
 * To to page 'Rental Services'.
 * Configure the rental service names by providing a prefix and suffix for the name and default code.

 Create the rental services:
 * Go to the previously created rentable storable product.
 * Go to page 'Rental Price'.
 * Activate the boolean fields for hourly, daily or monthly rental as needed.
 * Save the product, which creates the related rental services for the given time units.
 * Add a usual price for one hour, one day or one month.
 * Add bulk prices, e.g. one day costs 300 €, 7 days 290 €, 21 days 250 €, and so on.

Hint: The (bulk) prices are added in the product form view of the storable, rentable product
but are actually used for its related rental services!

Create a rental order:
 * Go to Rentals > Customer > Rental Quotations.
 * Create a new order and choose the type 'Rental Order'.
 * Choose the storable rental product (not the rental service!).
 * Choose the rental time unit, which actually loads the correct related rental service.
 * Set the quantity to rent out one or several storable rentable products.
 * Choose start and end date.
 * Confirm the order.
 * Check out the two deliveries, one for outgoing and one for incoming delivery.

Please also see the usage section of sale_rental and rental_base module.

Changelog
---------

- 8d191ff7 2022-04-10 15:41:16 +0200 wagner@elegosoft.com  add missing/lost documentation (issue #4516)
- 4509f78a 2022-02-23 20:48:33 +0100 wagner@elegosoft.com  (origin/feature_4516_add_files_ported_from_v12_v14, feature_4516_add_files_ported_from_v12_v14) add files ported to v14 by cpatel and khanhbui (issue #4516)

