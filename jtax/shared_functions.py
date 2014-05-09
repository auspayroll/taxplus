from jtax.models import *
from property.models import *
from asset.models import *
from datetime import date
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from log.mappers.LogMapper import LogMapper
from common.util import CommonUtil
from django.core.mail import EmailMultiAlternatives
from dev1 import ThreadLocal

"""
Send request info & etc to admin email for debug
"""
def sendEmailDebug(subject, form):
	content = "Form submit data:\n\n"
	content = content + str(dict(form.data.iterlists()))
	
	content = content +  "\n\nForm available districts:\n\n"
	content = content + str(form.fields['district'].choices)

	content = content + "\n\nForm available sectors:\n\n"
	content = content + str(form.fields['sector'].choices)


	content = content + "\n\nUser data:\n\n"
	user = ThreadLocal.get_current_user()
	user_data = str(user.__dict__)
	content = content + user_data

	content = content + "\n\nUser permission:\n\n"
	permissions = user.getPermissions()
	if permissions:
		for i in permissions:
			content = content + str(i.id) + " | "

	content = content + "\n\nUser allowed access districts:\n\n"
	districts = user.getDistricts()
	if districts:
		for i in districts:
			content = content + str(i.name) + "(" + str(i.id) + ") | "

	content = content + "\n\nUser allowed access sectors:\n\n"
	sectors = user.getSectors()
	if sectors:
		for i in sectors:
			content = content + str(i.name) + "(" + str(i.id) + ") | "

	#send email to admin
	CommonUtil.sendEmail(subject,content,content, variables.SUPPORT_EMAIL)
	CommonUtil.sendEmail(subject,content,content, 'simon@propertymode.com.au')
	#content = content + str()



"""
Get the province,district,tin info for a tax_item
"""
def get_location_and_tin_info(tax_item):
	location = {'province':'','district':'','tin':''}
	if isinstance(tax_item, (PropertyTaxItem, RentalIncomeTax)):
		if tax_item.property:
			if tax_item.property.sector:
				location['province'] = tax_item.property.sector.district.province.name
				location['district'] = tax_item.property.sector.district.name
	elif isinstance(tax_item, TradingLicenseTax):
		if tax_item.subbusiness:
			location['tin'] = tax_item.subbusiness.business.tin
			if tax_item.subbusiness.sector:
				location['province'] = tax_item.subbusiness.sector.district.province.name
				location['district'] = tax_item.subbusiness.sector.district.name
		elif tax_item.business:
			location['tin'] = tax_item.business.tin
			if tax_item.business.sector:
				location['province'] = tax_item.business.sector.district.province.name
				location['district'] = tax_item.business.sector.district.name
	return location


def get_tax_item_description(tax_item):
	if isinstance(tax_item, PropertyTaxItem):
		return 'Fixed Asset Tax ' + str(tax_item.due_date.year) + " for " + tax_item.property.getDisplayName()
	elif isinstance(tax_item, RentalIncomeTax):
		return 'Rental Income Tax ' + str(tax_item.due_date.year) + " for " + tax_item.property.getDisplayName()
	elif isinstance(tax_item, TradingLicenseTax):
		if tax_item.business:
			return 'Trading License tax ' + str(tax_item.due_date.year) + " for " + tax_item.business.name
		elif tax_item.subbusiness:
			return 'Trading License tax ' + str(tax_item.due_date.year) + " for " + tax_item.subbusiness.business.name + " - " + tax_item.subbusiness.branch
	elif isinstance(tax_item, Fee):
		if tax_item.fee_type == 'land_lease':
			return 'Land Lease fee ' + str(tax_item.due_date.year) + " for "+ tax_item.property.getDisplayName()
		elif tax_item.fee_type == 'market':
			return 'Market fee ' + str(tax_item.due_date.year) + " for " + tax_item.property.getDisplayName()
		elif tax_item.fee_type == 'cleaning':
			if tax_item.subbusiness:
				return 'Cleaning fee ' + tax_item.due_date.strftime('%b %Y') + " for " + tax_item.subbusiness.business.name + " - " + tax_item.subbusiness.branch
			elif tax_item.business:
				'Cleaning fee ' + tax_item.due_date.strftime('%b %Y')  + " for " + tax_item.business.name			



def get_tax_type_from_tax_item(tax_item):
	if isinstance(tax_item, PropertyTaxItem):
		return "fixed_asset"
	elif isinstance(tax_item, RentalIncomeTax):
		return "rental_income"
	elif isinstance(tax_item, TradingLicenseTax):
		return "trading_license"
	elif isinstance(tax_item, Fee):
		return tax_item.fee_type



