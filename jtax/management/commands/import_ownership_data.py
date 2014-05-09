"""
This script import ownership data from the specified CSV file.
PLEASE DOUBLE CHECK THE DATA FILE TO ENSURE IT HAS THE FOLLOWING FORMAT (WITH A HEADING ROW):
- UPI	
- AREA	
- DESCRIPTION
- APPROVAL DATE	
- VILLAGE	
- CELL	
- SECTOR	
- DISTRICT	
- PROVINCE	
- SURNAME	
- MIDDLE NAME	
- GIVEN NAME	
- ID CARD NUMBER																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																																		

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
from asset.models import Ownership
from datetime import datetime, date, time
class Command(BaseCommand):
	args = '<CSV data file (e.g data.csv)>'
	help = 'Import Ownership data from CSV files and .'
	name= 'Import Land Lease Script'

	new_property_list = []
	update_property_list = []
	new_citizen_list = []
	new_ownership_list = []

	error_list = {'no_id_multi_citizens_found':[],'invalid_locality':[]}


	def handle(self, *args, **options):	
		if len(args) == 0:
			print 'Please input the path to the CSV file.'
			exit()
		else:
			file_path = args[0]
			if not os.path.isfile(file_path) or file_path.find('.csv') < 0:
				print 'Invalid CSV file inputted.'
				exit()

			fo = open(file_path, "r+")
			content = fo.read()
			rows = content.split("\n")
			errorRows = []

			print 'TOTAL ROW FOUND: ' + str(len(rows) - 1)
			print 'Processing...'
			print '------'
			for k,i in enumerate(rows):
				#skip the heading row
				if k == 0:
					continue
				if i != '':
					result = self.process_data_row(i)
				if not result:
					errorRows.append(i)
				#print i

				#if k >10:
				#	break
			# Close opend file
			fo.close()

			#save error rows in a list to be double check
			if errorRows:
				handle1=open(file_path.replace('.csv','') + '_errors_' + datetime.now().strftime("%Y%m%d_%H%M") + '.csv' ,'w+')
				handle1.write("\n".join(errorRows))
				handle1.close();

			message = "===========" + \
				"\nTOTAL PROCESSED RECORDS: " + str((len(rows) - 1) - len(errorRows)) + \
				"\n - INSERTED NEW PROPERTIES: " + str(len(self.new_property_list)) + \
				"\n - UPDATED EXISTING PROPERTIES: " + str(len(self.update_property_list)) + \
				"\n - INSERTED NEW CITIZENS: " + str(len(self.new_citizen_list)) + \
				"\n - INSERTED NEW OWNERSHIPS: " + str(len(self.new_ownership_list)) + \
				"\n\nFAILED TO PROCESS RECORDS: " + str(len(errorRows)) + \
			    "\n - No citizen ID and multiple citizens found with the same name: " + str(len(self.error_list['no_id_multi_citizens_found'])) + \
			    "\n - Invalid locality data (sector/village/cell): " +  str(len(self.error_list['invalid_locality'])) + \
				"\n==========="

			print message

			#save this import into a summary file
			handle1=open(file_path.replace('.csv','') + '_summary_' + datetime.now().strftime("%Y%m%d_%H%M") + '.csv' ,'w+')
			handle1.write(message)
			handle1.close();



	def process_data_row(self,row):
		cols = row.split(",")
		#sanitize data

		upi = cols[0].rstrip('\n').strip('"').strip()
		parcel_id = upi.split('/')[4]
		area = cols[1].rstrip('\n').strip('"').strip()
		description = cols[2].rstrip('\n').strip('"').strip()
		approval_date = cols[3].rstrip('\n').strip('"').strip()
		village = cols[4].rstrip('\n').strip('"').strip()
		cell = cols[5].rstrip('\n').strip('"').strip()
		sector = cols[6].rstrip('\n').strip('"').strip()
		district = cols[7].rstrip('\n').strip('"').strip()
		province = cols[8].rstrip('\n').strip('"').strip()
		last_name = cols[9].rstrip('\n').strip('"').strip()
		middle_name = cols[10].rstrip('\n').strip('"').strip()
		first_name = cols[11].rstrip('\n').strip('"').strip()
		citizen_id = cols[12].rstrip('\n').strip('"').strip()

		'''processing each row in the following orders:
		1 - Check Property Info ( UPI / Village / Cell / Sector / District / Province)
			-> If property record not exist in DB add new record
			-> If exist check all info matched, if not matched put in a list to be reconfirmed
			-> For the concerning property, update area info for that property, if description is not Full ownership then set land lease applicable to be true, and save approval date if exist
		2 - Check Citizen Info ( ID Card Number / Surname / Middle Name / Given Name)
			-> If record not exist add new
			-> If exist check all info matched, if not matched put in a list to be reconfirmed
		3 - Check ownership details between Property & Citizen:
			-> IF record not exist add new
			-> If exist check all info matched, if not matched: if they have paid a tax since the person who paid the tax would consider as the current owner. if no taxes paid lets go with this info
		'''
		# process property info
		property = self.get_property_from_data(parcel_id,village,cell,sector,district,province)
		if property:
			if description != 'Full Ownership':
				property.is_land_lease = True
				if area != '':
					property.size_sqm = area
				if approval_date != '':
					property.land_lease_approval_date =  datetime.strptime(approval_date, "%d/%m/%Y")
			else:
				property.is_land_lease = False
			property.save()
		else:
			return False

		#process citizen info
		citizen = self.get_citizen_from_data(citizen_id,first_name,last_name,middle_name)

		#process ownership details
		if property and citizen:
			try:
				ownership = Ownership.objects.get(asset_property=property,owner_citizen=citizen,i_status='active')		
				return ownership		
			except:
				#remove any old deprecated ownership of this property
				old_ownerships = Ownership.objects.filter(asset_property=property,i_status='active')		
				if old_ownerships:
					old_ownerships.update(i_status='inactive')
				#add new ownership data
				ownership = Ownership(owner_citizen=citizen,asset_property=property,share=100)
				if approval_date != '':
					ownership.date_started = datetime.strptime(approval_date, "%d/%m/%Y")
				ownership.save()
				self.new_ownership_list.append(ownership)
				return ownership
		else:
			#print "ERROR IN PROCESSING PROPERTY UPI " + upi
			return False


	# skip those records with invalid citizen number
	def get_citizen_from_data(self,citizen_id,first_name,last_name,middle_name):
		citizen = None
		if len(citizen_id) == 16 and citizen_id.isdigit():
			citizen = CitizenMapper.getCitizenByCitizenId(citizen_id)
			if citizen:
				return citizen
			else:
				citizen = Citizen()
				citizen.first_name = first_name
				citizen.last_name = last_name
				citizen.middle_name = middle_name
				citizen.citizen_id = citizen_id
				citizen.save()
				self.new_citizen_list.append(citizen)
				return citizen
		else:
			citizens = CitizenMapper.getCitizensByConditions({'first_name':first_name,'last_name':last_name,'middle_name':middle_name})
			if citizens:
				if len(citizens) == 1:
					return citizens[0]
				else:
					self.error_list['no_id_multi_citizens_found'].append(first_name + ' ' + last_name + ' ' + middle_name)
					return None
			else:
				citizen = Citizen()
				citizen.first_name = first_name
				citizen.last_name = last_name
				citizen.middle_name = middle_name
				citizen.foreign_identity_number = citizen_id
				citizen.save()
				self.new_citizen_list.append(citizen)
				return citizen



	def get_property_from_data(self,parcel_id,village_name,cell_name,sector_name,district_name,province_name):
		sector = None
		cell = None
		village = None
		try:
			sector = Sector.objectsIgnorePermission.get(name__iexact = sector_name,district__name__iexact=district_name)
			cell = Cell.objects.get(sector=sector,name__iexact=cell_name)
			village = Village.objects.get(cell=cell,name__iexact=village_name)
		except Exception:
			self.error_list['invalid_locality'].append(district_name + ' > ' + sector_name  + ' > ' + cell_name  + ' > ' +  village_name)
			a = Sector.objectsIgnorePermission.get(name__iexact = 'Remera',district__name__iexact='GASABO')
			'''
			print district_name + ' > ' + sector_name  + ' > ' + cell_name  + ' > ' +  village_name
			print sector
			print cell
			print village
			print '------'
			'''
			return None

		properties = Property.objectsIgnorePermission.filter(sector=sector,cell=cell,village=village,parcel_id=parcel_id,status_id=1)
		if properties and len(properties) > 0:
			self.update_property_list.append(properties[0])
			return properties[0]
		else:
			property = Property(sector=sector,parcel_id=parcel_id,cell=cell,village=village)
			property.plot_id = self.getNextPlotId()
			property.status = Status.objects.get(pk = 1)
			property.save()

			self.new_property_list.append(property)
			return property


	def getNextPlotId(self):
		if Property.objectsIgnorePermission.count() == 0:
			return "PM0000000001"
		else:
			last_plot_id = Property.objectsIgnorePermission.order_by("-id")[0].plot_id
			plot_id_digit_part = int(last_plot_id[2:]) + 1
			plot_id_digit_part = str(plot_id_digit_part)
			zeros = ''
			for i in range(10-len(plot_id_digit_part)):
				zeros = zeros + '0'
			return 'PM' + zeros + plot_id_digit_part