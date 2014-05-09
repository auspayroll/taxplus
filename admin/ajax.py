from pmauth.models import PMPermission,PMContentType,PMModule,PMUser,PMGroup
from citizen.models import Citizen
from django.http import HttpResponse
from django.utils import simplejson
from jtax.models import DeclaredValue
from property.models import *
from django.contrib.gis.geos import Point, GEOSGeometry, Polygon
from django.forms import model_to_dict
from log.mappers.LogMapper import LogMapper
from property.mappers.DistrictMapper import DistrictMapper
from property.mappers.SectorMapper import SectorMapper
from property.mappers.PropertyMapper import PropertyMapper
from property.mappers.OwnershipMapper import OwnershipMapper
from property.mappers.CouncilMapper import CouncilMapper
from jtax.mappers.PropertyTaxItemMapper import PropertyTaxItemMapper
from jtax.mappers.DeclaredValueMapper import DeclaredValueMapper
from jtax.mappers.TaxMapper import TaxMapper

from datetime import datetime
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from jtax.models import PropertyTaxItem
from businesslogic.TaxBusiness import TaxBusiness
from admin.Common import Common
from common.models import *
from property.functions import *

from asset.models import *
import json
from django.db.models import Q
from django.db.models.loading import get_model
from jtax.models import  Setting
from admin.Common import Common


def getPaymentAmount(request):
	if request.method == 'GET':
		GET = request.GET
		payment_category = GET['payment_category']
		payment_subcategory = GET['payment_subcategory']
		payment_subcategory = Setting.objects.filter(tax_fee_name__iexact = payment_category, sub_type__iexact=payment_subcategory)
		result = {}
		if payment_subcategory:
			payment_subcategory = payment_subcategory[0]
			result['amount'] = payment_subcategory.value
		else:
			result['amount'] = 0
		return HttpResponse(json.dumps(result), mimetype="application/json")


def getPaymentSubcategory(request):
	if request.method == 'GET':
		GET = request.GET
		payment_category = GET['payment_category']
		payment_subcategories = Setting.objects.filter(tax_fee_name__iexact = payment_category, sub_type__isnull=False).exclude(sub_type='').values('sub_type')
		payment_subcategories = Common.get_value_list(payment_subcategories,'sub_type')
		result = {}
		result['subcategories'] = payment_subcategories
		if not payment_subcategories:
			payment_category = Setting.objects.get(tax_fee_name__iexact = payment_category)
			result['amount'] = payment_category.value
		else:
			result['amount'] = 0
		return HttpResponse(json.dumps(result), mimetype="application/json")


def getObjectsByParentId(request):
	if request.method == 'GET':
		GET = request.GET
		object_type = GET['object_type']
		object_id = GET['object_id']
		if object_type and object_id:
			result = {}
			objects_json = []
			if object_id:
				try:
					if(object_type=='province'):
						province = Province.objects.get(pk = object_id)
						districts = District.objects.filter(province = province)
						for district in districts:
							object_json = {}
							object_json['key'] = district.id
							object_json['value'] = district.name
							objects_json.append(object_json)
					if(object_type=='district'):
						district = District.objects.get(pk = object_id)
						sectors = Sector.objects.filter(district = district)
						for sector in sectors:
							object_json = {}
							object_json['key'] = sector.id
							object_json['value'] = sector.name
							objects_json.append(object_json)
					if(object_type=='sector'):
						try:
							sector = Sector.objects.get(pk = object_id)
							cells = Cell.objects.filter(sector = sector)
							for cell in cells:
								object_json = {}
								object_json['key'] = cell.id
								object_json['value'] = cell.name
								objects_json.append(object_json)
						except Exception as e:
							return HttpResponse('', mimetype="application/json")
					if(object_type=='cell'):
						cell  = Cell.objects.get(pk = object_id)
						villages = Village.objects.filter(cell = cell)
						for village in villages:
							object_json = {}
							object_json['key'] = village.id
							object_json['value'] = village.name
							objects_json.append(object_json)
				except Exception:
					objects_json = []
			result['objects'] = objects_json
			return HttpResponse(json.dumps(result), mimetype="application/json")
		return HttpResponse(json.dumps({'objects':[]}), mimetype="application/json")


