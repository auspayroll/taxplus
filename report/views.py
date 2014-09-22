import re
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import Http404
from django.core.paginator import *
from pmauth.mappers.ModuleMapper import ModuleMapper
from pmauth.mappers.ContentTypeMapper import ContentTypeMapper
from pmauth.mappers.PermissionMapper import PermissionMapper
from admin.views import login
from report.forms.forms import *
from property.mappers.CellMapper import CellMapper
from property.mappers.DistrictMapper import DistrictMapper
from property.mappers.SectorMapper import SectorMapper
from property.mappers.PropertyMapper import PropertyMapper
from property.mappers.OwnershipMapper import OwnershipMapper
from jtax.mappers.PayFixedAssetTaxMapper import PayFixedAssetTaxMapper
from jtax.mappers.PayRentalIncomeTaxMapper import PayRentalIncomeTaxMapper
from jtax.mappers.PayTradingLicenseTaxMapper import PayTradingLicenseTaxMapper
from jtax.mappers.PayFeeMapper import PayFeeMapper
from jtax.mappers.TaxMapper import TaxMapper
from dev1.variables import *
from jtax.models import *
from admin.Common import Common
from asset.mappers.BusinessMapper import BusinessMapper
import pprint
from urllib import urlencode
pp = pprint.PrettyPrinter()
from django.contrib.auth.decorators import login_required

@login_required
def access_content_type(request, content_type_name, action = None):
	"""
	This function direct request to the correspodding {module}_{contenttype}_default page
	"""
	if not request.session.get('user'):
		return login(request)
	
	if content_type_name == 'report':
		return report_default(request, action)

	raise Http404

@login_required
def report_properties_with_unpaid_tax(request):
	if request.method !='POST' and not request.GET.has_key('page'):
		form = UnpaidTaxSearchForm(request)
		return render_to_response("report/properties_with_unpaid_tax.html", {"form":form,},
			context_instance=RequestContext(request))
	else:
		page = 1
		records_in_page = 20
		if request.method == 'POST':
			form = UnpaidTaxSearchForm(request, request.POST)
			tax_types = request.POST.getlist('tax_types')
			district = ''
			sector = ''
			cell = ''
			if request.POST.has_key('district'):
				district = request.POST['district']
			if request.POST.has_key('sector'):
				sector = request.POST['sector']
			if request.POST.has_key('cell'):
				cell = request.POST['cell']
			conditions = {}
			
			graph_title = "Properties in [ "
			if (not district or district =='') and (not sector and sector =='') and (not cell and cell =='') and len(tax_types) ==0:
				graph_title = None
			else:
				if (not district or district =='') and (not sector and sector =='') and (not cell and cell ==''):
					graph_title = graph_title + 'all districts'
				else:
					arr = []
					if district and district !='':
						district = DistrictMapper.getDistrictById(int(district))
						conditions['district'] = district
						arr.append("district:"+district.name)
					if sector and sector !='':
						sector = SectorMapper.getSectorById(int(sector))
						conditions['sector'] = sector
						arr.append("sector:"+sector.name)
					if cell and cell !='':
						cell = CellMapper.getCellById(int(cell))
						conditions['cell'] = cell
						arr.append("cell:"+cell.name)
					graph_title = graph_title + ",".join(arr) + "]"
				if len(tax_types) != 0:
					graph_title = graph_title + " with unpaid tax ["
					graph_title = graph_title + ','.join(tax_types)
					graph_title = graph_title + "]"
		
				form = UnpaidTaxSearchForm(request, initial={"district":district,"sector":sector,"cell":cell,"tax_types":tax_types})
				request.session['unpaid_tax_search_form'] = form
				request.session['tax_types']=tax_types
				request.session['conditions'] = conditions
				request.session['graph_title'] = graph_title
				
		elif request.method == 'GET' and request.GET.has_key('page'):
			page = int(request.GET["page"])
			tax_types = request.session['tax_types']
			conditions = request.session['conditions']
			form =request.session['unpaid_tax_search_form']
			graph_title = request.session['graph_title']
		
		result_objects = []
		summary = {}
		
	
		property_ids = []
		
		
		if tax_types:
			if 'fixed_asset' in tax_types:
				items = PropertyTaxItem.objects.filter(i_status='active',is_paid=False)
				if conditions.has_key('cell') and conditions['cell'] and conditions['cell']!='':
					items = items.filter(property__cell = conditions['cell'])
				if conditions.has_key('sector') and conditions['sector'] and conditions['sector']!='':
					items = items.filter(property__sector = conditions['sector'])
				if conditions.has_key('district') and conditions['district'] and conditions['district']!='':
					items = items.filter(property__sector__district = conditions['district'])
				ids = items.values('property_id').distinct()
				ids = Common.get_value_list(ids,'property_id')
				
				if ids and len(ids) > 0:
					property_ids = ids
			if 'rental_income' in tax_types:
				items = RentalIncomeTax.objects.filter(i_status='active',is_paid=False)
				if conditions.has_key('cell') and conditions['cell'] and conditions['cell']!='':
					items = items.filter(property__cell = conditions['cell'])
				elif conditions.has_key('sector') and conditions['sector'] and conditions['sector']!='':
					items = items.filter(property__sector = conditions['sector'])
				elif conditions.has_key('district') and conditions['district'] and conditions['district']!='':
					items = items.filter(property__sector__district = conditions['district'])
				ids = items.values('property_id').distinct()
				ids = Common.get_value_list(ids,'property_id')
				if ids and len(ids) > 0:
					property_ids = property_ids + list(set(ids)-set(property_ids))
			if 'land_lease' in tax_types:
				items = Fee.objects.filter(fee_type='land_lease',i_status='active',is_paid=False, property__isnull=False)
				if conditions.has_key('cell') and conditions['cell'] and conditions['cell']!='':
					items = items.filter(property__cell = conditions['cell'])
				elif conditions.has_key('sector') and conditions['sector'] and conditions['sector']!='':
					items = items.filter(property__sector = conditions['sector'])
				elif conditions.has_key('district') and conditions['district'] and conditions['district']!='':
					items = items.filter(property__sector__district = conditions['district'])
				ids = items.values('property_id').distinct()
				ids = Common.get_value_list(ids,'property_id')
				if ids and len(ids) > 0:
					property_ids = property_ids + list(set(ids)-set(property_ids))
		

		num_of_properties = len(property_ids)

		if len(property_ids) > 0:
			property_ids = Property.objects.filter(id__in = property_ids).order_by("sector","cell","village","parcel_id").values('id')
			property_ids = Common.get_value_list(property_ids,'id')
			property_ids = property_ids[(page-1)*records_in_page:page*records_in_page]
			properties = []
			
			for property_id in property_ids:
				property = Property.objects.get(pk=property_id)
				upi = property.getUPI()
				if upi:
					property.upi = upi
				else:
					property_upi = ''
				property.address = property.getDisplayName()
				
				
				tax_description = []
				if 'fixed_asset' in tax_types:
					items = PropertyTaxItem.objects.filter(i_status='active',is_paid=False,property=property).order_by("-due_date")
					if len(items) > 0:
						for item in items:
							description = "Fixed Asset Tax - Due on " + item.due_date.strftime("%d/%m/%y")
							tax_description.append(description)
				if 'rental_income' in tax_types:
					items = RentalIncomeTax.objects.filter(i_status='active',is_paid=False,property=property).order_by("-due_date")
					if len(items) > 0:
						for item in items:
							description = "Rental Income Tax - Due on " + item.due_date.strftime("%d/%m/%y")
							tax_description.append(description)
				if 'land_lease' in tax_types:
					items = Fee.objects.filter(fee_type='land_lease',i_status='active',is_paid=False,property=property).order_by("-due_date")
					if len(items) > 0:
						for item in items:
							description = "Land Lease Tax - Due on " + item.due_date.strftime("%d/%m/%y")
							tax_description.append(description)
				
				property.tax_type = "<br>".join(tax_description)
				
				
				citizen_ids = None
				citizens = None
				citizen_ids = Ownership.objects.filter(i_status='active',asset_property = property, date_created__isnull=True).values('owner_citizen').distinct()
				if citizen_ids:
					citizen_ids = Common.get_value_list(citizen_ids,'citizen_id')
					citizens = Citizen.objects.filter(id__in = citizen_ids)
				if citizens:
					for citizen in citizens:
						citizen.display_name = citizen.getDisplayName()
				property.associated_citizens = citizens
				
				business_ids = None
				businesses = None
				subbusiness_ids = None
				subbusinesses = None
				
				business_ids = Ownership.objects.filter(i_status='active', date_ended__isnull=True,  owner_business__isnull=False, asset_property__id = property.id).values('owner_business_id').distinct()
				if business_ids:
					business_ids = Common.get_value_list(business_ids,'owner_business_id')
					businesses = Business.objects.filter(i_status='active',id__in = business_ids)
				property.associated_businesses = businesses
				
				subbusiness_ids = Ownership.objects.filter(i_status='active', date_ended__isnull=True,  owner_subbusiness__isnull=False, asset_property__id = property.id).values('owner_subbusiness_id').distinct()
				if subbusiness_ids:
					subbusiness_ids = Common.get_value_list(subbusiness_ids,'owner_subbusiness_id')
					subbusinesses = SubBusiness.objects.filter(i_status='active',id__in = subbusiness_ids)
				property.associated_subbusinesses = subbusinesses
				
				properties.append(property)
				
			### work to be continued here ... 
			
			geodata = None
			if properties:
				geodata = PropertyMapper.getPropertyGeoData(properties)
				
			
			paginator = {}
			paginator['count'] = num_of_properties
			paginator['number'] = page
			paginator['num_pages'] = 0
			paginator['has_next'] = False
			paginator['has_previous'] = False
			paginator['next_page_number'] = 0
			paginator['previous_page_number'] = 0
			
			
			if num_of_properties%records_in_page == 0:
				paginator['num_pages'] = num_of_properties/records_in_page
			else:
				paginator['num_pages'] = int(num_of_properties/records_in_page) + 1
			
			if page == 1:
				paginator['has_previous'] = False
			else:
			 	paginator['has_previous'] = True
			 	paginator['previous_page_number'] = page - 1
			 
			if page == paginator['num_pages']:
			 	 paginator['has_next'] = False
			else:
			 	paginator['has_next'] = True
			 	paginator['next_page_number'] = page + 1
			 				 				
			return render_to_response("report/properties_with_unpaid_tax.html", {"form":form,"properties":properties, "geodata":geodata, 'paginator':paginator,'graph_title': graph_title},
				context_instance=RequestContext(request))
		else:
			return render_to_response("report/properties_with_unpaid_tax.html", {"form":form,},
				context_instance=RequestContext(request))
		
