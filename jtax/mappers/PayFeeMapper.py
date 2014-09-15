from django.forms import model_to_dict
from datetime import datetime
from django.utils import timezone
from admin.Common import Common
import ast, pytz
from jtax.models import *
from django.db.models import Sum
from dev1.variables import *
from django.db.models import Q
from property.mappers.PropertyMapper import PropertyMapper
from jtax.mappers.PaymentMapper import PaymentMapper
from django.utils import timezone
import dateutil.parser

class PayFeeMapper:

	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get last 12-month paid tax and unpaid tax
	""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""" 
	
	@staticmethod
	def getTaxPayers(conditions=None):
		if conditions:
			fee_type = conditions['fee_type']
			if fee_type == "cleaning":
				"""
				fees = Fee.objects.filter(fee_type='cleaning', business__isnull=False)
				if conditions.has_key("district"):
					fees = fees.filter(business__sector__district = conditions['district'])
				if conditions.has_key("sector"):
					fees = fees.filter(business__sector = conditions['sector'])
				if conditions.has_key("cell"):
					fees = fees.filter(business__cell = conditions['cell'])
					
				businesses_ids = None
				if fees and len(fees)>0:
					business_ids = Common.get_value_list(fees.values('business').distinct(),'business')
					
				# get citizens based on the businesses_ids
				citizen_ids = None
				if businesses_ids:
					from asset.models import Ownership
					citizen_ids = Ownership.objects.filter(asset_business__id__in =  business_ids).value('owner_citizen').distinct()
					citizen_ids = Common.get_value_list(citizen_ids,'owner_citizen')
					
				citizens = None
				if citizen_ids:
					citizens = Citizen.objects.filter(id__in = citizen_ids)
				if citizens:
					result = []
					if len(citizens) >= 1:
						for citizen_obj in citizens:
							citizen_obj.tax_type = 'Cleaning fee'
							result.append(citizen_obj)
					if len(result) == 0:
						return None 
					else:
						return result
				"""
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
						i.tax_type = 'Cleaning fee'
						result.append(i)
				return result
			
			if fee_type == "land_lease":
				fees = Fee.objects.filter(fee_type='land_lease', property__isnull=False, i_status='active')
				if conditions.has_key("district"):
					fees = fees.filter(property__sector__district = conditions['district'])
				if conditions.has_key("sector"):
					fees = fees.filter(property__sector = conditions['sector'])
				if conditions.has_key("cell"):
					fees = fees.filter(property__cell = conditions['cell'])
				citizens = []
				for fee in fees:
					ownerships = fee.property.owners.filter(i_status='active')
					for ownership in ownerships:
						citizen = ownership.owner_citizen or ownership.owner_subbusiness or ownership.business
						if citizen:
							citizen.tax_type = 'Land lease fee'
							citizen.upi = fee.property.getUPI()
							citizen.property_id = fee.property.id
							citizens.append(citizen)

				return citizens or None
		return None

	@staticmethod
	def getFeePaidAndUnpaid(conditions = None):
		result = []
		year = datetime.now().year
		fee_type = None
		if conditions.has_key('calendar_year'):
			year = int(conditions['calendar_year'])
		if conditions.has_key('fee_type'):
			fee_type = conditions['fee_type']

		year_start = timezone.make_aware(dateutil.parser.parse(str(year) + '-01-01 00:00:00'), timezone.get_default_timezone())
		year_end = timezone.make_aware(dateutil.parser.parse(str(year) + '-12-31 23:59:59'), timezone.get_default_timezone())

		if fee_type == 'land_lease' :
			items = Fee.objects.filter(due_date__year=year, fee_type__istartswith = fee_type, i_status='active')

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

			unallocated_info = PaymentMapper.getUnallocatedPaymentStatistic(conditions)

			tmp = {}
			tmp['name'] = 'Land Lease fee'
			tmp['total'] = int(total)
			tmp['unpaid'] = int(unpaid)
			tmp['paid'] = int(paid)
			tmp['unallocated'] = int(unallocated_info['amount'])
			tmp['unallocated_count'] = int(unallocated_info['count'])
			tmp['total_count'] = int(total_count)
			tmp['unpaid_count'] = int(unpaid_count)
			tmp['paid_count'] = int(paid_count)
			result.append(tmp)

		elif fee_type in ('cleaning','market'):

			for count in range(1,13):
				#month_range = Common.get_previous_month_time_range(count)
				if year:
					month_range = Common.get_month_time_range(year, count)
				
				month_dict = {}
				month_dict['name'] = month_range[0].strftime('%B')
			
				items = Fee.objects.filter(period_to__range=month_range, fee_type__istartswith = fee_type,i_status='active')

				if conditions.has_key('district'):
					items = items.filter(Q(business__sector__district = conditions['district']) | Q(subbusiness__sector__district = conditions['district']))
				if conditions.has_key('sector'):
					items = items.filter(Q(business__sector = conditions['sector']) | Q(subbusiness__sector = conditions['sector']))
				if conditions.has_key('cell'):
					items = items.filter(Q(business__cell = conditions['cell']) | Q(subbusiness__cell = conditions['cell']))

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
		return result
	
	@staticmethod
	def getFeePaidAndUnpaidList(conditions = None,list='unpaid',limit=100):
		result = []
		year = datetime.now().year
		fee_type = None
		if conditions.has_key('calendar_year'):
			year = int(conditions['calendar_year'])
		if conditions.has_key('fee_type'):
			fee_type = conditions['fee_type']

		year_start = timezone.make_aware(dateutil.parser.parse(str(year) + '-01-01 00:00:00'), timezone.get_default_timezone())
		year_end = timezone.make_aware(dateutil.parser.parse(str(year) + '-12-31 23:59:59'), timezone.get_default_timezone())

		items = Fee.objects.filter(due_date__year=year, fee_type__istartswith = fee_type,i_status='active')
		if fee_type == 'land_lease':
			if conditions.has_key('district'):
				items = items.filter(property__sector__district = conditions['district'])
			if conditions.has_key('sector'):
				items = items.filter(property__sector = conditions['sector'])
			if conditions.has_key('cell'):
				items = items.filter(property__cell = conditions['cell'])
		elif fee_type == 'cleaning':
			if conditions.has_key('district'):
				items = items.filter(Q(business__sector__district = conditions['district']) | Q(subbusiness__sector__district = conditions['district']))
			if conditions.has_key('sector'):
				items = items.filter(Q(business__sector = conditions['sector']) | Q(subbusiness__sector = conditions['sector']))
			if conditions.has_key('cell'):
				items = items.filter(Q(business__cell = conditions['cell']) | Q(subbusiness__cell = conditions['cell']))

		if list == 'unpaid':
			items = items.filter(is_paid=False)
		elif list == 'paid':
			items = items.filter(is_paid=True)

		return items.all()[0:limit]
	
	
	@staticmethod
	def getPayFeeByBankPortfolio(conditions=None):
		today_range = Common.get_today_time_range()
		last7_range = Common.get_last7_days_time_range()
		last30_range = Common.get_last30_days_time_range()
		lastyear_range = Common.get_past_year_time_range()
		result = {}
		fee_type = conditions['fee_type']
		pay_fees_base = PayFee.objects.filter(fee__fee_type__iexact = fee_type, i_status='active')
		
		for bank_obj in banks:
			if bank_obj[0] == 'CSO':
				continue
			bank_name = bank_obj[0]
			bank_dict = {}
			pay_fees = pay_fees_base
			
			count = 0
			if conditions.has_key('district') and conditions['district']:
				if count == 0:
					if fee_type == 'land_lease':
						pay_fees = PayFee.objects.filter(fee__property__sector__district = conditions['district'])
					if fee_type == 'cleaning':
						pay_fees = PayFee.objects.filter(Q(fee__business__sector__district = conditions['district'])|Q(fee__subbusiness__sector__district = conditions['district']))
				else:
					if fee_type == 'land_lease':
						pay_fees = pay_fees.filter(fee__property__sector__district = conditions['district'])
					if fee_type == 'cleaning':
						pay_fees = pay_fees.filter(Q(fee__business__sector__district = conditions['district'])|Q(fee__subbusiness__sector__district = conditions['district']))
				count = count + 1
			if conditions.has_key('sector') and conditions['sector']:
				if count == 0:
					if fee_type == 'land_lease':
						pay_fees = PayFee.objects.filter(fee__property__sector = conditions['sector'])
					if fee_type == 'cleaning':
						pay_fees = PayFee.objects.filter(Q(fee__business__sector = conditions['sector'])|Q(fee__subbusiness__sector = conditions['sector']))
				else:
					if fee_type == 'land_lease':
						pay_fees = pay_fees.filter(fee__property__sector = conditions['sector'])
					if fee_type == 'cleaning':
						pay_fees = pay_fees.filter(Q(fee__business__sector = conditions['sector'])|Q(fee__subbusiness__sector = conditions['sector']))
				count = count + 1
			if conditions.has_key('cell') and conditions['cell']:
				if count == 0:
					if fee_type == 'land_lease':
						pay_fees = PayFee.objects.filter(fee__property__cell = conditions['cell'])
					if fee_type == 'cleaning':
						pay_fees = PayFee.objects.filter(Q(fee__business__cell = conditions['cell'])|Q(fee__subbusiness__cell = conditions['cell']))
				else:
					if fee_type == 'land_lease':
						pay_fees = pay_fees.filter(fee__property__cell = conditions['cell'])
					if fee_type == 'cleaning':
						pay_fees = pay_fees.filter(Q(fee__business__cell = conditions['cell'])|Q(fee__subbusiness__cell = conditions['cell']))
				count = count + 1
			
			if not pay_fees or len(pay_fees) == 0:
				bank_dict['today'] = 0
				bank_dict['last7'] = 0
				bank_dict['last30'] = 0
				bank_dict['lastyear'] = 0
			else:
				bank_dict['today'] = pay_fees.filter(fee__fee_type__iexact = fee_type, bank__iexact = bank_obj[0], paid_date__range=today_range).aggregate(Sum('amount'))['amount__sum']
				if not bank_dict['today']:
					bank_dict['today'] = 0
				bank_dict['last7'] = pay_fees.filter(fee__fee_type__iexact = fee_type, bank__iexact = bank_obj[0], paid_date__range=last7_range).aggregate(Sum('amount'))['amount__sum']
				if not bank_dict['last7']:
					bank_dict['last7'] = 0
				bank_dict['last30'] = pay_fees.filter(fee__fee_type__iexact = fee_type, bank__iexact = bank_obj[0], paid_date__range=last30_range).aggregate(Sum('amount'))['amount__sum']
				if not bank_dict['last30']:
					bank_dict['last30'] = 0
				bank_dict['lastyear'] = pay_fees.filter(fee__fee_type__iexact = fee_type, bank__iexact = bank_obj[0], paid_date__range=lastyear_range).aggregate(Sum('amount'))['amount__sum']
				if not bank_dict['lastyear']:
					bank_dict['lastyear'] = 0
			result[bank_name]=bank_dict
		return result
	
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get logs by conditions
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""    
	@staticmethod
	def getPayFeeByConditions(conditions,limit = None, offset = 0, sort = 'paid_date'):
		logs = []
		kwargs = {}
		for key, value in conditions.iteritems():
			if key == 'tin' and value:
				businesses = Business.objects.filter(tin__iexact=str(value))
				if businesses:
					fees = businesses[0].fee_set.all()
					kwargs['fee__in'] = fees
				else:
					return logs

			if key == 'payment_id' and value:
				kwargs['pk__exact'] = value

			if key == 'payment_ids' and value:
				kwargs['pk__in'] = value

			if key == 'citizen_id' and value:
				citizens = Citizen.objects.filter(citizen_id__exact=value)
				if citizens:
					kwargs['citizen_id__exact'] = citizens[0].id
				else:
					return logs

			if key == 'fee_type' and value:
				#fees = Fee.objects.filter(fee_type__exact=value.replace('_fee',''))
				kwargs['fee__fee_type'] = value.replace('_fee','')

			if key == 'upi' and value:
				property = PropertyMapper.getPropertyByUPI(value)
				if not property:
					return []
				else:
					fees = Fee.objects.filter(fee_type__exact='land_lease',property=property)
					if not fees:
						return []
					else:
						kwargs['fee_id'] = fees[0].id

			if key == 'bank' and value:
				kwargs['bank__exact'] = value

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


		if conditions.has_key('fee_type') and conditions['fee_type'] == 'misc_fee':
			del kwargs['fee__fee_type'] 
			if limit:
				logs = PayMiscellaneousFee.objects.filter(**kwargs).select_related('fee','fee__business','citizen').order_by(sort)[offset:limit]
			else:
				logs = PayMiscellaneousFee.objects.filter(**kwargs).select_related('fee','fee__business','citizen').order_by(sort)[offset:]

		else:
			if limit:
				logs = PayFee.objects.filter(**kwargs).select_related('fee','fee__property','fee__property__cell','fee__business','citizen','staff').order_by(sort)[offset:limit]
			else:
				logs = PayFee.objects.filter(**kwargs).select_related('fee','fee__property','fee__property__cell','fee__business','citizen','staff').order_by(sort)[offset:]

		return logs