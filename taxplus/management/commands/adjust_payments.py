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

		"""
		for business in Business.objects.filter(business_fees__fee_payments__isnull=False).distinct():
			 balance = business.adjust_payments()
			 print business, balance
		"""


		for p in Property.objects.filter(property_fees__fee_payments__isnull=False).distinct():
			print 'Adjusting %s ' % p
			balance = p.adjust_payments()
			print p, balance

