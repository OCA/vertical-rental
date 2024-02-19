Rental Off-Day
====================================================

*This file has been generated on 2023-02-19-14-21-34. Changes to it will be overwritten.*

Summary
-------

Manage off-days in rentals on daily basis

Description
-----------

During short-term rentals over several days or weeks, the customer and the salesman
agree on so called off-days. On these days the customer still have the rented products
but usually doesn't use them and, therefore, does not pay the daily price. This is often
the case for weekends and holidays, since there might be some legal limitations in using
the products on these days.
In order to meet this requirement, the salesman can add off-days on sale order lines for
products that are rentable in days. These days will not be included in price calculation.


Usage
-----

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

Changelog
---------

- 9089b1d5 2022-04-15 14:16:12 +0200 wagner@elegosoft.com  (tag: odoo-fox-v15_v15_int_current_daily, tag: daily_odoo-fox-v15_v15_fox_v15_daily_build-26, tag: daily_odoo-fox-v15_v15_fox_v15_daily_build-25, tag: daily_odoo-fox-v15_v15_fox_v15_daily_build-23, tag: daily_odoo-fox-v15_v15_fox_v15_daily_build-22, tag: daily_odoo-fox-v15_v15_fox_v15_daily_build-21, tag: daily_odoo-fox-v15_v15_fox_v15_daily_build-17, tag: daily_odoo-fox-v15_v15_fox_v15_daily_build-16, tag: daily_odoo-fox-v15_v15_fox_v15_daily_build-15, tag: daily_odoo-fox-v15_v15_fox_v15_daily_build-13, tag: daily_odoo-fox-v15_v15_fox_v15_daily_build-12, tag: bp_fox_v15_integration-ceqp-2, tag: bp_fox_v15_integration-cep-27, tag: bp_fox_v15_integration-cep-26, tag: bp_fox_v15_integration-cep-25, tag: bp_fox_v15_integration-cep-23, tag: bp_fox_v15_integration-cep-22, tag: bp_fox_v15_integration-cep-21, tag: bp_fox_v15_integration-cep-17, tag: bp_fox_v15_integration-cep-16, tag: bp_fox_v15_integration-cep-15, tag: bp_fox_v15_integration-cep-13, tag: bp_fox_v15_integration-cep-12, tag: baseline_odoo-fox-v15_v15_fox_v15_daily_build-26, origin/fox_v15_integration-cep-26, origin/fox_v15_integration-cep-25, origin/fox_v15_integration-cep-23, origin/fox_v15_integration-cep-22, origin/fox_v15_integration-cep-21, origin/fox_v15_integration-cep-17, origin/fox_v15_integration-cep-16, origin/fox_v15_integration-cep-15, origin/fox_v15_integration-cep-13, origin/fox_v15_integration-cep-12) update module versions for v15 and remove old migration scripts (issue #4967)
- 8d191ff7 2022-04-10 15:41:16 +0200 wagner@elegosoft.com  add missing/lost documentation (issue #4516)
- 4509f78a 2022-02-23 20:48:33 +0100 wagner@elegosoft.com  (origin/feature_4516_add_files_ported_from_v12_v14, feature_4516_add_files_ported_from_v12_v14) add files ported to v14 by cpatel and khanhbui (issue #4516)

