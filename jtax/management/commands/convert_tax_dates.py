from django.core.management.base import BaseCommand, CommandError 
from jtax.models import *
from log.models import CronLog
from datetime import date, datetime, time, timedelta
import dateutil.parser
from datetime import date
from jtax.mappers.TaxMapper import TaxMapper
from django.utils import timezone
from django import db
from dateutil.relativedelta import relativedelta


class Command(BaseCommand):
	#fixed_asset/rental_income/trading_license/cleaning_fee/market_fee/land_lease_fee
	args = ''
	help = 'Convert tax periods from timestamps to dates for simplicity'
	name= 'Convert tax dates'
	
	def handle(self, *args, **options):
		errors = []

		for fee in Fee.objects.filter(date_from__isnull=True, date_to__isnull=True).order_by('pk'): #filter(date_from__isnull=True):	
			if self.up_date(fee, 'fee'):
				self.stdout.write("%s id: %s date test OK" % (fee, fee.pk))
			else:
				self.stdout.write("%s date test FAILED" % fee)
				errors.append(fee)
				db.reset_queries()

		#PropertyTaxItem.objects.all().update(date_from=None, date_to=None)
		for fee in PropertyTaxItem.objects.filter(date_from__isnull=True, date_to__isnull=True).order_by('pk'): #filter(date_from__isnull=True):
			if not fee.property:
				continue
			if self.up_date(fee, 'pti'):
				self.stdout.write("%s id: %s date test OK" % (fee, fee.pk))
			else:
				self.stdout.write("%s date test FAILED" % fee)
				errors.append(fee)
			db.reset_queries()

		#RentalIncomeTax.objects.all().update(date_from=None, date_to=None)
		for fee in RentalIncomeTax.objects.filter(date_from__isnull=True, date_to__isnull=True).order_by('pk'): #filter(date_from__isnull=True):
			if not fee.property:
				continue
			if self.up_date(fee, 'rit'):
				self.stdout.write("%s id: %s date test OK" % (fee, fee.pk))
			else:
				self.stdout.write("%s date test FAILED" % fee)
				errors.append(fee)
			db.reset_queries()

		#TradingLicenseTax.objects.all().update(date_from=None, date_to=None)
		for fee in TradingLicenseTax.objects.filter(date_from__isnull=True, date_to__isnull=True).order_by('pk'):  #filter(date_from__isnull=True):
			if self.up_date(fee, 'tli'):
				self.stdout.write("%s id: %s date test OK" % (fee, fee.pk))
			else:
				self.stdout.write("%s date test FAILED" % fee)
				errors.append(fee)
			db.reset_queries()

		self.stdout.write("----------------------------------------------------")
		if not errors:
			self.stdout.write("All tests passed successfully")
		else:
			self.stdout.write("%s tests failed" % len(errors))
		for fee in errors:
			self.stdout.write("%s id: %s, date_from: %s, date_to: %s" % (fee, fee.id, fee.date_from, fee.date_to))


	def up_date(self, fee, fee_type):
		tz = timezone.get_default_timezone()
		date_from  = fee.period_from.astimezone(tz).date()
		date_to = fee.period_to.astimezone(tz).date()

		if date_from.day == 31 and date_from.month == 12 and date_from.year+1 == date_to.year: # day before 1st day of year
			date_from = date_from + timedelta(days=1)

		if date_to.day == 1 and date_to.month ==1 and date_from.year +1 == date_to.year: # day after last day of year
			date_to = date_to - timedelta(days=1)

		fee.date_from = date_from
		fee.date_to = date_to
		fee.save()
		return True
