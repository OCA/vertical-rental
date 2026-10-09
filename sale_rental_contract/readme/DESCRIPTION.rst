Long rentals are usually charged every month: this module invoices them
through a recurring contract (``contract``) instead of the sale order.

When the rental service of a ``sale_rental`` order line is also a contract
product (``product_contract``), confirming the order:

* creates the contract line with the number of rented units (not the number
  of days of the rental line), the new unit of measure *Month*, the monthly
  price and the rental start and end dates;
* leaves the sale order line with nothing to invoice;
* keeps the ``sale_rental`` delivery and return transfers of the rented goods.

The contract follows the rental:

* a rental extension adds a line to the same contract, successor of the
  previous one, from the day after the previous end;
* selling the rented product stops the contract lines on the sale date;
* returning the goods before the end stops the contract lines on the return
  date (never before the last invoiced day); extensions not started yet are
  cancelled.
