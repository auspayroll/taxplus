from django.core.management.base import BaseCommand, CommandError 
from log.models import CronLog
from datetime import date, datetime, time, timedelta
import dateutil.parser
from datetime import date
from django.utils import timezone
from django import db
from dateutil.relativedelta import relativedelta
from asset.models import Business, Duplicate
from django.db import connection
from fuzzywuzzy import fuzz


class Command(BaseCommand):
	#fixed_asset/rental_income/trading_license/cleaning_fee/market_fee/land_lease_fee
	args = ''
	help = 'Convert tax periods from timestamps to dates for simplicity'
	name= 'Convert tax dates'
	
	def handle(self, *args, **options):
		cursor = connection.cursor()
		cursor.execute("""
			select count(*), coalesce(phone1, phone2)
			from asset_business join property_sector on asset_business.sector_id = property_sector.id
			join property_district on property_sector.district_id = property_district.id
			where property_district.id = 22
			group by coalesce(phone1, phone2)
			having count(*) = 2 
			""")
		rows = [ list(item) for item in cursor.fetchall()]
		for row in rows:
			matches = Business.objects.filter(phone1=row[1], sector__district__pk=22)
			dup, created = Duplicate.objects.get_or_create(business1=matches[0], business2=matches[1], status=1)
			dup.similarity = fuzz.ratio(dup.business1, dup.business2)
			dup.save()
