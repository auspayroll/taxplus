from django.core.management.base import BaseCommand, CommandError 
from django.conf import settings
from dev1 import variables
from jtax.models import *
from log.models import CronLog
import dateutil.parser
import os
from property.functions import *
from property.models import *
from asset.models import Ownership, Business
from datetime import datetime, date, time
from jtax.models import Setting
from property.models import District, Sector, Cell, Village
from django.db import IntegrityError, transaction
import csv
import codecs
from django.core.exceptions import *
from taxplus.models import District, Sector, Cell, Village, Rate, CategoryChoice
from django.db.models import Q

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def UnicodeDictReader(unicode_data, **kwargs):
	csv_reader = csv.DictReader(utf_8_encoder(unicode_data), dialect=csv.excel, **kwargs)
	for row in csv_reader:
		yield dict([(unicode(key, 'utf-8').strip(), unicode(value, 'utf-8').strip()) for key, value in row.iteritems()] )

def utf_8_encoder(unicode_csv_data):
	for line in unicode_csv_data:
		yield line.encode('utf-8')

sub_types=[]
class Command(BaseCommand):
	args = 'None'
	help = 'Import Businesses in Kicukiro from csv and calculates fees/taxes'
	name= 'Import Kicukiro'

	# @transaction.commit_on_success
	def handle(self, *args, **options):
		file_path = os.sep.join([settings.ROOT_PATH, 'taxplus', 'excel', 'KK_landlease_fees.csv'])
		file = codecs.open(file_path, "r", "utf-8")

		lines = [row for row in UnicodeDictReader(file)]
		file.close()
		
		for line in lines:
			village = Village.objects.get(code=line['Village Code'])
			residential_rate = line['Residential']
			commercial_rate = line['Commercial']
			agricultural_rate = line['Agricultural']
			date_from = date(2012,1,1)
			date_to = date(2013,12,31)
			category = CategoryChoice.objects.get(category__code='fee_type', code='land_lease')

			sub_category = CategoryChoice.objects.get(category__code='land_use', code='residential')
			rate = Rate(village=village, date_from=date_from, date_to=date_to, category=category, sub_category=sub_category, amount=residential_rate)
			rate.save()
			

			sub_category = CategoryChoice.objects.get(category__code='land_use', code='commercial')
			rate = Rate(village=village, date_from=date_from, date_to=date_to, category=category, sub_category=sub_category, amount=commercial_rate)
			rate.save()




