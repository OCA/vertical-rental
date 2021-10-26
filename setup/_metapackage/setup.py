import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-vertical-rental",
    description="Meta package for oca-vertical-rental Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-rental_base',
        'odoo12-addon-rental_check_availability',
        'odoo12-addon-rental_offday',
        'odoo12-addon-rental_pricelist',
        'odoo12-addon-rental_pricelist_interval',
        'odoo12-addon-rental_product_pack',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 12.0',
    ]
)
