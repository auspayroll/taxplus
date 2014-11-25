from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.contrib.gis.geos import Point, GEOSGeometry, Polygon
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.forms import model_to_dict
from django.conf import settings
from dev1 import variables
from django.contrib.auth.decorators import login_required
from taxplus.models import CategoryChoice

import os
import json
from datetime import date, timedelta
from datetime import time
from log.forms.forms import LogSearchForm
from log.models import *
from media.models import Media

from property.modelforms.modelforms import *
from property.forms.forms import *
from log.mappers.LogMapper import LogMapper
from property.mappers.PropertyMapper import PropertyMapper
from property.mappers.SectorMapper import SectorMapper
from property.mappers.DistrictMapper import DistrictMapper
from property.mappers.CouncilMapper import CouncilMapper
from property.mappers.OwnershipMapper import OwnershipMapper
from property.mappers.PropertyCommonMapper import PropertyCommonMapper

from asset.models import Ownership, Business

from citizen.mappers.CitizenMapper import CitizenMapper
from jtax.mappers.DeclaredValueMapper import DeclaredValueMapper
from businesslogic.TaxBusiness import TaxBusiness
from pmauth.mappers.ModuleMapper import ModuleMapper
from pmauth.mappers.ContentTypeMapper import ContentTypeMapper
from pmauth.mappers.PermissionMapper import PermissionMapper
from jtax.mappers.TaxMapper import TaxMapper
from admin.views import login


from jtax.models import *
from media.mappers.MediaMapper import MediaMapper
from annoying.functions import get_object_or_None


