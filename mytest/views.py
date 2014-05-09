# Create your views here.
from django.shortcuts import render_to_response,HttpResponse
from django.http import HttpResponse
from django.template import RequestContext, Context, loader
from mytest.models import *
from property.models import *

from property.functions import *
from property.mappers.SectorMapper import SectorMapper
from property.mappers.PropertyMapper import PropertyMapper
from citizen.mappers.CitizenMapper import CitizenMapper
from common.models import Status
from citizen.models import Citizen
#from asset.models import Business
#from jtax.models import *
from django.db import IntegrityError, DatabaseError, connection
import xlrd, os
from admin.Common import Common
from django.template import RequestContext
from django.shortcuts import render_to_response,get_object_or_404
from  StringIO import StringIO
from django.http import HttpResponse
from property.mappers.VillageMapper import VillageMapper
from property.mappers.CellMapper import CellMapper
from property.mappers.SectorMapper import SectorMapper
from property.mappers.DistrictMapper import DistrictMapper
from property.mappers.OwnershipMapper import OwnershipMapper
import re
from jtax.models import * 
from log.models import Log
from pmauth.models import PMUser
import csv


def letter(request):
	return render_to_response('letters/fee_assessment_notice.html', {},context_instance=RequestContext(request))

def fk_test(request):
	fees = Fee.objects.filter(fee_type='land_lease', property__isnull=False).select_related()
	fee = fees[0]
	

def generate_tax_reminder(request):
	from jtax.shared_functions import *
	#property = Property.objects.get(pk =  18934)
	#tax_item = PropertyTaxItem.objects.get(pk = 1819)
	#print get_reminder_email_subject(tax_item)
	
	
	
	
	
	#citizens = get_contact_citizens(property)
	
	
	#tax_item = PropertyTaxItem.objects.get(property_id = 20879)
	#generate_tax_reminder_email(tax_item)
	return HttpResponse("OK")


"""
def populateCellAndVillage(request):
	for property in Property.objects.all():
		if property.cell_code:
			cell = Cell.objects.filter(code__iexact = property.cell_code)
			if cell and len(cell) > 0:
				cell = cell[0]
				property.cell1 = cell
				property.save()
		if not property.cell1:
			if property.cell and property.cell != '':
				cell = Cell.objects.filter(sector = property.sector, name__iexact = property.cell)
				if cell and len(cell) > 0:
					cell = cell[0]
					property.cell1 = cell
					property.save()
		if property.cell1:
			if property.village and property.village!='':
				village = Village.objects.filter(name__iexact=property.village,cell = property.cell1)
				if village and len(village) > 0:
					village = village[0]
					property.village1 = village
					property.save()
	return HttpResponse("oK")
"""					
	
	
"""					
def exportUPI(request):
	with open('upi.csv','wb') as f:
		writer = csv.writer(f)
		for province in Province.objects.all():
			districts = District.objects.filter(province = province)
			for district in districts:
				sectors = Sector.objects.filter(district = district)
				for sector in sectors:
					cells = Cell.objects.filter(sector = sector)
					for cell in cells:
						villages = Village.objects.filter(cell = cell)
						for village in villages:
							arr = []
							arr.append(province.name)
							arr.append(district.name)
							arr.append(sector.name)
							arr.append(cell.name)
							arr.append(village.name)
							writer.writerow(arr)
	return HttpResponse("OK")
"""


"""
def populateLog(request):
	for log in Log.objects.all():
		if log.plot_id:
			property = Property.objects.filter(plot_id__iexact = log.plot_id)
			if len(property) > 0:
				property = property[0]
				log.property = property
				log.save()
		if log.citizen_id:
			citizen = Citizen.objects.filter(citizen_id__iexact = log.citizen_id)
			if len(citizen) > 0:
				citizen = citizen[0]
				log.citizen1 = citizen
				log.save()
		if log.business_id:
			business = Business.objects.filter(pk = log.business_id)
			if len(business) > 0:
				business = business[0]
				log.business1 = business
				log.save()
		if log.user_id:
			user = PMUser.objects.filter(pk = log.user_id)
			if len(user) > 0:
				user = user[0]
				log.user1 = user
				log.save()
	return HttpResponse("OK")
"""

