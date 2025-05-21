# Part of rental-vertical See LICENSE file for full copyright and licensing details.


def set_product_def_interval_pricelist_id(env):
    interval_price_id = env.ref("rental_pricelist_interval.pricelist_interval").id
    env["product.product"].search([]).write(
        {
            "def_interval_pricelist_id": interval_price_id,
        }
    )
