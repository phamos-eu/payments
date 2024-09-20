frappe.ui.form.on('Payment Request', {
	refresh: function(frm) {
		frm.set_df_property('transaction_date', 'reqd', 1);
		frm.set_df_property('company', 'reqd', 1);
		frm.set_df_property('bank_account', 'reqd', 1);
		frm.set_df_property('party_bank_account', 'reqd', 1);
    },

    setup: function(frm) {
		frm.set_query("party_bank_account", function() {
			return {
				filters: {
					is_company_account: 0,
					party_type: frm.doc.party_type,
					party: frm.doc.party
				}
			}
		});

		frm.set_query("bank_account", function() {
			return {
				filters: {
					is_company_account: 1,
					company: frm.doc.company
				}
			}
		});	
	},
})