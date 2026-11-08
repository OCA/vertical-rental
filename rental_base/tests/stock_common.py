# Part of rental-vertical See LICENSE file for full copyright and licensing details.

from odoo.tests import common


class RentalStockCommon(common.TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Rental Type, Picking Type, Locations and Uoms
        cls.category_all = cls.env.ref("product.product_category_all")
        cls.rental_sale_type = cls.env.ref("rental_base.rental_sale_type")
        cls.picking_type_in = cls.env.ref("stock.picking_type_in")
        cls.picking_type_out = cls.env.ref("stock.picking_type_out")
        cls.stock_location = cls.env.ref("stock.stock_location_stock")
        cls.supplier_location = cls.env.ref("stock.stock_location_suppliers")
        cls.customer_location = cls.env.ref("stock.stock_location_customers")
        cls.uom_hour = cls.env.ref("uom.product_uom_hour")
        cls.uom_day = cls.env.ref("uom.product_uom_day")
        cls.uom_month = cls.env.ref("rental_base.product_uom_month")
        cls.uom_unit = cls.env.ref("uom.product_uom_unit")
        cls.uom_kgm = cls.env.ref("uom.product_uom_kgm")
        cls.warehouse0 = cls.env.ref("stock.warehouse0")
        cls.PartnerObj = cls.env["res.partner"]
        cls.partnerA = cls.PartnerObj.create(
            {
                "name": "Partner A",
                "country_id": cls.env.ref("base.de").id,
            }
        )

    @classmethod
    def _create_rental_service_day(cls, product):
        values = {
            "hw_product_id": product.id,
            "name": "Rental of %s (Day)" % product.name,
            "categ_id": product.categ_id.id,
            "copy_image": True,
        }
        res = (
            cls.env["create.rental.product"]
            .with_context(active_model="product.product", active_id=product.id)
            .create(values)
            .create_rental_product()
        )

        rental_service = cls.env["product.product"].browse(res["res_id"])
        rental_service.write(
            {
                "uom_id": cls.uom_day.id,
                "uom_po_id": cls.uom_day.id,
                "income_analytic_account_id": product.income_analytic_account_id.id,
                "list_price": 100,
            }
        )

        return rental_service

    @classmethod
    def _create_move(cls, product, src_location, dst_location, **values):
        Move = cls.env["stock.move"]
        move = Move.new(
            {
                "product_id": product.id,
                "location_id": src_location.id,
                "location_dest_id": dst_location.id,
            }
        )
        move.onchange_product_id()
        move_values = move._convert_to_write(move._cache)
        move_values.update(**values)
        return Move.create(move_values)

    @classmethod
    def _create_rental_order(cls, partner_id, date_start, date_end, qty=1):
        """
        Create a Rental Order with Product (self.service_rental)
        """
        date_qty = (date_end - date_start).days + 1
        rental_order = cls.env["sale.order"].create(
            {
                "type_id": cls.rental_sale_type.id,
                "partner_id": partner_id,
                "partner_invoice_id": partner_id,
                "partner_shipping_id": partner_id,
                "pricelist_id": cls.env.ref("product.list0").id,
                "picking_policy": "direct",
                "warehouse_id": cls.warehouse0.id,
                "order_line": [
                    (
                        0,
                        0,
                        {
                            "name": "Service for Rental",
                            "product_id": cls.service_rental.id,
                            "rental": True,
                            "rental_type": "new_rental",
                            "rental_qty": qty,
                            "product_uom_qty": date_qty * qty,
                            "start_date": date_start,
                            "end_date": date_end,
                            "price_unit": 100,
                            "product_uom": cls.uom_day.id,
                        },
                    )
                ],
            }
        )
        return rental_order
