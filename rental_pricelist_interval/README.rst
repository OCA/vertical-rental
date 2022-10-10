Rental Pricelist (Interval)
====================================================

*This file has been generated on 2022-05-04-12-21-41. Changes to it will be overwritten.*

Summary
-------

Enables the user to define different rental prices time uom (Month, Day and Hour).

Description
-----------

This Module implements a new rental service product for interval pricing under consideration
of odoo price lists. This enables to rent out products and charge for day interval ranges.

These ranges can be configured freely on general and/or product level. In contrast to rentals
on daily, monthly or yearly bases a different price computation is applied in sale order lines.


Configuration
-------------

To configure this module, you need to:

#. Go to company settings and define the default interval ranges on 'Rental Interval Prices' tab.
   These ranges will be applied for computation of price intervals for rental service products when interval pricing is activated
   in stockable product.

#. If desired go to 'RS (Prefix and Suffix)' tab an define how rental interval service product
   names and reference numbers are created.


Usage
-----

To use this module, you need to:

#. Create a new stockable product and define it as rental service or
   go to an existing one.

#. On 'Rental Price' tab check the 'Rented in interval' option.

#. Set the interval base price and define the max amount of days the product
   can be rented out.

#. Push the 'Reset Interval Prices' button to compute interval ranges and prices.
   from base price and interval ranges configured in company settings.

#. Adapt interval min. quantities or prices for the selected product if desired.

Changelog
---------

- 8d191ff7 2022-04-10 15:41:16 +0200 wagner@elegosoft.com  add missing/lost documentation (issue #4516)
- 4509f78a 2022-02-23 20:48:33 +0100 wagner@elegosoft.com  (origin/feature_4516_add_files_ported_from_v12_v14, feature_4516_add_files_ported_from_v12_v14) add files ported to v14 by cpatel and khanhbui (issue #4516)

