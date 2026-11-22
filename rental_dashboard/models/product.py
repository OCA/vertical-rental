from odoo import api, fields, models


class ProductProduct(models.Model):
    _inherit = "product.product"

    rental_color = fields.Integer(string="Rental Color Index", default=0)

    @api.model
    def _get_rental_locations(self):
        """Return rental-enabled warehouses and their location mappings."""
        warehouses = self.env["stock.warehouse"].search_read(
            [("rental_allowed", "=", True)],
            ["id", "name", "rental_in_location_id", "rental_out_location_id"],
        )
        locations = [
            {
                "id": wh["rental_in_location_id"][0],
                "name": wh["rental_in_location_id"][1],
                "display_name": wh["name"],
                "rental_out_location_id": wh["rental_out_location_id"][0],
                "warehouse_id": wh["id"],
            }
            for wh in warehouses
        ]
        return warehouses, locations

    @api.model
    def get_rental_dashboard_data(self, location_id=None, date_from=None, date_to=None):
        """Return all dashboard data in a single RPC call.

        Replaces separate JS calls to load locations, rental periods, and products.
        """
        warehouses, locations = self._get_rental_locations()

        periods = self.env["rental.period"].search_read(
            [("active", "=", True)],
            ["id", "name", "code", "hours_per_unit"],
            order="sequence, id",
        )

        products = self._get_rental_products(locations, location_id, date_from, date_to)

        return {
            "locations": locations,
            "warehouses": warehouses,
            "rental_periods": periods,
            "products": products,
        }

    @api.model
    def get_rental_products(self, location_id=None, date_from=None, date_to=None):
        """Return rental products with availability. Used on filter changes."""
        _, locations = self._get_rental_locations()
        return self._get_rental_products(locations, location_id, date_from, date_to)

    @api.model
    def _get_rental_products(
        self, locations, location_id=None, date_from=None, date_to=None
    ):
        """Compute rental product availability at rental locations."""
        if location_id:
            loc = next(
                (location for location in locations if location["id"] == location_id),
                None,
            )
            rental_in_ids = [location_id] if loc else []
            rental_out_ids = [loc["rental_out_location_id"]] if loc else []
        else:
            rental_in_ids = [location["id"] for location in locations]
            rental_out_ids = [
                location["rental_out_location_id"] for location in locations
            ]

        all_location_ids = rental_in_ids + rental_out_ids
        if not all_location_ids:
            return []

        rental_in_set = set(rental_in_ids)

        # Stock at rental locations — aggregate in SQL
        quant_groups = self.env["stock.quant"].read_group(
            [("location_id", "in", all_location_ids), ("quantity", ">", 0)],
            ["product_id", "location_id", "quantity:sum"],
            ["product_id", "location_id"],
            lazy=False,
        )
        rental_in_qty = {}
        total_qty = {}
        for g in quant_groups:
            if not g.get("product_id"):
                continue
            pid = g["product_id"][0]
            qty = g["quantity"]
            total_qty[pid] = total_qty.get(pid, 0) + qty
            if g["location_id"][0] in rental_in_set:
                rental_in_qty[pid] = rental_in_qty.get(pid, 0) + qty

        # Committed rental quantities — aggregate in SQL
        rental_domain = [("state", "=", "ordered")]
        if rental_in_ids:
            rental_domain.append(("out_picking_id.location_id", "in", rental_in_ids))
        if date_from:
            rental_domain.append(("start_datetime", "<=", date_to or date_from))
        if date_to:
            rental_domain.append(("end_datetime", ">=", date_from or date_to))
        rental_groups = self.env["sale.rental"].read_group(
            rental_domain,
            ["rented_product_id", "rental_qty:sum"],
            ["rented_product_id"],
        )
        committed_qty = {
            g["rented_product_id"][0]: g["rental_qty"]
            for g in rental_groups
            if g.get("rented_product_id")
        }

        # Products with rental services
        domain = [("rental_service_ids", "!=", False)]
        if location_id:
            product_ids = list(total_qty.keys())
            if not product_ids:
                return []
            domain.append(("id", "in", product_ids))

        products = self.search_read(
            domain, ["id", "name", "default_code", "rental_color"]
        )

        for p in products:
            p["qty_total"] = total_qty.get(p["id"], 0)
            avail = max(
                0,
                rental_in_qty.get(p["id"], 0) - committed_qty.get(p["id"], 0),
            )
            p["qty_available"] = avail
            if avail > 5:
                p["availability_status"] = "available"
            elif avail > 0:
                p["availability_status"] = "low"
            else:
                p["availability_status"] = "unavailable"

        return products

    @api.model
    def get_rental_modal_products(self, location_id=None, date_from=None, date_to=None):
        """Return service products with availability and pricings for the modal.

        Replaces 4+ separate JS RPC calls with a single one.
        Includes batch-loaded pricing data so the JS never needs
        separate pricing lookups.
        date_from/date_to (YYYY-MM-DD) filter committed rentals to those that
        overlap the booking period, matching sidebar availability logic.
        """
        if location_id:
            rental_in_ids = [location_id]
        else:
            warehouses = self.env["stock.warehouse"].search_read(
                [("rental_allowed", "=", True)], ["rental_in_location_id"]
            )
            rental_in_ids = [wh["rental_in_location_id"][0] for wh in warehouses]

        if not rental_in_ids:
            return []

        # Stock at rental_in locations — aggregate in SQL
        quant_groups = self.env["stock.quant"].read_group(
            [("location_id", "in", rental_in_ids), ("quantity", ">", 0)],
            ["product_id", "quantity:sum"],
            ["product_id"],
        )
        rental_in_qty = {
            g["product_id"][0]: g["quantity"]
            for g in quant_groups
            if g.get("product_id")
        }

        # Committed rentals overlapping the selected date range — aggregate in SQL
        rental_domain = [("state", "=", "ordered")]
        if rental_in_ids:
            rental_domain.append(("out_picking_id.location_id", "in", rental_in_ids))
        if date_from:
            rental_domain.append(
                ("start_datetime", "<=", (date_to or date_from) + " 23:59:59")
            )
        if date_to:
            rental_domain.append(
                ("end_datetime", ">=", (date_from or date_to) + " 00:00:00")
            )
        rental_groups = self.env["sale.rental"].read_group(
            rental_domain,
            ["rented_product_id", "rental_qty:sum"],
            ["rented_product_id"],
        )
        committed_qty = {
            g["rented_product_id"][0]: g["rental_qty"]
            for g in rental_groups
            if g.get("rented_product_id")
        }

        # Physical products with rental services
        physical_domain = [("rental_service_ids", "!=", False)]
        if location_id:
            product_ids = list(rental_in_qty.keys())
            if not product_ids:
                return []
            physical_domain.append(("id", "in", product_ids))

        physical = self.search_read(physical_domain, ["id", "rental_service_ids"])
        avail_map = {
            p["id"]: max(
                0,
                rental_in_qty.get(p["id"], 0) - committed_qty.get(p["id"], 0),
            )
            for p in physical
        }

        all_service_ids = []
        for p in physical:
            all_service_ids.extend(p["rental_service_ids"])

        if not all_service_ids:
            return []

        # Service products
        services = self.search_read(
            [("id", "in", all_service_ids)],
            ["id", "name", "rented_product_id"],
        )

        # Batch load all pricings for these services
        pricings = self.env["product.rental.pricing"].search_read(
            [("product_id", "in", all_service_ids)],
            ["product_id", "period_id", "price"],
        )
        pricing_map = {}
        for pr in pricings:
            pid = pr["product_id"][0]
            pricing_map.setdefault(pid, []).append(
                {"period_id": pr["period_id"][0], "price": pr["price"]}
            )

        for sp in services:
            physical_id = (
                sp["rented_product_id"][0] if sp["rented_product_id"] else None
            )
            sp["physicalProductId"] = physical_id
            sp["qty_available"] = avail_map.get(physical_id, 0) if physical_id else 0
            sp["pricings"] = pricing_map.get(sp["id"], [])

        return services

    @api.model
    def check_rental_availability(
        self, location_id, start_date, end_date, lines, exclude_order_id=None
    ):
        """Server-side availability check. Replaces 2 JS RPC calls with 1.

        :param location_id: rental_in location ID
        :param start_date: YYYY-MM-DD string
        :param end_date: YYYY-MM-DD string
        :param lines: [{'product_id': int (service), 'rental_qty': float}]
        :param exclude_order_id: order ID to exclude (for edits)
        :returns: list of error strings (empty = all available)
        """
        # Map service products to physical products
        service_ids = [line["product_id"] for line in lines]
        services = self.browse(service_ids)
        requested_qty = {}
        for line, service in zip(lines, services):
            physical_id = service.rented_product_id.id
            if physical_id:
                requested_qty[physical_id] = (
                    requested_qty.get(physical_id, 0) + line["rental_qty"]
                )

        if not requested_qty:
            return []

        # Stock at location — aggregate in SQL
        quant_groups = self.env["stock.quant"].read_group(
            [("location_id", "=", location_id), ("quantity", ">", 0)],
            ["product_id", "quantity:sum"],
            ["product_id"],
        )
        rental_in_qty = {
            g["product_id"][0]: g["quantity"]
            for g in quant_groups
            if g.get("product_id")
        }

        # Committed rentals overlapping date range — aggregate in SQL
        rental_domain = [
            ("state", "=", "ordered"),
            ("out_picking_id.location_id", "=", location_id),
            ("start_datetime", "<=", end_date + " 00:00:00"),
            ("end_datetime", ">=", start_date + " 00:00:00"),
        ]
        if exclude_order_id:
            rental_domain.append(("start_order_id", "!=", exclude_order_id))

        rental_groups = self.env["sale.rental"].read_group(
            rental_domain,
            ["rented_product_id", "rental_qty:sum"],
            ["rented_product_id"],
        )
        committed_qty = {
            g["rented_product_id"][0]: g["rental_qty"]
            for g in rental_groups
            if g.get("rented_product_id")
        }

        # Batch-load products only for those with insufficient availability
        errors = []
        error_ids = [
            pid
            for pid, req_qty in requested_qty.items()
            if req_qty > max(0, rental_in_qty.get(pid, 0) - committed_qty.get(pid, 0))
        ]
        if error_ids:
            products_by_id = {p.id: p for p in self.browse(error_ids)}
            for physical_id in error_ids:
                req_qty = requested_qty[physical_id]
                avail = max(
                    0,
                    rental_in_qty.get(physical_id, 0)
                    - committed_qty.get(physical_id, 0),
                )
                errors.append(
                    "%s: requested %s, available %s"
                    % (products_by_id[physical_id].display_name, req_qty, avail)
                )

        return errors
