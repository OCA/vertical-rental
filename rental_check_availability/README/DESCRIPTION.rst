Rental Check Availability
====================================================

*This file has been generated on 2022-04-20-11-34-50. Changes to it will be overwritten.*

Summary
-------

Extends the sale_rental module for checking availability of the rented product.

Description
-----------

This module activates availability checks on stockable products related to rental services in
sale orders. In the base functionality, only the total amount of products in stock is checked and the user is
informed when the amount of products to rent out in a sale order is higher.

After the installation of this module, the availability is checked in consideration of the total amount
of goods in stock and the amount of products used in concurrent sale orders at a certain desired timeframe.
In case of insufficient products in stock, the user receives a visual notification on the respective sale order line
and can access the list of concurrent sale orders directly.