@login_required
def access_content_type(request, content_type_name, action = None, content_type_name1 = None, obj_id=None, part=None):
	"""
	This function direct request to the correspodding {module}_{contenttype}_default page
	"""
	if not request.session.get('user'):
		return login(request);
	if content_type_name == 'property':
		if not request.session['user'].has_content_type_by_name('property','property'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
		return property_default(request, action, content_type_name1, obj_id, part)
	if content_type_name == 'district':
		if not request.session['user'].has_content_type_by_name('property','district'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
		return district_default(request, action, content_type_name1, obj_id, part)
	if content_type_name == 'sector':
		if not request.session['user'].has_content_type_by_name('property','sector'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
		return sector_default(request, action, content_type_name1, obj_id, part)
	if content_type_name == 'council':
		if not request.session['user'].has_content_type_by_name('property','council'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
		return council_default(request, action, content_type_name1, obj_id, part)

	raise Http404


@login_required
def council_default(request, action, content_type_name1, obj_id, part):
	if not action:
		user = request.session.get('user')
		module = ModuleMapper.getModuleByName("property")
		content_type = ContentTypeMapper.getContentTypeByModuleAndName('council', module)
		actions = user.getActionsByContentTypeWithLink(content_type)
		return render_to_response('property/property_council_default.html', {\
							 'permissions':actions},
							  context_instance=RequestContext(request))
	elif action == 'add':
		if not request.session['user'].has_action_by_name('property','council','add_council'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))

		if request.method != 'POST':
			form =  CouncilCreationForm(initial={'i_status':'active',})
			return render_to_response('property/property_council_add.html', {'form':form,},
							  context_instance=RequestContext(request))
	elif action == 'view':
		if not request.session['user'].has_action_by_name('property','council','view_council'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))

		if request.method != 'POST' and not request.GET.has_key("name"):
			form = select_council_form(initial={'superuser':request.session.get('user').superuser,})
			return render_to_response('property/property_council_view.html', {'form':form,},
							  context_instance=RequestContext(request))
		else:
			councils = []
			if request.method == 'POST':
				POST = request.POST
				if POST.has_key("showall"):
					councils_result = CouncilMapper.getAllCouncils()
					if councils_result:
						councils = councils_result
				else:
					form = select_council_form(request.POST)
					if form.is_valid():
						name = form.cleaned_data["name"]
						LogMapper.createLog(request,action="search", search_object_class_name="council", search_conditions = {"name":name})
						council=CouncilMapper.getCouncilByName(name)
						if council:
							councils.append(council)
					else:
						return render_to_response('property/property_council_view.html', {'form':form, },
								  context_instance=RequestContext(request))
			else:
				name = request.GET['name']
				LogMapper.createLog(request,action="search", search_object_class_name="council", search_conditions = {"name":name,})
				council = CouncilMapper.getCouncilByName(name)
				councils.append(council)

			if not councils or len(councils) == 0:
						error_message = "No council found!"
						return render_to_response('property/property_council_view.html', {'form':form, 'error_message': error_message},
								  context_instance=RequestContext(request))
			else:
				to_json = {}
				sectors_json = {}
				to_json['councils']=PropertyCommonMapper.getGeoData(councils)
				if len(councils) == 1:
					#LogMapper.createLog(request,action="view",object=districts[0])
					sectors = SectorMapper.getSectorsByCouncilName(councils[0].name)
					sectors = PropertyCommonMapper.getGeoData(sectors)
					sectors_json['sectors']=sectors
					return render_to_response('property/property_council_view1.html', {'council': councils[0], 'councils':to_json, 'sectors':sectors_json,},
												  context_instance=RequestContext(request))
				else:
					#LogMapper.createLog(request,search_message_all="view all districts", object = districts[0])
					return render_to_response('property/property_council_view1.html', { 'councils':to_json},
						  context_instance=RequestContext(request))
	else:
		raise Http404


@login_required
def sector_default(request, action, content_type_name1, obj_id, part):
	if not action:
		user = request.session.get('user')
		module = ModuleMapper.getModuleByName("property")
		content_type = ContentTypeMapper.getContentTypeByModuleAndName('sector', module)
		actions = user.getActionsByContentTypeWithLink(content_type)
		return render_to_response('property/property_sector_default.html', {\
							 'permissions':actions},
							  context_instance=RequestContext(request))
	elif action == 'add':
		if not request.session['user'].has_action_by_name('property','sector','add_sector'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))

		if request.method != 'POST':
			form = SectorCreationForm(request,initial={'i_status':'active',})
			return render_to_response('property/property_sector_add.html', {'form':form,},
							  context_instance=RequestContext(request))
	elif action == 'view':
		if not request.session['user'].has_action_by_name('property','sector','view_sector'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
		if request.method != 'POST' and not request.GET.has_key("name"):
			form = select_sector_form()
			return render_to_response('property/property_sector_view.html', {'form':form,},
							  context_instance=RequestContext(request))
		else:
			if request.method != 'POST':
				name = request.GET['name']
				sector = SectorMapper.getSectorByName(name)
			else:
				form = select_sector_form(request.POST)
				if form.is_valid():
					id = form.cleaned_data["id"]
					name = form.cleaned_data["name"]
					LogMapper.createLog(request,action="search", search_object_class_name="sector", search_conditions = {"name":name})
					error_message = ""
					sector = SectorMapper.getSectorById(id)
				else:
					return render_to_response('property/property_sector_view.html', {'form':form,},
							  context_instance=RequestContext(request))
			if not sector:
					error_message = "No sector found!"
					return render_to_response('property/property_sector_view.html', {'form':form, 'error_message': error_message},
							  context_instance=RequestContext(request))
			else:
				boundary = None
				points_json = None
				if sector.boundary:
					boundary = sector.boundary
					str1 = None
					if boundary.polygon_imported:
						str1=str(boundary.polygon_imported.wkt)
					elif boundary.polygon:
						str1=str(boundary.polygon.wkt)
					if str1:
						points_json = []
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
				LogMapper.createLog(request,action="view",object=sector)
				return render_to_response('property/property_sector_view1.html', {'sector': sector, 'points':points_json},
						  context_instance=RequestContext(request))
	else:
		raise Http404


@login_required
def district_default(request,  action, content_type_name1, obj_id, part):
	if not action:
		user = request.session.get('user')
		module = ModuleMapper.getModuleByName("property")
		content_type = ContentTypeMapper.getContentTypeByModuleAndName('district', module)
		actions = user.getActionsByContentTypeWithLink(content_type)
		return render_to_response('property/property_district_default.html', {\
							 'permissions':actions},
							  context_instance=RequestContext(request))
	elif action == 'add':
		if not request.session['user'].has_action_by_name('property','district','add_district'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))

		if request.method != 'POST':
			form = DistrictCreationForm(initial={'i_status':'active',})
			return render_to_response('property/property_district_add.html', {'form':form,},
							  context_instance=RequestContext(request))
	elif action == 'view':
		if not request.session['user'].has_action_by_name('property','district','view_district'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))

		if request.method != 'POST' and not request.GET.has_key("name"):
			form = select_district_form(initial={'superuser':request.session.get('user').superuser,})
			return render_to_response('property/property_district_view.html', {'form':form,},
							  context_instance=RequestContext(request))
		else:
			districts = []
			if request.method == 'POST':
				POST = request.POST
				if POST.has_key("showall"):
					districts_result = DistrictMapper.getAllDistricts()
					if districts_result:
						districts = districts_result
				else:
					form = select_district_form(request.POST)
					if form.is_valid():
						name = form.cleaned_data["name"]
						LogMapper.createLog(request,action="search", search_object_class_name="district", search_conditions = {"name":name,})
						district = DistrictMapper.getDistrictByName(name)
						districts.append(district)
					else:
						return render_to_response('property/property_district_view.html', {'form':form,},
							  context_instance=RequestContext(request))
			else:
				name = request.GET['name']
				LogMapper.createLog(request,action="search", search_object_class_name="district", search_conditions = {"name":name,})
				district = DistrictMapper.getDistrictByName(name)
				districts.append(district)

			if not districts or len(districts) == 0:
						error_message = "No district found!"
						return render_to_response('property/property_district_view.html', {'form':form, 'error_message': error_message},
								  context_instance=RequestContext(request))
			else:
				to_json = {}
				sectors_json = {}
				to_json['districts']=PropertyCommonMapper.getGeoData(districts)
				if len(districts) == 1:
					#LogMapper.createLog(request,action="view",object=districts[0])
					sectors = SectorMapper.getSectorsByDistrictName(districts[0].name)
					sectors = PropertyCommonMapper.getGeoData(sectors)
					sectors_json['sectors']=sectors
					return render_to_response('property/property_district_view1.html', {'district': districts[0], 'districts':to_json, 'sectors':sectors_json,},
												  context_instance=RequestContext(request))
				else:
					#LogMapper.createLog(request,search_message_all="view all districts", object = districts[0])
					return render_to_response('property/property_district_view1.html', { 'districts':to_json},
						  context_instance=RequestContext(request))
	else:
		raise Http404


