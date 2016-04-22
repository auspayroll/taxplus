from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
import dateutil.parser
import os
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
		yield dict([(unicode(key, 'utf-8').strip(), unicode(value, 'utf-8').strip()) for key, value in row.iteritems()] )

def utf_8_encoder(unicode_csv_data):
	for line in unicode_csv_data:
		yield line.encode('utf-8')

sub_types=[]
class Command(BaseCommand):
	args = 'None'
	help = ''
	name= 'Import Kicukiro'

	# @transaction.commit_on_success
	def handle(self, *args, **options):
		import pdb
		pdb.set_trace()
		for filename in args:
			last_closed_off = date(2015,12,31)
			file_path = os.sep.join([settings.ROOT_PATH, 'crud', 'csv', filename])
			file = codecs.open(file_path, "r", "utf-8")

			back_paid = {}
			account_fees_dict = {}
			account_start_dates = {}
			cleaning_rate_cat = Category.objects.get(code='cleaning_rate')
			cleaning_cat = CategoryChoice.objects.get(code='cleaning', category__code='fee_type')
			for line in UnicodeDictReader(file):
				year, month, day = (line['PAYMENT_DATE'].split()[0]).split('-')
				payment_date = date(int(year), int(month), int(day))
				district = District.objects.get(name=line['TAX_CENTER'])

				if Decimal(line['TAX']) == Decimal(line['TOTAL']):
					from_date = date(payment_date.year, payment_date.month, 1)

				else:
					months_back_paid = back_paid.setdefault(account.pk, 0) + 1
					from_date = payment_date - relativedelta(months=months_back_paid)
					from_date = date(from_date.year, 1, 1)
					back_paid[account.pk] = months_back_paid

				try:
					account = Account.objects.get(tin=line['TIN'])
				except Account.DoesNotExist:
					account = Account(start_date=from_date, name=line['TAX_PAYER_NAME'])
					business = Business.objects.create(tin=line['TIN'], date_started=date.today(), name=line['TAX_PAYER_NAME'], district=district)
					account.tin = line['TIN']
					AccountHolder.objects.create(holder=business, account=account)

				if account.start_date > from_date:
					account.start_date = from_date

				account.closed_off = last_closed_off
				account.save()
				rates = Rate.objects.filter(category=cleaning_cat, amount=int(line['TAX'])).order_by('id')
				if not rates:
					fee_subtype = CategoryChoice.objects.create(category=cleaning_rate_cat, code=line['TAX_PAYER_NAME'])
					rate = Rate.objects.create(amount=int(line['TAX']), sub_category=fee_subtype, category=cleaning_cat, date_from=date(2000,1,1))

				else:
					rate = rates[0]
				fee_subtype = rate.sub_category

				to_date = closed = None
				if from_date < last_closed_off:
					to_date = date(from_date.year, 12, 31)
					closed = last_closed_off

				af, created = AccountFee.objects.update_or_create(account=account, fee_type__code='cleaning', from_date=from_date, fee_subtype=fee_subtype, defaults=dict(due_days=5, district=district, to_date=to_date, closed=closed, auto=True, period=12, fee_type=cleaning_cat))

				deposit, created = BankDeposit.objects.update_or_create(account=account, bank_receipt_no=line['BANK_REF_NO'], note="imported Doc Id: %s" % line['DOC_ID'],
					defaults=dict(fee_date=payment_date, amount=line['TOTAL'], bank=line['BANK_NAME'], date_banked=payment_date, closed=closed ))

				account.transactions(update=True)
			file.close()






