# -*- coding: utf-8 -*-


def migrate(cr, version):
    sql = """UPDATE product_template p
              SET rental = p.rental_ok"""
    cr.execute(sql)