@login_required
def add_property(request):
	if request.method != 'POST':
		form = PropertyCreationForm(initial={'i_status':'active',})
		return render_to_response('property/property_property_add.html', {'form':form,},
							context_instance=RequestContext(request))
	else:
		form = PropertyCreationForm(request.POST)
		if form.is_valid():
			form.save(request)
			if request.GET.has_key("redirect"):
				redirect_url = '/'+request.GET['redirect']
				return HttpResponseRedirect(redirect_url)
			else:
				return access_content_type(request, "property", None, None)
		else:
			return render_to_response('property/property_property_add.html', {'form':form,},
								context_instance=RequestContext(request))

@login_required
def delete_property(request):
	return construction(request)

@login_required
def change_property(request):
	return construction(request)

@login_required
def view_property(request, action, content_type_name1, obj_id, part):
	plot_id = None
	parcel_id = None
	village = None
	cell = None
	sector = None
	property = None
	if not obj_id:
		if request.method != 'POST':
			form = select_property_upi_form()
			return render_to_response('property/property_property_view.html', {'form':form,},
				context_instance=RequestContext(request))
		else:
			form = select_property_upi_form(request.POST)
			if form.is_valid():
				upi = form.cleaned_data["upi"]
				parcel_id = form.cleaned_data["parcel_id"]
				district = form.cleaned_data["district"]
				sector = form.cleaned_data["sector"]
				cell = form.cleaned_data["cell"]

				conditions = {}
				search_conditions = {}

				if district and district!="":
					district = int(district)
					district = DistrictMapper.getDistrictById(district)
					conditions['district']=district
					search_conditions['district'] = district.name
				if sector and sector!="":
					sector = int(sector)
					sector = SectorMapper.getSectorById(sector)
					conditions['sector']=sector
					search_conditions['sector'] = sector.name
				if cell and cell!="":
					cell = int(cell)
					cell = Cell.objects.get(pk = cell)
					conditions['cell']=cell
					search_conditions['cell'] = cell.name
				if parcel_id and parcel_id !='':
					search_conditions['parcel_id'] = parcel_id
					conditions['parcel_id'] = parcel_id
				if upi and upi !="":
					search_conditions['upi'] = upi

				if search_conditions:
					LogMapper.createLog(request,action="search", search_object_class_name="property", search_conditions = search_conditions)
				if upi:
					conditions['upi'] = upi
					property = PropertyMapper.getPropertyByUPI(upi)
				else:
					if not district or not sector or not cell or not parcel_id or not str(parcel_id).isdigit():
						if not district:
							error_message = "Please select district!"
						elif not sector:
							error_message = "Please select sector!"
						elif not cell:
							error_message = "Please select cell!"
						elif not parcel_id:
							error_message = "Please enter parcel ID!"
						elif not str(parcel_id).isdigit():
							error_message = "Parcel ID is invalid!"

						form = select_property_upi_form(initial=conditions)
						return render_to_response('property/property_property_view.html', {'form':form, 'error_message': error_message},
								context_instance=RequestContext(request))
					else:
						property = PropertyMapper.getPropertiesByConditions(conditions)
						if property and len(property) > 0:
							property =property[0]
						else:
							property = None
				form = select_property_upi_form(initial=conditions)
				if not property:
					error_message = "No property found!"
					return render_to_response('property/property_property_view.html', {'form':form, 'error_message': error_message},
								context_instance=RequestContext(request))
				else:
					return_url = '/admin/property/property/view_property/'+str(property.id)+"/"
					return redirect(return_url)
			else:
				return render_to_response('property/property_property_view.html', {'form':form,},
					context_instance=RequestContext(request))
	else:
		property = get_object_or_404(Property,pk=obj_id)
		property.get_sq_m()
		LogMapper.createLog(request,action="view", plot_id=property.plot_id, object=property)
		property.upi = property.getUPI()

		hasOwnershipData = True
		ownerships = Ownership.objects.filter(asset_property=property,i_status='active')

		if not ownerships:
			hasOwnershipData = False

		if not part or part == 'map':
			boundary = property.boundary
			points_json = []
			if boundary:
				str1 = None
				if boundary.polygon_imported:
					str1=str(boundary.polygon_imported.wkt)
				elif boundary.polygon:
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
			return render_to_response('property/property_property_map.html', {'land_lease_types':variables.land_lease_types, 'land_use_types':variables.land_use_types,'property': property,'points':points_json,'hasOwnershipData':hasOwnershipData},
						context_instance=RequestContext(request))
		if part == 'owners':

			return render_to_response('property/property_property_ownerships.html', {'land_lease_types':variables.land_lease_types, 'land_use_types':variables.land_use_types,'property': property,'ownerships':ownerships,'hasOwnershipData':hasOwnershipData},
						context_instance=RequestContext(request))
		if part == 'declarevalues':
			if request.method == 'POST':
				new_declared_value = Common.cleanCurrencyInput(request.POST['declare_amount'])
				citizen_id =  int(request.POST['citizen_id'])
				citizen = Citizen.objects.get(pk = citizen_id)
				user=request.session.get('user')
				declareValue = DeclaredValue()
				declareValue.property = property
				declareValue.citizen = citizen
				declareValue.amount = new_declared_value
				declareValue.currency = "RWF"
				declareValue.user = user
				declareValue.accepted = 'YE'
				declareValue.save()
				LogMapper.createLog(request, object=declareValue, property=property, citizen=citizen, action="add")
			declarevalues = DeclaredValueMapper.getDeclaredValuesByProperty(property)
			declarevalues_json=[]
			if declarevalues:
				for declare_value in declarevalues:
					declare_value_json = {}
					citizen_obj = declare_value.citizen
					if citizen_obj:
						declare_value_json['citizen_id'] = citizen_obj.citizen_id
						declare_value_json['citizen_name'] = CitizenMapper.getDisplayName(citizen_obj)
					else:
						declare_value_json['citizen_id'] = ''
						declare_value_json['citizen_name'] = ''
					declare_value_json['currency']= declare_value.currency
					declare_value_json['amount']= str(declare_value.amount)
					user_obj = declare_value.user
					declare_value_json['staff'] = user_obj.getFullName()



					declare_value_json['accepted']=declare_value.accepted
					declare_value_json['datetime']=declare_value.date_time.strftime('%Y-%m-%d')
					declarevalues_json.append(declare_value_json)

			back_link = None
			if request.GET.get('redirect') and request.GET.get('redirect') != None:
				redirect_key = request.GET.get('redirect') + '_redirect'
				if request.session.has_key(redirect_key):
					back_link = request.session[redirect_key]

			return render_to_response('property/property_property_declarevalues.html', {'back_link':back_link,'land_lease_types':variables.land_lease_types,'land_use_types':variables.land_use_types,'property': property,'declaredvalues':declarevalues_json,'hasOwnershipData':hasOwnershipData},
						context_instance=RequestContext(request))
		if part == 'payment_history':
			paid_taxes = []
			paid_fees = []
			fixed_asset_taxes = PropertyTaxItem.objects.filter(plot_id__exact=property.plot_id,i_status__exact="active").order_by('date_time')
			if fixed_asset_taxes:
				for i in fixed_asset_taxes:
					if i.payments and i.payments.count() > 0:
						last_payment = i.payments.order_by('-pk')[0]
						i.paid_date = last_payment.date_time
					i.type = 'Fixed Asset Tax '+ str(i.period_from.year)
					if not i.remaining_amount:
						i.remaining_amount = 0

					staff = PMUser.getUserById(i.staff_id)
					if not staff:
						i.staff=None
					else:
						i.staff = staff.getFullName()

					if i.is_paid:
						i.is_paid = "Fully paid"
					else:
						if i.remaining_amount > 0 and i.remaining_amount < i.amount:
							i.is_paid = "Partially paid"
						else:
							i.is_paid = "Not paid"
					paid_taxes.append(i)
			rental_income_taxes = RentalIncomeTax.objects.filter(plot_id__exact=property.plot_id,i_status__exact="active").order_by('date_time')
			if rental_income_taxes:
				for i in rental_income_taxes:
					if i.payments and i.payments.count() > 0:
						last_payment = i.payments.order_by('-pk')[0]
						i.paid_date = last_payment.date_time
					i.type = 'Rental Income Tax '+ str(i.period_from.year)
					if hasattr(i, 'staff_id'):
						staff = PMUser.getUserById(i.staff_id)
						if staff:
							i.staff = staff.getFullName()
						else:
							i.staff = ''
					if not i.remaining_amount:
						i.remaining_amount = 0
					if i.is_paid:
						i.is_paid = "Fully paid"
					else:
						if i.remaining_amount > 0 and i.remaining_amount < i.amount:
							i.is_paid = "Partially paid"
						else:
							i.is_paid = "Not paid"
					paid_taxes.append(i)
			fees = Fee.objects.filter(property=property,i_status__exact="active").order_by('date_time')
			if fees:
				for i in fees:
					if i.payments and i.payments.count() > 0:
						last_payment = i.payments.order_by('-pk')[0]
						i.paid_date = last_payment.date_time
					i.type = i.fee_type.title() + ' Fee '
					if hasattr(i, 'staff_id'):
						staff = PMUser.getUserById(i.staff_id)
						if not staff:
							i.staff = ''
						else:
							i.staff = staff.getFullName()
					if not i.remaining_amount:
						i.remaining_amount = 0
					if i.is_paid:
						i.is_paid = "Fully paid"
					else:
						if i.remaining_amount > 0 and i.remaining_amount < i.amount:
							i.is_paid = "Partially paid"
						else:
							i.is_paid = "Not paid"
					paid_fees.append(i)
			return render_to_response('property/property_property_taxhistory.html', {'land_lease_types':variables.land_lease_types, 'land_use_types':variables.land_use_types,'paid_taxes':paid_taxes,'fees':paid_fees,'property': property,},
					context_instance=RequestContext(request))
		if part == 'media':
			media = MediaMapper.getMedia('property',property)
			request.session['property_url'] = '/admin/property/property/view_property/'+ str(property.id) + '/media/'
			return render_to_response('property/property_property_media.html', {'land_lease_types':variables.land_lease_types, 'land_use_types':variables.land_use_types,'property': property,'media':media,'hasOwnershipData':hasOwnershipData},context_instance=RequestContext(request))

		if part == "assign_ownership":
			if request.method == "POST":
				new_owners = request.POST['owners']
				if new_owners:
					to_str = ''
					new_owners = new_owners[:-1]
					new_owners = "["+str(new_owners)+"]"
					jdata = json.loads(new_owners)

					new_owner_count = 0

					#@KLUDGE - set start date of the newly assign ownership back to 3 years to cover any past unpaid taxes.
					start_date = date.today() - timedelta(days=365*3)
					for new_owner in jdata:
						if new_owner['type'] == 'citizen':
							citizen = CitizenMapper.getCitizenById(int(str(new_owner['id'])))
							share = int(new_owner['share'])
							Ownership.objects.create(asset_property =property, owner_citizen = citizen, share = share, date_started = start_date,i_status = 'active')
							new_owner_count = new_owner_count + 1
							if new_owner_count > 1:
								to_str = to_str + ','
							to_str = to_str + ', Citizen [Name:' + citizen.getDisplayName() + ', ID:' + citizen.citizen_id + ', Share:' + str(share) + '%]'
						elif new_owner['type'] == 'business':
							business = Business.objects.get(pk=int(str(new_owner['id'])))
							share = int(new_owner['share'])
							Ownership.objects.create(owner_business = business,asset_property=property,share = share,date_started=start_date)
							new_owner_count = new_owner_count + 1
							if new_owner_count > 1:
								to_str = to_str + ','
							to_str = to_str + ' Business [Name:' + business.name + ', TIN:' + str(business.tin) + ', Share:' + str(share) + '%]'
					log_message = 'Assign ownership of Property ['+ property.getDisplayName()+']'+ ' to ' + to_str

					LogMapper.createLog(request, message_all=log_message, plot_id = property.plot_id)
					property.save()
					TaxMapper.generateTaxes(property,request)

					#redirect to transfer ownership page after assigned
					return HttpResponseRedirect('/admin/property/property/view_property/' + str(property.id) + '/transfer_ownership/' )

			ownerships = Ownership.objects.filter(asset_property=property,i_status='active')

			if not ownerships:
				return render_to_response('property/property_property_assign_ownership.html', {'land_lease_types':variables.land_lease_types, 'land_use_types':variables.land_use_types,'property': property,'ownerships':ownerships,'hasOwnershipData':hasOwnershipData},context_instance=RequestContext(request))
			else:
				#redirect to transfer ownership page after assigned
				return HttpResponseRedirect('/admin/property/property/view_property/' + str(property.id) + '/transfer_ownership/' )


		if part == "transfer_ownership":
			if request.method == "POST":
				new_owners = request.POST['owners']
				if new_owners:
					from_str = ''
					to_str = ''
					new_owners = new_owners[:-1]
					new_owners = "["+str(new_owners)+"]"
					date_of_transfer = request.POST['date_of_transfer']
					if date_of_transfer and date_of_transfer != '':
						date_of_transfer = datetime.strptime(date_of_transfer,'%d/%m/%Y')
						date_today = timezone.make_aware(date_of_transfer, timezone.get_default_timezone())
					else:
						date_today = date.today()
					jdata = json.loads(new_owners)
					old_owner_count = 0
					new_owner_count = 0
					#deactivate all old ownerships
					ownerships = Ownership.objects.filter(asset_property=property,i_status='active')
					if ownerships:
						for obj in ownerships:
							obj.date_ended = date_today
							obj.save()
							old_owner_count = old_owner_count + 1
							if obj.owner_citizen:
								if old_owner_count == 1:
									from_str = from_str + 'Citizen [Name:' + obj.owner_citizen.getDisplayName() + ', ID:' + obj.owner_citizen.citizen_id + ', Share:' + str(int(obj.share)) + '%]'
								else:
									from_str = from_str + ', Citizen [Name:' + obj.owner_citizen.getDisplayName() + ', ID:' + obj.owner_citizen.citizen_id + ', Share:' + str(int(obj.share)) + '%]'
							elif obj.owner_business:
								if old_owner_count == 1:
									from_str = from_str + 'Business [Name:' + obj.owner_business.name + ', TIN:' + obj.owner_business.tin + ', Share:' + str(int(obj.share)) + '%]'
								else:
									from_str = from_str + ', Business [Name:' + obj.owner_business.name + ', TIN:' + obj.owner_business.tin + ', Share:' + str(int(obj.share)) + '%]'

					for new_owner in jdata:
						if new_owner['type'] == 'citizen':
							citizen = CitizenMapper.getCitizenById(int(str(new_owner['id'])))
							share = int(new_owner['share'])
							Ownership.objects.create(asset_property = property, date_started=date_today, owner_citizen = citizen, share = share, i_status = 'active')
							new_owner_count = new_owner_count + 1
							if new_owner_count == 1:
								to_str = to_str + 'Citizen [Name:' + citizen.getDisplayName() + ', ID:' + citizen.citizen_id + ', Share:' + str(share) + '%]'
							else:
								to_str = to_str + ', Citizen [Name:' + citizen.getDisplayName() + ', ID:' + citizen.citizen_id + ', Share:' + str(share) + '%]'
						elif new_owner['type'] == 'business':
							business = Business.objects.get(pk=int(str(new_owner['id'])))
							share = int(new_owner['share'])
							Ownership.objects.create(owner_business = business, asset_property=property,share = share,date_started=date_today)
							new_owner_count = new_owner_count + 1
							if new_owner_count == 1:
								to_str = to_str + 'Business [Name:' + business.name + ', TIN:' + str(business.tin) + ', Share:' + str(share) + '%]'
							else:
								to_str = to_str + ', Business [Name:' + business.name + ', TIN:' + str(business.tin) + ', Share:' + str(share) + '%]'
					log_message = 'transfer ownership of Property ['+ property.getDisplayName()+']'
					if from_str !='':
						log_message = log_message + ' from ' + from_str
					log_message = log_message + ' to ' + to_str
					LogMapper.createLog(request, message_all=log_message, property = property)
			ownerships = Ownership.objects.filter(asset_property=property,i_status='active')

			return render_to_response('property/property_property_transfer_ownership.html', {'land_lease_types':variables.land_lease_types, 'land_use_types':variables.land_use_types,'property': property,'ownerships':ownerships,'hasOwnershipData':hasOwnershipData},context_instance=RequestContext(request))
		if part == "logs":
			upi = property.getUPI()
			form = LogSearchForm(initial={'upi':upi,})
			conditions = {}
			conditions['upi']=upi
			logs = []
			if request.method == 'POST':
				form = LogSearchForm(request.POST)
				if form.is_valid():
					username = form.cleaned_data['username']
					upi = form.cleaned_data['upi']
					citizen_id = form.cleaned_data['citizen_id']
					period_from = form.cleaned_data['period_from']
					period_to = form.cleaned_data['period_to']
					logs = Log.objects.filter(username__icontains=username)
					if username is not None and username.strip() !='':
						conditions['username'] = username.strip()
					if citizen_id is not None and citizen_id.strip() !='':
						conditions['citizen_id'] = citizen_id.strip()
					if period_from is not None:
						conditions['period_from'] = timezone.make_aware(datetime.combine(period_from, time(0,0,0)), timezone.get_default_timezone())
					if period_to is not None:
						conditions['period_to'] = timezone.make_aware(datetime.combine(period_to, time(23,59,59)), timezone.get_default_timezone())
					LogMapper.createLog(request,action="search", search_object_class_name="log", search_conditions = {"username": username,"upi":upi,'citizenid':citizen_id,"period_from":period_from, "period_to":period_to})

			logs = LogMapper.getLogsByConditions(conditions)
			logs = list(logs)
			logs.sort(key=lambda x:x.date_time, reverse=True)
			for log in logs:
				log.message=log.message.replace("User [","<span class='loguser'>User [")
				log.message=log.message.replace("User[","<span class='loguser'>User [")
				log.message=log.message.replace("Property [","<span class='logproperty'>Property [")
				log.message=log.message.replace("property [","<span class='logproperty'>Property [")
				log.message=log.message.replace("Citizen [","<span class='logcitizen'>Citizen [")
				log.message=log.message.replace("citizen [","<span class='logcitizen'>Citizen [")
				log.message=log.message.replace("Group [","<span class='loggroup'>Group [")
				log.message=log.message.replace("group [","<span class='loggroup'>Group [")
				log.message=log.message.replace("]","]</span>")
			return render_to_response('property/property_property_logs.html', {'land_lease_types':variables.land_lease_types, 'land_use_types':variables.land_use_types,'property': property,'logs':logs, 'form':form,'hasOwnershipData':hasOwnershipData},
								context_instance=RequestContext(request))

