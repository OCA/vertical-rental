# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Rental quality control (OCA)",
    "version": "18.0.1.0.1",
    "category": "Quality control",
    "license": "AGPL-3",
    "author": "Kencove, Trobz, Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/vertical-rental",
    "depends": ["quality_control_stock_oca", "sale_rental"],
    "data": [
        "views/qc_inspection_view.xml",
        "views/sale_rental_views.xml",
    ],
    "installable": True,
}
