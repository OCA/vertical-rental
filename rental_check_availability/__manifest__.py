# Part of rental-vertical See LICENSE file for full copyright and licensing details.

{
    "name": "Rental Check Availability",
    "summary": """Extends the sale_rental module for checking availability
of the rented product.
""",
    "usage": """
To use this module, you need to:

#. Go to Rental Orders and create a new one.

#. Add a product available for being rented out in sale order line.

#. If there is not enough stock on hand to fullfil the order and
   possible concurrent ones the sale order line will be colorized.
   Yellow marks that there are concurrent quotations and red indicates
   concurrent orders.

#. To check the concurrent order for a critical sale order line just click
   on the inline button being displayed in the sale order line.
""",
    "contributors": """
* Ben Brich <b.brich@humanilog.org> (www.humanilog.org)
* Yu Weng <yweng@elegosoft.com> (www.elegosoft.com)
""",
    "version": "12.0.1.0.1",
    "category": "Rental",
    "author": "Odoo Community Association (OCA), Elego Software Solutions GmbH",
    "website": "https://github.com/OCA/vertical-rental",
    "depends": [
        "rental_pricelist",
    ],
    "data": [
        "views/sale_view.xml",
    ],
    "demo": [],
    "qweb": [],
    "application": False,
    "license": "AGPL-3",
}
