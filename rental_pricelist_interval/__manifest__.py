# Part of rental-vertical See LICENSE file for full copyright and licensing details.

{
    "name": "Rental Pricelist (Interval)",
    "summary": """
Enables the user to define different rental prices with time uom ("Month", "Day" and "Hour").
""",
    "usage": """
To use this module, you need to:

#. Create a new stockable product and define it as rental service or
   go to an existing one.

#. On 'Rental Price' tab check the 'Rented in interval' option.

#. Set the interval base price and define the max amount of days the product
   can be rented out.

#. Push the 'Reset Interval Prices' button to compute interval ranges and prices.
   from base price and interval ranges configured in company settings.

#. Adapt interval min. quantities or prices for the selected product if desired.
""",
    "contributors": """
* Ben Brich <b.brich@humanilog.org> (www.humanilog.org)
* Yu Weng <yweng@elegosoft.com> (www.elegosoft.com)
""",
    "configuration": """
To configure this module, you need to:

#. Go to company settings and define the default interval ranges on
   'Rental Interval Prices' tab. These ranges will be applied for computation of price intervals
   for rental service products when interval pricing is activated in stockable product.

#. If desired go to 'RS (Prefix and Suffix)' tab an define how rental interval service product
   names and reference numbers are created.
""",
    "version": "14.0.1.0.0",
    "category": "Rental",
    "author": "elego Software Solutions GmbH, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/vertical-rental",
    "depends": [
        "rental_pricelist",
    ],
    "data": [
        "security/ir.model.access.csv",
        "data/product_uom_data.xml",
        "data/product_pricelist_data.xml",
        "views/product_pricelist_view.xml",
        "views/product_view.xml",
        "views/res_company_view.xml",
    ],
    "demo": [],
    "qweb": [],
    "post_init_hook": "set_product_def_interval_pricelist_id",
    "application": False,
    "installable": True,
    "license": "AGPL-3",
}
