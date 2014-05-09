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
		file_path = os.sep.join([settings.ROOT_PATH, 'csv', 'import_businesses_002.csv'])
		file = codecs.open(file_path, "rb", "utf-8")

		i = 1
		district = District.objectsIgnorePermission.get(name='Kicukiro')

		for row in UnicodeDictReader(file):
			cell = None
			sector = None
			try:
				sector = Sector.objectsIgnorePermission.get(name__iexact=row['sector'], district=district)
			except:
				raise Exception(u"could not find sector %s for business %s, line %s" % (row['sector'], row['name'], i))
			i+= 1

			if row['cell']:
				try:
					cell = Cell.objects.get(name__iexact=row['cell'], sector=sector)
				except:
					pass

			business_type = 'Other businesses'
			area_type = 'City of Kigali'
			try:
				business, created = Business.objects.get_or_create(name=row['name'], sector=sector, cell=cell, defaults=dict(phone1=row['phone'], business_type=business_type, area_type=area_type))
			except MultipleObjectsReturned:
				pass


