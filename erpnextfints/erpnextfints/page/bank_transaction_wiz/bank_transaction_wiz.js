// Copyright (c) 2019, jHetzer and contributors
// For license information, please see license.txt
frappe.provide("erpnextfints.tools");

frappe.pages["bank-transaction-wiz"].on_page_load = function (wrapper) {
	erpnextfints.tools.assignWizardObj = new erpnextfints.tools.assignWizard(
		wrapper
	);
};

erpnextfints.tools.assignWizard = class assignWizard {
	constructor(wrapper) {
		this.page = frappe.ui.make_app_page({
			parent: wrapper,
			title: __("Bank Transaction Wizard"),
			single_column: true,
		});
		this.parent = wrapper;
		this.page = this.parent.page;
		this.remove_page_buttons();
		this.make();
	}
	remove_page_buttons(){
		$('.custom-actions').remove()
		$('.page-form').remove();	
	}

	async fetchKefiyaSettings() {
		const response = await frappe.call({
			method: "frappe.client.get",
			args: {
				doctype: "Kefiya Settings",
				name: "Kefiya Settings",
			},
		});
		return response.message;
	}

	async make() {
		const me = this;
		me.clear_page_content();
		let result = await this.fetchKefiyaSettings()
		me.make_assignWizard_tool(result);
		// me.add_actions();
	}

	add_actions() {
		const me = this;

		me.page.show_menu();
		me.page.add_menu_item(
			__("Auto assign"),
			function () {
				frappe.call({
					method: "erpnextfints.utils.client.auto_assign_payments",
					args: {},
					callback: function (r) {
						if (r.message.success === true) {
							var result = [];
							if (
								Array.isArray(r.message.payments) &&
								r.message.payments.length
							) {
								result.push(__("Assingment was successfull"));
								r.message.payments.forEach(function (item) {
									result.push(
										__("Payment") +
											" " +
											get_doc_link("Payment Entry", item.PaymentName) +
											" " +
											__("from customer") +
											" " +
											get_doc_link("Customer", item.CustomerName) +
											" " +
											__("has been assinged to sale invoice") +
											" " +
											get_doc_link("Sales Invoice", item.SaleName)
									);
								});
							} else {
								result.push(__("No payments were found for assignment"));
							}
							erpnextfints.tools.assignWizardList.refresh();
							frappe.msgprint(result);
						} else {
							frappe.msgprint(__("Failed to assign payments"));
						}
					},
				});
			},
			true
		);
	}

	clear_page_content() {
		const me = this;
		me.page.clear_fields();
		$(me.page.body).find(".frappe-list").remove();
	}

	make_assignWizard_tool(kefiyaSettings) {
		const me = this;
		// ensure that the metadata for the "Sales Invoice" DocType is loaded before proceeding with the wizard setup(AssignWizardTool).
		if (kefiyaSettings.assign_against==='Sales Invoice'){
			frappe.model.with_doctype("Sales Invoice", () => {
				erpnextfints.tools.assignWizardList =
					new erpnextfints.tools.AssignWizardTool({
						parent: me.parent,
						doctype: "Sales Invoice",
						page_title: __(me.page.title),
						kefiyaSettings: kefiyaSettings
					});
				frappe.pages["bank-transaction-wiz"].refresh =
					function (/* wrapper */) {
						window.location.reload(false);
					};
			});
		} else if (kefiyaSettings.assign_against==='Purchase Invoice'){
			frappe.model.with_doctype("Purchase Invoice", () => {
				erpnextfints.tools.assignWizardList =
					new erpnextfints.tools.AssignWizardTool({
						parent: me.parent,
						doctype: "Purchase Invoice",
						page_title: __(me.page.title),
						kefiyaSettings: kefiyaSettings
					});
				frappe.pages["bank-transaction-wiz"].refresh =
					function (/* wrapper */) {
						window.location.reload(false);
					};
			});
		}

	}
};

