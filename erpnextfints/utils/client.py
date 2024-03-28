# -*- coding: utf-8 -*-
# Copyright (c) 2019, jHetzer and contributors
# For license information, please see license.txt
from __future__ import unicode_literals

import frappe
from frappe.utils import getdate


@frappe.whitelist()
def import_fints_transactions(fints_import, fints_login, user_scope):
    """Create payment entries by FinTS transactions.

    :param fints_import: fints_import doc name
    :param fints_login: fints_login doc name
    :param user_scope: Current open doctype page
    :type fints_import: str
    :type fints_login: str
    :type user_scopet: str
    :return: List of max 10 transactions and all new payment entries
    """
    from erpnextfints.utils.fints_controller import FinTSController
    interactive = {"docname": user_scope, "enabled": True}

    return FinTSController(fints_login, interactive) \
        .import_fints_transactions(fints_import)


@frappe.whitelist()
def get_accounts(fints_login, user_scope):
    """Create payment entries by FinTS transactions.

    :param fints_login: fints_login doc name
    :param user_scope: Current open doctype page
    :type fints_login: str
    :type user_scopet: str
    :return: FinTS accounts json formated
    """
    from erpnextfints.utils.fints_controller import FinTSController
    interactive = {"docname": user_scope, "enabled": True}

    return {
        "accounts": FinTSController(
            fints_login,
            interactive).get_fints_accounts()
    }


@frappe.whitelist()
def new_bank_account(payment_doc, bankData):
    """Create new bank account.

    Create new bank account and if missing a bank entry.
    :param payment_doc: json formated payment_doc
    :param bankData: json formated bank information
    :type payment_doc: str
    :type bankData: str
    :return: Dict with status and bank details
    """
    from erpnextfints.utils.bank_account_controller import \
        BankAccountController
    return BankAccountController().new_bank_account(payment_doc, bankData)


@frappe.whitelist()
def get_missing_bank_accounts():
    """Get possibly missing bank accounts.

    Query payment entries for missing bank accounts.
    :return: List of payment entry data
    """
    from erpnextfints.utils.bank_account_controller import \
        BankAccountController
    return BankAccountController().get_missing_bank_accounts()


@frappe.whitelist()
def has_page_permission(page_name):
    """Check if user has permission for a page doctype.

    Based on frappe/desk/desk_page.py
    :param page_doc: page doctype object
    :type page_doc: page doctyp
    :return: Boolean
    """
    from erpnextfints.utils.bank_account_controller import \
        has_page_permission
    return has_page_permission(page_name)


@frappe.whitelist()
def add_payment_reference(payment_entry, sales_invoice):
    """Add payment reference to payment entry for sales invoice.

    Create new bank account and if missing a bank entry.
    :param payment_entry: json formated payment_doc
    :param sales_invoice: json formated bank information
    :type payment_entry: str
    :type sales_invoice: str
    :return: Payment reference name
    """
    from erpnextfints.utils.assign_payment_controller import \
        AssignmentController

    return AssignmentController().add_payment_reference(
        payment_entry,
        sales_invoice
    )


@frappe.whitelist()
def auto_assign_payments():
    """Query assignable payments and create payment references.

    Try to assign payments in 3 steps:
    1. payment to sale assingment
    2. multiple payments to sale assingment
    3. payment to sale assingment

    :return: List of assigned payments
    """
    from erpnextfints.utils.assign_payment_controller import \
        AssignmentController

    return AssignmentController().auto_assign_payments()



# Add sales invoice payment on the specified sales invoice
@frappe.whitelist()
def add_sales_invoice_payment(bank_transaction_name, sales_invoice_name):
    """Create sales invoice payment on sales invoice doctype.

    1, get sales_invoice document based on sales_invoice value
    2, create new entry on sales invoice payment child table
    3, save and return the sales invoice document
    """

    kefiya_setting = frappe.get_single("Payment Wizard Setting")
    
    # query to get account
    result = frappe.db.sql("""
        SELECT company, default_account
        FROM `tabMode of Payment Account`
        WHERE parent = %s
    """, (kefiya_setting.mode_of_payment,), as_dict=True)

    account = result[0].default_account
  
    
    bank_transaction = frappe.get_doc("Bank Transaction", bank_transaction_name)
    sales_invoice = frappe.get_doc("Sales Invoice", sales_invoice_name)
    
    
    unallocated_amount = bank_transaction.unallocated_amount
    outstanding_amount = sales_invoice.outstanding_amount
    paid_amount = 0

    if unallocated_amount >= outstanding_amount:
        paid_amount = outstanding_amount
        outstanding_amount = 0
        
    else:
        outstanding_amount = outstanding_amount - unallocated_amount
        paid_amount = unallocated_amount


    sales_invoice_payment = frappe.new_doc("Sales Invoice Payment")

    # Set fields for the Sales Invoice Payment document
    sales_invoice_payment.update({
        "mode_of_payment": kefiya_setting.mode_of_payment,
        "account": account,
        "amount": paid_amount, 
        "parent": sales_invoice_name,
        'parentfield': 'payments',
        'parenttype': 'Sales Invoice'
    })

    sales_invoice_payment.insert()

    # Get total paid amount on certain sales invoice
    paid_amounts = frappe.db.sql("""
        SELECT SUM(amount) AS total_paid_amount
        FROM `tabSales Invoice Payment`
        WHERE parent = %s
        GROUP BY parent
    """, (sales_invoice_name,), as_dict=True)

    if  outstanding_amount==0:
        status = "Paid"
    else:
        status = "Partly Paid"
    
    total_paid_amount = paid_amounts[0].total_paid_amount
    sql_query = """
        UPDATE `tabSales Invoice`
        SET is_pos = 1, outstanding_amount = %s, paid_amount = %s, status = %s
        WHERE name = %s
    """
    
    frappe.db.sql(sql_query, (outstanding_amount, total_paid_amount, status, sales_invoice_name))
    return total_paid_amount


@frappe.whitelist()
def remove_sales_invoice_payment(sales_invoice_name):
   
    sales_invoice = frappe.get_doc("Sales Invoice", sales_invoice_name)
    total_paid_amount = sales_invoice.paid_amount
    frappe.db.sql("""
        DELETE FROM `tabSales Invoice Payment`
        WHERE parent = %s
    """, (sales_invoice_name,))
    
    status="Draft"
    today = getdate()

    if sales_invoice.outstanding_amount == 0 and getdate(sales_invoice.due_date) >= today:
        status = "Unpaid"

    if sales_invoice.outstanding_amount > 0 and getdate(sales_invoice.due_date) >= today:
        status = "Partly Paid"

    if getdate(sales_invoice.due_date) < today:
        status = "Overdue"

    sql_query = """
        UPDATE `tabSales Invoice`
        SET is_pos = 0, outstanding_amount = %s, paid_amount = %s, status = %s
        WHERE name = %s
    """
    
    frappe.db.sql(sql_query, (total_paid_amount, 0, status, sales_invoice_name))
   
    message = frappe._("{0} unlinked successfully").format(sales_invoice_name)
    frappe.msgprint(message)