def getPropertySector(request):
	if request.method == 'POST':
		POST = request.POST
		boundary = POST['boundary']
		plist=[]
		points = boundary.split('#')
		for point in points:
			parts = point.split(',')
			point_x=parts[0]
			point_y=parts[1]
			plist.append(GEOSGeometry('POINT(%s %s)' %(point_x, point_y)))
		plist.append(plist[0])
		polygon = Polygon(plist)
		sectors = Sector.objects.all()
		sectors_results = []
		for sector in sectors:
			if sector.boundary:
				boundary = sector.boundary
				if boundary.polygon.intersects(polygon):
					sectors_results.append(sector)
		if len(sectors_results) == 0:
			return HttpResponse('')
		else:
			sector = sectors_results[0]
			info = {}
			info['district_id'] = sector.district.id
			info['district_name'] = sector.district.name
			info['sector_id'] = sector.id
			info['sector_name'] = sector.name
			cells = Cell.objects.filter(sector = sector).order_by('name')
			
			cells_to_return = []
			for cell in cells:
				cell_dict = {}
				cell_dict['id'] = cell.id
				cell_dict['name'] = cell.name
				cells_to_return.append(cell_dict)
			info['cells'] = cells_to_return
			return HttpResponse(json.dumps(info), mimetype="application/json")


def add_property(request):
	if request.method == 'POST':
		POST = request.POST
		is_leasing = POST['is_leasing']
		parcel_id = POST['parcel_id']
		sector = Sector.objects.get(id=POST['sector']) 
		cell = Cell.objects.get(id=POST["cell"]) 
		village = Village.objects.get(id=POST['village']) 
		
		conditions = {"parcel_id":parcel_id,"village":village,"cell":cell,"sector":sector}
		existing_properties = PropertyMapper.getPropertiesByConditions(conditions)
		if existing_properties:
			return HttpResponse('This plot already exists!')
		new_boundary = None
		boundary = POST['boundary']
		if boundary and str(boundary).strip()!='':
			plist=[]
			points = boundary.split('#')
			for point in points:
				parts = point.split(',')
				point_x=parts[0]
				point_y=parts[1]
				plist.append(GEOSGeometry('POINT(%s %s)' %(point_x, point_y)))
			plist.append(plist[0])
			polygon = Polygon(plist)
			new_boundary = Boundary.objects.create(polygon=polygon, type = "manual", i_status="active")
		
		property = Property()
		property.parcel_id = parcel_id
		property.village = village
		property.cell = cell
		property.sector = sector
		
		if is_leasing == 'true':
			property.is_leasing = True
		else:
			property.is_leasing = False
		
		if new_boundary:
			property.boundary = new_boundary
		property.status=Status.objects.get(name = 'Active')
		property.save()
		new_data = model_to_dict(property)
		LogMapper.createLog(request,object=property,action="add", property=property)
		return HttpResponse('OK')

"""
def generate_property_tax(request):
	if request.method == 'GET' and request.GET.has_key("plot_id"):
		to_json = {}
		to_json['message']=''
		plot_id = request.GET['plot_id']
		
		## No declared values at all.
		declaredValues = DeclaredValueMapper.getDeclaredValuesByPlotId(plot_id)
		if declaredValues is None:
			to_json['message']='Sorry! No declared value for this property.'
			to_json['propertytaxitems'] = []
			return HttpResponse(simplejson.dumps(to_json), mimetype='application/json')
		
		## No usable declared values to generate tax due form.
		declaredValueDueDate = None
		declaredValue = DeclaredValueMapper.getDeclaredValueByPlotId(plot_id)
		declaredValueDueDate = declaredValue.date_time + relativedelta(years=3)
		now = datetime.now()
		now = timezone.make_aware(now, timezone.get_default_timezone())
		if now > declaredValueDueDate:
			to_json['message']='No usable declared values to generate tax due form.'
			to_json['propertytaxitems'] = []
			return HttpResponse(simplejson.dumps(to_json), mimetype='application/json')
		
		tax_items = TaxBusiness.generatePropertyTax(request,plot_id)
		tax_items = PropertyTaxItemMapper.getCleanPropertyTaxItems(tax_items)
		to_json = {}
		to_json['propertytaxitems']=tax_items
		return HttpResponse(simplejson.dumps(to_json), mimetype='application/json')
"""
def add_district(request):
	
	if request.method == 'POST':
		POST = request.POST
		name = POST['name']
		boundary = POST['boundary']
		
		plist=[]
		points = boundary.split('#')
		for point in points:
			parts = point.split(',')
			point_x=parts[0]
			point_y=parts[1]
			plist.append(GEOSGeometry('POINT(%s %s)' %(point_x, point_y)))
		plist.append(plist[0])
		polygon = Polygon(plist)
		boundary = Boundary.objects.create(polygon=polygon, type = "manual", i_status="active")
		district = District()
		district.name = name
		district.boundary = boundary
		district.i_status="active"
		district.save()
		
		new_data = model_to_dict(district)
		LogMapper.createLog(request,object=district,action="add")
		return HttpResponse('OK')

