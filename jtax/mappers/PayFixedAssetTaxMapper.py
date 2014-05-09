from django.forms import model_to_dict
from datetime import datetime
from django.utils import timezone
from admin.Common import Common
import ast, pytz
from jtax.models import *
from property.mappers.PropertyMapper import PropertyMapper
from dev1.variables import *
from django.db.models import Sum
from django.db import connection
from citizen.models import *
from property.models import *
from asset.models import Ownership
from jtax.mappers.PaymentMapper import PaymentMapper



class PayFixedAssetTaxMapper:

	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get last 12-month paid tax and unpaid tax
	""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""" 
	
	@staticmethod
	def getTaxPayers(conditions=None):
		ownerships = Ownership.objects.filter(i_status='active')
		if conditions:
			if conditions.has_key("district"):
				ownerships = ownerships.filter(asset_property__sector__district = conditions['district'])
			if conditions.has_key("sector"):
				ownerships = ownerships.filter(asset_property__sector = conditions['sector'])
			if conditions.has_key("cell"):
				ownerships = ownerships.filter(asset_property__cell = conditions['cell'])

		ownerships = ownerships.select_related('owner_citizen','asset_property')
		citizens = []
		if ownerships and len(ownerships) > 0:
			for ownership in ownerships:				
				citizen = ownership.owner_citizen
				citizen.tax_type = 'Fixed asset tax'
				citizen.upi = ownership.asset_property.getUPI()
				citizen.property_id = ownership.asset_property.id
				citizens.append(citizen)

		if len(citizens) == 0:
			return None 
		else:
			return citizens
		
	@staticmethod
	def getFixedAssetTaxPaidAndUnpaid(conditions=None,group='year'):
		result = []
		year = datetime.now().year
		if conditions.has_key('calendar_year'):
			year = int(conditions['calendar_year'])

		if group == 'month':
			for count in range(1,13):
				#month_range = Common.get_previous_month_time_range(count)
				if year:
					month_range = Common.get_month_time_range(year, count)
					#print month_range
				
				month_dict = {}
				month_dict['name'] = month_range[0].strftime('%B')
			
				items = PropertyTaxItem.objects.filter(due_date__range=month_range,i_status='active')
				if conditions.has_key('district'):
					items = items.filter(property__sector__district = conditions['district'])
				if conditions.has_key('sector'):
					items = items.filter(property__sector = conditions['sector'])
				if conditions.has_key('cell'):
					items = items.filter(property__cell = conditions['cell'])

				total = items.aggregate(Sum('amount'))['amount__sum']
				unpaid = items.aggregate(Sum('remaining_amount'))['remaining_amount__sum']
				total_count = items.count()
				unpaid_count = items.filter(is_paid__exact=False).count()

				if not total:
					total = 0
				if not unpaid:
					unpaid = 0

				paid = total - unpaid
				paid_count = total_count - unpaid_count

				conditions['month_range'] = month_range
				conditions['tax_type'] = 'fixed_asset'
				unallocated_info = PaymentMapper.getUnallocatedPaymentStatistic(conditions)

				month_dict['total'] = int(total)
				month_dict['unpaid'] = int(unpaid)
				month_dict['paid'] = int(paid)
				month_dict['unallocated'] = int(unallocated_info['amount'])
				month_dict['unallocated_count'] = int(unallocated_info['count'])
				month_dict['total_count'] = int(total_count)
				month_dict['unpaid_count'] = int(unpaid_count)
				month_dict['paid_count'] = int(paid_count)
				result.append(month_dict)
		else:
			items = PropertyTaxItem.objects.filter(due_date__year=year,i_status='active')
			if conditions.has_key('district'):
				items = items.filter(property__sector__district = conditions['district'])
			if conditions.has_key('sector'):
				items = items.filter(property__sector = conditions['sector'])
			if conditions.has_key('cell'):
				items = items.filter(property__cell = conditions['cell'])

			total = items.aggregate(Sum('amount'))['amount__sum']
			unpaid = items.aggregate(Sum('remaining_amount'))['remaining_amount__sum']
			total_count = items.count()
			unpaid_count = items.filter(is_paid__exact=False).count()

			if not total:
				total = 0
			if not unpaid:
				unpaid = 0

			paid = total - unpaid
			paid_count = total_count - unpaid_count

			conditions['tax_type'] = 'fixed_asset'
			unallocated_info = PaymentMapper.getUnallocatedPaymentStatistic(conditions)

			tmp = {}
			tmp['name'] = 'Fixed asset tax'
			tmp['total'] = int(total)
			tmp['unpaid'] = int(unpaid)
			tmp['paid'] = int(paid)
			tmp['unallocated'] = int(unallocated_info['amount'])
			tmp['unallocated_count'] = int(unallocated_info['count'])
			tmp['total_count'] = int(total_count)
			tmp['unpaid_count'] = int(unpaid_count)
			tmp['paid_count'] = int(paid_count)
			result.append(tmp)
		return result

	@staticmethod
	def getFixedAssetTaxPaidAndUnpaidList(conditions=None,list='unpaid',limit=100):
		year = datetime.now().year
		items = PropertyTaxItem.objects.filter(i_status='active')
		if conditions.has_key('calendar_year'):
			year = int(conditions['calendar_year'])
			items = PropertyTaxItem.objects.filter(due_date__year=year)
		if conditions.has_key('district'):
			items = items.filter(property__sector__district = conditions['district'])
		if conditions.has_key('sector'):
			items = items.filter(property__sector = conditions['sector'])
		if conditions.has_key('cell'):
			items = items.filter(property__cell = conditions['cell'])

		if list == 'unpaid':
			items = items.filter(is_paid=False)
		elif list == 'paid':
			items = items.filter(is_paid=True)

		return items.all()[0:limit]


	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get total amount of tax for today, past 7, 30 days and past year 
	grouped by banks
	""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""" 
	
	@staticmethod
	def getFixedAssetTaxByBankPortfolio(conditions=None):
		today_range = Common.get_today_time_range()
		last7_range = Common.get_last7_days_time_range()
		last30_range = Common.get_last30_days_time_range()
		lastyear_range = Common.get_past_year_time_range()
		result = {}
		for bank_obj in banks:
			if bank_obj[0] == 'CSO':
				continue
			bank_name = bank_obj[0]
			bank_dict = {}
			taxes = PayFixedAssetTax.objects.filter(bank__iexact = bank_obj[0],i_status='active').filter(paid_date__range = today_range)
			for key, value in conditions.iteritems():
				if key == 'district' and value and value!="":
					taxes = taxes.filter(property_tax_item__property__sector__district=value)
				if key == 'sector' and value and value!="":
					taxes = taxes.filter(property_tax_item__property__sector=value)
				if key == 'cell' and value and value!="":
					taxes = taxes.filter(property_tax_item__property__cell=value)
			amount_sum = taxes.aggregate(Sum('amount'))['amount__sum']
			if amount_sum:
				bank_dict['today'] = int(amount_sum)
			else:
				bank_dict['today'] = 0
			
			taxes = PayFixedAssetTax.objects.filter(bank__iexact = bank_obj[0],i_status='active').filter(paid_date__range = last7_range)
			for key, value in conditions.iteritems():
				if key == 'district' and value and value!="":
					taxes = taxes.filter(property_tax_item__property__sector__district=value)
				if key == 'sector' and value and value!="":
					taxes = taxes.filter(property_tax_item__property__sector=value)
				if key == 'cell' and value and value!="":
					taxes = taxes.filter(property_tax_item__property__cell=value)
			amount_sum = taxes.aggregate(Sum('amount'))['amount__sum']
			if amount_sum:
				bank_dict['last7'] = int(amount_sum)
			else:
				bank_dict['last7'] = 0
			
			taxes = PayFixedAssetTax.objects.filter(bank__iexact = bank_obj[0],i_status='active').filter(paid_date__range = last30_range)
			for key, value in conditions.iteritems():
				if key == 'district' and value and value!="":
					taxes = taxes.filter(property_tax_item__property__sector__district=value)
				if key == 'sector' and value and value!="":
					taxes = taxes.filter(property_tax_item__property__sector=value)
				if key == 'cell' and value and value!="":
					taxes = taxes.filter(property_tax_item__property__cell=value)
			amount_sum = taxes.aggregate(Sum('amount'))['amount__sum']
			if amount_sum:
				bank_dict['last30'] = int(amount_sum)
			else:
				bank_dict['last30'] = 0
			
			
			taxes = PayFixedAssetTax.objects.filter(bank__iexact = bank_obj[0],i_status='active').filter(paid_date__range = lastyear_range)
			for key, value in conditions.iteritems():
				if key == 'district' and value and value!="":
					taxes = taxes.filter(property_tax_item__property__sector__district=value)
				if key == 'sector' and value and value!="":
					taxes = taxes.filter(property_tax_item__property__sector=value)
				if key == 'cell' and value and value!="":
					taxes = taxes.filter(property_tax_item__property__cell=value)
			amount_sum = taxes.aggregate(Sum('amount'))['amount__sum']
			if amount_sum:
				bank_dict['lastyear'] = int(amount_sum)
			else:
				bank_dict['lastyear'] = 0
			
			
			result[bank_name]=bank_dict
		return result
	
	@staticmethod
	def getPayFixedAssetTaxByConditions(conditions,limit = None, offset= 0, sort = 'paid_date'):
		logs = []
		kwargs = {}
		for key, value in conditions.iteritems():
			if key == 'tin' and value:
				return []

			if key == 'payment_id' and value:
				kwargs['pk__exact'] = value

			if key == 'citizen_id' and value:
				citizens = Citizen.objects.filter(citizen_id__iexact=str(value))
				if citizens:
					kwargs['citizen_id__iexact'] = str(citizens[0].id)
				else:
					return logs
			if key == 'upi' and value:
				property = PropertyMapper.getPropertyByUPI(value)
				if not property:
					return []
				else:
					taxes = PropertyTaxItem.objects.filter(property=property)
					kwargs['property_tax_item__in'] = taxes
			if key == 'plot_id' and value:
				taxes = PropertyTaxItem.objects.filter(plot_id__iexact=str(value))
				kwargs['property_tax_item__in'] = taxes

			if key == 'bank' and value:
				kwargs['bank__iexact'] = value

			if key == 'receipt_no' and value:
				kwargs['receipt_no__iexact'] = value

			if key == 'manual_receipt' and value:
				kwargs['manual_receipt__iexact'] = value

			if key == 'period_from' and value:
				kwargs['paid_date__gte'] = value

			if key == 'period_to' and value:
				kwargs['paid_date__lte'] = value
				
			if key == 'i_status' and value:
				kwargs['i_status__exact'] = value

		if limit:
			logs = PayFixedAssetTax.objects.filter(**kwargs).select_related('property_tax_item','property_tax_item__property','property_tax_item__property__cell','staff').order_by(sort)[offset:limit]
		else:
			logs = PayFixedAssetTax.objects.filter(**kwargs).select_related('property_tax_item','property_tax_item__property','property_tax_item__property__cell','staff').order_by(sort)[offset:]

		return logs