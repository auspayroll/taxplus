"""
This script generate tax items for all citizens & businesses in the system for current year.
SHOULD BE USED WITH CAUTION AS LOT OF LEGACY DATA IS MISSING ATM.
"""

from django.core.management.base import BaseCommand, CommandError 
from jtax.models import *
from log.models import CronLog
from datetime import date, datetime, time, timedelta
import dateutil.parser
from jtax.mappers.TaxMapper import TaxMapper

class Command(BaseCommand):
	#fixed_asset/rental_income/trading_license/cleaning_fee/market_fee/land_lease_fee
	args = '<type (all/property/business) - default to "all" > <from (e.g 2013) - default value is None> <sector_id (e.g Kicukiro is 65, Nyarugenge is 2, Remera is 3) - default value is None>'
	help = 'Generate taxes & fees items'
	name= 'Generate Tax Cron Job'

	def handle(self, *args, **options):
		#default
		type = 'all'
		method = 'all'
		from_year = None
		sector = None
		if len(args) > 0:
			if args[0] in {'all','property','business'}:
				type = args[0]
			else:
				print 'Invalid reminder type, pick one options from (all/property/business) - default to "all" '
				exit()
		if len(args) > 1:
			try:
				from_year = int(args[1])
			except ValueError:
				print 'Invalid from year inputted. Example format: 2013'
				exit()
		if len(args) > 2:
			try:
				sector = Sector.objectsIgnorePermission.get(pk=int(args[2]),i_status='active')
			except ValueError:
				print 'Invalid sector_id inputted. Example format: Kicukiro is 65, Nyarugenge is 2, Remera is 3'
				exit()

		command = 'generate_tax ' + (" ").join(args)

		#get the time to start generate tax from 
		#default to last cron log with the exact command started time or the beginning of current year
		crons = CronLog.objects.filter(command = command,name=self.name).order_by('date_time')[0:2]
		
		"""
		if crons:
			last_cron = crons[0]
			if from_year == None:
				from_year = last_cron.started
		else:
			if from_year == None:
				from_year = datetime.strptime('01/01/2010','%d/%m/%Y')
		"""

		#set up all the time variables
		#start generate taxes & fees
		if from_year:
			current_year = str(from_year)
			year_start = timezone.make_aware(dateutil.parser.parse(current_year + '-01-01 00:00:00'), timezone.get_default_timezone())
			year_end = timezone.make_aware(dateutil.parser.parse(current_year + '-12-31 23:59:59'), timezone.get_default_timezone())
			rental_year_start = timezone.make_aware(dateutil.parser.parse(str(from_year - 1) + '-01-01 00:00:00'), timezone.get_default_timezone())
			rental_year_end = timezone.make_aware(dateutil.parser.parse(str(from_year - 1) + '-12-31 23:59:59'), timezone.get_default_timezone())
		else:
			today = timezone.make_aware(datetime.combine(datetime.today(), time(0,0)), timezone.get_default_timezone())
			current_year = str(today.year)
			year_start = timezone.make_aware(dateutil.parser.parse(current_year + '-01-01 00:00:00'), timezone.get_default_timezone())
			year_end = timezone.make_aware(dateutil.parser.parse(current_year + '-12-31 23:59:59'), timezone.get_default_timezone())
			rental_year_start = timezone.make_aware(dateutil.parser.parse(str(current_year - 1) + '-01-01 00:00:00'), timezone.get_default_timezone())
			rental_year_end = timezone.make_aware(dateutil.parser.parse(str(current_year - 1) + '-12-31 23:59:59'), timezone.get_default_timezone())

		#create cron log
		now = timezone.make_aware(datetime.now(), timezone.get_default_timezone())
		cron = CronLog(name=self.name,started=now,command = command)
		cron.save()

		sector_name = ''
		businesses = Business.objects.filter(i_status='active')
		properties = Property.objectsIgnorePermission.filter(status__name='Active')
		if sector:
			businesses = businesses.filter(sector=sector)
			properties = properties.filter(sector=sector)
			sector_name = ' for ' + sector.name.title()

		print 'Year to generate taxes/fees for property/business: ' + str(from_year)
		logs = {'fixed_asset_tax':[],'rental_income_tax':[],'trading_license_tax':[],'cleaning_fee':[],'land_lease_fee':[],'market_fee':[]}
		if businesses and (type in ('all','business')):
			print 'Business found' + sector_name + ': ' + str(len(businesses))
			print 'Start processing business taxes' + sector_name + '...'
			for i in businesses:
				TaxMapper.generateBusinessTaxes(i, now, current_year, year_start, year_end, None, logs)
			print 'Finished processing business taxes' + sector_name 

		if properties and (type in ('all','property')):
			print 'Properties found' + sector_name + ': ' + str(len(properties))
			print 'Start processing property taxes ' + sector_name + '...'
			for i in properties:
				TaxMapper.generatePropertyTaxes(i, now, current_year, year_start, year_end,rental_year_start, rental_year_end, None, logs)
			print 'Finished processing property taxes' + sector_name 
		#update cron finished time
		now = timezone.make_aware(datetime.now(), timezone.get_default_timezone())
		desc = 'Tax item generated:'
		for k,v in logs.iteritems():
			desc = desc + k.replace('_',' ').title() + ': ' + str(len(v)) + "\n"

		cron.description = desc
		cron.finished = now
		cron.save()
