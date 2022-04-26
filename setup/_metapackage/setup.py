import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo14-addons-oca-vertical-rental",
    description="Meta package for oca-vertical-rental Odoo addons",
    version=version,
    install_requires=[
        'odoo14-addon-rental_base',
        'odoo14-addon-rental_offday',
        'odoo14-addon-rental_pricelist',
        'odoo14-addon-rental_pricelist_interval',
        'odoo14-addon-rental_product_pack',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 14.0',
    ]
)