erpnextfints.tools.AssignWizardTool = class AssignWizardTool extends (
	frappe.views.BaseList
) {
	constructor(opts) {
		super(opts);
		this.kefiyaSettings = opts.kefiyaSettings
		this.show();
	}

	// It establishes default settings for various aspects of the assignment wizard tool's data display and behavior
	setup_defaults() {
		super.setup_defaults();
		this.page_length = 100;
		this.sort_order = "asc";
		if (this.kefiyaSettings.assign_against === 'Sales Invoice'){
			this.sort_by = "customer";
			this.fields = [
				"name",
				"customer",
				"customer_name",
				"outstanding_amount",
				"posting_date",
				"due_date",
				"currency",
				"paid_amount",
			];
		} else if (this.kefiyaSettings.assign_against === 'Purchase Invoice'){
			this.sort_by = "supplier";
			this.fields = [
				"name",
				"supplier",
				"supplier_name",
				"outstanding_amount",
				"posting_date",
				"due_date",
				"currency",
				"paid_amount",
			];
		}
	}

	setup_view() {
		this.render_header();
	}

	setup_side_bar() {
		//
	}

	set_breadcrumbs() {
		frappe.breadcrumbs.add("ERPNextFinTS");
	}

	make_standard_filters() {
		//
	}

	freeze() {
		// this.$result.find('.list-count').html(`<span>${__('Refreshing')}...</span>`);
	}

	get_args() {
		const args = super.get_args();
		
		if (this.kefiyaSettings.assign_against === 'Sales Invoice'){
			return Object.assign({}, args, {
				...args.filters.push(
					["Sales Invoice", "docstatus", "=", 1],
					["Sales Invoice", "outstanding_amount", ">", 0]
				),
			});
		} else if(this.kefiyaSettings.assign_against === 'Purchase Invoice'){
			return Object.assign({}, args, {
				...args.filters.push(
					["Purchase Invoice", "docstatus", "=", 1],
					["Purchase Invoice", "outstanding_amount", ">", 0]
				),
			});
		}

	}

	get_row_call_args(party, optionValue, matchAgainst) {
		let doctype, fields, filters, order_by;
		
		if (optionValue == "Payment Entry") {
			doctype = "Payment Entry";
			fields = [
				"name",
				"party",
				"posting_date",
				"unallocated_amount",
				"remarks",
			];
			filters = {
				docstatus: 0,
				party: party,
			};
			order_by = "posting_date";
		} else if (optionValue == "Bank Transaction") {
			doctype = "Bank Transaction";
			fields = [
				"name", 
				"party",
				"date", 
				"unallocated_amount", 
				"description"
			];
			
			filters = {
				docstatus: 1,
				party: party,
				unallocated_amount: [">", 0],
				...(matchAgainst === "Sales Invoice" ? { deposit: [">", 0] } : {}),
				...(matchAgainst === "Purchase Invoice" ? { withdrawal: [">", 0] } : {})
			};
			order_by = "date";
		} else {
			// code if both are selected
		}
		return {
			method: "frappe.client.get_list",
			args: {
				doctype,
				fields,
				filters,
				order_by,
			},
			freeze: this.freeze_on_refresh || false,
			freeze_message: this.freeze_message || __("Loading") + "...",
		};
	}

	async render() {
		// Extract the selected value from "Kefiya Settings" doctype
		const optionValue = this.kefiyaSettings.show_entries_in_payment_assignment_wizard
		const matchAgainst = this.kefiyaSettings.assign_against

		const me = this;
		this.$result.find(".list-row-contain").remove();
		$('[data-fieldname="name"]').remove();
		$('[data-fieldname="status"]').remove();
		$('[data-fieldname="title"]').remove();
		
		let rowHTML;
		let party_value;
		// me.data - list of sales invoice. the below code fetchs all payment entries(Payment Entry and Bank Transaction) associated with single sales invoice

		for (const value of me.data) {
			rowHTML = '<div class="list-row-contain"></div>';

			if (matchAgainst==="Sales Invoice"){
				party_value = value.customer
			} else if (matchAgainst === "Purchase Invoice"){
				party_value = value.supplier
			}

			const r = await frappe.call(
				this.get_row_call_args(party_value, optionValue, matchAgainst)
			);

			// r.message - list of all payment entries
			if (Array.isArray(r.message) && r.message.length) {
				const row = $(rowHTML).data("data", value).appendTo(me.$result).get(0);

				new erpnextfints.tools.AssignWizardRow(
					row,
					value,
					r.message,
					optionValue,
					matchAgainst
				);
			}
		}
	}

	render_header() {
		const me = this;
		if ($(this.wrapper).find(".payment-assign-wizard-header").length === 0) {
			me.$result.append(frappe.render_template("bank_transaction_header"));
		}
	}
};

