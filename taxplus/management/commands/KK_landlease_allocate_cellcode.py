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
from taxplus.models import District, Sector, Cell, Village
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
			try:
				sector = Sector.objects.filter(district__name__iexact='Kicukiro').get(Q(name__iexact=line['Sector']) | Q(alias__iexact=line['Sector']))
			except Sector.DoesNotExist:
				continue
			else:
				line['Sector Code'] = sector.code
				try:
					cell = Cell.objects.filter(sector__pk=sector.pk).get(Q(name__iexact=line['Cell']) | Q(alias__iexact=line['Cell']))
				except Cell.DoesNotExist:
					continue
				else:
					line['Cell Code'] = cell.code
					try:
						village = Village.objects.get(name__iexact=line['Village'], cell__pk=cell.pk)
					except Village.DoesNotExist:
						continue
					else:
						line['Village Code'] = village.code


		file = codecs.open(file_path, "w", "utf-8")

		fieldnames=('Sector', 'Sector Code', 'Cell', 'Cell Code', 'Village', 'Village Code', 'Residential', 'Commercial', 'Agricultural')
		writer = csv.DictWriter(file, fieldnames)
		writer.writerow(dict([(i, i) for i in fieldnames]))
		writer.writerows(lines)

		file.close()


