"""
This script deactivate land lease data that is not in the official list.
It need the offical data list in CSV format and name <sector_name>_land_lease.csv
and put in jtax\management\data\
"""
from django.core.management.base import BaseCommand, CommandError 
from django.conf import settings
from dev1 import variables
from jtax.models import *
from log.models import CronLog
import dateutil.parser
import os
from property.functions import *
from property.models import *
from property.models import Property
from datetime import datetime, date, time
class Command(BaseCommand):

	args = '<sector_name (e.g Kicukiro, Nyarugenge)>'
	help = 'Deactivate land lease data that is not in the official data list CSV file'
	name= 'Deactivate Land Lease Script'
	year = 2013
	file_path = 'jtax/management/data/'


	def handle(self, *args, **options):	
		if len(args) < 1:
			print 'Please input sector name.'
			exit()
		else:
			sector_name = args[0]
			try:
				sector = Sector.objectsIgnorePermission.get(name__iexact=sector_name,province__name='KIGALI CITY',i_status='active')
			except ValueError:
				print 'Invalid sector name inputted.'
				exit()
			
			#check if there is a official data list file for checking
			file_path = self.file_path + sector_name.title() + '_land_lease.csv'
			if not os.path.isfile(file_path) or file_path.find('.csv') < 0:
				print 'Can not find CSV data file in ' + self.file_path
				exit()


			print 'Start fetching CSV data: ' 
			print 'Processing...'
			print '------'

			#get list of upi of properties in data list
			fo = open(file_path, "r+")
			content = fo.read()
			rows = content.split("\n")
			upis = []
			for k,i in enumerate(rows):
				#skip the heading row
				if k == 0:
					continue
				
				cols = i.split(",")
				upis.append(cols[0].rstrip('\n').strip('"').strip())

				#print i

				#if k >10:
				#	break
			# Close opend file
			fo.close()

			print 'Fetched ' + str(len(upis)) + ' UPIs from official list. Start valuating DB data: ' 
			print 'Processing...'
			print '------'


			#taxes = Fee.objects.filter(fee_type='land_lease',i_status='active', property__isnull=False,period_to__year=int(year),property__sector__name='Kicukiro')
			properties = Property.objectsIgnorePermission.filter(status__name='Active',sector=sector,is_land_lease=True)
			land_lease_property_count = len(properties)
			updated_count = 0
			non_official_paid_properties = []

			print 'Found ' + str(land_lease_property_count) + ' land lease properties in DB. Start compare data:' 
			print 'Processing...'
			print '------'

			db_upis = {}
			year = self.year
			if properties:
				for i in properties:
					if i.getUPI() == '' or i.getUPI() not in upis:
						#check if property had a paid land_lease fee for this year
						taxes = Fee.objects.filter(fee_type='land_lease',i_status='active', property=i,period_to__year=int(year),is_paid=True)
						if taxes:
							non_official_paid_properties.append(str(i.id))
						else:
							i.is_land_lease = False
							i.save()

							#deactivate all unpaid land lease fee of this property this year
							Fee.objects.filter(fee_type='land_lease',i_status='active', property=i,period_to__year=int(year),is_paid=False).update(i_status='inactive')

							updated_count = updated_count + 1
					else:
						if db_upis.has_key(i.getUPI()):
							db_upis[i.getUPI()].append(str(i.id))
						else:
							db_upis[i.getUPI()] = [str(i.id)]
						
			duplicates = []
			for k,i in db_upis.items():
				if len(i) > 1:
					duplicates.append(k + ': ' + ','.join(i))
			
			print 'DONE'

			summary = "===========" + \
				"\nTOTAL OFFICIAL LAND LEASE RECORDS: " + str(len(upis)) + \
				"\nTOTAL DB LAND LEASE RECORDS: " + str(land_lease_property_count) + \
				"\nTOTAL NON-OFFICIAL LAND LEASE PROPERTIES WHICH PAID FEE: " + str(len(non_official_paid_properties)) + \
				"\nTOTAL DEACTIVATE LAND LEASE STATUS PROPERTIES: " + str(updated_count) + \
				"\nTOTAL PROPERTIES WITH DUPLICATES UPIS: " + str(len(duplicates)) + \
				"\n==========="

			print summary 

			if non_official_paid_properties:
				summary = summary + "\n\n NON-OFFICIAL LAND LEASE PROPERTIES IDS:\n" + ','.join(non_official_paid_properties)

			summary = summary + "\n\n PROPERTIES WITH DUPLICATES UPIS:\n" + "\n".join(duplicates)

			#save summary data into the csv
			handle1=open(self.file_path + 'deactivate_land_lease_summary' + '_' + datetime.now().strftime("%Y%m%d_%H%M") + '.csv' ,'w+')
			handle1.write(summary)
			handle1.close()