"""
def populateLog1(request):
	for log in Log.objects.all():
		if log.citizen1:
			log.citizen = log.citizen1
			log.save()
		if log.business1:
			log.business = log.business1
			log.save()
		if log.user1:
			log.user = log.user1
			log.save()
	return HttpResponse("OK")

"""
"""
def populateDeclareValue1(request):
	for obj in DeclaredValue.objects.all():
		if obj.citizen_id:
			citizen = CitizenMapper.getCitizenById(obj.citizen_id)
			obj.citizen1 = citizen
			obj.save()
		if obj.staff_id:
			user = PMUser.getUserById(obj.staff_id)
			obj.user = user
			obj.save()
	return HttpResponse("oK")
"""

"""
def populateFee(request):
	for fee in Fee.objects.all():
		if fee.target == 'property':
			property = Property.objects.filter(pk = int(fee.target_id))
			if len(property) > 0:
				property = property[0]
				fee.property = property
				fee.save()
		elif fee.target == 'business':
			if fee.target_branch_id:
				subbusiness = SubBusiness.objects.filter(pk = int(fee.target_branch_id))
				if len(subbusiness) > 0:
					subbusiness = subbusiness[0]
					fee.subbusiness = subbusiness
					fee.save()
			else:
				business = Business.objects.filter(pk = int(fee.target_id))
				if len(business) > 0:
					business = business[0]
					fee.business = business
					fee.save()
	return HttpResponse("OK")	
"""
"""
def populatePropertyForPropertyTaxItem(request):
	for obj in PropertyTaxItem.objects.all():
		if obj.plot_id:
			properties = Property.objects.filter(plot_id__iexact=obj.plot_id)
			if len(properties) > 0:
				property = properties[0]
				obj.property = property
				obj.save()
	for obj in DeclaredValue.objects.all():
		if obj.plot_id:
			properties = Property.objects.filter(plot_id__iexact=obj.plot_id)
			if len(properties) > 0:
				property = properties[0]
				obj.property = property
				obj.save()
	for obj in AssignedValue.objects.all():
		if obj.plot_id:
			properties = Property.objects.filter(plot_id__iexact=obj.plot_id)
			if len(properties) > 0:
				property = properties[0]
				obj.property = property
				obj.save()
	for obj in LandRentalTax.objects.all():
		if obj.plot_id:
			properties = Property.objects.filter(plot_id__iexact=obj.plot_id)
			if len(properties) > 0:
				property = properties[0]
				obj.property = property
				obj.save()
	for obj in RentalIncomeTax.objects.all():
		if obj.plot_id:
			properties = Property.objects.filter(plot_id__iexact=obj.plot_id)
			if len(properties) > 0:
				property = properties[0]
				obj.property = property
				obj.save()
	
	return HttpResponse("OK")

def merge_property(request):
	for property in Property.objects.filter(cell__iexact = 'kiyovu'):
		if not property.village and not property.boundary:
			property1 = Property.objects.filter(cell__iexact = 'kiyovu').filter(parcel_id = property.parcel_id).exclude(id=property.id)
			if len(property1) > 0:
				property1 = property1[0]
				if not OwnershipMapper.getOwnershipsByPlotId(property1.plot_id):
					if property1.village:
						property.village = property1.village
					if property1.shape_leng:
						property.shape_leng = property1.shape_leng
					if property1.shape_area:
						property.shape_area = property1.shape_area
					if property1.boundary:
						property.boundary = property1.boundary
					property.save()
					property1.delete()
	return HttpResponse("OK")


def getArray(str):
	parts = []
	m = re.match('(\d+) (\D+) (\d+) (\D+) (\d+) (\D+) (\d+) (\D+)',str)
	for i in range(1,9):
		parts.append(m.group(i))
	return parts

def importcode(request):
	file_name = 'UPI coding.txt'
	path = os.path.dirname(os.path.realpath(__file__)) + '/' + file_name
	f = open(path,'r')
	line = f.readline()
	count = 0
	province_code, district_code, sector_code, cell_code, village_code = None, None, None, None,None
	province, sector, district, cell, village = None, None, None, None, None
	
	
	while line:
		count = count + 1
		print "Line: " + str(count)
		line = str(line).strip()
		if line == '':
			continue

		parts = getArray(line)

		'''
		Get the right province
		'''

		if count == 1 or parts[0][:2] != province.code:
			province_code = parts[0][:2]
			province = Province.objects.get(code = province_code)
		'''
		Check whether district exists.
		If it does not exist, add new district
		If it exists, update this district
		'''
		if count == 1 or parts[0]!= district.code:
			district_code = parts[0]
			district = DistrictMapper.getDistrictByName(parts[1])
			if district:
				district.code = district_code
				district.province = province
			else:
				district = District(name = str(parts[1]).upper(), code = district_code, province =province)
			district.save()
		

		'''
		Check whether sector exists.
		If it does not exist, add new sector
		If it exists, update this sector
		'''
		if count == 1 or parts[2]!= sector.code:
			sector_code = parts[2]
			sector = SectorMapper.getSectorByDistrictNameAndSectorName(district.name,parts[3])
			if sector:
				sector.code = sector_code
				sector.province = province
				sector.district = district
			else:
				sector = Sector(name = str(parts[3]).upper(), code = sector_code, province =province, district = district)
			sector.save()


		'''
		Check whether cell exists.
		If it does not exist, add new cell
		If it exists, update this cell
		'''
		if count == 1 or parts[4]!= cell.code:
			cell_code = parts[4]
			cell = CellMapper.getCellByCode(cell_code)
			if cell:
				cell.name = str(parts[5]).upper()
				cell.sector = sector
			else:
				cell = Cell(name = str(parts[5]).upper(), code = cell_code, sector = sector)
			cell.save()
		
		'''
		Check whether village exists.
		If it does not exist, add new village
		If it exists, update this village
		'''
		if count == 1 or parts[6]!= village.code:
			village_code = parts[6]
			village = VillageMapper.getVillageByCode(village_code)
			if village:
				village.name = str(parts[7]).upper()
				village.cell = cell
			else:
				village = Village(name = str(parts[7]).upper(), code = village_code, cell = cell)
			village.save()

		line = f.readline()
	f.close()
	return HttpResponse("OK")

def graph(request):
	value1 = ['foo', 32]
	value2 = ['bar', 64]
	value3 = ['baz', 96]
	values = []
	values.append(value1)
	values.append(value2)
	values.append(value3)


	line_values = []
	line_values.append(['2004',1000,400])
	line_values.append(['2005',1170,460])
	line_values.append(['2006',660,1120])
	line_values.append(['2007',1030,540])


	#table_values = []
	#table_values.append(['Mike', 10000, True])
	#table_values.append(['Jim',  8000,  False])
	#table_values.append(['Alice', 12500, True])
	#table_values.append(['Bob', 7000, True])


	return render_to_response('test/design.html', {'values':values,'line_values':line_values, },
							context_instance=RequestContext(request))

def home(request):
	file = "nyarugenge-2012-12-31.csv"
	#file = "remera-2013-02-20.csv"
	f = open(os.path.dirname(os.path.realpath(__file__)) + "/data/" + file,'r')
	fu = 0
	i = 0
	UPIL = []
	NIDL = []
	ownersfound = 0
	ownersnotfound = 0
	propertiesfound = 0
	propertiesnotfound = 0
	citizenfound = 0
	citizensnotfound = 0
	ownersskiped = 0
	for line in f:
		i = i +1
		if i == 1:
			continue
		if i <= 143:
			continue
		print 'line' + str(i)
		connection._rollback()
		data = line.split(',')
	
		#NYANUGENGE - FILE FORMAT 
		# SURNAME 
		# FIRST NAME 
		# MIDDLE NAME 
		# NATIONAL ID 
		# UPI 
		# AREA 
		# APROVED 
		# DESCRIPTION 
		# LEASE TIME 
		# CELL 
		# SECTOR 
		# DISTRICT 
		
		if file == "nyarugenge-2012-12-31.csv":
			if data[4] not in UPIL:
				UPIL.append(data[4])
			if data[3] not in NIDL:
				NIDL.append(data[3])
			# Setup person model for person import into system
			person = importDataPerson()
			if data[0] is not '':
				person.surname = data[0]
			if data[1] is not '':
				person.given_name = data[1]
			if data[2] is not '':
				person.middle_name = data[2]
			if data[3] is not '':
				person.national_id = data[3]
			
			#setup property for data import
			propertyA = importDataLand()
			if data[4] is not '':
				propertyA.upi = data[4]
			if data[5] is not '':
				propertyA.area = data[5]
			if data[6] is not '':
				propertyA.is_approved = data[6]
			if data[7] is not '':
				propertyA.short_description = data[7]
			if data[8] is not '':
				propertyA.lease_term = data[8]
			if data[9] is not '':
				propertyA.cell_name = data[9]
			if data[10] is not '':
				propertyA.sector_name = data[10]
			if data[11] is not '':
				propertyA.district_name = data[11]
		elif file == "remera-2013-02-20.csv":
			person = importDataPerson()
			propertyA = importDataLand()
			# new format - because the fucker is different 
			# SURNAME,GIVEN NAME,ID CARD NO,UPI, AREA ,STATUS,DESCRIPTION,TERM,ANNUAL LAND RENT,PROVINCE,DISTRICT,SECTOR,CELL,VILLAGE		
			if data[0] is not '':
				person.surname = data[0]
			if data[1] is not '':
				person.given_name = data[1]
			if data[2] is not '':
				person.national_id = data[2]
			if data[3] is not '':
				propertyA.upi = data[3]
			if data[4] is not '':
				propertyA.area = data[4]
			# data[5] is status
			# data[6] is description
			if data[7] is not '':
				propertyA.lease_term = data[7]
			
			if data[8] is not '':
				#this is land rent - how much was paid! 
				pass
			# data[10] is Province
			if data[10] is not '':
				propertyA.district_name = data[10]
			if data[11] is not '':
				propertyA.sector_name = data[11]
			if data[12] is not '':
				propertyA.cell_name = data[12]
			#data 13 is village!
			
			pass

		tmp1 = propertyA.upi.split('/')
		upia = "0"+tmp1[0] + tmp1[1] + tmp1[2] + tmp1[3]
		#print upia
		tmp2 = upiBreakdown.objects.get(province_id=tmp1[0],district_id=tmp1[1],sector_id=tmp1[2],cell_id=tmp1[3])
			
		try:
			print "UPI LOOKUP RECORD FOUND: " + tmp2.district.upper() + " / " + tmp2.sector.upper() + " / " + tmp2.cell.upper()
		except:
			print "UPI FINDER RECORD NOT FOUND"

		#theproperty = Property.objects.all().filter(cell_code = upia, parcel_id__exact=tmp1[4])
		try:
			theproperty = Property.objects.get(cell_code = upia, parcel_id__exact=tmp1[4])
		except:
			theproperty = None

		print "**************"
		print upia
		print theproperty
		print "**************"

		if theproperty:
				
			#tmp3 = Property.objects.filter(cell_code = upia, parcel_id__exact=tmp1[4])
			#print "PROPERTY FOUND : " + theproperty.plot_id
			propertiesfound = propertiesfound + 1
			if propertyA.lease_term and int(propertyA.lease_term) > 0:
				theproperty.is_land_lease = True
			else:
				theproperty.is_land_lease = False

			theproperty.save()

		else:
			theproperty = None
			print "Property Record Not Found in Database"
			#propertyA.save()
			propFF = Property()
			propFF.cell_code = upia
			propFF.cell = tmp2.cell.upper()
			propFF.parcel_id = tmp1[4]
			propFF.sector_id = 2

			if propertyA.lease_term and int(propertyA.lease_term) > 0:
				propFF.is_land_lease = True
			else:
				propFF.is_land_lease = False

			#bad hack just to get the fucking job done 
			# connection._rollback()
			connection._commit()
			connection._rollback()
			cursor = connection.cursor()
			cursor.execute('select max(plot_id) from property_property')
			plot_id = cursor.fetchone()
			#print plot_id[0]
			#print "PLOTID"+plot_id
			print "PLOGID2"+plot_id[0]
			PID = int(plot_id[0].replace('PM','')) + 1
			PID = str(PID) 
			PID = PID.zfill(10)
			FULLPID = "PM" + PID
			print FULLPID
			print ""
			print ""
			propFF.plot_id = FULLPID
			propFF.save()
			propertiesnotfound = propertiesnotfound + 1
			theproperty = Property.objects.get(cell_code = upia, parcel_id__exact=tmp1[4])
			connection._commit()
			# something is wrong here with the shit
	
		try:
			personcheck = CitizenMapper.getCitizenByCitizenId(person.national_id)
		except:
			personcheck = None
		print personcheck
		if not personcheck:
			#personcheck = False
			print "PERSON NOT FOUND"
			#person.save()
			citizen = Citizen()
			citizen.first_name = person.given_name
			citizen.last_name = person.surname
			citizen.middle_name = person.middle_name
			citizen.citizen_id = person.national_id
			citizen.save()
			personcheck = CitizenMapper.getCitizenByCitizenId(person.national_id)
			citizensnotfound = citizensnotfound +1
			connection._commit()
		else:
			citizenfound = citizenfound + 1
			print "Person Found"

			

## check ownership records
		if theproperty and personcheck:
			try:
				propertyownership = Ownership.objects.get(property=theproperty,citizen=personcheck)
					
			except:
				propertyownership = False

			if not propertyownership:
				propertyowner = Ownership()
				propertyowner.citizen = personcheck
				propertyowner.property = theproperty
				propertyowner.save()
				ownersnotfound = ownersnotfound + 1
				print "WE ADDED THIS RECORD TO THE DATABASE"
			else:
				print "WE FOUND THIS OWNERSHIP RECORDS IN OUR DATABASE"
				ownersfound = ownersfound + 1
		else:
			print "PROPERTY OWNERSHIP CHECK SKIPPED"
			ownersskiped = ownersskiped + 1
		connection._rollback()



#		personcheck = importDataPerson.objects.all().filter(national_id=person.national_id)
#		if not personcheck:
#			#print "person not found"
#			person.save()
#			#print "person saved"
#			print "PERSON NOT FOUND IN DATABASE"	
#		else:
#			print "PERSON FOUND IN DATABASE"
#			#pass


#		propertycheck = importDataLand.objects.all().filter(upi=property.upi)
#		if not propertycheck:
#			property.save()
#		else:
#			pass##
#
#		P1 = importDataPerson.objects.get(national_id=data[3])
#		P2 = importDataLand.objects.get(upi=data[4])
#			
#		if P1 and P2:
#			ownershipcheck = importDataLandOwnership.objects.all().filter(land_id=P2,person_id=P1)
#			if not ownershipcheck:
#				own = importDataLandOwnership()
#				own.land_id = P2
#				own.person_id = P1
#				own.save()
#				# print "item added"
#			else:
#				print "duplicate ownership record : " + str(P2.upi) + " / " + P1.surname + " " + P1.given_name
#				pass##
#
#		
#'''
	#	print "-------------------------------------"
	print "Records : " + str(i)
	UP =  str(len(UPIL))
	NI =  str(len(NIDL))
	print "UP " + UP
	print "NI " + NI
	print "FU's :" + str(fu)
	print "Owners : " + str(ownersfound) + " / " + str(ownersnotfound) + "/" + str(ownersskiped)
	print "Propertues : " + str(propertiesfound) + " / " + str(propertiesnotfound)
	list = {'UP':UP,
			'NI':NI,
			'fu':fu,}


	#t = loader.get_template('home.html')
	#c = Context({
	#			 'UP':UP,
	#			 'NI':NI,
	#			 'fu':fu,
				

	#})
	#return HttpResponse(t.render(c))
	return HttpResponse(str(list))


def import_property_data(request):
	
	'''
	### get all the boundary IDs for all council, district, sector, and delete other boundaries.
	boundary_keys = []
	for obj in Council.objects.all():
		if obj.boundary:
			if obj.boundary.pk not in boundary_keys:
				boundary_keys.append(obj.boundary.pk)
	for obj in District.objects.all():
		if obj.boundary:
			if obj.boundary.pk not in boundary_keys:
				boundary_keys.append(obj.boundary.pk)
	for obj in Sector.objects.all():
		if obj.boundary:
			if obj.boundary.pk not in boundary_keys:
				boundary_keys.append(obj.boundary.pk)
	
	### delete all boundaries with id in boundary_keys
	Boundary.objects.exclude(pk__in = boundary_keys).delete()
	### delete all properties 
	Property.objects.all().delete()
	'''

	
	for obj in ImportPropertyData.objects.all():
		''' 
		check whether province exists in property_province table or not
		If not, create a record for this province
		'''
		print obj.ogc_fid
		province = None
		if str(obj.province).lower() == 'kigali':
			province = Province.objects.filter(name__iexact='KIGALI CITY')
		else:
			province = Province.objects.filter(name__iexact=obj.province)
		if len(province) > 0:
			province = province[0]
		else:
			province = Province()
			province.name = obj.province
			province.i_status = 'active'
			province.save()
		''' 
		check whether district exists in property_district table or not
		If not, create a record for this district
		'''
		district = District.objects.filter(name__iexact=obj.district)
		if len(district) > 0:
			district = district[0]
		else:
			district = District()
			district.name = obj.district
			district.i_status = 'active'
			district.save()

		
		''' 
		check whether sector exists in property_sector table or not
		If not, create a record for this sector
		'''
		sector = SectorMapper.getSectorsByDistrictAndName(obj.district,obj.sector)
		if len(sector) > 0:
			sector = sector[0]
		else:
			sector = Sector()
			sector.district = district
			sector.province = province
			sector.name = obj.sector
			sector.i_status = 'active'
			sector.save()
	
		'''
		check whether property exists or not
		'''
		conditions = {}
		conditions['parcel_id'] = int(obj.parcels_id)
		conditions['cell'] = obj.cell
		#conditions['village'] = obj.village
		conditions['sector']= sector
		property = None
		properties = PropertyMapper.getPropertiesByConditions(conditions)
		if properties and len(properties) > 0:
			property = properties[0]
		else:
			property = Property()
			plot_id = getNextPlotId()
			property.plot_id = plot_id
			property.status = Status.objects.get(name='Active')
		
		'''
		create boundary for the new property record
		'''
		boundary = Boundary()
		boundary.polygon_imported = obj.wkb_geometry
		boundary.type = 'official'
		boundary.i_status = 'active'
		boundary.save()

		property.parcel_id = int(obj.parcels_id)
		property.cell = str(obj.cell).upper()
		property.cell_code = obj.cell_code
		property.village = str(obj.village).upper()
		property.shape_leng = obj.shape_leng
		property.shape_area = obj.shape_area
		property.boundary =  boundary
		property.sector = sector
		property.save()
	return HttpResponse('Hello')
















































def get_phone_numbers(phone_number_string):
	if not phone_number_string or phone_number_string.strip() == '':
		return None
	else:
		phone_numbers = []
		if ',' in phone_number_string:
			temp_numbers = phone_number_string.split(',')
			for obj in temp_numbers:
				obj = obj.strip()
				if obj and obj != '' and obj not in phone_numbers:
					phone_numbers.append(obj)
		elif '/' in phone_number_string:
			temp_numbers = phone_number_string.split('/')
			for obj in temp_numbers:
				obj = obj.strip()
				if obj and obj != '' and obj not in phone_numbers:
					phone_numbers.append(obj)
		elif '\\' in phone_number_string:
			temp_numbers = phone_number_string.split('\\')
			for obj in temp_numbers:
				obj = obj.strip()
				if obj and obj != '' and obj not in phone_numbers:
					phone_numbers.append(obj)
		else:
			phone_numbers.append(phone_number_string.strip())
		return phone_numbers

def get_names(name_str):
	name_str = name_str.strip()
	names = name_str.split(' ')
	name_dict = {}
	name_dict['first_name'] = names[0]
	name_dict['last_name'] = names[len(names)-1]
	if len(names) > 3:
		middle_name = name_str.replace(name_dict['first_name'],'').replace(name_dict['last_name'],'').strip()
		name_dict['middle_name'] = middle_name
	return name_dict

def convert_datetime_string(str):
	parts = str.split('/')
	str = parts[2] + '-'
	if parts[1] == '00':
		str = str + '01' +  '-'
	else:
		str = str + parts[1] + '-' 
	if parts[0] == '00':
		str = str + '01'
	else:
		str = str + parts[0]
	return str


def is_row_empty(row_values):
	empty = True
	for i in range(0, len(row_values)):
		if str(row_values[i]).strip()!='':
			empty = False
			break;
	return empty


def is_header(row_values):
	print "===========begin header====================="
	print row_values
	print "===========end header======================="
	result = True
	for i in range(0, len(row_values)):
		if str(row_values[i]).strip().isdigit() or str(row_values[i]).strip()=='':
			result = False
			break;
	return result
	
def is_sector_cell_village(row_values):
	if str(row_values[1]).strip()=='':
		return False
	else:
		result = True
		for i in range(2,7):
			if str(row_values[i]).strip()!='':
				result = False
				break
		return result

# skip those records with invalid citizen number
def get_citizen_from_row(row_values):
	nation_id = str(row_values[2]).strip()
	citizen = None
	name = get_names(row_values[1])
	if len(nation_id) == 16 and nation_id.isdigit():
		print "nation_id: " + nation_id
		citizen = CitizenMapper.getCitizenByCitizenId(nation_id)
		if citizen:
			return citizen
		else:
			citizen = Citizen()
			citizen.first_name = name['first_name']
			citizen.last_name = name['last_name']
			if name.has_key('middle_name'):
				citizen.middle_name = name['middle_name']
			citizen.citizen_id = nation_id
			citizen.save()
			return citizen
	else:
		print "nation_id: "  + nation_id + "	(None)"
		return None

"""
"""
def get_property_from_row(row_values, sector_name, cell_name, village_name):
	sector = Sector.objects.filter(name__iexact = sector_name).filter(district__name__istartswith = 'GAS')[0]
	parcel_id = int(row_values[0])
	conditions = {}
	conditions['parcel_id'] = parcel_id
	conditions['sector'] = sector
	cells = Cell.objects.filter(sector=sector,name__iexact=cell_name)
	if cells:
		conditions["cell"] = cells[0]
	villages = Village.objects.filter(cell=conditions["cell"],name__iexact=village_name)
	if villages:
		conditions["village"] = villages[0]

	properties = PropertyMapper.getPropertiesByConditions(conditions)
	if properties and len(properties) > 0:
		return properties[0]
	else:
		property = Property()
		property.plot_id = getNextPlotId()
		property.sector = sector
		property.parcel_id = parcel_id
		property.cell = cell_name
		property.village = village_name
		property.foreign_plot_id = row_values[4]
		property.status = Status.objects.get(pk = 1)
		property.save()
		return property
"""

