frappe.ui.form.on("Sales Invoice", {
	refresh: function (frm) {
		if (
			frm.doc.docstatus === 1 &&
			(frm.doc.status === "Paid" || frm.doc.status === "Partly Paid")
		) {
			frm.add_custom_button(__("Unpay"), function () {
				frappe.call({
					method: "erpnextfints.utils.client.remove_sales_invoice_payment",
					args: {
						sales_invoice_name: frm.doc.name,
					},
					callback(r) {
						// frappe.msgprint("Custom button clicked!");
					},
				});
			});
		}
	},
});
