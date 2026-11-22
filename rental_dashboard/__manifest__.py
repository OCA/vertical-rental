{
    "name": "Rental Dashboard",
    "version": "16.0.1.0.0",
    "summary": "Rental Dashboard with Calendar and Booking Management",
    "category": "Rental",
    "author": "Trobz, Odoo Community Association (OCA)",
    "depends": ["sale_rental"],
    "data": [
        "views/product_product_views.xml",
        "views/sale_order_line_views.xml",
        "views/dashboard_action.xml",
        "views/menus.xml",
    ],
    "demo": [],
    "assets": {
        "web.assets_backend": [
            "rental_dashboard/static/src/scss/rental_dashboard.scss",
            "rental_dashboard/static/src/js/rental_dashboard.js",
            "rental_dashboard/static/src/xml/rental_dashboard.xml",
        ],
    },
    "installable": True,
    "application": True,
    "license": "AGPL-3",
    "website": "https://github.com/OCA/vertical-rental",
}