def add_sector(request):
	"""
	Add property and create a log for this action
	"""
	if request.method == 'POST':
		POST = request.POST
		name = POST['name']
		district = POST['district']
		boundary = POST['boundary']
		council = POST['council']
		
		plist=[]
		points = boundary.split('#')
		for point in points:
			parts = point.split(',')
			point_x=parts[0]
			point_y=parts[1]
			plist.append(GEOSGeometry('POINT(%s %s)' %(point_x, point_y)))
		plist.append(plist[0])
		polygon = Polygon(plist)
		boundary = Boundary.objects.create(polygon=polygon, type = "manual", i_status="active")
		sector = Sector()
		sector.name = name
		sector.boundary = boundary
		sector.district = DistrictMapper.getDistrictById(district)
		sector.council = CouncilMapper.getCouncilById(council)
		sector.i_status="active"
		sector.save()
		new_data = model_to_dict(sector)
		LogMapper.createLog(request,object=sector,action="add")
		return HttpResponse('OK')

def add_council(request):
	"""
	Add property and create a log for this action
	"""
	if request.method == 'POST':
		POST = request.POST
		name = POST['name']
		address = POST['address']
		boundary = POST['boundary']
		
		plist=[]
		points = boundary.split('#')
		for point in points:
			parts = point.split(',')
			point_x=parts[0]
			point_y=parts[1]
			plist.append(GEOSGeometry('POINT(%s %s)' %(point_x, point_y)))
		plist.append(plist[0])
		polygon = Polygon(plist)
		boundary = Boundary.objects.create(polygon=polygon, type = "manual", i_status="active")
		council = Council()
		council.name = name
		council.boundary = boundary
		council.address = address
		council.i_status="active"
		council.save()
		new_data = model_to_dict(council)
		LogMapper.createLog(request,object=council,action="add")
		return HttpResponse('OK')




def search_user(request):
	"""
	search user with entered keyword, case-insensitive.
	Return a list of users having full name contains the entered keyword
	"""
	result =""
	match_count = 0
	if request.method == 'GET':
		GET = request.GET
		if GET.has_key('keyword'):	  
			keyword = GET['keyword'].lower()
			users = PMUser.objects.all()
			for user in users:
				fullname = user.firstname.lower() + ' ' + user.lastname.lower()
				match = keyword in fullname				 
				if match:
					match_count = match_count + 1
					if match_count == 1:
						result = ''+str(user.id)+':'+user.firstname.capitalize()+' '+user.lastname.capitalize()
					else:
						result = result + '#'+str(user.id)+':'+user.firstname.capitalize()+' '+user.lastname.capitalize()
	return HttpResponse(result)


def search_object_names(request):
	"""
	search district/council/sector with entered keyword, case-insensitive.
	Return a list of district having name contains the entered keyword
	"""
	result = []
	if request.method == 'GET':
		GET = request.GET
		if GET.has_key('term') and GET.has_key('type'):		 
			keyword = GET['term'].lower().strip()
			list = []
			if GET['type'] == 'district':
				list = District.objects.filter(name__istartswith=keyword).order_by('name')[:20]
			elif GET['type'] == 'council':
				list = Council.objects.filter(name__istartswith=keyword).order_by('name')[:20]
			elif GET['type'] == 'sector':
				list = Sector.objects.filter(name__istartswith=keyword).order_by('name')[:20]

			for i in list:
				record = { 'id': i.id, 'value': i.name }
				result.append(record)
	return HttpResponse(json.dumps(result), mimetype="application/json")

def search_citizen(request):
	"""
	search citizen with entered keyword, case-insensitive.
	Return a list of citizens having full name contains the entered keyword
	"""
	result =""
	match_count = 0
	if request.method == 'GET':
		GET = request.GET
		if GET.has_key('keyword'):		 
			keyword = GET['keyword'].lower()
			citizens = Citizen.objects.all()
			for citizen in citizens:
				if citizen.middle_name and citizen.middle_name !='':
					fullname = citizen.first_name.lower() + ' ' + citizen.middle_name.lower() + ' ' + citizen.last_name.lower()
				else:
					fullname = citizen.first_name.lower() + ' ' + citizen.last_name.lower()
				match = keyword in fullname				 
				if match:
					match_count = match_count + 1
					if match_count == 1:
						if citizen.middle_name and citizen.middle_name !='':
							result = ''+str(citizen.id)+':'+citizen.first_name.capitalize()  + ' ' + citizen.middle_name.capitalize()+ ' ' + citizen.last_name.capitalize()
						else:
							result = ''+str(citizen.id)+':'+citizen.first_name.capitalize()+' '+citizen.last_name.capitalize()
					else:
						result = result + '#'+str(citizen.id)+':'+citizen.first_name.capitalize()+' '+citizen.last_name.capitalize()
	return HttpResponse(result)

