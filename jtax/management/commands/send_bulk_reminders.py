"""
This script send out bulk email & sms for overdue & upcoming taxes. Should be run once a month
"""

from django.core.management.base import BaseCommand, CommandError 
from jtax.models import *
from log.models import CronLog
from datetime import date, datetime, time, timedelta
from django.db.models import Q
from django.utils import formats
from dateutil.relativedelta import relativedelta
import urllib2

from log.mappers.LogMapper import LogMapper
from common.util import CommonUtil
from jtax.send_email import *
from jtax.send_sms import *


class Command(BaseCommand):
	args = '<type (all/overdue/upcoming) - default to "all" > <method (email/sms/all) - default to "all"> <from (e.g 20/03/2013) - default to current time>'
	help = 'Send out bulk email /sms reminder for overdue and upcoming  taxes/fees'
	name= 'Send Bulk Reminders Cron Job'

	username = "Automate Email/SMS"

	# set up the days count to be consider as upcoming due date?
	upcoming_day_span = 30

	#set up error lists
	smsErrors = []
	emailErrors = []

	#set up description log for this cron job
	logs = ['Type: Total Count - Failed Count']

	def handle(self, *args, **options):
		#default
		type = 'all'
		method = 'all'
		time = datetime.now()

		if len(args) > 0:
			if args[0] in {'all','overdue','upcoming'}:
				type = args[0]
			else:
				print 'Invalid reminder type, pick one options from (all/overdue/upcoming)'
				exit()
		if len(args) > 1:
			if args[1] in {'all','email','sms'}:
				method = args[1]
			else:
				print 'Invalid sending method, pick one options from (email/sms/all)'
				exit()
		if len(args) > 2:
			try:
				time = datetime.strptime(args[2],'%d/%m/%Y')
			except ValueError:
				print 'Invalid from time inputted. Example format: 20/03/2013'
				exit()

		command = 'send_bulk_reminders ' + (" ").join(args)

		#set up all the time variables
		now = timezone.make_aware(datetime.now(), timezone.get_default_timezone())

		#create cron log
		cron = CronLog(name=self.name,started=now,command = command)
		cron.save()

		if type == 'upcoming' or type == 'all':
			self.send_email_reminders_for_upcomming_tax(method)
			self.send_sms_reminders_for_upcomming_tax(method)
		if type == 'overdue' or type == 'all':
			self.send_warning_email_for_overdue_tax(method)
			self.send_warning_sms_for_overdue_tax(method)

		#save cron finished time
		
		now = timezone.make_aware(datetime.now(), timezone.get_default_timezone())
		cron.finished =now
		cron.description = "\n".join(self.logs)
		cron.save()


	"""
	send email reminders for upcoming tax including fixed asset tax, rental income tax, trading license tax 
	"""
	def send_email_reminders_for_upcomming_tax(self, method):
		today = timezone.make_aware(datetime.combine(datetime.today(), time(0,0)), timezone.get_default_timezone())
		start = datetime(today.year,today.month,today.day,23,59,59)
		day_upcoming = today + relativedelta(days=self.upcoming_day_span)
		end = datetime(day_upcoming.year,day_upcoming.month,day_upcoming.day,0,0,0)
		date_range = (start,end)
		statistics = {'email_sent':0, 'email_failed':0}
		
		if method == 'email' or method == 'all':
			
			# Fixed asset tax items
			fixed_asset_tax_items = PropertyTaxItem.objects.filter(Q(property__owners__isnull=False) | Q(property__ownership__isnull=False), is_paid=False,due_date__range=date_range,i_status='active').distinct()
			if fixed_asset_tax_items:
				for obj in fixed_asset_tax_items:
					email_sent_result = send_reminder_emails(obj)
					statistics['email_sent'] = statistics['email_sent'] + email_sent_result['email_sent']
					statistics['email_failed'] = statistics['email_failed'] + email_sent_result['email_failed']
			
			# Rental income tax
			rental_income_tax_items = RentalIncomeTax.objects.filter(Q(property__owners__isnull=False) | Q(property__ownership__isnull=False), is_paid=False,due_date__range=date_range,i_status='active').distinct()	
			if rental_income_tax_items:
				for obj in rental_income_tax_items:
					email_sent_result = send_reminder_emails(obj)
					statistics['email_sent'] = statistics['email_sent'] + email_sent_result['email_sent']
					statistics['email_failed'] = statistics['email_failed'] + email_sent_result['email_failed']
			
			# Trading license tax items
			trading_license_tax_items = TradingLicenseTax.objects.filter(Q(business__isnull=False,business__owners__isnull=False)|Q(subbusiness__isnull=False,subbusiness__business__owners__isnull=False),due_date__range=date_range,is_paid=False,i_status='active').distinct()
			if trading_license_tax_items:
				for obj in trading_license_tax_items:
					email_sent_result = send_reminder_emails(obj)
					statistics['email_sent'] = statistics['email_sent'] + email_sent_result['email_sent']
					statistics['email_failed'] = statistics['email_failed'] + email_sent_result['email_failed']
			self.logs.append("Upcoming Email: total(" + str(statistics['email_sent']+statistics['email_failed']) +"), sent(" +str(statistics['email_sent']) + "), failed("+str(statistics['email_failed']) + ")")
	
	
	"""
	send sms reminders for upcoming tax including fixed asset tax, rental income tax, trading license tax 
	"""
	def send_sms_reminders_for_upcomming_tax(self, method):
		today = timezone.make_aware(datetime.combine(datetime.today(), time(0,0)), timezone.get_default_timezone())
		start = datetime(today.year,today.month,today.day,23,59,59)
		day_upcoming = today + relativedelta(days=self.upcoming_day_span)
		end = datetime(day_upcoming.year,day_upcoming.month,day_upcoming.day,0,0,0)
		date_range = (start,end)
		
		statistics = {'sms_sent':0, 'sms_failed':0}
		if method == 'sms' or method == 'all':
			# Fixed asset tax items
			fixed_asset_tax_items = PropertyTaxItem.objects.filter(Q(property__owners__isnull=False) | Q(property__ownership__isnull=False), is_paid=False,due_date__range=date_range,i_status='active').distinct()
			if fixed_asset_tax_items and len(fixed_asset_tax_items) > 0:
				count = 0
				for obj in fixed_asset_tax_items:
					sms_sent_result = send_reminder_sms(obj)
					statistics['sms_sent'] = statistics['sms_sent'] + sms_sent_result['sms_sent']
					statistics['sms_failed'] = statistics['sms_failed'] + sms_sent_result['sms_failed']
			# Rental income tax items
			rental_income_tax_items = RentalIncomeTax.objects.filter(Q(property__owners__isnull=False) | Q(property__ownership__isnull=False), is_paid=False,due_date__range=date_range,i_status='active').distinct()	
			if rental_income_tax_items:
				for obj in rental_income_tax_items:
					sms_sent_result = send_reminder_sms(obj)
					statistics['sms_sent'] = statistics['sms_sent'] + sms_sent_result['sms_sent']
					statistics['sms_failed'] = statistics['sms_failed'] + sms_sent_result['sms_failed']
			# Trading license tax items
			trading_license_tax_items = TradingLicenseTax.objects.filter(Q(business__isnull=False,business__owners__isnull=False)|Q(subbusiness__isnull=False,subbusiness__business__owners__isnull=False),due_date__range=date_range,is_paid=False,i_status='active').distinct()
			if trading_license_tax_items:
				for obj in trading_license_tax_items:
					sms_sent_result = send_reminder_sms(obj)
					statistics['sms_sent'] = statistics['sms_sent'] + sms_sent_result['sms_sent']
					statistics['sms_failed'] = statistics['sms_failed'] + sms_sent_result['sms_failed']
			# Fee
			fees = Fee.objects.filter(due_date__range=date_range,is_paid=False,i_status='active').distinct()
			if fees:
				for obj in fees:
					sms_sent_result = send_reminder_sms(obj)
					statistics['sms_sent'] = statistics['sms_sent'] + sms_sent_result['sms_sent']
					statistics['sms_failed'] = statistics['sms_failed'] + sms_sent_result['sms_failed']
			self.logs.append("Upcoming SMS: total(" + str(statistics['sms_sent']+statistics['sms_failed']) +"), sent(" +str(statistics['sms_sent']) + "), failed("+str(statistics['sms_failed']) + ")")
	
	"""
	send warning email for overdue tax including fixed asset tax, rental income tax, trading license tax, and fees
	"""
	def send_warning_email_for_overdue_tax(self, method):
		today = timezone.make_aware(datetime.combine(datetime.today(), time(0,0)), timezone.get_default_timezone())
		statistics = {'email_sent':0, 'email_failed':0}
		if method == 'email' or method == 'all':
			# Fixed asset tax items
			fixed_asset_tax_items = PropertyTaxItem.objects.filter(Q(property__owners__isnull=False) | Q(property__ownership__isnull=False), is_paid=False,due_date__lte=today,i_status='active').distinct()
			if fixed_asset_tax_items and len(fixed_asset_tax_items) > 0:
				for obj in fixed_asset_tax_items:
					email_sent_result = send_warning_emails(obj)
					statistics['email_sent'] = statistics['email_sent'] + email_sent_result['email_sent']
					statistics['email_failed'] = statistics['email_failed'] + email_sent_result['email_failed']
			# Rental income tax items
			rental_income_tax_items = RentalIncomeTax.objects.filter(Q(property__owners__isnull=False) | Q(property__ownership__isnull=False), is_paid=False,due_date__lte=today,i_status='active').distinct()	
			if rental_income_tax_items and len(rental_income_tax_items) > 0:
				for obj in rental_income_tax_items:
					email_sent_result = send_warning_emails(obj)
					statistics['email_sent'] = statistics['email_sent'] + email_sent_result['email_sent']
					statistics['email_failed'] = statistics['email_failed'] + email_sent_result['email_failed']
			# Trading license tax items
			trading_license_tax_items = TradingLicenseTax.objects.filter(Q(business__isnull=False,business__owners__isnull=False)|Q(subbusiness__isnull=False,subbusiness__business__owners__isnull=False),due_date__lte=today,is_paid=False,i_status='active').distinct()
			if trading_license_tax_items and len(trading_license_tax_items) > 0:
				for obj in trading_license_tax_items:
					email_sent_result = send_warning_emails(obj)
					statistics['email_sent'] = statistics['email_sent'] + email_sent_result['email_sent']
					statistics['email_failed'] = statistics['email_failed'] + email_sent_result['email_failed']
	
			# Fees
			fees = Fee.objects.filter(due_date__lte=today,is_paid=False,i_status='active').distinct()
			if fees and len(fees) > 0:
				for obj in fees:
					email_sent_result = send_warning_emails(obj)		
					statistics['email_sent'] = statistics['email_sent'] + email_sent_result['email_sent']
					statistics['email_failed'] = statistics['email_failed'] + email_sent_result['email_failed']
			self.logs.append("Overdue Email: total(" + str(statistics['email_sent']+statistics['email_failed']) +"), sent(" +str(statistics['email_sent']) + "), failed("+str(statistics['email_failed']) + ")")		
					
	
	"""
	send warning sms for overdue tax including fixed asset tax, rental income tax, trading license tax, and fees
	"""
	def send_warning_sms_for_overdue_tax(self, method):
		today = timezone.make_aware(datetime.combine(datetime.today(), time(0,0)), timezone.get_default_timezone())
		statistics = {'sms_sent':0, 'sms_failed':0}
		if method == 'sms' or method == 'all':
			# Fixed asset tax items
			fixed_asset_tax_items = PropertyTaxItem.objects.filter(Q(property__owners__isnull=False) | Q(property__ownership__isnull=False), is_paid=False,due_date__lte=today,i_status='active')
			if fixed_asset_tax_items:
				for obj in fixed_asset_tax_items:
					sms_sent_result = send_warning_sms(obj)
					statistics['sms_sent'] = statistics['sms_sent'] + sms_sent_result['sms_sent']
					statistics['sms_failed'] = statistics['sms_failed'] + sms_sent_result['sms_failed']
			
			# Rental income tax items
			rental_income_tax_items = RentalIncomeTax.objects.filter(Q(property__owners__isnull=False) | Q(property__ownership__isnull=False), is_paid=False,due_date__lte=today,i_status='active')	
			if rental_income_tax_items:
				for obj in rental_income_tax_items:
					sms_sent_result = send_warning_sms(obj)
					statistics['sms_sent'] = statistics['sms_sent'] + sms_sent_result['sms_sent']
					statistics['sms_failed'] = statistics['sms_failed'] + sms_sent_result['sms_failed']
			# Trading license tax items
			trading_license_tax_items = TradingLicenseTax.objects.filter(Q(business__isnull=False,business__owners__isnull=False)|Q(subbusiness__isnull=False,subbusiness__business__owners__isnull=False),due_date__lte=today,is_paid=False,i_status='active')
			if trading_license_tax_items:
				for obj in trading_license_tax_items:
					sms_sent_result = send_warning_sms(obj)
					statistics['sms_sent'] = statistics['sms_sent'] + sms_sent_result['sms_sent']
					statistics['sms_failed'] = statistics['sms_failed'] + sms_sent_result['sms_failed']
	
			# Fees
			fees = Fee.objects.filter(due_date__lte=today,is_paid=False,i_status='active')
			if fees:
				for obj in fees:
					sms_sent_result = send_warning_sms(obj)
					statistics['sms_sent'] = statistics['sms_sent'] + sms_sent_result['email_sent']
					statistics['sms_failed'] = statistics['sms_failed'] + sms_sent_result['sms_failed']
			self.logs.append("Overdue Email: total(" + str(statistics['sms_sent']+statistics['sms_failed']) +"), sent(" +str(statistics['sms_sent']) + "), failed("+str(statistics['sms_failed']) + ")")		
					
		