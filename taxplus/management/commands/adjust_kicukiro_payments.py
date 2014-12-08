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
		today = timezone.make_aware(datetime.now().replace(hour=0, minute=0, second=0, microsecond=0), timezone.get_default_timezone())
		fees = Fee.objects.filter(fee_payments__isnull=False, due_date__isnull=False, date_time__lt=today).distinct().order_by('id')
		for fee in fees:
			print fee.pk
			fee.adjust_payments()