def search_property_in_area(request):
	"""
	search properties within a specified area.
	For each property satisfying the above requirement, info is returned including plot_id, parcel_id, village, cell, sector 
	and shape (This is represented Propertyby a polygon with known vertice coordinates).
	The above info is returned with json format
	"""
	to_json = {}
	properties=[]
	purpose = None
	if request.method == 'GET':
		GET = request.GET
		if GET.has_key('purpose'):
			purpose = GET['purpose']
		if GET.has_key('boundary'):		 
			boundary = GET['boundary']
			plist=[]
			points = boundary.split('#')
			for point in points:
				parts = point.split(',')
				point_x=parts[0]
				point_y=parts[1]
				plist.append(GEOSGeometry('POINT(%s %s)' %(point_x, point_y)))
			plist.append(plist[0])
			polygon = Polygon(plist)


			boundaries1 = Boundary.objects.filter(polygon__intersects=polygon.wkt)
			boundaries2 = Boundary.objects.filter(polygon_imported__intersects=polygon.wkt)
			boundaries = []
			if len(boundaries1) > 0:
				for obj in boundaries1:
					if obj not in boundaries:
						boundaries.append(obj)
			if len(boundaries2) > 0:
				for obj in boundaries2:
					if obj not in boundaries:
						boundaries.append(obj)

			match_polygon = 0
			for boundary in boundaries:
				property = Property.objects.filter(boundary = boundary)
				if len(property) == 0:
					continue
				else:
					property = property[0]
				property_json = {}
				points_json = []

				str1 = None
				if boundary.polygon_imported:
					str1=str(boundary.polygon_imported.wkt)
				else:
					str1=str(boundary.polygon.wkt)
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
				property_json['points']=points_json
				
				property_json['plot_id']=property.plot_id
				property_json['upi'] = property.getUPI()
				property_json['parcel_id']=property.parcel_id
				property_json['village']=property.village
				property_json['cell']=property.cell
				property_json['sector']=property.sector.name
				
				
				
				propertytaxitems_json=[]
				propertytaxitems = PropertyTaxItemMapper.getCleanPropertyTaxItems(property)
				property_json['propertytaxitems'] = propertytaxitems
				
					
				declarevalues_json=[]
				declarevalues = DeclaredValue.objects.filter(plot_id = property.plot_id).order_by("-date_time")
				for declare_value in declarevalues:
					declare_value_json = {}
					declare_value_json['accepted']=declare_value.accepted
					declare_value_json['datetime']=declare_value.date_time.strftime('%Y-%m-%d')
					declare_value_json['staffid']=declare_value.staff_id
					declare_value_json['amount']=str(declare_value.currency) + " " +str(declare_value.amount)
					declarevalues_json.append(declare_value_json)
				property_json['declarevalues']=declarevalues_json				
				properties.append(property_json)
			to_json['properties'] = properties
	search_message_all = "does a map search of properties for " + purpose + " purpose."
	LogMapper.createLog(request,action="search", search_message_all=search_message_all)
	return HttpResponse(simplejson.dumps(to_json), mimetype='application/json')


def search_property_field(request):
	"""
	Give the user a list of sector names, cell names and vilages names with given entered words.
	The above info is returned with json format
	"""
	if request.method == 'GET':
		GET = request.GET
		if GET.has_key('sector'):		 
			keyword = GET['sector']
			matched_properties = Property.objects.filter(sector__pk = int(keyword))
			if len(matched_properties) == 0:
				return HttpResponse("")
			result = []
			for property in matched_properties:
				if property.sector not in result:
					result.append(property.sector)
			return HttpResponse(simplejson.dumps(result), mimetype='application/json')
		if GET.has_key('cell'):		 
			keyword = GET['cell']
			matched_cells = Cell.objects.filter(name__istartswith=keyword)
			if GET.has_key('sector_id'):
				matched_cells = matched_cells.filter(sector__id = int(GET['sector_id']))
			if len(matched_cells) == 0:
				return HttpResponse("")
			result = []
			for cell in matched_cells[:20]:
				result.append(cell.name)
			return HttpResponse(simplejson.dumps(result), mimetype='application/json')
		if GET.has_key('village'):		 
			keyword = GET['village']
			matched_properties = Property.objects.filter(village__istartswith=keyword)
			if len(matched_properties) == 0:
				return HttpResponse("")
			result = []
			for property in matched_properties:
				if property.village not in result:
					result.append(property.village)
			return HttpResponse(simplejson.dumps(result), mimetype='application/json')
		
