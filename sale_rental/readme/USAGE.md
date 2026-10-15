In a sale order line (form view, not tree view), if you select a rental
service, you can:

- create a new rental with a start date and an end date: when the sale
  order is confirmed, it will generate a delivery order and an incoming
  shipment.
- extend an existing rental: the incoming shipment will be postponed to
  the end date of the extension.

In a sale order line, if you select a product that has a corresponding
rental service, you can decide to sell the rented product that the
customer already has. If the sale order is confirmed, the incoming
shipment will be cancelled and a new delivery order will be created with
a stock move from *Rental Out* to *Customers*.

You can configure Rental Periods under Sales ▸ Configuration ▸ Rental Period. A rental period defines the unit of time (Hour, Day, Week, Month, …) with its conversion into hours. These periods are used to compute rental duration.

You can configure Rental Pricing under Sales ▸ Products ▸ Rental Pricing. For each rental service product, you define a price per rental period. When you create a rental order line, the system selects the period, computes the duration from the dates, and applies the corresponding rental price. If a product has no price defined for the selected period, the system will warn the user.