@login_required
def report_properties_with_no_owners(request):
	records_per_page = 50

	if request.method =='POST' or request.GET.get('page'):
		page = 1
		if request.method == 'POST':
			request_vars = request.POST
		else:
			request_vars = request.GET
			try:
				page = int(request_vars.get('page',0))
			except ValueError:
				page = 1
		try:
			district_id = int(re.sub('^$','0', request_vars.get('district', '0')))
			sector_id = int(re.sub('^$', '0', request_vars.get('sector', '0')))
			cell_id = int(re.sub('^$', '0', request_vars.get('cell', '0')))
		except ValueError:
			raise Http404;

		form = ReportSearchFormBasic(request, initial={"district":district_id,"sector":sector_id,"cell":cell_id})

		if not district_id and not sector_id and not cell_id:
			graph_title = 'Unowned Properties in all districts'
			properties = Property.objects.select_related('sector', 'sector__district').all()
		else:
			arr = []
			if district_id:
				district = DistrictMapper.getDistrictById(district_id)
				arr.append("District: " + district.name)
				properties = Property.objects.filter(sector__district=district)
			if sector_id:
				sector = SectorMapper.getSectorById(sector_id)
				arr.append("Sector: " + sector.name)
				properties = Property.objects.filter(sector=sector)
			if cell_id:
				cell = CellMapper.getCellById(cell_id)
				arr.append("Cell: " + cell.name)
				properties = Property.objects.filter(cell=cell)

			graph_title = "Unowned Properties in [" + ", ".join(arr) + "]"


		properties = properties.filter(owners__isnull=True).\
			select_related('boundary', 'village','cell', 'sector', 'sector__district')
	
		# used for district, sector, cell info in page links
		areas = {}
		if district_id:
			areas['district'] = district_id
		if sector_id:
			areas['sector'] = sector_id
		if cell_id:
			areas['cell'] = cell_id

		encoded_areas = urlencode(areas)
			
		paginator = Paginator(properties, records_per_page)
		properties = paginator.page(page)

		geodata = None
		if properties:
			geodata = PropertyMapper.getPropertyGeoData(properties.object_list)
			 				 				
		return render_to_response("report/properties_with_no_owners.html", 
			{ "form":form,"properties":properties, "geodata":geodata, 
				'paginator':paginator, 'graph_title':graph_title, 'encoded_areas':encoded_areas },
			context_instance=RequestContext(request))

	else:
		form = ReportSearchFormBasic(request)
		return render_to_response("report/properties_with_no_owners.html", {"form":form,},
			context_instance=RequestContext(request))


