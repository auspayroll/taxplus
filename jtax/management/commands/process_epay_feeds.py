"""
This script process the ePay CSV feeds from Banks and add new Payments.
should be run daily at night.
"""
from django.conf import settings
from dev1 import variables
from django.core.management.base import BaseCommand, CommandError 
from jtax.models import *
from log.models import CronLog
from datetime import date, datetime, time, timedelta
import dateutil.parser
from jtax.mappers.TaxMapper import TaxMapper
import os

class Command(BaseCommand):
	args = '<date (e.g 20/03/2013) - default to current date>'
	help = 'Process the ePay CSV feeds from Banks and add new Payments'
	name= 'Process ePay Feeds Cron Job'
	import_folder = settings.MEDIA_ROOT + 'epay_feeds/'

	def handle(self, *args, **options):
	
		command = 'process_epay_feeds ' + (" ").join(args)
		today = timezone.make_aware(datetime.combine(datetime.today(), time(0,0)), timezone.get_default_timezone())
		now = timezone.make_aware(datetime.now(), timezone.get_default_timezone())
		current_date = today
		if len(args) > 0:
			try:
				current_date = datetime.strptime(args[2],'%d/%m/%Y')
			except ValueError:
				print 'Invalid from time inputted. Example format: 20/03/2013'
				exit()

		#create cron log
		cron = CronLog(name=self.name,started=now,command = command)
		cron.save()

		#start exact data from the csv feeds for current date for each of the banks
		for i in variables.banks:			
			bank_folder =self.import_folder + i[0] + '/'
			if os.path.exists(bank_folder):				
				for file in os.listdir(bank_folder):
					if file == (current_date.strftime('%Y%m%d') + '.csv'):
						# Open the feed file and start read data
						fo = open(bank_folder + file, "r+")
						content = fo.read()
						rows = content.split("\n")
						#skip the heading row
						del rows[0]
						for i in rows:
							print i
						# Close opend file
						fo.close()



		#update cron finished time
		now = timezone.make_aware(datetime.now(), timezone.get_default_timezone())
		#desc = 'Tax item generated:'
		#for k,v in logs.iteritems():
		#	desc = desc + k.replace('_',' ').title() + ': ' + str(len(v)) + "\n"
		desc =''
		cron.description = desc
		cron.finished = now
		cron.save()
