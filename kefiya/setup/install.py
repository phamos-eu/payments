import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_fields
from frappe.custom.doctype.property_setter.property_setter import make_property_setter

def after_migrate():
	create_custom_fields(get_custom_fields())
	
def before_uninstall():
	delete_custom_fields(get_custom_fields())

def delete_custom_fields(custom_fields):
	for doctype, fields in custom_fields.items():
		for field in fields:
			custom_field_name = frappe.db.get_value(
				"Custom Field", dict(dt=doctype, fieldname=field.get("fieldname"))
			)
			if custom_field_name:
				frappe.delete_doc("Custom Field", custom_field_name)

		frappe.clear_cache(doctype=doctype)

def get_custom_fields():
	custom_fields_payment_request = [
        {
            "fieldname": "company",
            "fieldtype": "Link",
            "label": "Company",
            "options": "Company",
            "print_hide": 1,
            "remember_last_selected_value": 1,
            "insert_after": "mode_of_payment",
        },
		{
			"label": "Party Bank Account",
			"fieldname": "party_bank_account",
			"fieldtype": "Link",
            "options": "Bank Account",
            "depends_on": "party",
			"insert_after": "bank_account",
		}
	]

	return {
		"Payment Request": custom_fields_payment_request
	}