@login_required
def report_tax_payers(request):
	if request.method !='POST' and not request.GET.has_key('page'):
		form = ReportSearchForm(request)
		return render_to_response("report/report_tax_payers.html", {"form":form,},
			context_instance=RequestContext(request))
	else:
		tax_types = None
		form = None
		conditions = {}
		page = 1
		records_in_page = 20
		if request.method == 'POST':
			form = ReportSearchForm(request, request.POST)
			tax_types = request.POST.getlist('tax_types')
			district = ''
			sector = ''
			cell = ''
			if request.POST.has_key('district'):
				district = request.POST['district']
			if request.POST.has_key('sector'):
				sector = request.POST['sector']
			if request.POST.has_key('cell'):
				cell = request.POST['cell']
			
			graph_title = "Report on tax payers "
			if (not district or district =='') and (not sector and sector =='') and (not cell and cell =='') and len(tax_types) ==0:
				graph_title = None
			else:
				if (not district or district =='') and (not sector and sector =='') and (not cell and cell ==''):
					graph_title = graph_title + 'in all districts'
				else:
					arr = []
					if district and district !='':
						district = DistrictMapper.getDistrictById(int(district))
						conditions['district'] = district
						arr.append("district:"+district.name)
					if sector and sector !='':
						sector = SectorMapper.getSectorById(int(sector))
						conditions['sector'] = sector
						arr.append("sector:"+sector.name)
					if cell and cell !='':
						cell = CellMapper.getCellById(int(cell))
						conditions['cell'] = cell
						arr.append("cell:"+cell.name)
					graph_title = graph_title + ",".join(arr) + "]"
				if len(tax_types) != 0:
					graph_title = graph_title + " with tax ["
					graph_title = graph_title + ','.join(tax_types)
					graph_title = graph_title + "]"
				form = ReportSearchForm(request, initial={"district":district,"sector":sector,"cell":cell,"tax_types":tax_types})
				request.session['tax_payer_form'] = form
				request.session['tax_types']=tax_types
				request.session['conditions'] = conditions
				request.session['graph_title'] = graph_title
		elif request.method == 'GET' and request.GET.has_key('page'):
			page = request.GET["page"]
			tax_types = request.session['tax_types']
			conditions = request.session['conditions']
			form =request.session['tax_payer_form']
			graph_title = request.session['graph_title']

		result_objects = []
		summary = {}
		if tax_types:
			if 'fixed_asset' in tax_types:
				result_obj = PayFixedAssetTaxMapper.getTaxPayers(conditions)
				if result_obj:
					summary['Fixed asset tax'] = len(result_obj) 
					result_objects = result_objects + result_obj
				else:
					summary['Fixed asset tax'] = 0
				
			if 'rental_income' in tax_types:
				result_obj = PayRentalIncomeTaxMapper.getTaxPayers(conditions)
				if result_obj:
					summary['Rental income tax'] = len(result_obj)
					result_objects = result_objects + result_obj
				else:
					summary['Rental income tax'] = 0
			if 'trading_license' in tax_types:
				result_obj = PayTradingLicenseTaxMapper.getTaxPayers(conditions)
				if result_obj:
					summary['Trading license tax'] = len(result_obj)
					result_objects = result_objects + result_obj

				else:
					summary['Trading license tax'] = 0
			if 'land_lease' in tax_types:
				conditions['fee_type'] = 'land_lease'
				result_obj = PayFeeMapper.getTaxPayers(conditions)
				if result_obj:
					summary['Land lease fee'] = len(result_obj)
					result_objects = result_objects + result_obj

				else:
					summary['Land lease fee'] = 0
			if 'market' in tax_types:
				conditions['fee_type'] = 'market'
				result_obj = PayFeeMapper.getTaxPayers(conditions)
				if result_obj:
					summary['Market fee'] = len(result_obj)
					result_objects = result_objects + result_obj

				else:
					summary['Market fee'] = 0
			if 'cleaning' in tax_types:
				conditions['fee_type'] = 'cleaning'
				result_obj = PayFeeMapper.getTaxPayers(conditions)
				if result_obj:
					summary['Cleaning'] = len(result_obj)
					result_objects = result_objects + result_obj
				else:
					summary['Cleaning fee'] = 0
			
		#set up list of sms and emails to be stored in session for Bulk Messaging later
		smsList = {}
		emailList = {}
		if result_objects:
			for obj in result_objects:
				sms = ''
				email = ''
				if type(obj) is Citizen:
					if obj.phone_1 and obj.phone_1 != '':
						sms = obj.phone_1
					elif obj.phone_2 and obj.phone_2 != '':
						sms = obj.phone_2
					if obj.email and obj.email != '':
						email = obj.email
					if sms != '':
						smsList[sms] = {'cid':obj.id}
					if email != '':
						emailList[email] = {'cid':obj.id}

				elif type(obj) is Business:
					if obj.phone1 and obj.phone1 != '':
						sms = obj.phone1
					elif obj.phone2 and obj.phone2 != '':
						sms = obj.phone2
					if obj.email and obj.email != '':
						email = obj.email
					if sms != '':
						smsList[sms] = {'bid':obj.id}
					if email != '':
						emailList[email] = {'bid':obj.id}

		request.session['tax_payers_sms'] = smsList
		request.session['tax_payers_email'] = emailList
		#print smsList
		#print emailList
		#print '@@@@@'

		if not request.POST.has_key('toPrint'):
			paginator = Paginator(result_objects, records_in_page)
			try:
				tax_payers = paginator.page(page)
			except PageNotAnInteger:
				# If page is not an integer, deliver first page.
				tax_payers = paginator.page(1)
			except EmptyPage:
				# If page is out of range (e.g. 9999), deliver last page of results.
				tax_payers = paginator.page(paginator.num_pages)

			return render_to_response("report/report_tax_payers.html", {"tax_payers":tax_payers,"form":form, "graph_title":graph_title,"summary":summary},
				context_instance=RequestContext(request))				
		else:
			tax_payers = result_objects
			return render_to_response("report/report_tax_payers_print.html", {"tax_payers":tax_payers,"form":form,"graph_title":graph_title,"summary":summary},
				context_instance=RequestContext(request))


@login_required
def report_revenue_received_breakdown(request):
	if request.method !='POST':
		form = ReportSearchForm(request)
		return render_to_response("report/report_revenue_received_breakdown.html", {"form":form,},
			context_instance=RequestContext(request))
	else:
		form = ReportSearchForm(request, request.POST)
		years = request.POST.getlist('years')
		tax_types = request.POST.getlist('tax_types')
		district = ''
		sector = ''
		cell = ''
		if request.POST.has_key('district'):
			district = request.POST['district']
		if request.POST.has_key('sector'):
			sector = request.POST['sector']
		if request.POST.has_key('cell'):
			cell = request.POST['cell']
		#year = request.POST['calendar_year']
		
		conditions = {}
		conditions['years'] = years
		conditions['tax_types'] = tax_types
		graph_title = "Revenue received within years("
		graph_title = graph_title + ','.join(years) + ") "
	
		if len(tax_types) == 0:
			graph_title = None
		else:
			if (not district or district =='') and (not sector or sector ==''):
				graph_title = graph_title + 'in all districts'
			else:
				count = 0
				graph_title = graph_title + 'in ['
				arr = []
				if district and district !='':
					district = DistrictMapper.getDistrictById(int(district))
					conditions['district'] = district
					arr.append("district:"+district.name)
				if sector and sector !='':
					sector = SectorMapper.getSectorById(sector)
					conditions['sector'] = sector
					arr.append("sector:"+sector.name)	
				if cell and cell !='':
					cell = CellMapper.getCellById(cell)
					conditions['cell'] = cell
					arr.append("cell:"+cell.name)
				graph_title = graph_title+",".join(arr)+"]"
				
			graph_title = graph_title + ' on ['	
			
			form = ReportSearchForm(request, initial={"district":district,"sector":sector,"cell":cell,"tax_types":tax_types,'years':years,})			
			arr = []
			
			if 'fixed_asset' in tax_types:
				arr.append("fixed asset tax")
			if 'rental_income' in tax_types:
				arr.append("rental income tax")
			if 'trading_license' in tax_types:
				arr.append("trading license tax")
			if 'land_lease_fee' in tax_types:
				arr.append("land lease fee")
			if 'market_fee' in tax_types:
				arr.append("market fee")
			if 'cleaning_fee' in tax_types:
				arr.append("cleaning fee")
				
			graph_title = graph_title + ",".join(arr)+ ']'
			result = TaxMapper.getYearlyRevenueByConditions(conditions)
						
			##########################################
			############# start of graph #############
			##########################################
			
			line_chart_data = []
			line_chart_data_dict = {}
			
			new_x_labels = []
			total_revenues = []
			
			for year in years:
				line_chart_data_element = []
				year_result = result[year]
				count = 0
				total_revenue = 0
				for item in year_result:
					count = count + 1
					line_chart_data_element.append([count,int(item[1])])
					total_revenue = total_revenue + int(item[1])
					if year ==  years[0]:
						new_x_labels.append(item[0][:3])
				total_revenue__dict = {}
				total_revenue__dict['year'] = year
				total_revenue__dict['revenue'] = total_revenue
				total_revenues.append(total_revenue__dict)				
				line_chart_data_dict_element = {}
				line_chart_data_dict_element['data'] = line_chart_data_element
				line_chart_data_dict_element['label'] = int(year)
				line_chart_data.append(line_chart_data_dict_element)

			line_chart_data_dict['data'] = line_chart_data
			line_chart_data_dict['x_labels'] = new_x_labels
			
			
			if not request.POST.has_key('toPrint'):
				return render_to_response("report/report_revenue_received_breakdown.html", {"total_revenues":total_revenues,"graph_title":graph_title, "form":form,"line_chart_data":line_chart_data_dict,"years":years,},
					context_instance=RequestContext(request))
			else:
				return render_to_response("report/report_revenue_received_breakdown_print.html", {"total_revenues":total_revenues,"graph_title":graph_title, "form":form,"line_chart_data":line_chart_data_dict,"years":years,},
						context_instance=RequestContext(request))
		return render_to_response("report/report_revenue_received_breakdown.html", {"form":form,},
									context_instance=RequestContext(request))


