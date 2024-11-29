frappe.ui.form.on('Payment Request', {
    refresh: function(frm) {
        frm.set_df_property('transaction_date', 'reqd', 1);
        frm.set_df_property('company', 'reqd', 1);
        frm.set_df_property('bank_account', 'reqd', 1);
        frm.set_df_property('company_bank_account', 'reqd', 1);
    },

    setup: function(frm) {
        frm.set_query("company_bank_account", function() {
            return {
                filters: {
                    is_company_account: 1,
                    company: frm.doc.company
                }
            }
        });

        frm.set_query("bank_account", function() {
            return {
                filters: {
                    is_company_account: 0,
                    party_type: frm.doc.party_type,
                    party: frm.doc.party
                }
            }
        });
    },

    before_submit: function(frm) {

        frappe.call({
            method: "kefiya.events.hammer_script.payment_request_on_submit.export_request",
            args: {
                payment_request_name: frm.doc.name
            },
            callback: function(r) {
                if (r.message.status == "success") {
                    if (r.message.csv_action == "Download CSV"){
						var csvContent = r.message.data;
						var blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });

						var link = document.createElement("a");
						if (link.download !== undefined) {
							var url = URL.createObjectURL(blob);
							link.setAttribute("href", url);
							link.setAttribute("download", "moneyplex_" + frm.doc.name + ".csv");
							link.style.visibility = 'hidden';
							document.body.appendChild(link);
							link.click();
							document.body.removeChild(link);
						}
					}
					else if (r.message.csv_action == "Send CSV via Email") {

						const recipient_email = r.message.recipient_email;
						const csv_content = r.message.data;

                        frappe.msgprint({
                            title: __('Sending Email'),
                            indicator: 'blue',
                            message: __('Email is being sent to {0}. Please wait...', [recipient_email])
                        });

						frappe.call({
							method: "kefiya.events.hammer_script.payment_request_on_submit.send_csv_via_email",
							args: {
								recipient_email,
								csv_content
							},
							callback: function (r) {
								
								if (r.message) {
									if (r.message.status === "success") {
										frappe.show_alert({
                                            message: __('Email sent successfully to {0}', [recipient_email]),
                                            indicator: 'green'
                                        });
									} else {
										frappe.msgprint({
											title: __('Error'),
											indicator: 'red',
											message: r.message.message
										});
										frappe.validated = false;
									}
								}
							}
						})
					}
                } else {
					frappe.msgprint(__('Error during CSV export: {0}', [r.message.message]));
					frappe.validated = false;
                }
            }
        });
    }
});
