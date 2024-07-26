# -*- coding: utf-8 -*-
# Copyright (c) 2019, jHetzer and contributors
# For license information, please see license.txt

from __future__ import unicode_literals

import frappe


def execute(): # noqa E103
    frappe.reload_doc("kefiya", "doctype", "fints_login")
    frappe.db.sql("""
            Update
                `tabKefiya Login`
            set
                `tabKefiya Login`.enable_pay = 0
            where
                `tabKefiya Login`.default_supplier IS NULL
                and `tabKefiya Login`.enable_pay = 1""")
