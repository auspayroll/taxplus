# Create your views here.
from django.shortcuts import render_to_response,HttpResponse
from django.template import RequestContext
from test.models import *
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


'''
Import property data into property and boundary tables
'''

def search(request):
	if GET.has_key('page'):
		geodata = PropertyMapper.getPropertyGeoData(properties.object_list)
		form = tax_search_property_form()
		return render_to_response('tax/tax_tax_search1.html', {'form':form,'properties':properties,'geodata':geodata},
                            context_instance=RequestContext(request))



def import_historical_data(request):
	imported_fee_types = {}
	imported_fee_types[5] = 'Rental tax'
	imported_fee_types[6] = 'Real eastate tax'
	imported_fee_types[36] = 'Property tax'
	imported_fee_types[39] = 'Billboard tax'
	imported_fee_types[41] = 'Cleaning fee'
	
	Historical.objects.all().delete()
	fee = ImportFeeData()
	for fee in ImportFeeData.objects.all():
		print fee.ID_Redevance
		historical = Historical()
		citizens = Citizen.objects.filter(foreign_record_id = fee.ID_Contribuable)
		businesses = Business.objects.filter(foreign_record_id = fee.ID_Contribuable)
		if len(citizens) > 0:
			historical.citizen = citizens[0]
		elif len(businesses) >0:
			historical.business = businesses[0]
		else:
			continue
		historical.amount_due = fee.Redevance
		historical.fee_id = fee.ID_Redevance
		if fee.ID_TypRecette in [5, 6, 36, 39, 41]:
			historical.fee_type = imported_fee_types[fee.ID_TypRecette]
		else:
			continue
		historical.due_date = fee.DateLimitePayment
		historical.late_paymemt_penalty = fee.Accroissement
		historical.late_payment_interest = fee.IntRetard
		if fee.ID_Facture:
			historical.is_paid = True
			invoices = ImportInvoiceData.objects.filter(ID_Facture = fee.ID_Facture)
			if len(invoices) > 0:
				invoice = ImportInvoiceData()
				invoice = invoices[0]
				historical.invoince_no = invoice.NumFacture
		period = ImportPeriodData()
		period = ImportPeriodData.objects.get(ID_Periode=fee.ID_Periode)
		historical.period_from = period.DateDebut
		historical.period_to = period.DateFin
		historical.save()

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
		conditions['parcel_id'] = int(obj.parcel_id)
		conditions['cell'] = obj.cell
		conditions['village'] = obj.village
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

		property.parcel_id = int(obj.parcel_id)
		property.cell = str(obj.cell).upper()
		property.cell_code = obj.cell_code
		property.village = str(obj.village).upper()
		property.shape_leng = obj.shape_leng
		property.shape_area = obj.shape_area
		property.boundary =  boundary
		property.sector = sector
		property.save()
	return HttpResponse('Hello')



'''
Import citizen and business data
'''

