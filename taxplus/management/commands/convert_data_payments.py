from django.core.management.base import BaseCommand, CommandError 
from datetime import date, datetime, time, timedelta
from taxplus.models import PaymentReceipt, PayFee, MultipayReceiptPaymentRelation, CategoryChoice, Entity
import dateutil.parser
from datetime import date
from django.utils import timezone
from django import db
from dateutil.relativedelta import relativedelta
import pdb
from django.db.models import Q


class Command(BaseCommand):
	#fixed_asset/rental_income/trading_license/cleaning_fee/market_fee/land_lease_fee
	args = ''
	help = """
	Transform old payment relational tables from jtax
	"""
	name= 'Convert tax dates'
	
	def handle(self, *args, **options):
		errors = []
		
		#handle existing multiple payments
		for pr in PaymentReceipt.objects.all():
			pay_fee = None
			for pay_fee in pr.line_items.all(): #filter(receipt__isnull=True):
				pay_fee.receipt = pr
				pay_fee.save()

			if pay_fee:
				pr.citizen_id = pay_fee.citizen_id
				pr.business_id = pay_fee.business_id
				pr.paid_date = pay_fee.paid_date
				pr.bank_receipt = pay_fee.receipt_no
				pr.sector_receipt = pay_fee.manual_receipt
				pr.bank = pay_fee.bank
				pr.note = pay_fee.note
				pr.status = CategoryChoice.objects.get(category__code='status', code=(pay_fee.i_status or 'active'))

				if pay_fee.business_id:
					try:
						pr.payer = Entity.objects.get(business_id = pay_fee.business_id)
					except Entity.DoesNotExist:
						pass
					else:
						pr.payer_name = pr.payer.name

				elif pay_fee.citizen_id:		
					try:
						pr.payer = Entity.objects.get(citizen_id = pay_fee.citizen_id)
					except Entity.DoesNotExist:
						pass
					else:
						pr.payer_name = pr.payer.name
				else:
					pass
					# print 'no payer found'

				pr.save()
				
		
		#handle payments that aren't multiple
		for pay_fee in PayFee.objects.filter(receipt__isnull=True):
			pr = PaymentReceipt()
			pr.amount = pay_fee.amount
			pr.citizen_id = pay_fee.citizen_id
			pr.business_id = pay_fee.business_id
			pr.paid_date = pay_fee.paid_date
			pr.bank_receipt = pay_fee.receipt_no
			pr.sector_receipt = pay_fee.manual_receipt
			pr.bank = pay_fee.bank
			pr.note = pay_fee.note
			try:
				pr.status = CategoryChoice.objects.get(category__code='status', code=(pay_fee.i_status or 'active'))
			except:
				raise Exception("Invalid status '%s'" % pay_fee.i_status)

			if pay_fee.business_id:
				try:
					pr.payer = Entity.objects.get(business_id = pay_fee.business_id)
				except Entity.DoesNotExist:
					pass
					#raise Exception("Cant find business %s" % pay_fee.business_id)
				else:
					pr.payer_name = pr.payer.name		

			elif pay_fee.citizen_id:
				try:
					pr.payer = Entity.objects.get(citizen_id = pay_fee.citizen_id)
				except Entity.DoesNotExist:
					pass
					#raise Exception("Cant find citizen %s" % pay_fee.citizen_id)
				else:
					pr.payer_name = pr.payer.name

			pr.save()
			pay_fee.receipt = pr
			pay_fee.save()
		


		cursor = db.connection.cursor()
		query = """
		begin;
		update jtax_fee set category_id = (select id from taxplus_categorychoice where category_id = 'fee_type' and code = jtax_fee.fee_type),
		status_id = (select id from taxplus_categorychoice where category_id = 'status' and code= jtax_fee.i_status )
		where fee_type in ('land_lease', 'cleaning') and category_id is null or status_id is null;
		commit;
		"""
		cursor.execute(query)

		query = """
		begin;
		update jtax_payfee set
		status_id = (select id from taxplus_categorychoice where category_id = 'status' and code= jtax_payfee.i_status )
		where status_id is null;
		commit;
		"""
		cursor.execute(query)





