from django.core.management.base import BaseCommand, CommandError
from datetime import date, datetime, time, timedelta
from taxplus.models import Business, Property, Fee, PaymentReceipt
import dateutil.parser
from datetime import date
from django.utils import timezone
from django import db
from dateutil.relativedelta import relativedelta
from django.db.models import Sum



class Command(BaseCommand):
	#fixed_asset/rental_income/trading_license/cleaning_fee/market_fee/land_lease_fee
	args = ''
	help = """
	Adds entity relationship to fees
	This will be the entity responsible for fee payment

	"""
	name= 'Convert land use types'

	def handle(self, *args, **options):
		errors = []

		for prop in Property.objects.filter(property_fees__fee_payments__isnull=False).distinct():
			credit = 0
			for fee in prop.property_fees.filter(fee_payments__isnull=False).distinct():
				credit += fee.pay()

			prop.credit = credit
			prop.save(update_fields=['credit'])
			print prop.upi, credit


		for business in Business.objects.filter(business_fees__fee_payments__isnull=False).distinct():
			credit = 0
			for fee in business.business_fees.filter(fee_payments__isnull=False).distinct():
				credit += fee.pay()

			business.credit = credit
			business.save(update_fields=['credit'])
			print business, credit


		for receipt in PaymentReceipt.objects.all():
			receipt.credit = receipt.receipt_payments.aggregate(total=Sum('credit'))['total'] or 0
			print receipt.credit
			receipt.save(update_fields=['credit'])

