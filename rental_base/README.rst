Rental Base
====================================================

*This file has been generated on 2023-02-19-14-21-34. Changes to it will be overwritten.*

Summary
-------

Manage Rental of Products

Description
-----------

Base Module for Rental Management

This module provides a new menu for rental management.
It is based on the sale_rental module that currently can be found in sale-workflow repository.


Usage
-----

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

Changelog
---------

- c0f830f7 2022-04-21 13:21:31 +0200 wagner@elegosoft.com  (elego-github/v15) complete remove references to product_packaging (issue #4968)
- 1a0c6ce1 2022-04-21 11:28:55 +0200 wagner@elegosoft.com  adapt to product_packaging removal (issue #4968)
- 9089b1d5 2022-04-15 14:16:12 +0200 wagner@elegosoft.com  (tag: odoo-fox-v15_v15_int_current_daily, tag: daily_odoo-fox-v15_v15_fox_v15_daily_build-26, tag: daily_odoo-fox-v15_v15_fox_v15_daily_build-25, tag: daily_odoo-fox-v15_v15_fox_v15_daily_build-23, tag: daily_odoo-fox-v15_v15_fox_v15_daily_build-22, tag: daily_odoo-fox-v15_v15_fox_v15_daily_build-21, tag: daily_odoo-fox-v15_v15_fox_v15_daily_build-17, tag: daily_odoo-fox-v15_v15_fox_v15_daily_build-16, tag: daily_odoo-fox-v15_v15_fox_v15_daily_build-15, tag: daily_odoo-fox-v15_v15_fox_v15_daily_build-13, tag: daily_odoo-fox-v15_v15_fox_v15_daily_build-12, tag: bp_fox_v15_integration-ceqp-2, tag: bp_fox_v15_integration-cep-27, tag: bp_fox_v15_integration-cep-26, tag: bp_fox_v15_integration-cep-25, tag: bp_fox_v15_integration-cep-23, tag: bp_fox_v15_integration-cep-22, tag: bp_fox_v15_integration-cep-21, tag: bp_fox_v15_integration-cep-17, tag: bp_fox_v15_integration-cep-16, tag: bp_fox_v15_integration-cep-15, tag: bp_fox_v15_integration-cep-13, tag: bp_fox_v15_integration-cep-12, tag: baseline_odoo-fox-v15_v15_fox_v15_daily_build-26, origin/fox_v15_integration-cep-26, origin/fox_v15_integration-cep-25, origin/fox_v15_integration-cep-23, origin/fox_v15_integration-cep-22, origin/fox_v15_integration-cep-21, origin/fox_v15_integration-cep-17, origin/fox_v15_integration-cep-16, origin/fox_v15_integration-cep-15, origin/fox_v15_integration-cep-13, origin/fox_v15_integration-cep-12) update module versions for v15 and remove old migration scripts (issue #4967)
- 8d191ff7 2022-04-10 15:41:16 +0200 wagner@elegosoft.com  add missing/lost documentation (issue #4516)
- 39ff8efc 2022-03-14 15:15:31 +0100 cpatel@elegosoft.com  [IMP] rental_tour correction, (issue#4516)
- ac980b89 2022-02-28 17:36:28 +0100 cpatel@elegosoft.com  [FIX][IMP] correct code, (issue#4516)
- 4509f78a 2022-02-23 20:48:33 +0100 wagner@elegosoft.com  (origin/feature_4516_add_files_ported_from_v12_v14, feature_4516_add_files_ported_from_v12_v14) add files ported to v14 by cpatel and khanhbui (issue #4516)

