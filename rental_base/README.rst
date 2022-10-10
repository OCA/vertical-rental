Rental Base
====================================================

*This file has been generated on 2022-05-04-12-21-41. Changes to it will be overwritten.*

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

- 8d191ff7 2022-04-10 15:41:16 +0200 wagner@elegosoft.com  add missing/lost documentation (issue #4516)
- 39ff8efc 2022-03-14 15:15:31 +0100 cpatel@elegosoft.com  [IMP] rental_tour correction, (issue#4516)
- ac980b89 2022-02-28 17:36:28 +0100 cpatel@elegosoft.com  [FIX][IMP] correct code, (issue#4516)
- 4509f78a 2022-02-23 20:48:33 +0100 wagner@elegosoft.com  (origin/feature_4516_add_files_ported_from_v12_v14, feature_4516_add_files_ported_from_v12_v14) add files ported to v14 by cpatel and khanhbui (issue #4516)