@login_required
def report_revenue_received(request):
	if request.method !='POST':
		form = ReportSearchForm(request)
		return render_to_response("report/report_revenue_received.html", {"form":form,},
			context_instance=RequestContext(request))
	else:
		form = ReportSearchForm(request, request.POST)
		tax_types = request.POST.getlist('tax_types')
		district = ''
		sector = ''
		cell = ''
		if request.POST.has_key('district'):
			district = request.POST['district']
		if request.POST.has_key('sector'):
			sector = request.POST['sector']
		if request.POST.has_key('cell'):
			cell = request.POST['cell']

		#period_from = request.POST['period_from']
		#period_to = request.POST['period_to']
		conditions = {}

		graph_title = "Report on received revenue "
		if (not district or district =='') and (not sector and sector =='') and len(tax_types) == 0:
			graph_title = None
		else:
			if (not district or district =='') and (not sector and sector ==''):
				graph_title = graph_title + 'in all districts'
			else:
				count = 0
				graph_title = graph_title + 'in ['
				arr = []
				if district and district !='':
					district = DistrictMapper.getDistrictById(int(district))
					conditions['district'] = district
					arr.append("district:"+district.name)
				if sector and sector !='':
					sector = SectorMapper.getSectorById(sector)
					conditions['sector'] = sector
					arr.append("sector:"+sector.name)	
				if cell and cell !='':
					cell = CellMapper.getCellById(cell)
					conditions['cell'] = cell
					arr.append("cell:"+cell.name)
				graph_title = graph_title+",".join(arr)+"]"
				
				#if period_from and period_from!='':
				#	conditions['period_from'] = period_from
				#if period_to and period_to!='':
				#	conditions['period_to'] = period_to

			graph_title = graph_title + ' on ['	
			
			form = ReportSearchForm(request, initial={"district":district,"sector":sector,"cell":cell,"tax_types":tax_types})			
			arr = []
			result_objects = []
			if 'fixed_asset' in tax_types:
				result_obj = PayFixedAssetTaxMapper.getFixedAssetTaxByBankPortfolio(conditions)
				result_objects.append(result_obj)
				arr.append("fixed asset tax")
			if 'rental_income' in tax_types:
				result_obj = PayRentalIncomeTaxMapper.getRentalIncomeTaxByBankPortfolio(conditions)
				result_objects.append(result_obj)
				arr.append("rental income tax")
			if 'trading_license' in tax_types:
				result_obj = PayTradingLicenseTaxMapper.getTradingLicenseTaxByBankPortfolio(conditions)
				result_objects.append(result_obj)
				arr.append("trading license tax")
			if 'land_lease_fee' in tax_types:
				conditions['fee_type'] = 'land_lease'
				result_obj = PayFeeMapper.getPayFeeByBankPortfolio(conditions)
				result_objects.append(result_obj)
				arr.append("land lease fee")

			if 'market_fee' in tax_types:
				conditions['fee_type'] = 'market'
				result_obj = PayFeeMapper.getPayFeeByBankPortfolio(conditions)
				result_objects.append(result_obj)
				arr.append("market fee")
			if 'cleaning_fee' in tax_types:
				conditions['fee_type'] = 'cleaning'
				result_obj = PayFeeMapper.getPayFeeByBankPortfolio(conditions)
				result_objects.append(result_obj)
				arr.append("cleaning fee")
			graph_title = graph_title + ",".join(arr)+ ']'

			new_result = {}

			for bank_obj in banks:
				if bank_obj[0] == 'CSO':
					continue
				bank_name = bank_obj[0]

				bank_dict = {}
				bank_dict['today'] = 0
				bank_dict['last7'] = 0
				bank_dict['last30'] = 0
				bank_dict['lastyear'] = 0

				for result_obj in result_objects:
					bank_dict['today'] += result_obj[bank_name]['today']
					bank_dict['last7'] += result_obj[bank_name]['last7']
					bank_dict['last30'] += result_obj[bank_name]['last30']
					bank_dict['lastyear'] += result_obj[bank_name]['lastyear']

				new_result[bank_name] = bank_dict
		
			total = {}
			total['today'] = 0
			total['last7'] = 0
			total['last30'] = 0
			total['lastyear'] = 0	
			for key, value in new_result.iteritems():
				total['today'] += value['today']
				total['last7'] += value['last7']
				total['last30'] += value['last30']
				total['lastyear'] += value['lastyear']
			new_result['Total'] = total


			message = "Revenue from taxes other than fixed asset tax and rental income tax is not considered."

			if not request.POST.has_key('toPrint'):
				if conditions and (conditions.has_key('district') or conditions.has_key('sector')):
					return render_to_response("report/report_revenue_received.html", {"data":new_result,"form":form,"message":message,"graph_title":graph_title,},
						context_instance=RequestContext(request))
				else:
					return render_to_response("report/report_revenue_received.html", {"data":new_result,"form":form,"graph_title":graph_title,},
						context_instance=RequestContext(request))
			else:
				if conditions and (conditions.has_key('district') or conditions.has_key('sector')):
					return render_to_response("report/report_revenue_received_print.html", {"data":new_result,"form":form,"message":message,"graph_title":graph_title,},
						context_instance=RequestContext(request))
				else:
					return render_to_response("report/report_revenue_received_print.html", {"data":new_result,"form":form,"graph_title":graph_title,},
						context_instance=RequestContext(request))
		return render_to_response("report/report_revenue_received.html", {"form":form,},
									context_instance=RequestContext(request))
		
				