def search_property_by_fields(request):
	"""
	Search a property or properties by provided conditions
	If plotid is given, the remaining conditions will not be considered, as each plotid corresponds to a property
	The above info is returned with json format
	"""
	
	result = ""
	to_json = {}
	properties=[]
	upi = None
	sector = None
	parcel_id = None
	village = None
	cell = None
	purpose = None
	refresh = None
	matched_properties = []
	if request.method == 'GET':
		GET = request.GET
		if GET.has_key('purpose'):
			purpose = GET['purpose']
		if GET.has_key('refresh'):
			refresh = GET['refresh']
		if GET.has_key('upi') and GET['upi']!='':
			upi = GET['upi']
		if GET.has_key('sector') and GET['sector']!='':
			sector = SectorMapper.getSectorById(int(GET['sector']))
		#if GET.has_key('village') and GET['village']!='':
		#	village = GET['village']
		if GET.has_key('cell') and GET['cell']!='':
			cells = Cell.objects.filter(sector=sector,name__iexact=GET['cell'])
			if cells:
				cell = cells[0]
		if GET.has_key('parcel_id') and GET['parcel_id']!='':
			parcel_id = GET['parcel_id']
		
		if upi:
			matched_properties = PropertyMapper.getPropertyByUPI(upi)
		else:
			#matched_properties = PropertyMapper.getPropertiesByConditions({'sector':sector,'cell':cell, 'village':village, 'parcel_id':parcel_id})
			matched_properties = PropertyMapper.getPropertiesByConditions({'sector':sector,'cell':cell, 'parcel_id':parcel_id})
		
		property_list = []
		if type(matched_properties) == Property:
			property_list.append(matched_properties)
		else:
			property_list = matched_properties

		for property in property_list:
			points_json = []
			property_json = {}
			boundary=property.boundary
			if boundary:
				str1 = None
				if boundary.polygon_imported:
					str1=str(boundary.polygon_imported.wkt)
				else:
					str1=str(boundary.polygon.wkt)
				str1=str1.replace('POLYGON', '').replace('((', '').replace('))', '')[1:]
				points = str1.split(', ')
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
				property_json['points']=points_json
			property_json['upi'] = property.getUPI()
			property_json['parcel_id']=property.parcel_id
			property_json['village']=property.village
			property_json['cell']=property.cell
			property_json['sector']=property.sector.name
			
			propertytaxitems_json=[]
			propertytaxitems = PropertyTaxItemMapper.getCleanPropertyTaxItems(property)
			property_json['propertytaxitems'] = propertytaxitems
			
			declarevalues_json=[]
			declarevalues = DeclaredValue.objects.filter(property = property).order_by("-date_time")
			for declare_value in declarevalues:
				declare_value_json = {}
				declare_value_json['accepted']=declare_value.accepted
				declare_value_json['datetime']=declare_value.date_time.strftime('%Y-%m-%d')
				user = declare_value.user
				username = user.firstname + ' '+ user.lastname
				declare_value_json['staff']=username
				citizen = declare_value.citizen
				if citizen.middle_name and citizen.middle_name != '':
					declare_value_json['citizen']= citizen.first_name + ' '+ citizen.middle_name+ '' + citizen.last_name
				else:
					declare_value_json['citizen']= citizen.first_name + ' '+citizen.last_name
				declare_value_json['amount']=str(declare_value.currency) + " " +str(declare_value.amount)
				declarevalues_json.append(declare_value_json)
			property_json['declarevalues']=declarevalues_json
			properties.append(property_json)			
		to_json['properties'] = properties
		
		"""
		if int(refresh) == 0:
			if sector:
				LogMapper.createLog(request,action="search", search_message_action=" does a text search of properties", search_message_purpose=purpose, search_conditions={"parcel_id":parcel_id,"village":village,"sector":sector.name})
			else:
				LogMapper.createLog(request,action="search", search_message_action=" does a text search of properties", search_message_purpose=purpose, search_conditions={"parcel_id":parcel_id,"village":village})
		else:
			matched_properties = Property.objects.filter(plot_id=plot_id)
			matched_property = matched_properties[0]
			property_info = str(matched_property.parcel_id)+" " +matched_property.village+", "+matched_property.cell + ", " +matched_property.sector.name
			search_message_action = " views property ["+property_info+"]"
			LogMapper.createLog(request,action="search", search_message_action=search_message_action, search_message_purpose=purpose)
		"""
		return HttpResponse(simplejson.dumps(to_json), mimetype='application/json')


