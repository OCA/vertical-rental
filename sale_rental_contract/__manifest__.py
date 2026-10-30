# Copyright 2026 KMEE
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Sale Rental Contract",
    "summary": "Invoice long rentals monthly through recurring contracts",
    "version": "16.0.1.0.0",
    "development_status": "Alpha",
    "category": "Sales",
    "author": "KMEE, Odoo Community Association (OCA)",
    "maintainers": ["mileo"],
    "website": "https://github.com/OCA/vertical-rental",
    "license": "AGPL-3",
    # the rental service must have start/end dates (sale_start_end_dates):
    # contract_invoice_start_end_dates fills them with the invoiced period
    "depends": ["sale_rental", "product_contract", "contract_invoice_start_end_dates"],
    "data": [
        "data/uom_data.xml",
        "views/product_template_view.xml",
    ],
    "installable": True,
}
