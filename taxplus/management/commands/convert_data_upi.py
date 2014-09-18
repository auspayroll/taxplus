from django.core.management.base import BaseCommand, CommandError 
from datetime import date, datetime, time, timedelta
from taxplus.models import Property
import dateutil.parser
from datetime import date
from django.utils import timezone
from django import db
from dateutil.relativedelta import relativedelta


class Command(BaseCommand):
	#fixed_asset/rental_income/trading_license/cleaning_fee/market_fee/land_lease_fee
	args = ''
	help = """
	Transform old payment relational tables from jtax

	"""
	name= 'Convert land use types'
	
	def handle(self, *args, **options):
		errors = []

		for p in Property.objects.filter(upi__isnull=True):
			p.upi = p.get_upi()
			p.save





