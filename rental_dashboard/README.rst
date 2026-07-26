================
Rental Dashboard
================

A unified dashboard for managing rental operations, built as an OWL client action
embedded in the Odoo backend.

Features
========

Calendar View
-------------
Displays all active rental bookings on a month calendar, color-coded by customer.
Users can see at a glance when equipment is booked and by whom.

Product Sidebar
---------------
Lists all rental-eligible products with real-time availability (available / total fleet),
calculated from warehouse stock minus committed rentals.

Filtering
---------
Filter by warehouse location, date range, and stock availability. Selecting a location
scopes both the product list and calendar to that warehouse. Date range highlights the
selected period on the calendar and recalculates availability for that window.

Quick Booking
-------------
Create rental orders directly from the dashboard: select products from the sidebar,
drag a date range on the calendar, or click "Create rental". A modal lets you pick
customer, warehouse, dates, equipment, rental period, and quantity — with live pricing
and availability checks.

Edit Bookings
-------------
Click any calendar event to open the rental order in an edit modal. View order status,
modify lines, confirm the order, or navigate to the full sale order form.

Hover Tooltips
--------------
Hovering over a calendar event shows a tooltip with product name, customer, order
reference, dates, and quantity.

Configuration
=============

1. Enable **Rental Allowed** on the warehouses you want to use for rentals
   (Inventory > Configuration > Warehouses).
2. Create physical products and use "Create Rental Service" on their form to make
   them available for rental.
3. Configure rental pricing per period on each rental service product
   (product form > Rental Pricing tab).

Usage
=====

1. Open the **Rentals** top-level menu.
2. The **Dashboard** sub-menu opens the rental dashboard.
3. Use the left sidebar to filter by location, dates, and availability.
4. Click products to pre-select them, then click **Rent** or **Create rental**.
5. Fill in customer, dates, equipment lines, and quantities in the modal.
6. Click **Create Order** to save as a draft quotation, then optionally confirm.

Dependencies
============

* ``sale_rental``

Credits
=======

Authors
-------

* Trobz

Contributors
------------

* Trobz

Maintainers
-----------

This module is maintained by the OCA.