@login_required
def property_default(request,  action, content_type_name1, obj_id, part):
	"""
	This function adds property entity
	"""

	if not action:
		user = request.session.get('user')
		module = ModuleMapper.getModuleByName("property")
		content_type = ContentTypeMapper.getContentTypeByModuleAndName('property', module)
		actions = user.getActionsByContentTypeWithLink(content_type)
		return render_to_response('property/property_property_default.html', {\
							 'permissions':actions},
							  context_instance=RequestContext(request))
	elif action == 'add':
		if not request.session['user'].has_action_by_name('property','property','add_property'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
		return add_property(request)
	elif action == 'view':
		if not request.session['user'].has_action_by_name('property','property','view_property'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
		return view_property(request, action, content_type_name1, obj_id, part)
	elif action == "change":
		if not request.session['user'].has_action_by_name('property','property','change_property'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
		return change_property(request)
	elif action == "delete":
		if not request.session['user'].has_action_by_name('property','property','delete_property'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
		return delete_property(request)
	elif action == "toggle" and content_type_name1 == "lease":
		property = get_object_or_404(Property,id=obj_id)
		status = request.GET['status']
		if status == '1':
			property.is_leasing = True
		else:
			property.is_leasing = False
		property.save()
		LogMapper.createLog(request,object=property,action="change", property = property,message="updated Rental Income Tax Applicable to " + str(property.is_leasing) )

		return HttpResponse("")
	elif action == "toggle" and content_type_name1 == "landlease":
		property = get_object_or_404(Property,id=obj_id)
		property.get_sq_m()
		status = request.GET['status']
		if status == '1':
			property.is_land_lease = True
		else:
			property.is_land_lease = False
		property.save()
		LogMapper.createLog(request,object=property,action="change", property = property,message="updated Land Lease Fee Applicable to " + str(property.is_land_lease) )
		return HttpResponse("")
	elif action == "update" and content_type_name1 == "landusetype":
		property = get_object_or_404(Property,id=obj_id)
		property.get_sq_m()
		if request.GET.get('land_use_type'):
			land_zone = CategoryChoice.objects.get(category__code='land_use', code=request.GET.get('land_use_type'))
			property.land_zone = land_zone
			property.save()
			LogMapper.createLog(request,object=property,action="change", property = property,message="updated Land Use Type to %s" % land_zone.name )
		return HttpResponse("")
	elif action == "update" and content_type_name1 == "landleasetype":
		property = get_object_or_404(Property,id=obj_id)
		if request.GET.get('land_lease_type',None) != None:
			for i in variables.land_lease_types:
				if i[0] == request.GET.get('land_lease_type'):
					property.land_lease_type = i[0]
					property.save()
					LogMapper.createLog(request,object=property,action="change", property = property,message="updated Land Lease Type to " + str(property.land_lease_type) )
		return HttpResponse("")

	elif action == "update" and content_type_name1 == "size":
		property = get_object_or_404(Property,id=obj_id)
		if request.GET.get('size',None) != None and request.GET.get('size').strip() != '':
			size_type = 'sqm'
			if property.land_lease_type != 'Agriculture':
				property.size_sqm = request.GET.get('size')
			else:
				property.size_hectare= request.GET.get('size')
				size_type = 'hectares'
			property.save()
			LogMapper.createLog(request,object=property,action="change", property = property,message="updated Land Size to " + str(request.GET.get('size')) + ' ' + size_type )
		return HttpResponse("")

	elif action == "update" and content_type_name1 == "taxexempt":
		property = get_object_or_404(Property,id=obj_id)
		form = PropertyUpdateTaxExemptForm(initial=model_to_dict(property))
		user = request.session.get('user')

		if request.method == 'POST':
			form = PropertyUpdateTaxExemptForm(request.POST, request.FILES)
			if form.is_valid():
				if request.FILES.has_key('proof') and request.FILES['proof'] != '':
					now = str(datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
					file = request.FILES['proof']
					file_info = os.path.splitext(file.name)
					file_name = 'Tax_Exempt_Proof_' + now + file_info[1]
					folder = 'property/' + str(property.id) + '/'
					file_path = folder + file_name
					if os.path.exists(settings.MEDIA_ROOT + folder) == False:
						os.mkdir(settings.MEDIA_ROOT + folder)
					with open(settings.MEDIA_ROOT + file_path, 'wb+') as destination:
						for chunk in file.chunks():
							destination.write(chunk)
					media = Media(title='Tax Exemption Proof',tags='property',file_name=file_name,path=file_path,file_type=file.content_type,
									file_size=file.size,property=property,user_id=user.id)
					media.save()

				property.is_tax_exempt = form.cleaned_data['is_tax_exempt']
				property.tax_exempt_reason = form.cleaned_data['tax_exempt_reason']
				property.tax_exempt_note = form.cleaned_data['tax_exempt_note']

				property.save()
				if property.is_tax_exempt:
					tax_exempt_status = ' True (Reason: ' + property.tax_exempt_reason + ') [' + property.tax_exempt_note + ']'

				else:
					tax_exempt_status = ' False'
				for tax in property.outstanding_taxes:
						tax.exempt = property.is_tax_exempt
						tax.calc_tax()
				LogMapper.createLog(request,object=property,action="change", property = property,message="updated Tax Exempt Status to " + tax_exempt_status)
				return HttpResponseRedirect('/admin/property/property/view_property/' + str(property.id) + '/')

		return render_to_response('property/_update_tax_exempt.html', {'form':form,'property':property},
							context_instance=RequestContext(request))
	else:
		raise Http404

def construction(request):
	#return HttpResponse('Unauthorized', status=401)
	raise Http404
	#return render_to_response('admin/construction.html', {}, context_instance=RequestContext(request))
