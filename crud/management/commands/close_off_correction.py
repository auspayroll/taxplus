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


class Command(BaseCommand):
	args = 'None'
	help = ''
	name= 'Import Kicukiro'

	# @transaction.commit_on_success
	def handle(self, *args, **options):
		accounts = Account.objects.filter(end_date__isnull=False, closed_off__isnull=True)
		for account in accounts:
			print account.pk
			fees = account.account_fees.all()
			if fees:
				if fees[0].fee_type.code == 'land_lease' and account.end_date < date(2014,12,31):
					account.close_off_period(write_off=True)
					account.transactions(update=True)
				elif fees[0].fee_type.code == 'cleaning' and account.end_date < date(2015,12,31):
					account.close_off_period(write_off=True)
					account.transactions(update=True)