def import_citizen_and_business_data(request):
	Business.objects.all().delete()
	Citizen.objects.all().delete()
	

	for obj1 in ImportCitizenData.objects.all():
		obj = ImportCitizenData()
		obj = obj1
		print obj.ID_Contribuable
		if obj.TIN and obj.TIN !='':
			business = None
			business_objects = Business.objects.filter(tin=obj.TIN)
			if len(business_objects) > 0:
				business = business_objects[0]
			else:
				business = Business()
				business.tin = obj.TIN
			business.foreign_record_id = obj.ID_Contribuable
			business.i_status = 'active'
			business.name = obj.Noms
			business.date_started = obj.DateCreation
			
			## processing telephone number
			phone_numbers = get_phone_numbers(obj.Tel)
			if phone_numbers:
				business.phone1 = phone_numbers[0]
				if len(phone_numbers) > 1:
					business.phone2 = phone_numbers[1]
			try:
				business.save()
			except Exception, DatabaseError:
				connection._rollback()
				continue
		else:
			citizen = Citizen()
			names = get_names(obj.Noms)
			citizen.first_name = names['first_name']
			citizen.last_name = names['last_name']
			if names.has_key('middle_name'):
				citizen.middle_name = names['middle_name']

			province = None
			district = None
			sector = None
			cell = None
			village = None
			address = None

			if obj.ID_Res_Province and obj.ID_Res_District and obj.ID_Res_Secteur and obj.ID_Res_Cellule and obj.ID_Res_Mudugudu:
				if obj.ID_Res_Province.strip()!='' and obj.ID_Res_District.strip()!='' and obj.ID_Res_Secteur.strip()!='' and obj.ID_Res_Cellule.strip()!='' and obj.ID_Res_Mudugudu.strip()!='':
					try:
						province = ImportProvinceData.objects.get(pk = obj.ID_Res_Province).Libelle
						district = ImportDistrictData.objects.get(pk = obj.ID_Res_District).Libelle
						sector = ImportSectorData.objects.get(pk = obj.ID_Res_Secteur).Libelle
						cell = ImportCellData.objects.get(pk = obj.ID_Res_Cellule).Libelle
						village = ImportVillageData.objects.get(pk = obj.ID_Res_Mudugudu).Libelle
						address = str(village)+' '+str(cell)+' '+str(sector)+' '+str(district)+' '+str(province)
					except Exception:
						address = None
						connection._rollback()
				else: address = None
			else:
				address = None
			citizen.address = address
			citizen.citizen_id = obj.NumID
			citizen.date_of_birth = convert_datetime_string(obj.DateNaiss)
			citizen.foreign_record_id = obj.ID_Contribuable
			if obj.ID_Sexe == 1:
				citizen.gender = 'Female'
			elif obj.ID_Sexe == 2:
				citizen.gender = 'Male'
			elif obj.ID_Sexe == 0:
				citizen.gender = 'Unknown'
			
			## processing telephone number
			phone_numbers = get_phone_numbers(obj.Tel)
			if phone_numbers:
				citizen.phone_1 = phone_numbers[0]
				if len(phone_numbers) > 1:
					citizen.phone_2 = phone_numbers[1]
			try:
				citizen.save()
			except IntegrityError, DatabaseError:
				connection._rollback()
				continue
	return HttpResponse("Hello")
def test(request):
	boundary=Boundary.objects.get(pk=9999)
	points_json = []
	str1=str(boundary.property_boundary_3857.wkt)
	str1=str1.replace('POLYGON', '').replace('((', '').replace('))', '')[1:]
	points = str1.split(', ')
	poly = ''
	for point in points:
		point_json={}
		point_parts = point.split(' ')
		point_x_parts=point_parts[0].replace(' ','').split('.')
		point_x=point_x_parts[0]+'.'+point_x_parts[1][:5]
		point_y_parts=point_parts[1].replace(' ','').split('.')
		point_y=point_y_parts[0]+'.'+point_y_parts[1][:5]
		point_json['x']=point_x
		point_json['y']=point_y
		points_json.append(point_json)
	return render_to_response('test/property_sector_view1.html', {'points':points_json},
                context_instance=RequestContext(request))



'''
cope with phone formats like 
	(1) '0788502086,/0750303718'
	(2) '0788593946/574327'
	(3) '0788533569\0788305004' 
	(4) '0788301489 \ 504466'
	(5) '0788772087\ 501564'
'''
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

def generate_cental_point_for_boundaries(request):
	for boundary in Boundary.objects.all():
		if boundary.polygon_imported:
			boundary.central_point = boundary.polygon_imported.centroid
		else:
			boundary.central_point = boundary.polygon.centroid
		boundary.save()
	return HttpResponse("OK")

def mytest(request):
	boundary =  Boundary.objects.get(id = 19)

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
		print "nation_id: "  + nation_id + "   (None)"
		return None

def get_property_from_row(row_values, sector_name, cell_name, village_name):
	sector = Sector.objects.filter(name__iexact = sector_name).filter(district__name__istartswith = 'GAS')[0]
	parcel_id = int(row_values[0])
	conditions = {}
	conditions['parcel_id'] = parcel_id
	conditions['village'] = village_name
	conditions['cell'] = cell_name
	conditions['sector'] = sector
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