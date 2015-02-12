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
	Increments outstanding interest and penalties for all business fees.
	This should be run on the 5th of every month

	"""
	name= 'Convert land use types'

	def handle(self, *args, **options):
		for fee in Fee.objects.filter(is_paid=False, due_date__lte=date.today(), prop__isnull=False):
			fee.update_interest_penalty()

		print "Business fee interest/penalties updated %s" % datetime.now()


