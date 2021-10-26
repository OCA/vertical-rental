from openupgradelib import openupgrade
from odoo.tools.float_utils import float_compare, float_round, float_is_zero
import logging

_logger = logging.getLogger(__name__)


@openupgrade.migrate()
def migrate(env, version):
    products = env["product.product"].search([("rental_of_interval", "=", True)])
    count = 0
    updated_product_ids = []
    for p in products:
        _logger.info(
            "[MIG] Try add Interval Service and pricelist items for %s (ID: %s)"
            % (p.name, p.id)
        )
        if not p.product_rental_interval_id:
            service_product = env["product.product"]._create_rental_service(
                "interval", p, p.rental_price_interval
            )
            p.product_rental_interval_id = service_product
        values = []
        for item in env["rental.price.interval.item"].search(
            [("product_id", "=", p.id)]
        ):
            values.append(
                (
                    0,
                    0,
                    {
                        "fixed_price": item.price,
                        "min_quantity": item.min_quantity,
                        "compute_price": "fixed",
                        "applied_on": "0_product_variant",
                        "product_id": p.product_rental_interval_id.id,
                        "pricelist_id": p.def_interval_pricelist_id.id,
                    },
                )
            )
        p.interval_scale_pricelist_item_ids = values
        _logger.info(
            "[MIG] Successfully add Interval Service and pricelist items for %s (ID: %s)"
            % (p.name, p.id)
        )
        count += 1
        updated_product_ids.append(p.id)
    _logger.info(
        "[MIG] %s Products (IDs: %s) was updated successfully."
        % (count, updated_product_ids)
    )