"""
def import_citizen_own_property_from_excel(request):
	path = str(os.getcwd()) + '\\test\\' + 'REMERA LAND VRAIS.xls'
	wb = xlrd.open_workbook(path)
	sh = wb.sheet_by_index(0)
	sector_name = None
	cell_name = None
	village_name = None
	heading = []
	count = 0

	for row_no in range(sh.nrows):
		#if row_no < 1244:
		#	continue
		print "**********************************"
		print row_no +  1
		print "**********************************"
		row_values = sh.row_values(row_no)
		
		# skip if this line is empty 
		if is_row_empty(row_values):
			print "empty row"
			continue

		#  check whether this line gives new village, cell or sector info
		if is_sector_cell_village(row_values):
			heading.append(row_values[1])
			print "add to heading::: " + str(row_values[1]) 
			continue
		
		# check whether this is table header
		if is_header(row_values):
			print "headings: " + str(heading)
			village_name = heading.pop()
			print "village: "+village_name			
			if len(heading) > 0:
				cell_name = heading.pop()
				print "cell: "+cell_name
			if len(heading) > 0:
				sector_name = heading.pop()
				print "sector: "+sector_name
			continue
		
		# process pure record from here ...	
		citizen = get_citizen_from_row(row_values)
		if not citizen:
			continue
		property = get_property_from_row(row_values, sector_name, cell_name, village_name)
		ownership = Ownership()
		ownership.citizen = citizen
		ownership.property = property
		ownership.share = 100
		ownership.save()

	return HttpResponse('yes')
"""