erpnextfints.tools.AssignWizardRow = class AssignWizardRow {
	constructor(row, data, payments, optionValue, matchAgainst) {
		this.data = data;
        // system default for date
		let sysdefaults = frappe.sys_defaults;
		let date_format = sysdefaults && sysdefaults.date_format ? sysdefaults.date_format : "yyyy-mm-dd";
		date_format = date_format.replace('yyyy', 'YYYY').replace('dd', 'DD').replace('mm', 'MM');

		// formatting date based on system defaults
		this.data.outstanding_amount = format_currency(this.data.outstanding_amount, this.data.currency); 
		this.data.posting_date = moment(this.data.posting_date).format(date_format);

		this.data.payments = payments;

		this.data.payments.forEach(payment => {
			payment.date = moment(payment.date).format(date_format);
			payment.unallocated_amount = format_currency(payment.unallocated_amount, this.data.currency);
		});

		this.data.optionValue = optionValue;
		this.data.matchAgainst = matchAgainst;
		this.row = row;
		this.make();
		this.bind_events();
	}

	make() {
	
		$(this.row).append(frappe.render_template("bank_transaction_row", this.data));
	}

	bind_events() {
		const me = this;

		$(me.row).on("click", ".hide_row", function () {
			me.row.remove();
		});
		// assign payment entries to sales invoice
		$(me.row).on("click", ".assign_payment", function () {
			frappe.call({
				method: "erpnextfints.utils.client.add_payment_reference",
				args: {
					sales_invoice: me.data.name,
					payment_entry: $(this).attr("data-name"),
				},
				callback(/* r */) {
					// Refresh page after asignment
					erpnextfints.tools.assignWizardList.refresh();
				},
			});
		});

		// reconcile bank transaction against sales invoice
		$(me.row).on("click", ".reconcile_transaction", function () {
			const currency = me.data.currency;
			const invoice_name = me.data.name;
			const match_against = me.data.matchAgainst;
			const bank_transaction_name = $(this).attr("data-name");

			frappe.call({
				method: "erpnextfints.utils.client.create_payment_entry",
				args: {
					bank_transaction_name: bank_transaction_name,
					invoice_name: invoice_name,
					match_against: match_against
				},
				callback: function (r) {
					let vouchers = [];

					const paid_amount = r.message[0];
					const payment_entry_name = r.message[1];

					vouchers.push({
						payment_doctype: "Payment Entry",
						payment_name: payment_entry_name,
						amount: format_currency(paid_amount, currency),
					});
					
					frappe.call({
						method:
							"erpnext.accounts.doctype.bank_reconciliation_tool.bank_reconciliation_tool.reconcile_vouchers",
						args: {
							bank_transaction_name: bank_transaction_name,
							vouchers: vouchers,
						},
						callback(/* r */) {
							// Refresh page after asignment		
							erpnextfints.tools.assignWizardList.refresh();
						},
					});
				},
			});

		});
	}
};

function get_doc_link(doctype, name) {
	return '<a href="#Form/' + doctype + "/" + name + '"><b>' + name + `</b></a>`;
}