@login_required
def report_tax_paid_and_unpaid(request):
	if request.method !='POST' and not request.GET.has_key('page'):
		form = ReportSearchForm(request)
		return render_to_response("report/report_tax_paid_and_unpaid.html", {"form":form,},
			context_instance=RequestContext(request))
	else:
		if request.method == 'POST':
			page = 1
			form = ReportSearchForm(request, request.POST)

			tax_types = request.POST.getlist('tax_types')
			district = ''
			sector = ''
			cell = ''
			if request.POST.has_key('district'):
				district = request.POST['district']
			if request.POST.has_key('sector'):
				sector = request.POST['sector']
			if request.POST.has_key('cell'):
				cell = request.POST['cell']
			calendar_year = request.POST['calendar_year']
			conditions = {}
			if district and district !='':
				district = DistrictMapper.getDistrictById(int(district))
				conditions['district'] = district
			if sector and sector !='':
				sector = SectorMapper.getSectorById(sector)
				conditions['sector'] = sector
			if cell and cell !='':
				cell = CellMapper.getCellById(cell)
				conditions['cell'] = cell
			if calendar_year and calendar_year!='':
				conditions['calendar_year'] = calendar_year
		
			form = ReportSearchForm(request, initial={'sector':sector,'district':district,'cell':cell,'tax_types':tax_types,'calendar_year':calendar_year,})	

			request.session['tax_types'] = tax_types
			request.session['report_search_form'] = form
			request.session['conditions'] = conditions

		else:
			page = request.GET["page"]
			form = request.session['report_search_form']
			conditions = request.session['conditions']
			tax_types = request.session['tax_types']

		graph_title = "Report on paid and unpaid amount for taxes ("
		result_objects = []
		result_objects_monthly_list = {}
		unpaid_objects = {}
		type = 'unpaid'
		if 'fixed_asset' in tax_types:
			result_obj = PayFixedAssetTaxMapper.getFixedAssetTaxPaidAndUnpaid(conditions=conditions)
			unpaid_objects['fixed asset tax'] = PayFixedAssetTaxMapper.getFixedAssetTaxPaidAndUnpaidList(conditions,type)
			#result_obj.reverse()
			result_objects.append(result_obj)
			graph_title = graph_title + 'fixed asset, '
		if 'rental_income' in tax_types:
			result_obj = PayRentalIncomeTaxMapper.getRentalIncomeTaxPaidAndUnpaid(conditions=conditions)
			unpaid_objects['rental income tax'] = PayRentalIncomeTaxMapper.getRentalIncomeTaxPaidAndUnpaidList(conditions,type)
			#result_obj.reverse()
			result_objects.append(result_obj)
			graph_title = graph_title + 'rental income, '
		if 'trading_license' in tax_types:
			result_obj = PayTradingLicenseTaxMapper.getTradingLicenseTaxPaidAndUnpaid(conditions = conditions)
			unpaid_objects['trading license tax'] = PayTradingLicenseTaxMapper.getTradingLicenseTaxPaidAndUnpaidList(conditions,type)
			#result_obj.reverse()
			result_objects.append(result_obj)
			graph_title = graph_title + 'trading license, '
		if 'land_lease' in tax_types:
			conditions['fee_type'] = 'land_lease'
			result_obj = PayFeeMapper.getFeePaidAndUnpaid(conditions = conditions)
			unpaid_objects['land lease fee'] = PayFeeMapper.getFeePaidAndUnpaidList(conditions,type)
			#result_obj.reverse()
			result_objects.append(result_obj)
			graph_title = graph_title + 'land lease, '
		if 'market' in tax_types:
			conditions['fee_type'] = 'market'
			result_obj = PayFeeMapper.getFeePaidAndUnpaid(conditions = conditions)
			unpaid_objects['market fee'] = PayFeeMapper.getFeePaidAndUnpaidList(conditions,type)
			#result_obj.reverse()
			result_objects_monthly_list['market fee'] = [result_obj]
			graph_title = graph_title + 'market fee, '
		if 'cleaning' in tax_types:
			conditions['fee_type'] = 'cleaning'
			result_obj = PayFeeMapper.getFeePaidAndUnpaid(conditions = conditions)
			unpaid_objects['cleaning fee'] = PayFeeMapper.getFeePaidAndUnpaidList(conditions,type)
			#result_obj.reverse()
			result_objects_monthly_list['cleaning fee'] = [result_obj]
			graph_title = graph_title + 'cleaning fee, '
		if graph_title[-2:] == ', ':
			graph_title = graph_title[:len(graph_title)-2] + ')'

		if len(result_objects) == 0 and len(result_objects_monthly_list) == 0:
			return render_to_response("report/report_tax_paid_and_unpaid.html", {"form":form,},
				context_instance=RequestContext(request))
		
		total_amount_sum = 0
		paid_amount_sum = 0
		unpaid_amount_sum = 0
		total_count_sum = 0
		paid_count_sum =0
		unpaid_count_sum = 0
		unallocated_amount_sum = 0
		unallocated_count_sum = 0

		bar_data_dict = None
		bar_data_dict_monthly_list = {}

		#set up data for yearly graph
		if len(result_objects) > 0:

			x_labels = []
		
			line_chart_data_total = []
			line_chart_data_paid = []
			line_chart_data_unpaid = []
			line_chart_data_unallocated = []

			count = 0
			for result_obj in result_objects:
				for obj in result_obj:
					count = count + 1
					x_labels.append(obj['name'])

					paid_amount_sum += int(obj['paid'])
					unpaid_amount_sum  += int(obj['unpaid'])
					paid_count_sum  += int(obj['paid_count'])
					unpaid_count_sum  += int(obj['unpaid_count'])
					unallocated_amount_sum += int(obj['unallocated'])
					unallocated_count_sum += int(obj['unallocated_count'])

					line_chart_data_unallocated.append([count,int(obj['unallocated_count'])])
					line_chart_data_total.append([count,int(obj['total_count'])])
					line_chart_data_paid.append([count,int(obj['paid_count'])])
					line_chart_data_unpaid.append([count,int(obj['unpaid_count'])])

			line_chart_data_total_dict = {}
			line_chart_data_total_dict['data'] = line_chart_data_total
			line_chart_data_total_dict['label'] = 'Total'
			line_chart_data_paid_dict = {}
			line_chart_data_paid_dict['data'] = line_chart_data_paid
			line_chart_data_paid_dict['label'] = 'Tax paid'
			line_chart_data_unpaid_dict = {}
			line_chart_data_unpaid_dict['data'] = line_chart_data_unpaid
			line_chart_data_unpaid_dict['label'] = 'Tax unpaid'
			line_chart_data_unallocated_dict = {}
			line_chart_data_unallocated_dict['data'] = line_chart_data_unpaid
			line_chart_data_unallocated_dict['label'] = 'Tax unallocated'

			line_chart_data = []
			line_chart_data.append(line_chart_data_total_dict)
			line_chart_data.append(line_chart_data_paid_dict)
			line_chart_data.append(line_chart_data_unpaid_dict)
			line_chart_data.append(line_chart_data_unallocated_dict)

			line_chart_data_dict = {}
			line_chart_data_dict['data'] = line_chart_data
			line_chart_data_dict['x_labels'] = x_labels

			bar_data = []

			bar_data1 = line_chart_data_paid
			bar_data1_dict={}
			bar_data1_dict['data'] = bar_data1
			bar_data1_dict['label'] = "Tax paid"
			bar_data1_dict['bars'] = {"order":1}

			bar_data2 = line_chart_data_unpaid
			bar_data2_dict={}
			bar_data2_dict['data'] = bar_data2
			bar_data2_dict['label'] = "Tax unpaid"
			bar_data2_dict['bars'] = {"order":2}

			bar_data3 = line_chart_data_unallocated
			bar_data3_dict={}
			bar_data3_dict['data'] = bar_data3
			bar_data3_dict['label'] = "Tax unallocated"
			bar_data3_dict['bars'] = {"order":3}

			bar_data.append(bar_data1_dict)
			bar_data.append(bar_data2_dict)
			bar_data.append(bar_data3_dict)

			bar_data_dict = {}
			bar_data_dict['data'] = bar_data
			#new_x_labels = []
			#for x_label in x_labels:
			#	new_x_labels.append(x_label[0:3])
			bar_data_dict['x_labels'] = x_labels

		#set up data for monthly graph
		if len(result_objects_monthly_list) > 0:
			for k, result_objects_monthly in result_objects_monthly_list.items():
				x_labels = []

				line_chart_data_total = []
				line_chart_data_paid = []
				line_chart_data_unpaid = []
				line_chart_data_unallocated = []

				single_result = result_objects_monthly[0]

				for single_month in single_result:
					x_labels.append(single_month['name'])
				count = 0
				for month_name in x_labels:
					count = count + 1
					total_count = 0
					paid_count = 0
					unpaid_count = 0
					paid_amount = 0
					unpaid_amount = 0
					unallocated_amount = 0
					unallocated_count = 0

					for result_obj in result_objects_monthly:
						for obj in result_obj:
							if obj['name'] == month_name:
								total_count += obj['total_count']
								paid_count += obj['paid_count']
								unpaid_count += obj['unpaid_count']
								unallocated_count += obj['unallocated_count']
								paid_amount += obj['paid']
								unpaid_amount += obj['unpaid']
								unallocated_amount += obj['unallocated']
					paid_amount_sum += int(paid_amount)
					unpaid_amount_sum  += int(unpaid_amount)
					paid_count_sum  += int(paid_count)
					unpaid_count_sum  += int(unpaid_count)
					unallocated_count_sum += int(unallocated_count)
					unallocated_amount_sum += int(unallocated_amount)

					line_chart_data_total.append([count,int(total_count)])
					line_chart_data_paid.append([count,int(paid_count)])
					line_chart_data_unpaid.append([count,int(unpaid_count)])
					line_chart_data_unallocated.append([count,int(unallocated_count)])

				line_chart_data_total_dict = {}
				line_chart_data_total_dict['data'] = line_chart_data_total
				line_chart_data_total_dict['label'] = 'Total'
				line_chart_data_paid_dict = {}
				line_chart_data_paid_dict['data'] = line_chart_data_paid
				line_chart_data_paid_dict['label'] = 'Tax paid'
				line_chart_data_unpaid_dict = {}
				line_chart_data_unpaid_dict['data'] = line_chart_data_unpaid
				line_chart_data_unpaid_dict['label'] = 'Tax unpaid'
				line_chart_data_unallocated_dict = {}
				line_chart_data_unallocated_dict['data'] = line_chart_data_unpaid
				line_chart_data_unallocated_dict['label'] = 'Tax unallocated'

				line_chart_data = []
				line_chart_data.append(line_chart_data_total_dict)
				line_chart_data.append(line_chart_data_paid_dict)
				line_chart_data.append(line_chart_data_unpaid_dict)
				line_chart_data.append(line_chart_data_unallocated_dict)

				line_chart_data_dict = {}
				line_chart_data_dict['data'] = line_chart_data
				line_chart_data_dict['x_labels'] = x_labels

				bar_data = []

				bar_data1 = line_chart_data_paid
				bar_data1_dict={}
				bar_data1_dict['data'] = bar_data1
				bar_data1_dict['label'] = "Tax paid"
				bar_data1_dict['bars'] = {"order":1}

				bar_data2 = line_chart_data_unpaid
				bar_data2_dict={}
				bar_data2_dict['data'] = bar_data2
				bar_data2_dict['label'] = "Tax unpaid"
				bar_data2_dict['bars'] = {"order":2}

				bar_data3 = line_chart_data_unallocated
				bar_data3_dict={}
				bar_data3_dict['data'] = bar_data3
				bar_data3_dict['label'] = "Tax unallocated"
				bar_data3_dict['bars'] = {"order":3}

				bar_data.append(bar_data1_dict)
				bar_data.append(bar_data2_dict)
				bar_data.append(bar_data3_dict)

				bar_data_dict_monthly = {}
				bar_data_dict_monthly['data'] = bar_data
				new_x_labels = []
				for x_label in x_labels:
					new_x_labels.append(x_label[0:3])
				bar_data_dict_monthly['x_labels'] = new_x_labels

				bar_data_dict_monthly_list[k] = bar_data_dict_monthly

		total_amount_sum = total_amount_sum + paid_amount_sum + unpaid_amount_sum + unallocated_amount_sum
		total_count_sum = total_count_sum + paid_count_sum + unpaid_count_sum + unallocated_count_sum

		result = {}
		result['paid_amount']=paid_amount_sum
		result['unpaid_amount']=unpaid_amount_sum
		result['total'] = total_amount_sum
		result['paid_count']=paid_count_sum
		result['unpaid_count']=unpaid_count_sum
		result['total_count'] = total_count_sum
		result['unallocated_count']=unallocated_count_sum
		result['unallocated_amount']=unallocated_amount_sum
		if int(total_count_sum) == 0:
			result['paid_percentage'] = '0%'
			result['unpaid_percentage'] = '0%'
			result['unallocated_percentage'] = '0%'
		else:			
			result['paid_percentage']="{0:.0f}%".format(float(paid_count_sum)/total_count_sum * 100)
			result['unpaid_percentage']="{0:.0f}%".format(float(unpaid_count_sum)/total_count_sum * 100)
			result['unallocated_percentage'] ="{0:.0f}%".format(float(unallocated_count_sum)/total_count_sum * 100)

		unpaid_list = None
		#set up list of sms and emails to be stored in session for Bulk Messaging later
		smsList = {}
		emailList = {}
		if unpaid_objects > 0:
			#get list of unpaid people:
			unpaid_list = format_paid_or_unpaid_list(unpaid_objects)
			for i in unpaid_list:
				tmp = {}
				if i.has_key('cid'):
					tmp['cid'] = i['cid']
				if i.has_key('bid'):
					tmp['bid'] = i['bid']
				if i.has_key('pid'):
					tmp['pid'] = i['pid']

				if i.has_key('phone') and i['phone'] != '':
					if i['phone'].find("\n") >= 0:
						phones = i['phone'].split("\n")
						for phone in phones:
							smsList[phone] = tmp
					else:
						smsList[i['phone']] = tmp
				if i.has_key('email') and i['email'] != '':
					emailList[i['email']] = tmp
		
		request.session['unpaid_sms'] = smsList
		request.session['unpaid_email'] = emailList
		#print len(smsList)
		#print len(emailList)
		#print '@@@@@'
		if not request.POST.has_key("toPrint"):
			page = 1
			if request.GET.get('page',None) != None:
				page = request.GET["page"]
			records_in_page = 20
			paginator = Paginator(unpaid_list, records_in_page)
			try:
				unpaid_list = paginator.page(page)
			except PageNotAnInteger:
				# If page is not an integer, deliver first page.
				unpaid_list = paginator.page(1)
			except EmptyPage:
				# If page is out of range (e.g. 9999), deliver last page of results.
				unpaid_list = paginator.page(paginator.num_pages)
			
			return render_to_response("report/report_tax_paid_and_unpaid.html", {"form":form,'graph_title':graph_title,"bar_data":bar_data_dict,"result":result,"bar_data_monthly_list":bar_data_dict_monthly_list,'unpaid_list':unpaid_list},
				context_instance=RequestContext(request))
		else:
			return render_to_response("report/report_tax_paid_and_unpaid_print.html", {"form":form,'graph_title':graph_title,"bar_data":bar_data_dict,"result":result,"bar_data_monthly_list":bar_data_dict_monthly_list,'unpaid_list':unpaid_list},
				context_instance=RequestContext(request))


