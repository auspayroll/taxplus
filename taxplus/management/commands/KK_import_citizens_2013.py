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
from taxplus.models import Citizen, Entity
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
		file_path = os.sep.join([settings.ROOT_PATH, 'taxplus', 'excel', 'outstandinglandlease.csv'])
		file = codecs.open(file_path, "r", "utf-8")

		lines = [row for row in UnicodeDictReader(file)]
		file.close()
		
		#Surname,Middlename,Firstname,Citizen Id,Print date
		not_found = 0
		found = 0
		active = CategoryChoice.objects.get(category__code='status', code='active')
		#inactive = CategoryChoice.objects.get(category_code='status', code='inactive')

		for line in lines:
			try:
				citizen = Citizen.objects.get(citizen_id=line['Citizen Id'])
			except:
				not_found += 1
				citizen = Citizen(first_name=line['Firstname'], last_name=line['Surname'], citizen_id=line['Citizen Id'], status_new=active, status_id=1)

			citizen.first_name = line['Firstname']
			citizen.last_name = line['Surname']
			citizen.middle_name = line['Middlename']
			citizen.status_id = 1
			citizen.save()

			try:
				entity = Entity.objects.get(citizen_id=citizen.pk)
			except Entity.DoesNotExist:
				entity = Entity(citizen_id=citizen.pk, entity_type=CategoryChoice.objects.get(category__code='entity_type', code='individual'), status=active)
				entity.save()

			citizen.entity_id = entity.pk
			citizen.save(update_fields=['entity_id',])

			found += 1

		print "found %s" % found
		print "not found %s" % not_found