"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Get the contact citizens of a tax item
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def get_contact_citizens_for_tax_item(tax_item):
	citizens = None
	if isinstance(tax_item, (PropertyTaxItem, RentalIncomeTax)):
		if tax_item.property:
			citizens = get_contact_citizens_for_property_or_business(tax_item.property)
	if isinstance(tax_item, TradingLicenseTax):
		if tax_item.subbusiness:
			citizens = get_contact_citizens_for_property_or_business(tax_item.subbusiness)
		elif tax_item.business:
			citizens = get_contact_citizens_for_property_or_business(tax_item.business)
	if isinstance(tax_item, Fee):
		if tax_item.fee_type == 'land_lease':
			if tax_item.property:
				citizens = get_contact_citizens_for_property_or_business(tax_item.property)
		elif (tax_item.fee_type == 'market' or tax_item.fee_type == 'cleaning'):
			if tax_item.subbusiness:
				citizens = get_contact_citizens_for_property_or_business(tax_item.subbusiness)
			elif tax_item.business:
				citizens = get_contact_citizens_for_property_or_business(tax_item.business)
	return citizens


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Get the contact citizens of a business, subbusiness or property
Return value: a list of citizens
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def get_contact_citizens_for_property_or_business(obj):
	citizens = []
	if isinstance(obj, Property):

		# check Asset_Ownership Table
		ownerships = obj.owners.all()
		if ownerships:
			for ownership in ownerships:
				if ownership.owner_citizen:
					citizens.append(ownership.owner_citizen)
				elif ownership.owner_business:
					business_ownerships = ownership.owner_business.owners.filter(date_ended__isnull = True)
					if business_ownerships:
						for business_ownership in business_ownerships:
							business_owner =  business_ownership.owner_citizen
							if business_owner and business_owner not in citizens:
								citizens.append(business_owner)
	elif isinstance(obj, (Business,SubBusiness)):
		business = None
		if isinstance(obj, Business):
			business = obj
		else:
			business = obj.business
			
		business_ownerships = business.owners.filter(date_ended__isnull = True)
		if business_ownerships:
			for business_ownership in business_ownerships:
				business_owner =  business_ownership.owner_citizen
				if business_owner and business_owner not in citizens:
					citizens.append(business_owner)
	return citizens


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Get the list of contact emails given a list of citizens
Return value: a list of emails
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def get_contact_emails(citizens):
	emails = []
	for citizen in citizens:
		if citizen.email:
			emails.append(citizen.email)
	return emails


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Get the list of contact phones given a list of citizens
Return value: a list of phone numbers
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def get_contact_phones(citizens):
	phones = []
	for citizen in citizens:
		if citizen.phone_1:
			phones.append(citizen.phone_1)
	return phones

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
This function is designed for log purpose

Return a dictionary including business, subbusiness, property,
as keys, and the values are decided by tax_item
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def get_log_dict_for_tax_item(tax_item):
	business = None
	subbusiness = None
	property = None
	if isinstance(tax_item, TradingLicenseTax):
		if tax_item.subbusiness:
			subbusiness = tax_item.subbusiness
			business = tax_item.subbusiness.business
		elif tax_item.business:
			business = tax_item.business
	elif isinstance(tax_item, (PropertyTaxItem,RentalIncomeTax)):
		property = tax_item.property
	elif isinstance(tax_item, Fee):
		if tax_item.fee_type == 'land_lease':
			property = tax_item.property
		elif (tax_item.fee_type == 'market' or tax_item.fee_type == 'cleaning'):
			if tax_item.subbusiness:
				subbusiness = tax_item.subbusiness
				business = tax_item.subbusiness.business
			elif tax_item.business:
				business = tax_item.business
	log_dict={}
	log_dict['business'] = business
	log_dict['subbusiness'] = subbusiness
	log_dict['property'] = property
	return log_dict




"""
return late fee dict including
1. interest
2. surchage
3. tax amount
4. total debt based on the above three
"""
def get_late_fee_details(tax_item):
	tax_type = get_tax_type_from_tax_item(tax_item)
	late_fee = calculateLateFee(tax_type,tax_item)
	if late_fee:
		if tax_item.amount:
			late_fee['due_amount'] = tax_item.amount
		else:
			late_fee['due_amount'] = 0
		late_fee['total'] = late_fee['due_amount'] + late_fee['interest'] + late_fee['surcharge']
	return late_fee


