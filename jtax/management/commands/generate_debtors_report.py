from django.core.management.base import BaseCommand, CommandError 
from jtax.models import Fee
from log.models import CronLog
from datetime import date, datetime, time, timedelta
import dateutil.parser
from datetime import date
from django.utils import timezone
from django import db
from dateutil.relativedelta import relativedelta
from taxplus.models import DebtorsReport, DebtorsReportLine
from django.db.models import Q, Sum


class Command(BaseCommand):
	#fixed_asset/rental_income/trading_license/cleaning_fee/market_fee/land_lease_fee
	args = ''
	help = 'Convert tax periods from timestamps to dates for simplicity'
	name= 'Convert tax dates'
	
	def handle(self, *args, **options):
			as_at = date.today()
			fees = Fee.objects.filter(fee_type='cleaning', remaining_amount__gt=0, i_status='active', due_date__lt=as_at, business__sector__isnull=False, business__sector__district__name__iexact='Kicukiro').select_related('business').order_by('date_time')
			debtorsreport, created = DebtorsReport.objects.get_or_create(fee_type='cleaning')
			debtorsreport.as_at = as_at
			debtorsreport.save()

			for fee in fees:
				if fee.subbusiness:
					reportline, created = DebtorsReportLine.objects.get_or_create(subbusiness=fee.subbusiness, business=fee.business, report=debtorsreport)
				else:
					reportline, created = DebtorsReportLine.objects.get_or_create(business=fee.business, report=debtorsreport)

				principle, interest = fee.amount_owing(debtorsreport.as_at)
				owing = principle + interest
				if (as_at - fee.due_date).days >= 365:
					reportline.month_12 += owing
				elif (as_at - fee.due_date).days >= 180:
					reportline.month_6 += owing
				elif (as_at - fee.due_date).days >= 90:
					reportline.month_3 += owing
				elif (as_at - fee.due_date).days >= 30:
					reportline.month_1 += owing
				else:
					reportline.month += owing

				reportline.total += owing
				reportline.rate = fee.amount
				reportline.save()

