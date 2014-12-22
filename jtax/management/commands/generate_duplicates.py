from django.core.management.base import BaseCommand, CommandError
from log.models import CronLog
from datetime import date, datetime, time, timedelta
import dateutil.parser
from datetime import date
from django.utils import timezone
from django import db
from dateutil.relativedelta import relativedelta
from taxplus.models import Business, Duplicate
from django.db import connection
from fuzzywuzzy import fuzz


class Command(BaseCommand):
	#fixed_asset/rental_income/trading_license/cleaning_fee/market_fee/land_lease_fee
	args = ''
	help = 'Convert tax periods from timestamps to dates for simplicity'
	name= 'Convert tax dates'

	def handle(self, *args, **options):

		fuzz_threshold = 85
		for b in Business.objects.filter(i_status='active').order_by('id'):
			print "searching %s" % b
			for b2 in Business.objects.filter(i_status='active', pk__gt=b.pk).order_by('pk'):
				similarity = fuzz.ratio(b.name.upper(), b2.name.upper())
				if similarity >= fuzz_threshold:
					dup, created = Duplicate.objects.get_or_create(business1=b, business2=b2, defaults=dict(status=1))
					if not created:
						if dup.status <> 1:
							continue

					if similarity >= fuzz_threshold:
						dup.similary = similarity
						print "name match %s " % similarity
					else: # phone match
						dup.similary = -1
						print "phone match"

					dup.save()