def search_properties_for_printing(request):
	if request.method == 'GET':
		GET = request.GET
		citizen_id = None
		citizen = None
		#plot_id = None
		parcel_id = None
		village = None
		cell = None
		sector =None
		page = None
		has_ownership = 'all'
		page_records = 20
		properties_to_return = []
		
		if GET.has_key("boundary"):
			boundary = GET['boundary']
			plist=[]
			points = boundary.split(',')
			count = 0;
			for point in points:
				count = count + 1
				if count%2 == 1:
					point_x=point
					point_y = points[count]				
				else:
					continue
				plist.append(GEOSGeometry('POINT(%s %s)' %(point_x, point_y)))
			plist.append(plist[0])
			polygon = Polygon(plist)

			boundaries1 = Boundary.objects.filter(polygon__intersects=polygon.wkt)
			boundaries2 = Boundary.objects.filter(polygon_imported__intersects=polygon.wkt)
			boundaries = []
			if len(boundaries1) > 0:
				for obj in boundaries1:
					if obj not in boundaries:
						boundaries.append(obj)
			if len(boundaries2) > 0:
				for obj in boundaries2:
					if obj not in boundaries:
						boundaries.append(obj)

			match_polygon = 0
			for boundary in boundaries:
				property = Property.objects.filter(boundary = boundary)
				if len(property) == 0:
					continue
				else:
					property = property[0]
					property.upi = PropertyMapper.getUPIByPropertyId(property.id)
					properties_to_return.append(property)
			if properties_to_return and len(properties_to_return) > 0:
				properties_to_return.sort(key=lambda x: (x.sector, x.parcel_id), reverse=False)
		else:
			if GET.has_key('citizen_id'):
				citizen_id = GET['citizen_id']
				if citizen_id:
					from citizen.mappers.CitizenMapper import CitizenMapper
					citizen = CitizenMapper.getCitizenByCitizenId(citizen_id)
			#if GET.has_key('plot_id'):
			#	plot_id = GET['plot_id']
			if GET.has_key('parcel_id'):
				parcel_id = GET['parcel_id']
				if not parcel_id or str(parcel_id) == 'None':
					parcel_id = None
			if GET.has_key('village'):
				village = GET['village']
				if village and village!="":
					from property.mappers.VillageMapper import VillageMapper
					village = VillageMapper.getVillageById(village)
			if GET.has_key('cell'):
				cell = GET['cell']
				if cell and cell!="":
					from property.mappers.CellMapper import CellMapper
					cell = CellMapper.getCellById(cell)
			if GET.has_key('sector'):
				sector = GET['sector']
				if sector and sector!="":
					sector = SectorMapper.getSectorById(sector)
			if GET.has_key('has_ownership'):
				has_ownership = GET['has_ownership']
			if GET.has_key('page'):
				page = int(GET['page'])
			properties_to_return = PropertyMapper.getPropertiesByConditions({'sector':sector,'village':village, 'cell':cell, 'parcel_id':parcel_id,'citizen':citizen,'has_ownership':has_ownership,})
		
		
		if page:
			if (page+1)*page_records<=len(properties_to_return):
				properties_to_return = properties_to_return[page*page_records:page*page_records+20]
			else:
				properties_to_return = properties_to_return[page*page_records:len(properties_to_return)]
		property_array = []

		upi_prefix = ''
		if len(properties_to_return) > 0:
			upi_prefix = Common.get_upi_prefix(properties_to_return[0])
		for obj in properties_to_return:
			
			property_obj = {}
			property_obj['upi'] = obj.upi
			property_obj['parcel_id'] = obj.parcel_id
			
			if obj.sector:
				property_obj['sector'] = obj.sector.getDisplayName()
			else:
				property_obj['sector'] = ''
			
			if obj.cell:
				property_obj['cell'] = obj.cell.name
			else:
				property_obj['cell'] = ''
			
			if obj.village:
				property_obj['village'] = obj.village.name
			else:
				property_obj['village'] = ''
			
			property_obj['address'] = obj.getDisplayName()
			

			ownerships = OwnershipMapper.getCurrentOwnershipsByPropertyId(obj.id)
			owners = ''
			phone = ''
			email = ''
			taxes = ''
			if ownerships:
				owner_count = 0
				for ownership in ownerships:
					if owner_count > 0:
						owners = owners + "<br>"
					owners = owners + ownership.owner_citizen.getDisplayName()
					if phone == '' and ownership.owner_citizen.phone_1:
						phone = ownership.owner_citizen.phone_1
					if email == '' and ownership.owner_citizen.email:
						email = ownership.owner_citizen.email
			TaxMapper.generateTaxes(obj,request)
					
			# check whether rental income tax application to this property
			tax_count = 0
			if obj.is_leasing:
				taxes = taxes + 'Rental income tax'
				tax_count = tax_count + 1
			if not obj.is_land_lease:
				fix_asset_tax_item = PropertyTaxItemMapper.getPropertyTaxItem(obj)
				if not fix_asset_tax_item.is_paid:
					if tax_count > 0:
						taxes = taxes + '<br>'
					taxes = taxes + "Fixed asset tax"
			property_obj['all_owners'] = owners
			property_obj['taxes'] = taxes
			property_obj['phone'] = phone
			property_obj['email'] = email

			property_array.append(property_obj)
		if sector:
			result = {"properties":property_array, "upi_prefix":upi_prefix, "sector":sector.getDisplayName(),}
		else:
			result = {"properties":property_array, "upi_prefix":upi_prefix,}
		return HttpResponse(json.dumps(result), mimetype="application/json")

