from django.core.management.base import BaseCommand, CommandError 
from jtax.models import *
from log.models import CronLog
from datetime import date, datetime, time, timedelta
import dateutil.parser
from datetime import date
from jtax.mappers.TaxMapper import TaxMapper
from django.utils import timezone
from dev1 import variables
from property.models import LandUse

class Command(BaseCommand):
	#fixed_asset/rental_income/trading_license/cleaning_fee/market_fee/land_lease_fee
	args = ''
	help = 'Initializes table data'
	name= 'Initial data'
	
	def handle(self, *args, **options):
		for code, name_list in variables.land_use_types_class.iteritems():

			land_use, created = LandUse.objects.get_or_create(code=code, defaults=dict(name=name_list[0]))
			if not created:
				land_use.name = name_list[0]
				land_use.save()

		LandUse.objects.exclude(code__in=[ code for (code, name) in variables.land_use_types_class.iteritems()]).delete()