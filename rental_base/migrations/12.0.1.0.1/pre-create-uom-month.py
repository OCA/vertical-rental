# -*- coding: utf-8 -*-


def migrate(cr, version):
    sql = """UPDATE ir_model_data
              SET module = 'rental_base'
            WHERE model = 'uom.uom'
              AND name = 'product_uom_month'"""
    cr.execute(sql)
