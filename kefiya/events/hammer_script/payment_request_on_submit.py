import frappe
from frappe.utils import flt
from datetime import datetime

def export_request(doc,method):
    print('here******************')
    filename = "/tmp/payment_request_on_submit.log"
    
    with open(filename, "a") as f:
        f.write(f"{doc.doctype} | {doc.name} | {method} | start hook\n")
        f.write(f"{doc.doctype} | {doc.name} | {method} | {str(doc.as_dict())}\n")
  
    paymentrequest = frappe.get_doc("Payment Request", doc.name)
    partybankaccount = frappe.get_doc("Bank Account", doc.party_bank_account)
    bankaccount = frappe.get_doc("Bank Account", doc.bank_account)
    invoicedoc = frappe.get_doc(doc.reference_doctype, doc.reference_name)

    moneyfile = "/tmp/moneyplex_" + doc.name + ".csv"

    try:
        with open(moneyfile, "r"):
            pass
    except:
        with open(moneyfile, "a") as m:
            hdrtext =   "Kontoname;" + \
                        "Kontonummer;" + \
                        "Bankleitzahl;" + \
                        "Datum;" + \
                        "Valuta;" + \
                        "Name;" + \
                        "Iban;" + \
                        "Bic;" + \
                        "Zweck;" + \
                        "Kategorie;" + \
                        "Betrag;" + \
                        "Währung" + \
                        u"\n"
            m.write(hdrtext)  
    
    def safe_format(value):
        return f'"{value}"' if value is not None else ""

    with open(moneyfile, "a") as m:
        postext = f'{safe_format(doc.company)};'
        postext += f'{safe_format(bankaccount.iban)};'
        postext += f'{safe_format(bankaccount.branch_code)};'

        if doc.transaction_date:
            date_obj = datetime.strptime(doc.transaction_date, '%Y-%m-%d')
            formatted_date = date_obj.strftime('%d.%m.%Y')
            date = f'{formatted_date}'
            
            postext += f'{date};{date};'
        else:
            postext += ';;'

        postext += f'{safe_format(doc.party)};'
        postext += f'{safe_format(partybankaccount.iban)};'
        postext += f'{safe_format(partybankaccount.branch_code)};'
        
        if doc.payment_request_type == "Outward":
            bill_no = invoicedoc.bill_no if doc.reference_doctype == "Purchase Invoice" else ""
            postext += f'"Rechnung {bill_no if bill_no else doc.name}";'

        elif doc.payment_request_type == "Inward":
            postext += f'"Lastschrift {doc.name}";'

        postext += f'{safe_format(doc.mode_of_payment)};'

        if doc.payment_request_type == "Outward":
            postext += f'"{frappe.format(flt(invoicedoc.grand_total), {"fieldtype": "Float"})}";'
        elif doc.payment_request_type == "Inward":
            postext += f'"{frappe.format(-flt(invoicedoc.grand_total), {"fieldtype": "Float"})}";'

        postext += f'{safe_format(doc.currency)}\n'
        m.write(postext)