def format_paid_or_unpaid_list(full_list):
	result = {}
	citizenIds = []
	businessIds = []
	subbusinessIds = []
	for type,list in full_list.iteritems():
		for i in list:
			if i.due_date and i.due_date > datetime.now().date():
				continue

			citizen = None
			property = None
			business = None
			subbusiness = None
			if hasattr(i, 'citizen') and i.citizen:
				citizen = i.citizen
			if hasattr(i, 'property')and i.property:
				property = i.property
				owners = property.owners.all()
				if owners:
					citizen = owners[0].owner_citizen

				#also check the old ownership table
				ownerships = OwnershipMapper.getCurrentOwnershipsByPropertyId(property.id)
				if ownerships:
					citizen = ownerships[0].owner_citizen
			if hasattr(i, 'business') and i.business:
				business = i.business
				owners = business.owners.all()
				if owners:
					citizen = owners[0].owner_citizen
			if hasattr(i, 'subbusiness') and i.subbusiness:
				subbusiness = i.subbusiness
				business = subbusiness.business
				owners = business.owners.all()
				if owners:
					citizen = owners[0].owner_citizen
		
			sign = getSignCheck(citizen,business,subbusiness)
			#if ((citizen and citizen.id in citizenIds) and (not business or business in businessIds) and (not subbusiness or subbusiness in subbusinessIds)):
			#	tmp = results[sign]			   
			#elif (not citizen and business and business in businessIds and (not subbusiness or subbusiness in subbusinessIds)):
			#	tmp = results[sign]

			if sign in result:
				tmp = result[sign]
			else:
				tmp = {'tax_type':''}
				if citizen:
					citizenIds.append(citizen.id)
					tmp['citizen_id'] = citizen.citizen_id
					tmp['citizen_name'] = citizen.getDisplayName()
					phones = []
					if citizen.phone_1:
						phones.append(citizen.phone_1)
					if citizen.phone_2:
						phones.append(citizen.phone_2)
					tmp['phone'] = "\n".join(phones)
					tmp['email'] = citizen.email
					tmp['cid'] = citizen.id

				if business:
					businessIds.append(business.id)
					tmp['business'] = business.name
					tmp['tin'] = business.tin
					phones = []
					if business.phone1:
						phones.append(business.phone1)
					if business.phone2:
						phones.append(business.phone2)
					tmp['phone'] = "\n".join(phones)
					tmp['email'] = business.email
					tmp['bid'] = business.id

				if subbusiness:
					subbusinessIds.append(subbusiness.id)
					tmp['business'] = tmp['business'] + " (Branch " + subbusiness.branch + ")"

			if property:
				tmp['address'] = property.getDisplayName() + " (" + property.getUPI() + ")"
				tmp['pid'] = property.id
				
			tax_type = type.title()
			if i.due_date and i.due_date != '':
				tax_type += ' - Due on ' + i.due_date.strftime('%d/%m/%Y')
			if tmp['tax_type']  == '':
				tmp['tax_type'] = tax_type
			else:
				tmp['tax_type'] = tmp['tax_type'] + "\n" + tax_type

			for k,v in tmp.iteritems():
				if not v:
					tmp[k] = ''
			result[sign] = tmp

	return result.values()