def search_property_by_plot_id(request):
	"""
	search business with entered business name or TIN, case-insensitive.
	Return a list of businesses having full name contains the entered keyword
	"""
	result = []
	if request.method == 'GET':
		GET = request.GET
		if GET.has_key('term'):		 
			keyword = GET['term'].lower().strip()
			properties = Property.objects.filter(plot_id__istartswith=keyword).order_by('plot_id','cell')[:20]
			for b in properties:
				record = { 'id': b.id, 'value': b.getDisplayName() + ' (PID: ' + b.plot_id + ')'}
				result.append(record)
	return HttpResponse(json.dumps(result), mimetype="application/json")

def search_property_by_upi(request):
	"""
	search business with entered business name or TIN, case-insensitive.
	Return a list of businesses having full name contains the entered keyword
	"""
	result = []
	if request.method == 'GET':
		GET = request.GET
		if GET.has_key('term'):		 
			keyword = GET['term'].lower().strip()
			b = PropertyMapper.getPropertyByUPI(keyword)
			if b:
				record = { 'id': b.id, 'value': b.getDisplayName() + ' (UPI: ' + keyword + ')'}
				result.append(record)
	return HttpResponse(json.dumps(result), mimetype="application/json")

#def search_citizen_clean(request):
#	"""
#	search citizen with entered citizen name or citizenID, case-insensitive.
#	Return a list of businesses having full name contains the entered keyword
#	"""
#	result = []
#	if request.method == 'GET':
#		GET = request.GET
#		if GET.has_key('term'):		 
#			keyword = GET['term'].lower().strip()
			#check if user enter 2 words
#			if " " in keyword:
#				terms = keyword.split(' ')
#				citizens = Citizen.objects.filter(Q(first_name__iexact=terms[0],last_name__icontains=terms[1]) | Q(last_name__iexact=terms[0],first_name__icontains=terms[1]) | Q(citizen_id__istartswith=keyword)).order_by('first_name','last_name','citizen_id')[:50]
#				print citizens
#			else:
#				citizens = Citizen.objects.filter(Q(first_name__icontains=keyword) | Q(last_name__icontains=keyword) | Q(citizen_id__istartswith=keyword)).order_by('first_name','last_name','citizen_id')[:50]
#			for b in citizens:
#				record = { 'id': b.id, 'value': b.first_name + ' ' + b.last_name + ' (CID: ' + b.citizen_id +')'}
#				result.append(record)
#	return HttpResponse(json.dumps(result), mimetype="application/json")

