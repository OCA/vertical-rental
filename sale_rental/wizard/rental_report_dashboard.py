from odoo import api, fields, models


class RentalReportDashboard(models.TransientModel):
    _name = "rental.report.dashboard"
    _description = "Rental Report Dashboard"

    date_from = fields.Date(readonly=True)
    date_to = fields.Date(readonly=True)

    total_rental_products = fields.Integer(compute="_compute_kpis")
    active_rentals = fields.Integer(compute="_compute_kpis")
    average_rental_duration = fields.Float(
        "Average Rental Duration (hrs)", compute="_compute_kpis"
    )
    average_utilization_rate = fields.Float(
        "Average Utilization Rate (%)", compute="_compute_kpis"
    )

    @api.depends("date_from", "date_to")
    def _compute_kpis(self):
        Rental = self.env["sale.rental"]
        for rec in self:
            domain = []
            if rec.date_from:
                domain.append(
                    (
                        "end_datetime",
                        ">=",
                        fields.Datetime.from_string(str(rec.date_from) + " 00:00:00"),
                    )
                )
            if rec.date_to:
                domain.append(
                    (
                        "start_datetime",
                        "<=",
                        fields.Datetime.from_string(str(rec.date_to) + " 23:59:59"),
                    )
                )

            rentals = Rental.search(domain)

            total_products = len(set(rentals.mapped("rented_product_id.id")))
            active_rentals = len(
                rentals.filtered(lambda r: r.state in ("out", "sell_progress"))
            )
            total_hours = sum(r.actual_rental_hours for r in rentals)
            total_available = sum(r.available_hours for r in rentals)
            total_orders = len(rentals)
            avg_duration = total_hours / total_orders if total_orders else 0.0
            util_rate = (
                (total_hours / total_available * 100) if total_available else 0.0
            )

            rec.total_rental_products = total_products
            rec.active_rentals = active_rentals
            rec.average_rental_duration = avg_duration
            rec.average_utilization_rate = util_rate
