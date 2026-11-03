# Part of rental-vertical See LICENSE file for full copyright and licensing details.


def set_multi_sales_price(env):
    conf_page = env["res.config.settings"].create({})
    conf_page.group_uom = True
    conf_page.group_product_pricelist = True
    conf_page.product_pricelist_setting = "advanced"
    conf_page.execute()
