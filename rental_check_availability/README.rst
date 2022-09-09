Rental Check Availability
====================================================

*This file has been generated on 2022-07-26-13-09-49. Changes to it will be overwritten.*

Summary
-------

Extends the sale_rental module for checking availability of the rented product.

Description
-----------

This module activates availability checks on stockable products related to rental services in
sale orders. In the base functionality only the total amount of products in stock is checked and user is
informed when the amount of products to rent out in a sale order is higher.

After the installation of this module the availability is checked in consideration of the total amount
of goods in stock and the amount of products used in concurrent sale orders at the certain desired timeframe.
In case of insufficient products in stock the user receives visual notification on respective sale order line
and can access the list of concurrent sale orders directly.


Usage
-----

To use this module, you need to:

#. Go to Rental Orders and create a new one.

#. Add a product available for being rented out in sale order line.

#. If there is not enough stock on hand to fullfil the order and
   possible concurrent ones the sale order line will be colorized.
   Yellow marks that there are concurrent quotations and red indicates
   concurrent orders.

#. To check the concurrent order for a critical sale order line just click
   on the inline button being displayed in the sale order line.


Changelog
---------

- 1e549e87 2022-05-04 12:56:56 +0200 wagner@elegosoft.com  (origin/feature_2832_blp7_new_logos_v12, feature_2832_blp7_new_logos_v12) update doc (issue #3613, issue #4016)
- eee26e11 2022-05-04 12:20:20 +0200 wagner@elegosoft.com  add missing README.rst files (issue #4016)
- 02eb49c8 2022-05-04 12:18:32 +0200 wagner@elegosoft.com  update doc (issue #4016)
- 4ff94cf3 2022-05-04 12:09:50 +0200 wagner@elegosoft.com  add new rental logo (issue #3613, issue #4016)
- 296b6193 2021-10-25 10:20:28 +0200 wagner@elegosoft.com  regenrate documentation (issue #4016)
- 39845816 2021-10-21 14:15:20 +0200 yweng@elegosoft.com  (origin/feature_4436_blp1250_unittest_rental_check_availability_v12) [IMP] update translations and manifest of module rental_pricelist_interval and rental_check_availability (issue 4436)
- d8665dd9 2021-10-19 12:26:31 +0200 yweng@elegosoft.com  [IMP] Add Unittest for module rental_check_availability and adjust Unittest of rental_pricelist and rental_pricelist_interval (issue 4436)
- 8b4d40c4 2021-09-23 09:19:24 +0200 wagner@elegosoft.com  regenerate doc (issue #4016)
- dd988a2f 2021-06-09 12:42:47 +0200 wagner@elegosoft.com  update documentation (issue #3613)
- 78a00cdd 2021-04-28 02:43:00 +0200 yweng@elegosoft.com  (origin/feature_4222_blp622_rental_check_availability_v12, feature_4222_blp622_rental_check_availability_v12) [IMP] adjust tree view of sale.order and hide the button 'show concurrent order' for product with zero quantity
- 0cc27ac8 2021-03-28 21:45:23 +0200 yweng@elegosoft.com  (origin/feature_4046_blp564_rental_check_availability_v12) [ADD] Module rental_check_availability (issue 4046)