"""
Get capitalized fee or tax name for incomplete payment
"""
def get_tax_type_display_name(tax_type):
	if tax_type:
		tax_type_name = ''
		if tax_type == 'fixed_asset':
			tax_type_name = 'Fixed Asset Tax'
		elif tax_type == 'rental_income':
			tax_type_name = 'Rental Income Tax'
		elif tax_type == 'trading_license':
			tax_type_name = 'Trading License Tax'
		elif tax_type == 'land_lease_fee':
			tax_type_name = 'Land Lease Fee'
		elif tax_type == 'market_fee':
			tax_type_name = 'Market Fee'
		elif tax_type == 'cleaning_fee':
			tax_type_name = 'Cleaning Fee'
		elif tax_type == 'misc_fee':
			tax_type_name = 'Miscellaneous Fee'
		else:
			tax_type_name = tax_type
		return tax_type_name
	else:
		return 'N/A'

"""
Get reference for incomplete payment
"""

def get_reference_for_incomplete_payment(incomplete_payment, property_or_business = None):
	reference = {"message":"","period":""}
	if isinstance(property_or_business, Property):
		reference['message']  = "[UPI:" + property_or_business.getUPI() + "] " + property_or_business.getDisplayName()
		if incomplete_payment.period_from and incomplete_payment.period_to:
			reference['period'] = "From " + incomplete_payment.period_from.strftime('%d/%m/%Y') + " to " + incomplete_payment.period_to.strftime('%d/%m/%Y') 
	elif isinstance(property_or_business, Business):
		reference['message'] = "[TIN:" + property_or_business.tin + "] " + property_or_business.name
		if incomplete_payment.tax_type == 'cleaning_fee':
			if incomplete_payment.period_from:
				month_name = str(incomplete_payment.period_from.strftime('%B'))[:3]
				year = incomplete_payment.period_from.strftime('%Y')
				reference['message'] = reference['message'] + ' for ' + month_name + " " + str(year)
		elif incomplete_payment.tax_type == 'trading_license':
			if incomplete_payment.period_from and incomplete_payment.period_to:
				reference['message'] = reference['message'] + ' for the period from ' + str(incomplete_payment.period_from.strftime('%d/%m/%Y')) + ' to ' + str(incomplete_payment.period_from.strftime('%d/%m/%Y'))
			
			
	return reference


def add_extra_info_to_incomplete_payment_for_invoince(incomplete_payment):
	if incomplete_payment.tax_type:
		tax_type = incomplete_payment.tax_type
		incomplete_payment.tax_or_fee = get_tax_type_display_name(tax_type)
		if tax_type in ['fixed_asset', 'rental_income', 'land_lease_fee']:
			if incomplete_payment.district and incomplete_payment.sector and incomplete_payment.cell and incomplete_payment.village and incomplete_payment.parcel_id:
				try:
					int(incomplete_payment.parcel_id)
					properties = Property.objects.filter(parcel_id = incomplete_payment.parcel_id, village = incomplete_payment.village, sector =incomplete_payment.sector)
					if properties:
						property = properties[0]
						property.upi = property.getUPI()
						property.address = property.getDisplayName()
						incomplete_payment.property = property
						incomplete_payment.reference = get_reference_for_incomplete_payment(incomplete_payment, property)
				except:
					print ''

		elif tax_type in ['trading_license','market_fee','cleaning_fee']:
			if incomplete_payment.tin:
				business = Business.objects.filter(tin__iexact = incomplete_payment.tin)
				if business:
					business = business[0]
					subbusinesses = SubBusiness.objects.filter(business = business)
					if subbusinesses:
						branches = []
						for obj in subbusinesses:
							branches.append(obj)
						business.branches = branches
					incomplete_payment.business = business
					incomplete_payment.reference = get_reference_for_incomplete_payment(incomplete_payment, business)
		return incomplete_payment



def calc_interest(due_date, due_amount, surcharge_rate, surcharge_max, interest_rate, pay_amount=None, pay_date=None):

	if not pay_amount:
		pay_amount = due_amount

	if pay_amount >= due_amount:
		amount = due_amount # only pay interest on amount due
		#apply surcharge if final payment
		surcharge = (surcharge_rate * amount).quantize(Decimal('.01'))
		if surcharge > surcharge_max:
			surcharge = surcharge_max
	else: # only calculate interest on the payment amount, ie part payment
		amount = pay_amount
		surcharge = 0

	if not pay_date:
		pay_date = date.today()

	months_late = (pay_date.year - due_date.year ) * 12 + (pay_date.month - due_date.month)

	interest = (interest_rate * months_late * amount).quantize(Decimal('.01'))
	late_fee = interest + surcharge
	return late_fee, months_late, interest, surcharge, amount

