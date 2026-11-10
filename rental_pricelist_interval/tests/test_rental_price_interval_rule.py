# Part of rental-vertical See LICENSE file for full copyright and licensing details.

from odoo.exceptions import AccessError
from odoo.tests import new_test_user

from odoo.addons.rental_base.tests.stock_common import RentalStockCommon


class TestRentalPriceIntervalRule(RentalStockCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.RuleObj = cls.env["rental.price.interval.rule"]
        cls.company = cls.env.company
        cls.other_company = cls.env["res.company"].create(
            {"name": "Rental Interval Other Company"}
        )
        cls.rule = cls.RuleObj.create(
            {
                "name": "0-7 interval",
                "factor": 1,
                "min_quantity": 0,
                "company_id": cls.company.id,
            }
        )
        cls.other_rule = cls.RuleObj.create(
            {
                "name": "0-7 interval (other)",
                "factor": 1.5,
                "min_quantity": 0,
                "company_id": cls.other_company.id,
            }
        )
        company_values = {
            "company_id": cls.company.id,
            "company_ids": [(6, 0, cls.company.ids)],
        }
        cls.user = new_test_user(
            cls.env,
            login="rental_interval_user",
            groups="base.group_user",
            **company_values,
        )
        cls.manager = new_test_user(
            cls.env,
            login="rental_interval_access_manager",
            groups="base.group_user,base.group_erp_manager",
            **company_values,
        )

    def test_internal_user_reads_own_company_rules(self):
        rules = self.RuleObj.with_user(self.user).search([])
        self.assertIn(self.rule, rules)
        self.assertNotIn(self.other_rule, rules)

    def test_internal_user_cannot_change_rules(self):
        with self.assertRaises(AccessError):
            self.rule.with_user(self.user).write({"factor": 2})
        with self.assertRaises(AccessError):
            self.RuleObj.with_user(self.user).create(
                {"name": "8-14 interval", "factor": 1.75, "min_quantity": 8}
            )
        with self.assertRaises(AccessError):
            self.rule.with_user(self.user).unlink()

    def test_access_manager_edits_rules_from_company(self):
        self.company.with_user(self.manager).write(
            {
                "rental_price_interval_rule_ids": [
                    (0, 0, {"name": "8-14 interval", "factor": 1.75, "min_quantity": 8})
                ]
            }
        )
        self.assertIn(
            "8-14 interval",
            self.company.rental_price_interval_rule_ids.mapped("name"),
        )