def getSignCheck(citizen,business,subbusiness):
	sign = ''
	if citizen:
		sign += 'C' + str(citizen.id)
	else:
		sign += 'C'
	if business:
		sign += 'B' + str(business.id)
	else:
		sign += 'B'
	if subbusiness:
		sign += 'S' + str(subbusiness.id)
	else:
		sign += 'S'

	return sign


def report_property_log(request):
	if request.method !='POST': 
		form = ReportSearchForm(request)
		return render_to_response("report/report_report_log.html", {"form":form,},
			context_instance=RequestContext(request))
	else:
		form = ReportSearchForm(request, request.POST)
		if form.is_valid():
			conditions = {}
			district = form.cleaned_data['district']
			sector = form.cleaned_data['sector']
			cell = form.cleaned_data['cell']
			upi = form.cleaned_data['upi']
			year = form.cleaned_data['calendar_year']
			
			conditions['calendar_year']=year

			graph_title = "Report on logs throughout the year "+ year + " for properties "
			if (not district or district =='') and (not sector and sector =='') and (not cell or cell =='') and (not upi or upi ==''):
				graph_title = graph_title + 'in all districts.'
			else:
				arr = []
				graph_title = graph_title + "["
				count = 0 
				if district and district !='':
					district = 	DistrictMapper.getDistrictById(int(district))
					conditions['district']=district
					arr.append('district:'+district.name)
				if sector and sector !='':
					sector = SectorMapper.getSectorById(sector)
					conditions['sector']=sector
					arr.append('sector:'+sector.name)
				if cell and cell !='':
					cell = Cell.objects.get(pk = int(cell))
					conditions['cell']=cell
					arr.append('cell:'+cell.name)
				if upi and upi !='':
					conditions['upi']=upi
					arr.append('upi:'+upi)
				graph_title = graph_title + ','.join(arr) + '].'
				
			
			form = ReportSearchForm(request, initial={'district':district,'sector':sector,'cell':cell,'upi':upi,'calendar_year':year,})
			result = PropertyMapper.getLogActivities(conditions = conditions)


			## ******************************************************* ##
			line_chart_data = []
			line_chart_data1 = []
			line_chart_data1_dict = {}
			line_chart_data_dict = {}
			count = 0
			total_log_activities = 0
			for value in result['values']:
				count = count + 1
				line_chart_data1.append([count,int(value)])
				total_log_activities = total_log_activities + int(value)

			line_chart_data1_dict['data'] = line_chart_data1
			line_chart_data1_dict['label'] = "log activity"
			line_chart_data.append(line_chart_data1_dict)
			line_chart_data_dict['data'] = line_chart_data

			new_x_labels = []
			for x_label in result['labels']:
				new_x_labels.append(x_label[0:3])

			line_chart_data_dict['x_labels'] = new_x_labels

			if not request.POST.has_key('toPrint'):
				return render_to_response("report/report_report_log.html", {"total_log_activities":total_log_activities,"graph_title":graph_title, "form":form,"line_chart_data":line_chart_data_dict,},
					context_instance=RequestContext(request))
			else:
				return render_to_response("report/report_report_log_print.html", {"total_log_activities":total_log_activities,"graph_title":graph_title, "form":form,"line_chart_data":line_chart_data_dict,},
					context_instance=RequestContext(request))
		return render_to_response("report/report_report_log.html", {"form":form,},
			context_instance=RequestContext(request))


@login_required
def report_property_contact(request):
	if request.method !='POST':
		form = ReportSearchForm(request)
		pp.pprint( request.__dict__)
		return render_to_response("report/report_report_contact.html", {"form":form,},
			context_instance=RequestContext(request))
	else:
		form = ReportSearchForm(request, request.POST)
		if form.is_valid():
			district = form.cleaned_data['district']
			sector = form.cleaned_data['sector']
			cell = form.cleaned_data['cell']

			
			graph_title = "Report on contacts of property "
			if (not district or district =='') and (not sector and sector =='') and (not cell or cell ==''):
				graph_title = graph_title + 'in all districts.'
			else:
				count = 0 
				graph_title = graph_title + '( '
				if district and district !='':
					district = DistrictMapper.getDistrictById(district)
					graph_title = graph_title + 'district:' + district.name
					count = count + 1
				if sector and sector !='':
					sector = SectorMapper.getSectorById(sector)
					if count == 0:
						graph_title = graph_title + 'sector:' + sector.name
					else:
						graph_title = graph_title + ',sector:' + sector.name
					count = count + 1
				if cell and cell !='':
					cell = CellMapper.getCellById(cell)
					if count == 0:
						graph_title = graph_title + 'cell:' + cell.name
					else:
						graph_title = graph_title + ',cell:' + cell.name
				graph_title = graph_title + ').'
			
			form = ReportSearchForm(request, initial={'district':district,'sector':sector,'cell':cell,})
			nums = PropertyMapper.getNumOfPropertiesWithContact({'district':district,'sector':sector,'cell':cell,})
			both = nums['both']
			with_contact = nums['with']
			without_contact = both - with_contact
				
			simple_pie_data = [
				{ "label": "With contact",  "data": int(with_contact), "color": "#88bbc8"},
				{ "label": "Without contact",  "data": int(without_contact), "color": "#ed7a53"},
			];
			pp.pprint(simple_pie_data)
			result = {}
			result['with_contact']=with_contact
			result['without_contact']=without_contact
			result['both'] = both
			if int(both) == 0:
				result['with_contact_percentage'] = '0%'
				result['without_contact_percentage'] = '0%'
			else:			
				result['with_contact_percentage']="{0:.0f}%".format(float(with_contact)/both * 100)
				result['without_contact_percentage']="{0:.0f}%".format(float(without_contact)/both * 100)

			if not request.POST.has_key('toPrint'):
				return render_to_response("report/report_report_contact.html", {"simple_pie_data":simple_pie_data,"form":form, "graph_title":graph_title,"result":result,},
							  context_instance=RequestContext(request))				
			else:
				return render_to_response("report/report_report_contact_print.html", {"simple_pie_data":simple_pie_data,"form":form, "graph_title":graph_title,"result":result,},
							  context_instance=RequestContext(request))


