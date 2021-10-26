import setuptools

with open('VERSION.txt', 'r') as f:
    version = f.read().strip()

setuptools.setup(
    name="odoo12-addons-oca-vertical-rental",
    description="Meta package for oca-vertical-rental Odoo addons",
    version=version,
    install_requires=[
        'odoo12-addon-rental_base',
        'odoo12-addon-rental_pricelist',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Framework :: Odoo',
        'Framework :: Odoo :: 12.0',
    ]
)
