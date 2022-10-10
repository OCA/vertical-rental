Rental Product Pack
====================================================

*This file has been generated on 2022-05-04-12-21-41. Changes to it will be overwritten.*

Summary
-------

Manage rentals with product packs

Description
-----------

This module allows to manage rentals with product packs.
You can define product packs as described in the module product_pack.
The components of the pack are added to both rental stock pickings after order confirmation.


Usage
-----

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

Changelog
---------

- 8d191ff7 2022-04-10 15:41:16 +0200 wagner@elegosoft.com  add missing/lost documentation (issue #4516)
- 4509f78a 2022-02-23 20:48:33 +0100 wagner@elegosoft.com  (origin/feature_4516_add_files_ported_from_v12_v14, feature_4516_add_files_ported_from_v12_v14) add files ported to v14 by cpatel and khanhbui (issue #4516)

