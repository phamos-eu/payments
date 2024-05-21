// Copyright (c) 2024, jHetzer and contributors
// For license information, please see license.txt

frappe.ui.form.on("Kefiya Bank Statement Import", {
	setup(frm){
		frappe.realtime.on('update_import_status', function(data) {
			frm.reload_doc();
		});
	},
	refresh(frm) {
		$('.menu-btn-group').remove()
		frm.page.hide_icon_group();


		if (frm.doc.import_file &&
			frm.doc.status !== 'Success' && 
            frm.doc.status !== 'Partial Success' && 
            frm.doc.status !== 'Error'
		) {
			 frm.disable_save();
			frm.page.set_primary_action("Start Import", () =>  {
					frm.call("start_import", {
						file_url: frm.doc.import_file,
						bank_account: frm.doc.bank_account,
						company: frm.doc.company,
					});
				});
		}


		if (frm.doc.status.includes("Success")) {
			frm.disable_save();
			frm.add_custom_button(__("Go to Bank Transaction List"), () =>
				frappe.set_route("List", "Bank Transaction")
			);
		}

		if (frm.doc.status.includes("Error")) {
			frm.disable_save();
			frm.page.set_primary_action("Retry", () =>  {
					frm.call("start_import", {
						file_url: frm.doc.import_file,
						bank_account: frm.doc.bank_account,
						company: frm.doc.company,
					});
				});
		}

		if(!frm.is_new()){
			frm.trigger('set_headline')
		}
	},

	set_headline(frm){
		let message='';
		let indicator='';
	
		if (frm.doc.status === 'Success') {
			message = `Successfully imported ${ frm.doc.imported_records} records.`;
			indicator = 'blue';
		} 
		else if (frm.doc.status === 'Partial Success') {
			message = `Successfully imported ${ frm.doc.imported_records} records out of ${frm.doc.payload_count}. Fix the error for unimported rows.`;
			indicator = 'orange';
		}
		
		frm.dashboard.set_headline(message, indicator);
	}
});