def search_citizen_clean(request):
	"""
	search citizen with entered citizen name or citizenID, case-insensitive.
	Return a list of businesses having full name contains the entered keyword
	"""
	result = []
	citizens = None
	if request.method == 'GET':
		GET = request.GET
		if GET.has_key('term'):		 
			keyword = GET['term'].lower().strip()
			if GET.has_key('stype') and GET['stype'] in ['nid','first_name','last_name']:
				if GET['stype'] == 'nid':
					citizens = Citizen.objects.filter(citizen_id__istartswith=keyword).order_by('citizen_id')[:20]
				elif GET['stype'] == 'name':
					citizens = Citizen.objects.filter(Q(first_name__istartswith=keyword) | Q(last_name__istartswith=keyword) | Q(middle_name__istartswith=keyword)).order_by('first_name')[:20]
			else:
				# Intelligent search allowing any combination of names and citizenid
				terms = []
				names = []
				ids = []
				if ' ' in keyword:
					terms = keyword.split(' ')
				else:
					terms.append(keyword)
				for term in terms:
					if term.isnumeric():
						ids.append(term)
					else:
						names.append(term)
				if len(names) == 1:
					citizens = Citizen.objects.filter(Q(first_name__istartswith=names[0]) | Q(last_name__istartswith=names[0]) | Q(middle_name__istartswith=names[0])).order_by('first_name','last_name','citizen_id')
				elif len(names) == 2:
					citizens = Citizen.objects.filter(Q(first_name__iexact=names[0], middle_name__istartswith=names[1]) | \
													  Q(middle_name__iexact=names[0], first_name__istartswith=names[1]) | \
													  Q(first_name__iexact=names[0], last_name__istartswith=names[1]) | \
													  Q(last_name__iexact=names[0], first_name__istartswith=names[1]) | \
													  Q(last_name__iexact=names[0], middle_name__istartswith=names[1]) | \
													  Q(middle_name__iexact=names[0], last_name__istartswith=names[1])).order_by('first_name','last_name','citizen_id')
				elif len(names) == 3:
					citizens = Citizen.objects.filter(Q(first_name__iexact=names[0], middle_name__iexact=names[1], last_name__istartswith=names[2]) | \
													  Q(middle_name__iexact=names[0], first_name__iexact=names[1], last_name__istartswith=names[2]) | \
													  Q(first_name__iexact=names[0], last_name__iexact=names[1], middle_name__istartswith=names[2]) | \
													  Q(middle_name__iexact=names[0], last_name__iexact=names[1], first_name__istartswith=names[2]) | \
													  Q(last_name__iexact=names[0], middle_name__iexact=names[1], first_name__istartswith=names[2]) | \
													  Q(last_name__iexact=names[0], first_name__iexact=names[1], middle_name__istartswith=names[2])).order_by('first_name','last_name','citizen_id')

				if citizens:
					if len(ids) ==1:
						citizens =citizens.filter(citizen_id__istartswith=ids[0])[:20]
					elif len(ids) == 0:
						citizens = citizens[:20]
					else:
						citizens = []
				else:
					if len(ids) ==1:
						citizens =Citizen.objects.filter(citizen_id__istartswith=ids[0])[:20]
					elif len(ids) == 0:
						citizens = []
					else:
						citizens = []
			for b in citizens:
				fullname = None
				if b.middle_name:
					fullname = b.first_name + ' ' + b.middle_name + ' ' + b.last_name
				else:
					fullname = b.first_name + ' ' + b.last_name
				record = { 'id': b.id, 'value': b.first_name + ' ' + b.last_name + ' (CID: ' + b.citizen_id +')', 'first_name':b.first_name,'last_name':b.last_name,'middle_name':b.middle_name,'nid':b.citizen_id, 'fullname':fullname}
				result.append(record)
	return HttpResponse(json.dumps(result), mimetype="application/json")


def search_business(request):
	"""
	search business with entered business name or TIN, case-insensitive.
	Return a list of businesses having full name contains the entered keyword
	"""
	result = []
	if request.method == 'GET':
		GET = request.GET
		if GET.has_key('term'):		 
			keyword = GET['term'].lower().strip()
			if GET.has_key('stype') and GET['stype'] in ['nid','first_name','last_name']:
				if GET['stype'] == 'tin':
					businesses = Business.objects.filter(tin__istartswith=keyword).order_by('tin')[:20]

				elif GET['stype'] == 'name':
					businesses = Business.objects.filter(name__icontains=keyword).order_by('name')[:20]
			else:
				businesses = Business.objects.filter(Q(name__icontains=keyword) | Q(tin__istartswith=keyword)).distinct().order_by('name','tin')[:20]

			for b in businesses:
				branches = {}
				subbusinesses = b.subbusiness_set.all().order_by('branch')
				if subbusinesses:
					for i in subbusinesses:
						branches[i.id] = i.branch

				record = { 'id': b.id, 'value': b.name + ' (TIN: ' + b.tin +')','tin':b.tin,'name':b.name,'branches':branches}
				result.append(record)
	return HttpResponse(json.dumps(result), mimetype="application/json")

def search_vehicle(request):
	"""
	search vehicle with entered plate number, case-insensitive.
	Return a list of vehicles
	"""
	result = []
	if request.method == 'GET':
		GET = request.GET
		if GET.has_key('term'):		 
			keyword = GET['term'].lower().strip()
			list = Vehicle.objects.filter(plate_number__icontains=keyword)[:20]
			for i in list:
				record = { 'id': i.id, 'value': i.vehicle_type.title() + ' [Plate No: ' + i.plate_number + ']'}
				result.append(record)
	return HttpResponse(json.dumps(result), mimetype="application/json")

def search_billboard(request):
	return search_asset_by_name(request,'Billboard')

def search_shop(request):
	return search_asset_by_name(request,'Shop')

def search_stall(request):
	return search_asset_by_name(request,'Stall')

def search_office(request):
	return search_asset_by_name(request,'Office')

def search_asset_by_name(request,modelName):
	"""
	search asset with entered name, case-insensitive.
	Return a list of assets having full name contains the entered keyword
	depend on the provided asset type
	"""
	result = []
	if request.method == 'GET':
		GET = request.GET
		if GET.has_key('term'):		 
			keyword = GET['term'].lower().strip()
			list = get_model('asset',modelName).objects.filter(name__icontains=keyword).order_by('name')[:20]
			for i in list:
				record = { 'id': i.id, 'value': i.name}
				result.append(record)
	return HttpResponse(json.dumps(result), mimetype="application/json")