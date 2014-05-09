from asset.models import *
from property.models import *
from jtax.models import *
from admin.Common import Common
import json
from django.http import HttpResponse


def properties_with_unpaid_tax_for_printing(request):
	conditions = request.session['conditions']
	tax_types = request.session['tax_types']
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
		if 'land_lease_fee' in tax_types:
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

	if len(property_ids) > 0:
		property_ids = Property.objects.filter(id__in = property_ids).order_by("sector","cell","village","parcel_id").values('id')
		property_ids = Common.get_value_list(property_ids,'id')
		properties = []
		
		for property_id in property_ids:
			property_dict = {}
			property = Property.objects.get(pk=property_id)
			upi = property.getUPI()
			if upi:
				property_dict['upi'] = upi
			else:
				property_dict['upi'] = ''
			
			property_dict['address'] =  property.getDisplayName()
			
			
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
			if 'land_lease_fee' in tax_types:
				items = Fee.objects.filter(fee_type='land_lease',i_status='active',is_paid=False,property=property).order_by("-due_date")
				if len(items) > 0:
					for item in items:
						description = "Rental Income Tax - Due on " + item.due_date.strftime("%d/%m/%y")
						tax_description.append(description)
			
			property_dict['tax_types'] = "<br>".join(tax_description)
			
			citizen_names_str = []
			citizen_ids_str = []
			business_names_str = []
			phones_str = []
			emails_str = []
			property_dict['business_names'] = ""
			property_dict['citizen_names'] = ""
			property_dict['citizen_ids'] = ""
			property_dict["phones"] = ""
			property_dict["emails"] = ""
		
			citizen_ids = None
			citizens = None
			
			citizen_ids = Ownership.objects.filter(i_status='active',asset_property = property, date_ended__isnull=True).values('owner_citizen').distinct()
			if citizen_ids:
				citizen_ids = Common.get_value_list(citizen_ids,'owner_citizen')
				citizen = Citizen.objects.filter(id__in=citizen_ids,status_id=1)
			if citizens:
				for citizen in citizens:
					citizen_names_str.append(citizen.getDisplayName())
					if citizen.citizen_id:
						citizen_ids_str.append(citizen.citizen_id)
					if citizen.phone_1:
						phones_str.append(citizen.phone_1)
					if citizen.email:
						emails_str.append(citizen.email)
				property_dict['citizen_ids'] = "<br>".join(citizen_ids_str)
				property_dict["citizen_names"] = "<br>".join(citizen_names_str)
				property_dict["phones"] = "<br>".join(phones_str)
				property_dict["emails"] = "<br>".join(emails_str)

			business_ids = None
			businesses = None
			subbusiness_ids = None
			subbusinesses = None
			
			business_ids = Ownership.objects.filter(i_status='active', date_ended__isnull=True,  owner_business__isnull=False, asset_property__id = property.id).values('owner_business_id').distinct()
			if business_ids:
				business_ids = Common.get_value_list(business_ids,'owner_business_id')
				businesses = Business.objects.filter(i_status='active',id__in = business_ids)
				if businesses:
					for business in businesses:
						if business.phone1:
							phones_str.append(business.phone1)
						if business.email:
							emails_str.append(business.email)
						business_names_str.append(business.name)
			
			subbusiness_ids = Ownership.objects.filter(i_status='active', date_ended__isnull=True,  owner_subbusiness__isnull=False, asset_property__id = property.id).values('owner_subbusiness_id').distinct()
			if subbusiness_ids:
				subbusiness_ids = Common.get_value_list(subbusiness_ids,'owner_subbusiness_id')
				subbusinesses = SubBusiness.objects.filter(i_status='active',id__in = subbusiness_ids)
				if subbusinesses:
					for subbusiness in subbusinesses:
						if subbusiness.business.phone1:
							phones_str.append(subbusiness.business.phone1)
						if subbusiness.business.email:
							emails_str.append(subbusiness.business.email)
						business_names_str.append(subbusiness.business.name + "(Branch: "+ subbusiness.branch + ")")
			if subbusiness_ids or business_ids:
				if len(business_names_str) > 0:
					property_dict['business_names'] = "<br>".join(business_names_str)
				if len(phones_str):
					property_dict['phones'] = "<br>".join(phones_str)
				if len(emails_str):
					property_dict['emails'] = "<br>".join(emails_str)
			properties.append(property_dict)
		
		result = {}
		result['properties'] = properties 
		return HttpResponse(json.dumps(result), mimetype="application/json")
	return HttpResponse("")


	