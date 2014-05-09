from django.http import Http404,HttpResponse, HttpResponseRedirect
from django.forms import model_to_dict
from datetime import *
from django.utils import timezone
from admin.Common import Common
import ast, pytz
from dev1.variables import *
from jtax.models import *
from property.mappers.PropertyMapper import PropertyMapper
from django.db.models import Sum
from django.db import connection
from citizen.models import *
from property.models import *
from citizen.models import Citizen
from  property.models import Property
from asset.models import Business
import dateutil.parser
from jtax.mappers.DeclaredValueMapper import DeclaredValueMapper
from property.mappers.OwnershipMapper import OwnershipMapper
from asset.models import Ownership as NewOwnership
import calendar
from django.db.models import Q,F
import json
from jtax.models import Setting

class TaxMapper:
	"""
	Calculate the base amount of tax or fee for an incomplete_payment
	return a float type (amount)
	"""
	@staticmethod
	def get_base_amount_for_incomplete_payment(incomplete_payment, extra_info = None):
		base_amount = 0
		
		if incomplete_payment.tax_type == 'cleaning_fee':
			business = incomplete_payment.business
			tax_setting = None
			if business.sector:
				tax_setting = TaxMapper.getTaxSetting('cleaning_fee', {'sector':business.sector})
			else:
				tax_setting = TaxMapper.getTaxSetting('cleaning_fee')
			base_amount = tax_setting['fee_matches'][business.area_type + '-' + business.business_type]
		elif incomplete_payment.tax_type == 'land_lease_fee':
			land_lease_rate = 0
			property = extra_info['property']
			if property.land_lease_type == 'Urban Area':
				land_lease_rate = 30
			elif property.land_lease_type == 'Trading Centre':
				land_lease_rate = 10
			elif property.land_lease_type == 'Rural Area':
				land_lease_rate = 5
			elif property.land_lease_type == 'Agriculture':
				land_lease_rate = 4000
			elif property.land_lease_type == 'Quarries Exploitation':
				land_lease_rate = 10
			if property.size_sqm:
				base_amount = land_lease_rate * property.size_sqm
			else:
				base_amount = land_lease_rate * property.size_hectare * 10000
			months = Common.num_of_months_between_dates(incomplete_payment.period_from, incomplete_payment.period_to)
			base_amount = int(int(base_amount) * months / 12)	
		
		elif incomplete_payment.tax_type == 'rental_income':
			rental_income = extra_info['rental_income']
			bank_interest_paid = extra_info['bank_interest_paid']
			taxable_amount = 0
			if bank_interest_paid == 0:
				taxable_amount = int(rental_income) * 0.5
			elif bank_interest_paid > 0:
				taxable_amount = int(rental_income) - int(rental_income) * 0.3 - int(bank_interest_paid)
			
			if taxable_amount >= 1000000:
				base_amount = (taxable_amount - 1000000) * 0.3 + (1000000-180000) * 0.2
			elif taxable_amount < 1000000 and taxable_amount >= 180000:
				base_amount = (taxable_amount-180000) * 0.2
		elif incomplete_payment.tax_type == 'fixed_asset':
			declared_value = extra_info['declared_value']
			# calculate 
			months = Common.num_of_months_between_dates(incomplete_payment.period_from, incomplete_payment.period_to)
			base_amount = int(int(declared_value) * 0.001 * months / 12)
		elif incomplete_payment.tax_type == 'trading_license':
			if incomplete_payment.business.vat_register and extra_info and extra_info.has_key('turnorver') and extra_info['turnorver']:
				turnover = int(extra_info['turnover'])
				if turnover <= 40000000:
					base_amount = 60000
				elif turnover <= 60000000:
					base_amount = 90000
				elif turnover <= 150000000:
					base_amount = 150000
				else:
					base_amount = 250000
			
				months = Common.num_of_months_between_dates(incomplete_payment.period_from, incomplete_payment.period_to)
				base_amount = int(int(base_amount) * months / 12)
			else:
				base_amount = incomplete_payment.paid_amount
		return int(base_amount)
	
	
	"""
	calculate the total late fee including interest and penalty for an incomplete payment
	return a float type (late fee amount)
	"""
	@staticmethod
	def get_late_fee_for_incomplete_payment(incomplete_payment, base_amount=None):		
		due_date = None
		
		late_fee = 0
		late_fee_interest = 0
		late_fee_surcharge = 0
		month_late = 0
		due_date = None
		feeSettings = None
		
		if incomplete_payment.tax_type == 'cleaning_fee' or incomplete_payment.tax_type == 'market_fee' :
			due_date = timezone.make_aware(datetime(incomplete_payment.period_from.year, incomplete_payment.period_from.month,5),timezone.get_default_timezone()).date()
			business = incomplete_payment.business
			if business.sector:
				feeSettings = TaxMapper.getTaxSetting('general_fee', {'sector':business.sector})
			else:
				feeSettings = TaxMapper.getTaxSetting('general_fee')
		elif incomplete_payment.tax_type in ('rental_income','fixed_asset'):
			due_date = timezone.make_aware(datetime(incomplete_payment.period_from.year+1,3,31),timezone.get_default_timezone()).date()
			feeSettings = TaxMapper.getTaxSetting('general_fee')
		elif incomplete_payment.tax_type == 'land_lease_fee':
			due_date = timezone.make_aware(datetime(incomplete_payment.period_from.year,12,31),timezone.get_default_timezone()).date()
			feeSettings = TaxMapper.getTaxSetting('general_fee')
			
		if due_date < incomplete_payment.paid_date:
			#get the late time in months
			month1 = incomplete_payment.paid_date.month
			month2 = due_date.month
			if( month2 > month1):
				month_late = (month1 - month2) + 12
			else:
				month_late = month1 - month2

			#even if 1 date late, round it to full month late
			if due_date.day < incomplete_payment.paid_date.day:
				month_late = month_late + 1
				
			if not base_amount:
				base_amount = TaxMapper.get_base_amount_for_incomplete_payment(incomplete_payment)
			late_fee_interest = (float(feeSettings['late_fee_interest_rate']) * month_late) * float(base_amount)
			late_fee_surcharge = float(feeSettings['late_fee_surcharge_rate']) * float(base_amount)
			if late_fee_surcharge > float(feeSettings["late_fee_surcharge_max"]):
				late_fee_surcharge = float(feeSettings["late_fee_surcharge_max"])
				
		late_fee = int(round(late_fee_interest,0)) + int(round(late_fee_surcharge,0))
		return int(late_fee)

	
	
	
	@staticmethod
	def getYearlyRevenueByConditions(conditions):
		years = conditions['years']
		tax_types = None
		
		if conditions.has_key('tax_types'):
			tax_types = conditions['tax_types']
		
		arrs = {}
		for year in years:
			revenue = {}
			for count in range(1,13):
				month_range = Common.get_month_time_range(int(year), count)
				month_name = month_range[0].strftime('%B') 
				revenue[month_name] = 0
				if tax_types and len(tax_types) > 0:
					if 'fixed_asset' in tax_types:
						revenue_obj = PayFixedAssetTax.objects.filter(paid_date__range=month_range,i_status__iexact = 'active')
						if conditions.has_key('cell') and conditions['cell']:
							revenue_obj = revenue_obj.filter(property_tax_item__property__cell = conditions['cell'])
						elif conditions.has_key('sector') and conditions['sector']:
							revenue_obj = revenue_obj.filter(property_tax_item__property__sector = conditions['sector'])
						elif conditions.has_key('district') and conditions['district']:
							revenue_obj = revenue_obj.filter(property_tax_item__property__sector__district = conditions['district'])
						revenue_obj = revenue_obj.aggregate(Sum('amount'))['amount__sum']
						if not revenue_obj:
							revenue_obj = 0
						revenue[month_name] = revenue[month_name] + revenue_obj 
					if 'rental_income' in tax_types:
						revenue_obj = PayRentalIncomeTax.objects.filter(paid_date__range=month_range,i_status__iexact = 'active')
						if conditions.has_key('cell') and conditions['cell']:
							revenue_obj = revenue_obj.filter(rental_income_tax__property__cell = conditions['cell'])
						elif conditions.has_key('sector') and conditions['sector']:
							revenue_obj = revenue_obj.filter(rental_income_tax__property__sector = conditions['sector'])
						elif conditions.has_key('district') and conditions['district']:
							revenue_obj = revenue_obj.filter(rental_income_tax__property__sector__district = conditions['district'])
						revenue_obj = revenue_obj.aggregate(Sum('amount'))['amount__sum']
						if not revenue_obj:
							revenue_obj = 0
						revenue[month_name] = revenue[month_name] + revenue_obj
					if 'trading_license' in tax_types:
						revenue_obj = PayTradingLicenseTax.objects.filter(paid_date__range=month_range,i_status__iexact = 'active')
						if conditions.has_key('cell') and conditions['cell']:
							revenue_obj = revenue_obj.filter(Q(trading_license_tax__business__cell = conditions['cell'])|Q(trading_license_tax__subbusiness__cell = conditions['cell']))
						elif conditions.has_key('sector') and conditions['sector']:
							revenue_obj = revenue_obj.filter(Q(trading_license_tax__business__sector = conditions['sector'])|Q(trading_license_tax__subbusiness__sector = conditions['sector']))
						elif conditions.has_key('district') and conditions['district']:
							revenue_obj = revenue_obj.filter((Q(trading_license_tax__business__sector__district = conditions['district'])|Q(trading_license_tax__subbusiness__sector__district = conditions['district'])))
						revenue_obj = revenue_obj.aggregate(Sum('amount'))['amount__sum']
						if not revenue_obj:
							revenue_obj = 0
						revenue[month_name] = revenue[month_name] + revenue_obj
					if 'land_lease_fee' in tax_types:
						revenue_obj = PayFee.objects.filter(paid_date__range=month_range,i_status__iexact = 'active', fee__fee_type__iexact = 'land_lease')
						if conditions.has_key('cell') and conditions['cell']:
							revenue_obj = revenue_obj.filter(fee__property__cell = conditions['cell'])
						elif conditions.has_key('sector') and conditions['sector']:
							revenue_obj = revenue_obj.filter(fee__property__sector = conditions['sector'])
						elif conditions.has_key('district') and conditions['district']:
							revenue_obj = revenue_obj.filter(fee__property__sector__district = conditions['district'])
						revenue_obj = revenue_obj.aggregate(Sum('amount'))['amount__sum']
						if not revenue_obj:
							revenue_obj = 0
						revenue[month_name] = revenue[month_name] + revenue_obj
					if 'market_fee' in tax_types:
						continue
					if 'cleaning_fee' in tax_types:
						revenue_obj = PayFee.objects.filter(paid_date__range=month_range,i_status__iexact = 'active', fee__fee_type__iexact = 'cleaning')
						if conditions.has_key('cell') and conditions['cell']:
							revenue_obj = revenue_obj.filter(Q(fee__business__cell = conditions['cell'])|Q(fee__subbusiness__cell = conditions['cell']))
						elif conditions.has_key('sector') and conditions['sector']:
							revenue_obj = revenue_obj.filter(Q(fee__business__sector = conditions['sector'])|Q(fee__subbusiness__sector = conditions['sector']))
						elif conditions.has_key('district') and conditions['district']:
							revenue_obj = revenue_obj.filter(Q(fee__business__sector__district = conditions['district'])|Q(fee__subbusiness__sector__district = conditions['district']))
						revenue_obj = revenue_obj.aggregate(Sum('amount'))['amount__sum']
						if not revenue_obj:
							revenue_obj = 0
						revenue[month_name] = revenue[month_name] + revenue_obj
			arr = []
			if revenue:
				arr.append(('January',revenue['January']))
				arr.append(('February',revenue['February']))
				arr.append(('March',revenue['March']))
				arr.append(('April',revenue['April']))	
				arr.append(('May',revenue['May']))
				arr.append(('June',revenue['June']))
				arr.append(('July',revenue['July']))
				arr.append(('August',revenue['August']))
				arr.append(('September',revenue['September']))
				arr.append(('October',revenue['October']))
				arr.append(('November',revenue['November']))
				arr.append(('December',revenue['December']))
			arrs[year]=arr
		return arrs	

	"""
		generate taxes for citizen / business / property if required
		@params:
		model: Model of citizen / business / property
		request: current request obj
	"""


	@staticmethod
	def generateTaxes(model, request):
		type1 = type(model)
		today = timezone.make_aware(datetime.combine(datetime.today(), time(0,0)), timezone.get_default_timezone())
		now = timezone.make_aware(datetime.now(), timezone.get_default_timezone())
		current_year = str(today.year)
		year_start = timezone.make_aware(dateutil.parser.parse(current_year + '-01-01 00:00:00'), timezone.get_default_timezone())
		year_end = timezone.make_aware(dateutil.parser.parse(current_year + '-12-31 23:59:59'), timezone.get_default_timezone())
		staff_id = request.session.get('user').id
		property_ids = []
		business_ids = []

		rental_year_start = timezone.make_aware(dateutil.parser.parse(str(today.year - 1) + '-01-01 00:00:00'), timezone.get_default_timezone())
		rental_year_end = timezone.make_aware(dateutil.parser.parse(str(today.year - 1) + '-12-31 23:59:59'), timezone.get_default_timezone())

		if type1 == Citizen:
			#check Fixed Asset Tax / Rental Asset Tax if there is a property belong to this citizen
			ownership_objs= OwnershipMapper.getOwnershipsByCitizenNativeId(model.id)
			if len(ownership_objs)>0:
				for ownership in ownership_objs:
					property_id = ownership.asset_property.id
					if property_id not in property_ids:
						property_ids.append(property_id)
						property = ownership.asset_property
						# TaxMapper.generatePropertyTaxes(property, now, current_year,year_start,year_end, rental_year_start, rental_year_end, staff_id)

			request.session['property_ids'] = property_ids

			#start checking trading license tax, check if there is business belong to this citizen
			ownerships = NewOwnership.objects.filter(owner_citizen=model,asset_business__isnull=False,i_status__exact='active')
			if ownerships:
				for ownership in ownerships:
					#if there is no Trading License Tax Item for this business in the current year, add a new Trading License Tax
					business = ownership.asset_business
					if business.id not in business_ids:
						business_ids.append(business.id)
						# TaxMapper.generateBusinessTaxes(business, now, current_year, year_start, year_end, staff_id)

			request.session['business_ids'] = business_ids


		elif type1 == Business:
			#check Fixed Asset Tax / Rental Asset Tax if there is a property belong to this business
			ownership_objs= NewOwnership.objects.filter(owner_business=model,asset_property__isnull=False,i_status__exact='active')
			if len(ownership_objs)>0:
				for ownership in ownership_objs:
					property = ownership.asset_property
					property_id = property.id
					property_ids.append(property_id)
					# TaxMapper.generatePropertyTaxes(property, now, current_year,year_start,year_end,rental_year_start, rental_year_end, staff_id)
			request.session['property_ids'] = property_ids

			#if there is no Trading License Tax Item for this business in the current year, add a new Trading License Tax
			business = model
			business_ids.append(business.id)
			# TaxMapper.generateBusinessTaxes(business, now, current_year, year_start, year_end, staff_id)
			request.session['business_ids'] = business_ids



		elif type1 == Property:
			#check Fixed Asset Tax / Rental Asset Tax belong to this property
			property = model
			property_id = property.id
			property_ids.append(property_id)
			# TaxMapper.generatePropertyTaxes(property, now, current_year,year_start,year_end,rental_year_start, rental_year_end, staff_id)

			request.session['property_ids'] = property_ids
			request.session['business_ids'] = []

	"""
		generate property taxes & fees(Fixed Asset, Rental Income, Land Lease Fee)
	"""
	@staticmethod
	def generatePropertyTaxes(property, now, current_year, year_start, year_end,rental_year_start, rental_year_end, staff_id, logs=None):
		plot_id = property.plot_id
		settingFilters = {}
		if property.sector and property.sector != None:
			settingFilters['sector'] = property.sector
			if property.sector.district:
				settingFilters['district'] = property.sector.district

		#a property can only have either Fixed Asset Tax or Land Lease Fee
		if property.is_land_lease:
			#disable unpaid Fixed Asset and Rental Income for the current year
			fixed_asset_taxes = PropertyTaxItem.objects.filter(is_paid=False,plot_id__exact=plot_id,period_from__gte=year_start,period_from__lte=year_end,i_status='active')
			if fixed_asset_taxes:
				for i in fixed_asset_taxes:
					i.i_status = 'inactive'
					i.save()

			#also do a check if this property is Tax Exempt 
			if property.is_tax_exempt:
				# check whether it exists unpaid landlease status before, deactive them
				land_lease_fees = Fee.objects.filter(is_paid=False,fee_type='land_lease',property=property,period_from=year_start,period_to=year_end,i_status='active')
				if land_lease_fees:
					for i in land_lease_fees:
						i.i_status = 'inactive'
						i.save()
			else:
				#if this property is land lease and there is no land lease fee record for this current year, add new and lease record
				#leave tax amount to be calculated dynamically when pay tax
				tax_amount = None
				#tax_amount = TaxMapper.calculateTax('land_lease',property,settingFilters)
				land_lease_fees = Fee.objects.filter(fee_type='land_lease',property=property,period_from__gte=year_start,period_to__lte=year_end,i_status='active')
				if land_lease_fees.count() == 0:
					fee = Fee(amount=tax_amount,remaining_amount=tax_amount,fee_type='land_lease',property=property,currency='RWF',period_from=year_start,period_to=year_end,due_date=year_end,date_time=now,is_paid=False,staff_id=staff_id)
					fee.save()
					if logs:
						logs['land_lease_fee'].append(fee.id)
				"""
				elif land_lease_fees.filter(submit_details__icontains='installment').count() == 4:
					#double check if there is overdue payment installments, if there is then deactivate all unpaid installments
					#and create a new land lease fee that force user to pay all remaining amount in 1 payment
					unpaid_overdue_installments = land_lease_fees.filter(is_paid=False,due_date__lte=now,submit_details__icontains='installment')
					if unpaid_overdue_installments.count() > 0:
						remaining_amount = 0
						unpaid_installments = land_lease_fees.filter(is_paid=False,submit_details__icontains='"installment"')
						paid_installments = land_lease_fees.filter(is_paid=True,submit_details__icontains='"installment"')
						paidIds = []
						for i in paid_installments:
							paidIds.append(i.id)
						for i in unpaid_installments:
							remaining_amount = remaining_amount + i.remaining_amount
						submit_details = json.dumps({"overdue_installment":True,"paid_installments":paidIds})
						fee = Fee(submit_date=now,submit_details=submit_details,amount=tax_amount,remaining_amount=remaining_amount,fee_type='land_lease',property=property,currency='RWF',period_from=year_start,period_to=year_end,due_date=year_end,date_time=now,is_paid=False,staff_id=staff_id)
						fee.save()
						if logs:
							logs['land_lease_fee'].append(fee.id)

						#deactive those unpaid installments
						unpaid_installments.update(i_status='inactive')
				"""		

		else:
			# check whether it exists unpaid landlease status before, deactive them
			land_lease_fees = Fee.objects.filter(is_paid=False,fee_type='land_lease',property=property,period_from=year_start,period_to=year_end,i_status='active')
			if land_lease_fees:
				for i in land_lease_fees:
					i.i_status = 'inactive'
					i.save()

			#if there is no PropertyTaxItem for this citizen in the current year, add a new PropertyTaxItem
			if PropertyTaxItem.objects.filter(amount__isnull=False,property=property,period_from__gte=year_start,period_to__lte=year_end,i_status='active').count() == 0:
				fixedAssetSettings = TaxMapper.getTaxSetting('fixed_asset_tax',settingFilters)
				fixed_asset_due_date = current_year + '-' + fixedAssetSettings['due_date']
				tax_items = PropertyTaxItem.objects.filter(property=property, period_from__gte=year_start,period_to__lte=year_end,i_status='active')

				#if there is already an tax item with undefined amount, update that tax item
				if tax_items:
					tax = tax_items[0]
					tax.property = property
					tax.date_time=now
				#otherwise create new tax item
				elif not tax_items:
					tax = PropertyTaxItem(plot_id=plot_id,currency='RWF', property = property, period_from=year_start,period_to=year_end,due_date=fixed_asset_due_date,date_time=now,is_paid=False,staff_id=staff_id)

				#leave tax amount to be calculated dynamically when pay tax
				tax_amount = TaxMapper.calculateTax(tax)

				if tax_amount != None:
					tax.amount = round(tax_amount)
					tax.remaining_amount = round(tax_amount)

				#if there is no tax amount due for this tax item, complete the payment automatically
				if tax_amount == 0:
					staff = None
					if staff_id:
						try:
							staff = PMUser.objects.get(pk=staff_id)
						except Exception:
							staff = None

					tax.is_paid = True
					tax.save()

					payment = PayFixedAssetTax(property_tax_item=tax,staff=staff, amount=0, receipt_no = '', bank = '', note='Declared value under taxable threadhold, taxable amount is 0.',paid_date=now)
					payment.save()
				else:
					tax.save()

				if logs:
					logs['fixed_asset_tax'].append(tax.id)

		#if this property is leasing and there is no RentalIncomeTax for this citizen in the current year, add new
		if property.is_leasing and RentalIncomeTax.objects.filter(property=property,period_from__gte=rental_year_start,period_from__lte=rental_year_end,i_status='active').count() == 0:
			rentalIncomeSettings = TaxMapper.getTaxSetting('rental_income_tax', settingFilters)
			rental_income_due_date = current_year + '-' + rentalIncomeSettings['due_date']
			tax = RentalIncomeTax(plot_id=plot_id,property=property,currency='RWF',period_from=rental_year_start,period_to=rental_year_end,due_date=rental_income_due_date,date_time=now,is_paid=False)
			tax.save()
			if logs:
				logs['rental_income_tax'].append(tax.id)
		#if property is not leasing, deactive all the unpaid rental income tax item for it
		elif not property.is_leasing:
			rental_income_taxes = RentalIncomeTax.objects.filter(is_paid=False,property=property,period_from__gte=rental_year_start,period_from__lte=rental_year_end,i_status='active')
			if rental_income_taxes:
				for i in rental_income_taxes:
					i.i_status = 'inactive'
					i.save()



	"""
		generate business taxes & fees(Trading Licence, Cleaning Fee)
	"""
	@staticmethod
	def generateBusinessTaxes(business, now, current_year, year_start, year_end, staff_id, logs = None):
		settingFilters = {}
		if business.sector and business.sector != None:
			settingFilters['sector'] = business.sector
			if business.sector.district:
				settingFilters['district'] = business.sector.district

		#KLUDGE - currently the due date for Trading license tax is the same as rental income tax
		rentalIncomeSettings = TaxMapper.getTaxSetting('rental_income_tax', settingFilters)
		due_date = current_year + '-' + rentalIncomeSettings['due_date']

		# generate trading license fee for Business if required ( check with business start date)
		if not business.date_started or business.date_started < datetime.date(year_end):
			if TradingLicenseTax.objects.filter(business=business,period_from__range = [year_start, year_end], period_to__range=[year_start, year_end],i_status='active').count() == 0:
				if business.date_started and business.date_started > datetime.date(year_start):
					period_from = business.date_started
				else:
					period_from = year_start

				tax = TradingLicenseTax(due_date=due_date,business=business,currency='RWF',period_from=period_from,period_to=year_end,date_time=now,is_paid=False,staff_id=staff_id)
				tax.save()
				if logs:
					logs['trading_license_tax'].append(tax.id)
			
			# generate trading license fee for Subbusiness
			subbusinesses = SubBusiness.objects.filter(business = business,i_status='active')
			if len(subbusinesses) > 0:
				for subbusiness in subbusinesses:
					if TradingLicenseTax.objects.filter(subbusiness=subbusiness,period_from__range = [year_start, year_end], period_to__range=[year_start, year_end],i_status='active').count() == 0:
						if business.date_started and business.date_started > datetime.date(year_start):
							period_from = business.date_started
						else:
							period_from = year_start

						tax = TradingLicenseTax(due_date=due_date,subbusiness=subbusiness,currency='RWF',period_from=period_from,period_to=year_end,date_time=now,is_paid=False,staff_id=staff_id)
						tax.save()
						if logs:
							logs['trading_license_tax'].append(tax.id)


			#if there is no Cleaning fee for this business in the current year, add monthly Cleaning fee, also exclude the business with no cleaning_fee_amount (No premise)
			if Fee.objects.filter(fee_type='cleaning',business=business,period_from__gte=year_start,period_to__lte=year_end,i_status='active').count() == 0:
				feeSettings = TaxMapper.getTaxSetting('general_fee', settingFilters)

				#only insert new monthly fees record from the business start date
				months = []
				if not business.date_started or (business.date_started and business.date_started < datetime.date(year_start)):
					i = 1
				else:
					i = business.date_started.month
				while i < 13:
					months.append(i)
					i = i + 1
				for i in months:
					period_month_from = timezone.make_aware(datetime(int(current_year), int(i), 1, 0,0,0), timezone.get_default_timezone())
					period_month_to = timezone.make_aware(datetime(int(current_year), int(i),  calendar.mdays[int(i)] , 23,59,59), timezone.get_default_timezone())
					#due date is located on the next month

					if int(i) == 12:
						due_date = timezone.make_aware(datetime(int(current_year) + 1, 1,  int(feeSettings["monthly_due_date"])), timezone.get_default_timezone())
					else:
						due_date = timezone.make_aware(datetime(int(current_year), int(i) + 1,  int(feeSettings["monthly_due_date"])), timezone.get_default_timezone())

					fee = Fee(fee_type='cleaning',business = business,currency='RWF',period_from=period_month_from,period_to=period_month_to,due_date=due_date,date_time=now,is_paid=False,staff_id=staff_id)
					fee.save()
					if logs:
						logs['cleaning_fee'].append(fee.id)

			# generate cleaning fees for sub businesses
			if subbusinesses and len(subbusinesses) > 0:
				for subbusiness in subbusinesses:
					if Fee.objects.filter(fee_type='cleaning',subbusiness=subbusiness,period_from__gte=year_start,period_to__lte=year_end,i_status='active').count() == 0:
						feeSettings = TaxMapper.getTaxSetting('general_fee', settingFilters)
						#only insert new monthly fees record from the business start date
						months = []
						if not business.date_started or (business.date_started and business.date_started < datetime.date(year_start)):
							i = 1
						else:
							i = business.date_started.month
						while i < 13:
							months.append(i)
							i = i + 1
						for i in months:
							period_month_from = timezone.make_aware(datetime(int(current_year), int(i), 1, 0,0,0), timezone.get_default_timezone())
							period_month_to = timezone.make_aware(datetime(int(current_year), int(i),  calendar.mdays[int(i)] , 23,59,59), timezone.get_default_timezone())
							#due date is located on the next month
							if int(i) == 12:
								due_date = timezone.make_aware(datetime(int(current_year) + 1, 1,  int(feeSettings["monthly_due_date"])), timezone.get_default_timezone())
							else:
								due_date = timezone.make_aware(datetime(int(current_year), int(i) + 1,  int(feeSettings["monthly_due_date"])), timezone.get_default_timezone())
							fee = Fee(fee_type='cleaning',subbusiness = subbusiness,currency='RWF',period_from=period_month_from,period_to=period_month_to,due_date=due_date,date_time=now,is_paid=False,staff_id=staff_id)
							fee.save()
							if logs:
								logs['cleaning_fee'].append(fee.id)

			#start generate market fees
			#if there is no Market fee for this business in the current year, add monthly Market fees
			if Fee.objects.filter(fee_type='market',business=business,period_from__gte=year_start,period_to__lte=year_end,i_status='active').count() == 0:
				feeSettings = TaxMapper.getTaxSetting('general_fee', settingFilters)


				#only insert new monthly fees record from the business start date
				months = []
				if not business.date_started or (business.date_started and business.date_started < datetime.date(year_start)):
					i = 1
				else:
					i = business.date_started.month
				while i < 13:
					months.append(i)
					i = i + 1
				for i in months:
					period_month_from = timezone.make_aware(datetime(int(current_year), int(i), 1, 0,0,0), timezone.get_default_timezone())
					period_month_to = timezone.make_aware(datetime(int(current_year), int(i),  calendar.mdays[int(i)] , 23,59,59), timezone.get_default_timezone())
					#due date is located on the next month

					if int(i) == 12:
						due_date = timezone.make_aware(datetime(int(current_year) + 1, 1,  int(feeSettings["monthly_due_date"])), timezone.get_default_timezone())
					else:
						due_date = timezone.make_aware(datetime(int(current_year), int(i) + 1,  int(feeSettings["monthly_due_date"])), timezone.get_default_timezone())

					fee = Fee(fee_type='market',business = business,currency='RWF',period_from=period_month_from,period_to=period_month_to,due_date=due_date,date_time=now,is_paid=False,staff_id=staff_id)
					fee.save()
					if logs:
						logs['market_fee'].append(fee.id)

			# generate market fees for sub businesses
			if subbusinesses and len(subbusinesses) > 0:
				for subbusiness in subbusinesses:
					if Fee.objects.filter(fee_type='market',subbusiness=subbusiness,period_from__gte=year_start,period_to__lte=year_end,i_status='active').count() == 0:
						feeSettings = TaxMapper.getTaxSetting('general_fee', settingFilters)
						#only insert new monthly fees record from the business start date
						months = []
						if not business.date_started or (business.date_started and business.date_started < datetime.date(year_start)):
							i = 1
						else:
							i = business.date_started.month
						while i < 13:
							months.append(i)
							i = i + 1
						for i in months:
							period_month_from = timezone.make_aware(datetime(int(current_year), int(i), 1, 0,0,0), timezone.get_default_timezone())
							period_month_to = timezone.make_aware(datetime(int(current_year), int(i),  calendar.mdays[int(i)] , 23,59,59), timezone.get_default_timezone())
							#due date is located on the next month
							if int(i) == 12:
								due_date = timezone.make_aware(datetime(int(current_year) + 1, 1,  int(feeSettings["monthly_due_date"])), timezone.get_default_timezone())
							else:
								due_date = timezone.make_aware(datetime(int(current_year), int(i) + 1,  int(feeSettings["monthly_due_date"])), timezone.get_default_timezone())
							fee = Fee(fee_type='market',subbusiness = subbusiness,currency='RWF',period_from=period_month_from,period_to=period_month_to,due_date=due_date,date_time=now,is_paid=False,staff_id=staff_id)
							fee.save()
							if logs:
								logs['market_fee'].append(fee.id)





	"""
		fetch the tax setting saved in DB
		@params:
		model: Model of citizen / business / property
		request: current request obj
	"""
	@staticmethod
	def getTaxSetting(tax_name, filterOptions = None,setting_name = None,valid_from = None, valid_to = None):

		settings = None
		if valid_from == None:
			valid_from = date.today()
		kwargs = {'i_status__exact':'active','tax_fee_name__exact':tax_name,'valid_from__lte':valid_from}

		if filterOptions:
			for k,v in filterOptions.iteritems():
				kwargs[k] = v
			settings = Setting.objects.filter(**kwargs)
		#if can't find settings for sectors, apply district settings, otherwise use default settings
		if not settings and kwargs.has_key('district') and kwargs.has_key('sector'):
			settings = Setting.objects.filter(i_status='active',tax_fee_name=tax_name,valid_from__lte=valid_from,district=kwargs['district'])
		if not settings:
			settings = Setting.objects.filter(i_status='active',tax_fee_name=tax_name,valid_from__lte=valid_from,council=None, district=None, sector=None)

		if valid_to:
			settings = settings.filter(valid_to__gte=valid_to)

		#order the settings to always use the latest valid setting
		settings = settings.order_by('valid_from','id')

		if setting_name != None:
			settings.filter(setting_name=setting_name).order_by('valid_from','id')
			if settings:
				if len(settings) > 1:
					list = {}
					for i in settings:
						list[i.sub_type] = i.value
					return list
				else:
					return settings[0].value
			else:
				raise Http404("Invalid Tax Setting called " + str(tax_name) + " - " + str(setting_name))

		elif settings:
			list = {}
			for i in settings:
				if i.sub_type == "":
					list[i.setting_name] = i.value
				else:
					if list.has_key(i.setting_name):
						list[i.setting_name][i.sub_type] = i.value
					else:
						list[i.setting_name] = {i.sub_type:i.value}

			return list

		else:
			raise Http404("Invalid Tax Setting called " + str(tax_name) + " - " + str(setting_name))


	"""
		fetch the list of tax setting valid ranges within a period
		@params:
		model: Model of citizen / business / property
		request: current request obj
	"""
	@staticmethod
	def getTaxChangeList(tax_name,period_from,period_to,filterOptions = None,setting_name = None):

		kwargs = {'i_status__exact':'active','tax_fee_name__exact':tax_name}
		kwargs_with_filter = {'i_status__exact':'active','tax_fee_name__exact':tax_name}
		if filterOptions:
			for k,v in filterOptions.iteritems():
				kwargs_with_filter[k] = v

			settings = Setting.objects.filter(**kwargs_with_filter).filter(Q(valid_from__gte=period_from,valid_from__lte=period_to)|Q(valid_from__lte=period_from,valid_to__gte=period_from)|Q(valid_to__isnull=True,valid_from__gte=period_from,valid_from__lte=period_to))

		#if can't find settings for sectors, apply district settings, otherwise use default settings
		if not settings and kwargs.has_key('district') and kwargs.has_key('sector'):
			del kwargs_with_filter['sector']
			settings = Setting.objects.filter(**kwargs_with_filter).filter(Q(valid_from__gte=period_from,valid_from__lte=period_to)|Q(valid_from__lte=period_from,valid_to__gte=period_from)|Q(valid_to__isnull=True,valid_from__gte=period_from,valid_from__lte=period_to))
		if not settings:
			settings = Setting.objects.filter(**kwargs).filter(Q(valid_from__gte=period_from,valid_from__lte=period_to)|Q(valid_from__lte=period_from,valid_to__gte=period_from)|Q(valid_to__isnull=True,valid_from__gte=period_from,valid_from__lte=period_to),district=None,sector=None,)
		
		settings = settings.distinct('valid_from','valid_to').order_by('-valid_from')
		#return valid date list
		matches = {}
		if settings:
			for i in settings:
				if not matches.has_key(i.valid_from) or matches[i.valid_from] == None:
					matches[i.valid_from] = i.valid_to

		list = []
		if matches:
			#sort the matches by date
			keylist = matches.keys()
			keylist.sort()
			for key in keylist:
				list.append({'valid_from':key,'valid_to':matches[key]})

		return list


	"""
		calculate the tax amount
		@params:
		tax: Tax Item obj
		@return: <int> amount
	"""
	
	@staticmethod
	def calculateTax(tax):
		return tax.amount

	"""
		update taxes on details changes
		@params:
		model: Model of citizen / business / property
		request: current request obj
	"""
	@staticmethod
	def updateTaxesOnDetailsChanged(type, id, update_all=False):

		if type == 'business':
			businesses = Business.objects.filter(pk=id)
			business = businesses[0]
			settingFilters = {}
			if business.sector and business.sector != None:
				settingFilters['sector'] = business.sector
				if business.sector.district:
					settingFilters['district'] = business.sector.district

			#calculate the cleaning fee amount for this business
			cleaning_fee_amount = ''
			if business.area_type and business.area_type != '' and business.business_type and business.business_type != '':
				fee_matches = TaxMapper.getTaxSetting('cleaning_fee',settingFilters,'fee_matches')
				match = business.area_type + '-' + business.business_type

				for type,rate in fee_matches.iteritems():
					if type == match:
						cleaning_fee_amount = rate

			if cleaning_fee_amount != '':
				today = timezone.make_aware(datetime.combine(datetime.today(), time(0,0)), timezone.get_default_timezone())
				current_year = str(today.year)
				year_start = timezone.make_aware(dateutil.parser.parse(current_year + '-01-01 00:00:00'), timezone.get_default_timezone())
				year_end = timezone.make_aware(dateutil.parser.parse(current_year + '-12-31 23:59:59'), timezone.get_default_timezone())
				kwargs = {'business__exact':business,'is_paid__exact':False,'i_status__exact':'active','fee_type__exact':'cleaning','period_from__gte':year_start,'period_to__lte':year_end}

				if not update_all:
					kwargs['period_to__gte'] = today

				fees = Fee.objects.filter(Q(remaining_amount__exact=F('amount'))|Q(amount__isnull=True),**kwargs)

				if fees:
					for i in fees:
						i.amount = cleaning_fee_amount
						i.remaining_amount = cleaning_fee_amount
						i.save()
			
				# update cleaning fees for sub businesses
				subbusinesses = SubBusiness.objects.filter(business = business)
				if subbusinesses and len(subbusinesses) > 0:
					del kwargs['business__exact']
					kwargs['subbusiness__in'] = subbusinesses
					fees = Fee.objects.filter(Q(remaining_amount__exact=F('amount'))|Q(amount__isnull=True),**kwargs)
					if fees:
						for i in fees:
							i.amount = cleaning_fee_amount
							i.remaining_amount = cleaning_fee_amount
							i.save()
			

	"""
		get tax name
		@params:
		tax: The tax object
	"""
	@staticmethod
	def getTaxName(tax):
		name = ''
		if type(tax) is PropertyTaxItem:
			name = 'Fixed Asset Tax ' + str(tax.due_date.year)
		elif type(tax) is RentalIncomeTax:
			name = 'Rental Income Tax ' + str(tax.due_date.year)
		elif type(tax) is TradingLicenseTax:
			name = 'Trading License Tax'
			if tax.due_date:
				name = name + str(tax.due_date.year)
		elif type(tax) is MiscellaneousFee:
			name = '' + str(tax.due_date.year)
		elif type(tax) is Fee:
			if tax.fee_type == 'cleaning' or tax.fee_type == 'market':
				tax_name =  tax.fee_type.replace('_',' ').title() + ' Fee for ' + Common.localizeDate(tax.period_from).strftime('%b %Y')
			else:
				tax_name =  tax.fee_type.replace('_',' ').title() + ' Fee for '+ str(tax.period_from.year)

		return name

	
	@staticmethod
	def generateInstallments(tax):

		if type(tax.period_from) is datetime:
			date_from = tax.period_from.astimezone(timezone.get_default_timezone()).date()

		installments = Installment.previewInstallments(tax.amount, date_from)
		for due_date, amount in installments.iteritems():
			if type(tax) is Fee:
				Installment.objects.create(fee=tax, amount=amount, paid=0, due=due_date)
			elif type(tax) is RentalIncomeTax:
				Installment.objects.create(rentalIncomeTax=tax, amount=amount, paid=0, due=due_date)
			elif type(tax) is TradingLicenseTax:
				Installment.objects.create(tradingLicenseTax=tax, amount=amount, paid=0, due=due_date)
			elif type(tax) is PropertyTaxItem:
				Installment.objects.create(propertyTaxItem=tax, amount=amount, paid=0, due=due_date)
		return tax.installments.all()

	@staticmethod
	def pay_installment(tax, amount, paid_on=None):
		installments = tax.installments.filter(paid__lt=F('amount'))
		if type(tax) is PropertyTaxItem:
			installments = installments.filter(propertyTaxItem=tax)

		elif type(tax) is RentalIncomeTax:
			installments = installments.filter(rentalIncomeTax=tax)

		elif type(tax) is TradingLicenseTax:
			installments = installments.filter(tradingLicenseTax=tax)

		elif type(tax) is Fee:
			installments = installments.filter(fee=tax)

		installments = installments.order_by('due')
		paid_on = paid_on or date.today()
		for installment in installments:
			unpaid = installment.amount - installment.paid
			if amount <= unpaid:
				installment.paid += amount
				installment.paid_on = paid_on
				installment.save()
				break
			else:
				installment.paid = installment.amount
				installment.paid_on = paid_on
				installment.save()
				amount -= unpaid


	@staticmethod
	def next_outstanding_installment(tax):
		installments = Installment.objects.filter(paid__lt=F('amount'))

		if type(tax) is PropertyTaxItem:
			installments = installments.filter(propertyTaxItem=tax)

		elif type(tax) is RentalIncomeTax:
			installments = installments.filter(rentalIncomeTax=tax)

		elif type(tax) is TradingLicenseTax:
			installments = installments.filter(tradingLicenseTax=tax)

		elif type(tax) is Fee:
			installments = installments.filter(fee=tax)

		installments = installments.order_by('due')

		if installments:
			return installments[0]
		else:
			return None

	@staticmethod
	def getSettingList(conditions = None,regex='',limit=None):
		today=datetime.now().date()
		items = []
# 		print conditions['district']
# 		print conditions['sector']
# 		print conditions['cell']
# 		print conditions['village']
		items= Setting.objects.filter(i_status="active", tax_fee_name__regex=regex)
		if conditions.has_key('district'):
			replaces = items.filter(district = conditions['district'])
			if replaces:
				items=replaces
		if conditions.has_key('sector'):
			replaces = items.filter(sector = conditions['sector'])
			if replaces:
				items=replaces
		if conditions.has_key('cell'):
			replaces = items.filter(cell = conditions['cell'])
			if replaces:
				items=replaces
		if conditions.has_key('village'):
			replaces = items.filter(village=conditions['village'])
			if replaces:
				items=replaces
		items=items.filter(Q(valid_from__lte=datetime.today())|Q(valid_to__gte=datetime.today())).order_by("valid_from","tax_fee_name","setting_name","sub_type")
		return items
		
	@staticmethod
	def getFeeSettingList(conditions = None,limit=None):
		return TaxMapper.getSettingList(conditions,regex='(fee)+$')
	
	@staticmethod
	def getTaxSettingList(conditions = None,limit=None):
		return TaxMapper.getSettingList(conditions,regex='(tax)+$')
	