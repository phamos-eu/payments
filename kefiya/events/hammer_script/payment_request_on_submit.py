import frappe
from frappe.utils import flt
from datetime import datetime
from frappe import _
import io

@frappe.whitelist()
def export_request(payment_request_name):
    
    buffer = io.StringIO()

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
                "Währung\n"
    buffer.write(hdrtext)

    def safe_format(value):
        return f'"{value}"' if value is not None else ""

    try:
        doc = frappe.get_doc("Payment Request", payment_request_name)
        partybankaccount = frappe.get_doc("Bank Account", doc.party_bank_account)
        bankaccount = frappe.get_doc("Bank Account", doc.bank_account)
        invoicedoc = frappe.get_doc(doc.reference_doctype, doc.reference_name)

        postext = f'{safe_format(doc.company)};'
        postext += f'{safe_format(bankaccount.iban)};'
        postext += f'{safe_format(bankaccount.branch_code)};'

        if doc.transaction_date:
            date_obj = datetime.strptime(str(doc.transaction_date), '%Y-%m-%d')
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
        buffer.write(postext)

        settings = frappe.get_single("Kefiya Settings")

        return {
            "status": "success",
            "csv_action": settings.payment_request_csv_action,
            "recipient_email": settings.recipient_email,
            "data": buffer.getvalue()
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}


@frappe.whitelist()
def send_csv_via_email(recipient_email, csv_content):
    try:
        subject = _("Your CSV File")
        message = _("Please find the attached CSV file.")
        
        attachments = [{
            "fname": "moneyplex_request.csv",
            "fcontent": csv_content,
        }]
        
        frappe.sendmail(
            recipients=[recipient_email],
            subject=subject,
            message=message,
            attachments=attachments,
            delayed=False,
            retry=3
        )

        return {"status": "success", "message": _("Email sent successfully.")}
    except Exception as e:
        return {"status": "error", "message": str(e)}