Rental Pricelist (Interval)
====================================================

*This file has been generated on 2023-02-19-14-21-34. Changes to it will be overwritten.*

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

- 9089b1d5 2022-04-15 14:16:12 +0200 wagner@elegosoft.com  (tag: odoo-fox-v15_v15_int_current_daily, tag: daily_odoo-fox-v15_v15_fox_v15_daily_build-26, tag: daily_odoo-fox-v15_v15_fox_v15_daily_build-25, tag: daily_odoo-fox-v15_v15_fox_v15_daily_build-23, tag: daily_odoo-fox-v15_v15_fox_v15_daily_build-22, tag: daily_odoo-fox-v15_v15_fox_v15_daily_build-21, tag: daily_odoo-fox-v15_v15_fox_v15_daily_build-17, tag: daily_odoo-fox-v15_v15_fox_v15_daily_build-16, tag: daily_odoo-fox-v15_v15_fox_v15_daily_build-15, tag: daily_odoo-fox-v15_v15_fox_v15_daily_build-13, tag: daily_odoo-fox-v15_v15_fox_v15_daily_build-12, tag: bp_fox_v15_integration-ceqp-2, tag: bp_fox_v15_integration-cep-27, tag: bp_fox_v15_integration-cep-26, tag: bp_fox_v15_integration-cep-25, tag: bp_fox_v15_integration-cep-23, tag: bp_fox_v15_integration-cep-22, tag: bp_fox_v15_integration-cep-21, tag: bp_fox_v15_integration-cep-17, tag: bp_fox_v15_integration-cep-16, tag: bp_fox_v15_integration-cep-15, tag: bp_fox_v15_integration-cep-13, tag: bp_fox_v15_integration-cep-12, tag: baseline_odoo-fox-v15_v15_fox_v15_daily_build-26, origin/fox_v15_integration-cep-26, origin/fox_v15_integration-cep-25, origin/fox_v15_integration-cep-23, origin/fox_v15_integration-cep-22, origin/fox_v15_integration-cep-21, origin/fox_v15_integration-cep-17, origin/fox_v15_integration-cep-16, origin/fox_v15_integration-cep-15, origin/fox_v15_integration-cep-13, origin/fox_v15_integration-cep-12) update module versions for v15 and remove old migration scripts (issue #4967)
- 8d191ff7 2022-04-10 15:41:16 +0200 wagner@elegosoft.com  add missing/lost documentation (issue #4516)
- 4509f78a 2022-02-23 20:48:33 +0100 wagner@elegosoft.com  (origin/feature_4516_add_files_ported_from_v12_v14, feature_4516_add_files_ported_from_v12_v14) add files ported to v14 by cpatel and khanhbui (issue #4516)

