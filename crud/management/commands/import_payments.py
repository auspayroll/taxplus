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
			last_closed_off = date(2015,12,31)
			file_path = os.sep.join([settings.ROOT_PATH, 'crud', 'csv', filename])
			file = codecs.open(file_path, "r", "utf-8")

			back_paid = {}
			account_fees_dict = {}
			account_start_dates = {}
			cleaning_rate_cat = Category.objects.get(code='cleaning_rate')
			cleaning_cat = CategoryChoice.objects.get(code='cleaning', category__code='fee_type')
			active = CategoryChoice.objects.get(code='active', category__code='status')
			inactive = CategoryChoice.objects.get(code='inactive', category__code='status')
			i = 2
			for line in UnicodeDictReader(file):
				line['TAX'] = line['TAX'].replace(',','')
				line['TOTAL'] = line['TOTAL'].replace(',','')
				print 'processing line %s' % i, line['DOC_ID']

				year, month, day = (line['PAYMENT_DATE'].split()[0]).split('-')
				payment_date = date(int(year), int(month), int(day))
				district = District.objects.get(name=line['TAX_CENTER'])

				accounts = Account.objects.filter(tin=line['TIN']).order_by('-id')

				if Decimal(line['TAX']) == Decimal(line['TOTAL']):
					from_date = date(payment_date.year, payment_date.month, 1)

				else:
					months_back_paid = back_paid.setdefault(line['TIN'], 0) + 1
					from_date = payment_date - relativedelta(months=months_back_paid)
					from_date = date(from_date.year, from_date.month, 1)
					back_paid[line['TIN']] = months_back_paid

				if accounts:
					account = accounts[0]
				else:
					account = Account(start_date=from_date, name=line['TAX_PAYER_NAME'])
					business = Business.objects.create(tin=line['TIN'], date_started=date.today(), name=line['TAX_PAYER_NAME'], district=district)
					account.tin = line['TIN']
					account.save()
					AccountHolder.objects.create(holder=business, account=account)


				if account.start_date > from_date:
					account.start_date = from_date

				rates = Rate.objects.filter(category=cleaning_cat, amount=int(line['TAX'])).order_by('id')
				if not rates:
					fee_subtype = CategoryChoice.objects.create(category=cleaning_rate_cat, code=line['TAX'])
					rate = Rate.objects.create(amount=int(line['TAX']), sub_category=fee_subtype, category=cleaning_cat, date_from=date(2000,1,1))

				else:
					rate = rates[0]
				fee_subtype = rate.sub_category

				if from_date < last_closed_off:
					closed = last_closed_off
					status = inactive
				else:
					try:
						af, created = AccountFee.objects.update_or_create(account=account, fee_type__code='cleaning', status=active, from_date=from_date, fee_subtype=fee_subtype, defaults=dict(due_days=5, district=district, auto=True, period=12, fee_type=cleaning_cat))
					except AccountFee.MultipleObjectsReturned:
						pass
					status = active
					closed = None

				deposit, created = BankDeposit.objects.update_or_create(account=account, bank_receipt_no=line['BANK_REF_NO'],
					defaults=dict(note="%s, imported Doc Id:%s" % (datetime.strftime(from_date, '%d %b %Y'), line['DOC_ID']), depositor_name=line['TAX_PAYER_NAME'], amount=line['TOTAL'], bank=line['BANK_NAME'], date_banked=payment_date, closed=closed, status=status ))

				account.transactions(update=True)
				i = i + 1
			file.close()






