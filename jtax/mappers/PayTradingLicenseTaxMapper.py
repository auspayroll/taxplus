from django.forms import model_to_dict
from datetime import datetime
from django.utils import timezone
from admin.Common import Common
import ast, pytz
from jtax.models import *
from django.db.models import Sum
from dev1.variables import *
from asset.models import *
from citizen.models import *
from jtax.mappers.PaymentMapper import PaymentMapper
from asset.models import *
from django.utils import timezone
import dateutil.parser

class PayTradingLicenseTaxMapper:

	@staticmethod
	def getTaxPayers(conditions=None):

		#just return all the active businesses / subbusinesses which each have to pay trading license tax
		businesses = Business.objects.filter(i_status='active')
		if conditions:
			if conditions.has_key("district"):
				businesses = businesses.filter(sector__district = conditions['district'])
			if conditions.has_key("sector"):
				businesses = businesses.filter(sector = conditions['sector'])
			if conditions.has_key("cell"):
				businesses = businesses.filter(cell = conditions['cell'])

		businesses.distinct()
		result = None
		if businesses and len(businesses) > 0:
			result = []
			for i in businesses:
				i.tax_type = 'Trading license tax'
				result.append(i)
		return result

	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get last 12-month paid tax and unpaid tax
	""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""" 
	
	@staticmethod
	def getTradingLicenseTaxPaidAndUnpaid(conditions = None,group='year'):
		result = []
		year = datetime.now().year

		if conditions.has_key('calendar_year'):
			year = int(conditions['calendar_year'])

		year_start = timezone.make_aware(dateutil.parser.parse(str(year) + '-01-01 00:00:00'), timezone.get_default_timezone())
		year_end = timezone.make_aware(dateutil.parser.parse(str(year) + '-12-31 23:59:59'), timezone.get_default_timezone())

		if group == 'month':
			for count in range(1,13):
				#month_range = Common.get_previous_month_time_range(count)
				if year:
					month_range = Common.get_month_time_range(year, count)

				month_dict = {}
				month_dict['name'] = month_range[0].strftime('%B')
			
				items = TradingLicenseTax.objects.filter(period_from__range=month_range,i_status='active')
				items_business = items.filter(business__isnull=False)
				items_subbusiness = items.filter(subbusiness__isnull=False)
				if conditions.has_key('district'):
					items_business = items_business.filter(business__sector__district = conditions['district'])
					items_subbusiness = items_subbusiness.filter(subbusiness__sector__district = conditions['district'])
				if conditions.has_key('sector'):
					items_business = items_business.filter(business__sector = conditions['sector'])
					items_subbusiness = items_subbusiness.filter(subbusiness__sector = conditions['sector'])
				if conditions.has_key('cell'):
					items_business = items_business.filter(business__cell = conditions['cell'])
					items_subbusiness = items_subbusiness.filter(subbusiness__cell = conditions['cell'])
				total = 0
				unpaid = 0
				total_count = 0
				unpaid_count = 0
				if items_business:
					items_business_total = items_business.aggregate(Sum('amount'))['amount__sum']
					items_business_unpaid = items_business.aggregate(Sum('remaining_amount'))['remaining_amount__sum']
					if items_business_total:
						total = total + int(items_business_total)
					if items_business_unpaid:
						unpaid = unpaid + int(items_business_unpaid)
					total_count = total_count + items_business.count()
					unpaid_count = unpaid_count + items_business.filter(is_paid__exact=False).count()

				if items_subbusiness:
					items_subbusiness_total = items_subbusiness.aggregate(Sum('amount'))['amount__sum']
					items_subbusiness_unpaid = items_subbusiness.aggregate(Sum('remaining_amount'))['remaining_amount__sum'] 
					if items_subbusiness_total:
						total = total + int(items_subbusiness_total)
					if items_subbusiness_unpaid:
						unpaid = unpaid +  int(items_subbusiness_unpaid)
					total_count = total_count + items_subbusiness_unpaid.count()
					unpaid_count = unpaid_count + items_subbusiness_unpaid.filter(is_paid__exact=False).count()

				paid = total - unpaid
				paid_count = total_count - unpaid_count

				conditions['month_range'] = month_range
				conditions['tax_type'] = 'trading_license'
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


			items = TradingLicenseTax.objects.filter(period_from__range=(year_start,year_end),i_status="active")
			items_business = items.filter(business__isnull=False)
			items_subbusiness = items.filter(subbusiness__isnull=False)
			if conditions.has_key('district'):
				items_business = items_business.filter(business__sector__district = conditions['district'])
				items_subbusiness = items_subbusiness.filter(subbusiness__sector__district = conditions['district'])
			if conditions.has_key('sector'):
				items_business = items_business.filter(business__sector = conditions['sector'])
				items_subbusiness = items_subbusiness.filter(subbusiness__sector = conditions['sector'])
			if conditions.has_key('cell'):
				items_business = items_business.filter(business__cell = conditions['cell'])
				items_subbusiness = items_subbusiness.filter(subbusiness__cell = conditions['cell'])
			total = 0
			unpaid = 0
			total_count = 0
			unpaid_count = 0
			if items_business:
				total_count = total_count + items_business.count()
				unpaid_count = unpaid_count + items_business.filter(is_paid__exact=False).count()
				items_business_total = items_business.aggregate(Sum('amount'))['amount__sum']
				items_business_unpaid = items_business.aggregate(Sum('remaining_amount'))['remaining_amount__sum']
				if items_business_total:
					total = total + int(items_business_total)
				if items_business_unpaid:
					unpaid = unpaid + int(items_business_unpaid)

			if items_subbusiness:
				total_count = total_count + items_subbusiness.count()
				unpaid_count = unpaid_count + items_subbusiness.filter(is_paid__exact=False).count()
				items_subbusiness_total = items_subbusiness.aggregate(Sum('amount'))['amount__sum']
				items_subbusiness_unpaid = items_subbusiness.aggregate(Sum('remaining_amount'))['remaining_amount__sum'] 
				if items_subbusiness_total:
					total = total + int(items_subbusiness_total)
				if items_subbusiness_unpaid:
					unpaid = unpaid +  int(items_subbusiness_unpaid)

			paid = total - unpaid
			paid_count = total_count - unpaid_count

			conditions['tax_type'] = 'trading_license'
			unallocated_info = PaymentMapper.getUnallocatedPaymentStatistic(conditions)

			tmp = {}
			tmp['name'] = 'Trading License tax'
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
	def getTradingLicenseTaxPaidAndUnpaidList(conditions=None,list='unpaid',limit=100):
		year = datetime.now().year

		if conditions.has_key('calendar_year'):
			year = int(conditions['calendar_year'])

		year_start = timezone.make_aware(dateutil.parser.parse(str(year) + '-01-01 00:00:00'), timezone.get_default_timezone())
		year_end = timezone.make_aware(dateutil.parser.parse(str(year) + '-12-31 23:59:59'), timezone.get_default_timezone())

		items = TradingLicenseTax.objects.filter(period_from__range=(year_start,year_end),i_status='active')
		items_business = items.filter(business__isnull=False)
		items_subbusiness = items.filter(subbusiness__isnull=False)
		if conditions.has_key('district'):
			items_business = items_business.filter(business__sector__district = conditions['district'])
			items_subbusiness = items_subbusiness.filter(subbusiness__sector__district = conditions['district'])
		if conditions.has_key('sector'):
			items_business = items_business.filter(business__sector = conditions['sector'])
			items_subbusiness = items_subbusiness.filter(subbusiness__sector = conditions['sector'])
		if conditions.has_key('cell'):
			items_business = items_business.filter(business__cell = conditions['cell'])
			items_subbusiness = items_subbusiness.filter(subbusiness__cell = conditions['cell'])

		if list == 'unpaid':
			items_business = items_business.filter(is_paid=False)
			items_subbusiness = items_subbusiness.filter(is_paid=False)
		elif list == 'paid':
			items_business = items_business.filter(is_paid=True)
			items_subbusiness = items_subbusiness.filter(is_paid=True)

		result = items_business.all() | items_subbusiness.all()
		return result[0:limit]

	
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get total amount of tax for today, past 7, 30 days and past year 
	grouped by banks
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""    
	
	@staticmethod
	def getTradingLicenseTaxByBankPortfolio(conditions = None):
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
			if conditions and (conditions.has_key('council') or conditions.has_key('sector')):
				bank_dict['today'] = 0
				bank_dict['last7'] = 0
				bank_dict['last30'] = 0
				bank_dict['lastyear'] = 0
			else:
				bank_dict['today'] = PayTradingLicenseTax.objects.filter(i_status='active',bank__iexact = bank_obj[0], paid_date__range=today_range).aggregate(Sum('amount'))['amount__sum']
				if not bank_dict['today']:
					bank_dict['today'] = 0
				bank_dict['last7'] = PayTradingLicenseTax.objects.filter(i_status='active',bank__iexact = bank_obj[0], paid_date__range=last7_range).aggregate(Sum('amount'))['amount__sum']
				if not bank_dict['last7']:
					bank_dict['last7'] = 0
				bank_dict['last30'] = PayTradingLicenseTax.objects.filter(i_status='active',bank__iexact = bank_obj[0], paid_date__range=last30_range).aggregate(Sum('amount'))['amount__sum']
				if not bank_dict['last30']:
					bank_dict['last30'] = 0
				bank_dict['lastyear'] = PayTradingLicenseTax.objects.filter(i_status='active',bank__iexact = bank_obj[0], paid_date__range=lastyear_range).aggregate(Sum('amount'))['amount__sum']
				if not bank_dict['lastyear']:
					bank_dict['lastyear'] = 0
			result[bank_name]=bank_dict
		return result

	
	@staticmethod
	def getPayTradingLicenseTaxByConditions(conditions,limit = None, offset = None, sort = 'paid_date'):
		logs = []
		kwargs = {}
		for key, value in conditions.iteritems():
			if key == 'plot_id' and value:
				return []

			if key == 'payment_id' and value:
				kwargs['pk__exact'] = value

			if key == 'citizen_id' and value:
				citizens = Citizen.objects.filter(citizen_id__iexact=str(value))
				if citizens:
					kwargs['citizen_id__exact'] = citizens[0].id
				else:
					return logs

			if key == 'upi' and value:
				return []

			if key == 'tin' and value:
				businesses = Business.objects.filter(tin__iexact=str(value))
				if businesses:
					taxes = businesses[0].tradinglicensetax_set.all()
					kwargs['trading_license_tax__in'] = taxes
				else:
					return logs
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
			logs = PayTradingLicenseTax.objects.filter(**kwargs).select_related('trading_license_tax','trading_license_tax__business','citizen','staff').order_by(sort)[offset:limit]
		else:
			logs = PayTradingLicenseTax.objects.filter(**kwargs).select_related('trading_license_tax','trading_license_tax__business','citizen','staff').order_by(sort)[offset:]

		return logs