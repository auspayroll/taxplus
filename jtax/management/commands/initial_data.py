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
import csv
from asset.models import BusinessCategory
import os

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



		#import cleaning fee categories
		file_path = os.sep.join([settings.ROOT_PATH, 'csv', 'cleaning_categories.csv'])
		file = open(file_path, "rb")

		for row in csv.DictReader(file):
			category, created = BusinessCategory.objects.get_or_create(pk=row['pk'], defaults=dict(name=row['name']))
			if not created:
				category.name = row['name']
				category.save()



		#import cleaning fee categories
		file_path = os.sep.join([settings.ROOT_PATH, 'csv', 'cleaning_subcategories.csv'])
		file = open(file_path, "rb")

		for row in csv.DictReader(file):
			business_category = BusinessCategory.objects.get(pk=row['cat'])
			subcategory, created = BusinessSubCategory.objects.get_or_create(pk=row['pk'], defaults=dict(name=row['name'], business_category=business_category))
			if not created:
				subcategory.name = row['name']
				subcategory.business_category = business_category
				subcategory.save()


		#import cleaning fees
		file_path = os.sep.join([settings.ROOT_PATH, 'csv', 'cleaning_fees.csv'])
		file = open(file_path, "rb")

		for row in csv.DictReader(file):
			fields = {}
			valid_from = row['valid_from']
			if not valid_from:
				vfrom = datetime(2000,1,1)
			else:
				vfrom = datetime.strptime(valid_from,'%d/%m/%Y')

			cell = row['cell']
			if cell:
				cell = Cell.objects.get(name__iexact=cell)
			else:
				cell = None
			sector = row['sector']
			if sector:
				sector = Sector.objectsIgnorePermission.get(name__iexact=sector)
			else:
				sector = None
			district = row['district']
			if district:
				district = District.objectsIgnorePermission.get(name__iexact=district)
			else:
				district = None

			business_category = BusinessCategory.objects.get(pk=row['cat'])

			cleaning_schedule, created = CleaningSchedule.objects.get_or_create(valid_from=vfrom, district=district, cell=cell, sector=sector, business_category=business_category, defaults=dict(amount=row['amount']))
			if not created:
				cleaning_schedule.amount = row['amount']
				cleaning_schedule.save()

