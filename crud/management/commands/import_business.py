from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import dateutil.parser
import os
import re
from datetime import datetime, date, time
from django.db import IntegrityError, transaction
import csv
import codecs
from django.core.exceptions import *
from crud.models import *
from django.db.models import Q
from decimal import Decimal
from datetime import date
from taxplus.models import Category, CategoryChoice
from dateutil.relativedelta import relativedelta

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

def UnicodeDictReader(unicode_data, **kwargs):
	csv_reader = csv.DictReader(utf_8_encoder(unicode_data), dialect=csv.excel, **kwargs)
	for row in csv_reader:
		yield dict([(unicode(key, 'utf-8').strip(), unicode(value, 'utf-8', errors='replace').strip()) for key, value in row.iteritems()] )

def utf_8_encoder(unicode_csv_data):
	for line in (unicode_csv_data):
		yield line.encode('utf-8')

sub_types=[]
class Command(BaseCommand):
	args = 'None'
	help = ''
	name= 'Import Kicukiro'

	# @transaction.commit_on_success
	def handle(self, *args, **options):
		for filename in args:
			file_path = os.sep.join([settings.ROOT_PATH, 'crud', 'csv', filename])
			file = codecs.open(file_path, "r", "utf-8")
			i = 2
			for line in UnicodeDictReader(file):
				print 'processing line %s' % i
				district = District.objects.get(name__iexact=line['District'])
				accounts = Account.objects.filter(tin=line['TIN']).order_by('-id')
				match = re.search(r'7\d{8}', line['Phone'])

				if match:
					phone = '0' + match.group()
				else:
					phone = None

				businesses = Business.objects.filter(tin=line['TIN']).order_by('-id')
				if businesses:
					business = businesses[0]
					if phone:
						if business.phone1 and not business.phone2 and phone != business.phone1:
							business.phone2 = business.phone1
						business.phone1 = phone
						business.save()
				else:
					business = Business.objects.create(tin=line['TIN'], date_started=date.today(), name=line['Name'], district=district, phone1=phone)


				if accounts:
					account = accounts[0]
					if phone:
						account.phone = phone
						account.save()

						if not account.business:
							account.business = business
							account.save()
							AccountHolder.objects.create(account=account, holder=business)
				else:
					account = Account.objects.create(start_date=date.today(), name=line['Name'], tin=line['TIN'], phone=phone, business=business)
					AccountHolder.objects.create(account=account, holder=business)

				i = i + 1
			file.close()






