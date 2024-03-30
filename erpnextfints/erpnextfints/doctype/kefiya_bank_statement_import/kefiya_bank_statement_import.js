// Copyright (c) 2024, jHetzer and contributors
// For license information, please see license.txt

frappe.ui.form.on("Kefiya Bank Statement Import", {
	// after_save: function (frm) {
	// 	// Add a custom button after saving the document

	// 	// Add your custom button logic here
	// 	// For example, you can trigger a function or open a dialog
	// 	frm.add_custom_button(__("Unreconcile Transaction"), () => {
	// 		frm.call("remove_payment_entries").then(() => frm.refresh());
	// 	});
	// },

	refresh(frm) {
		if (frm.doc.import_file) {
			frm.add_custom_button(__("Start Import"), () => {
				frm.call("remove_payment_entries").then(() => frm.refresh());
			});
		}
	},
});
