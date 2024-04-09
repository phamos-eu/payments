import frappe
from frappe.model.document import Document
import csv
import os
from frappe.utils.file_manager import get_file_path
from datetime import datetime
from frappe import _
import chardet
import locale

class KefiyaBankStatementImport(Document):
	@frappe.whitelist()
	def start_import(self, file_url, bank_account, company):
		file_path = self.get_file_from_url(file_url)
		# Detect encoding
		with open(file_path, 'rb') as f:
			rawdata = f.read()
			result = chardet.detect(rawdata)
			encoding = result['encoding']

		total_rows = sum(1 for _ in open(file_path, mode='r', encoding=encoding))-7
		
		with open(file_path, mode='r', encoding=encoding, errors='replace') as csvfile:
			csv_reader = csv.reader(csvfile)
			# skip header (the first 7 rows)
			for _ in range(7):
				next(csv_reader)

			frappe.publish_progress(0, title='Importing Bank Transaction', description='Starting import...')

			if encoding=='utf-8':
		
				for index, row in enumerate(csv_reader):
					
					self.create_new_doc_utf8(row, bank_account, company)
					index+=1
					progress = int((index / total_rows) * 100)
					frappe.publish_progress(progress, title='Importing Bank Transaction', description=f'Processing row {index}/{total_rows}')

			if encoding=='ISO-8859-1':
				
				for index, row in enumerate(csv_reader):
					
					self.create_new_doc_iso(row, bank_account, company)
					index+=1
					progress = int((index / total_rows) * 100)
					frappe.publish_progress(progress, title='Importing Bank Transaction', description=f'Processing row {index}/{total_rows}')

	def get_file_from_url(self, file_url):
		
		file_path = get_file_path(file_url.split('/')[-1])
		if not os.path.exists(file_path):
			frappe.throw(_('File not found: {0}').format(file_path))
		
		return file_path

	# utf-8
	def create_new_doc_utf8(self, row_data, bank_account, company):
        # This function create a new document from a csv row
		try:
			bank_transaction = frappe.new_doc("Bank Transaction")
			date =  datetime.strptime( row_data[0], '%d.%m.%Y')
			description = row_data[4]
			bank_party_iban = row_data[5]
			deposit, withdrawal = self.format_amount_utf8(row_data[7])			

			bank_transaction.update({
				"date": date.strftime('%Y-%m-%d'),
				"deposit": deposit,
				"withdrawal": withdrawal, 
				"bank_account": bank_account,
				"company": company,
				"description": description,
				'bank_party_iban': bank_party_iban,
				'allocated_amount': 0,
				'unallocated_amount': abs(withdrawal - deposit)
			})

			bank_transaction.insert()
		except Exception as e:
			frappe.msgprint(f'Error creating document for row: {row_data} - {e}')
	
	def format_amount_utf8(self, amount):
		deposit, withdrawal = 0,0

		if '.' in amount:
			amount = amount.replace('.', '')
		if ',' in amount:
			amount = amount.replace(',', '.')

		amount = float(amount)
		if amount >= 0:
			deposit = amount
		else:
			withdrawal = abs(amount)

		return [deposit, withdrawal]


	# ISO-8859-1
	def create_new_doc_iso(self, row_data, bank_account, company):
        # This function create a new document from a csv row
		
		row_data = ''.join(row_data)
		row_data = row_data.split(';')
		try:
			bank_transaction = frappe.new_doc("Bank Transaction")
			date =  datetime.strptime( row_data[0], '%d.%m.%Y')
			description = row_data[4].replace('"', '')
			bank_party_iban = row_data[5].replace('"', '')
			deposit, withdrawal = self.format_amount_iso(row_data[7])			

			bank_transaction.update({
				"date": date.strftime('%Y-%m-%d'),
				"deposit": deposit,
				"withdrawal": withdrawal, 
				"bank_account": bank_account,
				"company": company,
				"description": description,
				'bank_party_iban': bank_party_iban,
				'allocated_amount': 0,
				'unallocated_amount': abs(withdrawal - deposit)
			})

			bank_transaction.insert()
		except Exception as e:
			frappe.msgprint(f'Error creating document for row: {row_data} - {e}')
	
	def format_amount_iso(self, amount):
		deposit, withdrawal = 0,0

		if '"' in amount:
			amount = amount.replace('"', '')

		if ',' in amount and '.' in amount:
			amount = amount.replace('.', '').replace(',', '.')
		elif ',' in amount:
			amount = amount.replace(',', '.')
		elif '.' in amount:
			amount = amount.replace('.', '')
			integer_part = amount[:-2]
			decimal_part = amount[-2:]
			amount = integer_part + '.' + decimal_part
		else:
			try:
				integer_part = amount[:-2]
				decimal_part = amount[-2:]
				amount = integer_part + '.' + decimal_part
			except Exception as e:
				frappe.msgprint(f'currency formatting not supported for row: {row_data} - {e}')

		amount = float(amount)
		if amount >= 0:
			deposit = amount
		else:
			withdrawal = abs(amount)

		return [deposit, withdrawal]