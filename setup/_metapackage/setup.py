import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo-addons-oca-vertical-rental",
    description="Meta package for oca-vertical-rental Odoo addons",
    version=version,
    install_requires=[
        'odoo-addon-rental_base>=16.0dev,<16.1dev',
        'odoo-addon-rental_offday>=16.0dev,<16.1dev',
        'odoo-addon-rental_pricelist>=16.0dev,<16.1dev',
        'odoo-addon-rental_product_pack>=16.0dev,<16.1dev',
        'odoo-addon-sale_rental>=16.0dev,<16.1dev',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 16.0',
    ]
)
