# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import SUPERUSER_ID, Command, api


def migrate(cr, version):
    """Keep the Rentals menu visible for the salesmen who saw it before it
    was restricted to group_rental_menu."""
    if not version:
        return
    env = api.Environment(cr, SUPERUSER_ID, {})
    salesmen = env.ref("sales_team.group_sale_salesman").users
    env.ref("rental_base.group_rental_menu").write(
        {"users": [Command.link(user.id) for user in salesmen]}
    )