@login_required
def report_business_no_tin(request):
	if request.method !='POST' and not request.GET.has_key('page'):
		form = ReportSearchForm(request)
		return render_to_response("report/report_tax_business_no_tin.html", {"form":form,},
			context_instance=RequestContext(request))
	else:
		graph_title = ""
		records_in_page = 20
		conditions = {} 
		if request.method == 'POST':
			page = 1
			form = ReportSearchForm(request, request.POST)
			graph_title = "Report on business without TIN"
		else:
			page = request.GET["page"]
			graph_title = request.session['graph_title']
			form = request.session['business_no_tin_form']
		if form.is_valid():
			if request.method == 'POST':
				district = form.cleaned_data['district']
				sector = form.cleaned_data['sector']
				cell = form.cleaned_data['cell']
				if (not district or district =='') and (not sector and sector =='') and (not cell or cell ==''):
					graph_title = graph_title + " in all districts"
				else:
					graph_title = graph_title + " ("
					arr = []
					if district and district !='':
						district = DistrictMapper.getDistrictById(int(district))
						conditions['district'] = district
						arr.append("district:"+district.name)
					if sector and sector !='':
						sector = SectorMapper.getSectorById(sector)
						conditions['sector'] = sector
						arr.append("sector:"+sector.name)
					if cell and cell !='':
						cell=Cell.objects.get(pk=int(cell))
						conditions['cell'] = cell
						arr.append("cell:"+cell.name)
					graph_title = graph_title + ",".join(arr) + ")"
				form = ReportSearchForm(request, initial={'sector':sector,'district':district,'cell':cell,})
				request.session['conditions'] = conditions
				request.session['business_no_tin_form'] = form
				request.session['graph_title'] = graph_title
			else:
				conditions = request.session['conditions']
			
			figures = BusinessMapper.getBusinessTinFigures(conditions)
			businesses = []
			conditions['tin'] = 'null'
			businesses = BusinessMapper.getBusinessByConditionsOrAllByPage(conditions, records_in_page, 0)
			count = 0
			for business in businesses:
				count = count + 1
				business.loopcount = count
			paginator = Paginator(businesses, records_in_page)
			try:
				businesses = paginator.page(page)
			except PageNotAnInteger:
				# If page is not an integer, deliver first page.
				businesses = paginator.page(1)
			except EmptyPage:
				# If page is out of range (e.g. 9999), deliver last page of results.
				businesses = paginator.page(paginator.num_pages)			
			
		
		
			# graph section	
			simple_pie_data = [
				{ "label": "With tin number",  "data": int(figures['with_tin_number']), "color": "#88bbc8"},
				{ "label": "Without tin number",  "data": int(figures['without_tin_number']), "color": "#ed7a53"},
			];
			result = {}
			figures['all'] = int(figures['with_tin_number']) + int(figures['without_tin_number'])
			if int(figures['all']) == 0:
				figures['with_tin_percentage'] = '0%'
				figures['without_tin_percentage'] = '0%'
			else:			
				figures['with_tin_percentage']="{0:.0f}%".format(float(figures['with_tin_number'])/figures['all'] * 100)
				figures['without_tin_percentage']="{0:.0f}%".format(float(figures['without_tin_number'])/figures['all'] * 100)
				
			if not request.POST.has_key("toPrint"):
				return render_to_response("report/report_tax_business_no_tin.html", {"simple_pie_data":simple_pie_data,"businesses":businesses,"graph_title":graph_title,"form":form,"figures":figures},
					context_instance=RequestContext(request))
			else:
				return render_to_response("report/report_tax_business_no_tin_print.html", {"simple_pie_data":simple_pie_data,"businesses":businesses,"graph_title":graph_title,"figures":figures},
					context_instance=RequestContext(request))
	return render_to_response("report/report_tax_business_no_tin.html", {"form":form,},
			context_instance=RequestContext(request))
	

@login_required		
def report_default(request, action):
	if not action or action == 'property_contact':
		return report_property_contact(request)
	if action == 'log_activities':
		return report_property_log(request)
	if action == 'revenue_received':
		return report_revenue_received(request)
	if action == 'revenue_received_breakdown':
		return report_revenue_received_breakdown(request)
	if action == 'tax_paid_and_unpaid':
		return report_tax_paid_and_unpaid(request)
	if action == 'tax_payers':
		return report_tax_payers(request)
	if action == 'business_no_tin':
		return report_business_no_tin(request)
	if action == 'properties_with_unpaid_tax':
		return report_properties_with_unpaid_tax(request)
	if action == 'properties_with_no_owners':
		return report_properties_with_no_owners(request)
	raise Http404


@login_required
def report_staff(request):
	if request.method !='POST' and not request.GET.has_key('page'):
		form = ReportSearchForm(request)
		return render_to_response("report/report_staff.html", {"form":form,},
			context_instance=RequestContext(request))
	else:
		tax_types = None
		form = None
		conditions = {}
		page = 1
		records_in_page = 20
		if request.method == 'POST':
			form = ReportSearchForm(request, request.POST)
			tax_types = request.POST.getlist('tax_types')
			district = request.POST['district']
			sector = request.POST['sector']
			cell = request.POST['cell']
			
			graph_title = "Report on tax payers "
			if (not district or district =='') and (not sector and sector =='') and (not cell and cell =='') and len(tax_types) ==0:
				graph_title = None
			else:
				if (not district or district =='') and (not sector and sector =='') and (not cell and cell ==''):
					graph_title = graph_title + 'in all districts'
				else:
					arr = []
					if district and district !='':
						district = DistrictMapper.getDistrictById(int(district))
						conditions['district'] = district
						arr.append("district:"+district.name)
					if sector and sector !='':
						sector = SectorMapper.getSectorById(int(sector))
						conditions['sector'] = sector
						arr.append("sector:"+sector.name)
					if cell and cell !='':
						cell = CellMapper.getCellById(int(cell))
						conditions['cell'] = cell
						arr.append("cell:"+cell.name)
					graph_title = graph_title + ",".join(arr) + "]"
				if len(tax_types) != 0:
					graph_title = graph_title + " with tax ["
					graph_title = graph_title + ','.join(tax_types)
					graph_title = graph_title + "]"
				form = ReportSearchForm(request, initial={"district":district,"sector":sector,"cell":cell,"tax_types":tax_types})
				request.session['tax_payer_form'] = form
				request.session['tax_types']=tax_types
				request.session['conditions'] = conditions
				request.session['graph_title'] = graph_title
		elif request.method == 'GET' and request.GET.has_key('page'):
			page = request.GET["page"]
			tax_types = request.session['tax_types']
			conditions = request.session['conditions']
			form =request.session['tax_payer_form']
			graph_title = request.session['graph_title']

		result_objects = []
		summary = {}
		if tax_types:
			if 'fixed_asset' in tax_types:
				result_obj = PayFixedAssetTaxMapper.getTaxPayers(conditions)
				if result_obj:
					summary['Fixed asset tax'] = len(result_obj) 
					for citizen in result_obj:
						result_objects.append(citizen)
				else:
					summary['Fixed asset tax'] = 0
				
			if 'rental_income' in tax_types:
				result_obj = PayRentalIncomeTaxMapper.getTaxPayers(conditions)
				if result_obj:
					summary['Rental income tax'] = len(result_obj)
					for citizen in result_obj:
						result_objects.append(citizen)
				else:
					summary['Rental income tax'] = 0
			if 'trading_license' in tax_types:
				result_obj = PayTradingLicenseTaxMapper.getTaxPayers(conditions)
				if result_obj:
					summary['Trading license tax'] = len(result_obj)
					for i in result_obj:
						result_objects.append(i)
				else:
					summary['Trading license tax'] = 0
			if 'land_lease_fee' in tax_types:
				conditions['fee_type'] = 'land_lease'
				result_obj = PayFeeMapper.getTaxPayers(conditions)
				if result_obj:
					summary['Land lease fee'] = len(result_obj)
					for citizen in result_obj:
						result_objects.append(citizen)
				else:
					summary['Land lease fee'] = 0
			if 'market_fee' in tax_types:
				conditions['fee_type'] = 'market'
				result_obj = PayFeeMapper.getTaxPayers(conditions)
				if result_obj:
					summary['Market fee'] = len(result_obj)
					for citizen in result_obj:
						result_objects.append(citizen)
				else:
					summary['Market fee'] = 0
			if 'cleaning_fee' in tax_types:
				conditions['fee_type'] = 'cleaning'
				result_obj = PayFeeMapper.getTaxPayers(conditions)
				if result_obj:
					summary['Cleaning'] = len(result_obj)
					for i in result_obj:
						result_objects.append(i)
				else:
					summary['Cleaning fee'] = 0
		if len(result_objects) > 1:
			result_objects.sort(key=lambda x: x.tax_type, reverse=False)


		if not request.POST.has_key('toPrint'):
			paginator = Paginator(result_objects, records_in_page)
			try:
				tax_payers = paginator.page(page)
			except PageNotAnInteger:
				# If page is not an integer, deliver first page.
				tax_payers = paginator.page(1)
			except EmptyPage:
				# If page is out of range (e.g. 9999), deliver last page of results.
				tax_payers = paginator.page(paginator.num_pages)

			return render_to_response("report/report_tax_payers.html", {"tax_payers":tax_payers,"form":form, "graph_title":graph_title,"summary":summary},
				context_instance=RequestContext(request))				
		else:
			tax_payers = result_objects
			return render_to_response("report/report_tax_payers_print.html", {"tax_payers":tax_payers,"form":form,"graph_title":graph_title,"summary":summary},
				context_instance=RequestContext(request))


def construction(request):
	#return HttpResponse('Unauthorized', status=401)
	raise Http404
	#return render_to_response('admin/construction.html', {}, context_instance=RequestContext(request))
