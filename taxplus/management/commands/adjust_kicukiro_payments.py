from django.core.management.base import BaseCommand, CommandError
from datetime import date, datetime, time, timedelta
from taxplus.models import Fee
import dateutil.parser
from datetime import date, datetime
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
		fees = Fee.objects.filter(fee_payments__isnull=False, due_date__isnull=False).distinct()
		for fee in fees:
			fee.adjust_payments()
			print fee.pk






