# -*- coding: utf-8 -*-
# Copyright (c) 2019, jHetzer and contributors
# For license information, please see license.txt
from __future__ import unicode_literals

from frappe import _


def get_data():  # noqa: D103
    return[{
        "label": _("Integrations"),
        "icon": "octicon octicon-git-compare",
        "items": [{
            "type": "doctype",
            "name": "Kefiya Import",
            "label": _("Kefiya Import"),
            "description": _("Kefiya Import")
        }, {
            "type": "doctype",
            "name": "Kefiya Login",
            "label": _("Kefiya Login"),
            "description": _("Kefiya Login")
        }, {
            "type": "doctype",
            "name": "Kefiya Schedule",
            "label": _("Kefiya Schedule"),
            "description": _("Kefiya Schedule")
        }]
    }, {
        "label": _("Tools"),
        "icon": "octicon octicon-git-compare",
        "items": [{
            "type": "page",
            "name": "bank_account_wizard",
            "label": _("Bank Account Wizard"),
            "description": _("Create bank accounts for parties")
        }, {
            "type": "page",
            "name": "assign_payment_entries",
            "label": _("Assign Payment Entries"),
            "description": _("Assign payment entries to sale invoices")
        }]
    }]
