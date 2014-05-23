from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.contrib.gis.geos import *
from django.contrib import messages
from django.core.paginator import *
from django.core.urlresolvers import reverse
from django.http import Http404,HttpResponse, HttpResponseRedirect
from django.forms import model_to_dict, DateField
from property.modelforms.modelforms import PropertyCreationForm
from property.forms.forms import *
from jtax.forms.forms import *
from citizen.models import *
from log.forms.forms import LogSearchForm
from citizen.modelforms.modelforms import *
from asset.modelforms.modelforms import BusinessForm
from log.mappers.LogMapper import LogMapper
from property.mappers.PropertyMapper import PropertyMapper
from property.mappers.SectorMapper import SectorMapper
from property.mappers.OwnershipMapper import OwnershipMapper
from property.models import Property
from jtax.mappers.DeclaredValueMapper import DeclaredValueMapper
from jtax.mappers.PropertyTaxItemMapper import PropertyTaxItemMapper
from jtax.mappers.PayFixedAssetTaxMapper import PayFixedAssetTaxMapper
from jtax.mappers.PayRentalIncomeTaxMapper import PayRentalIncomeTaxMapper
from jtax.mappers.PayTradingLicenseTaxMapper import PayTradingLicenseTaxMapper
from asset.mappers.BusinessMapper import BusinessMapper
from asset.models import Business
from asset.models import Ownership
from asset.modelforms.modelforms import *
from media.mappers.MediaMapper import MediaMapper
from admin.Common import Common
from dateutil.relativedelta import relativedelta

from jtax.mappers.PayFeeMapper import PayFeeMapper
from businesslogic.TaxBusiness import TaxBusiness
from citizen.mappers.CitizenMapper import CitizenMapper
from property.mappers.CellMapper import CellMapper
from property.mappers.DistrictMapper import DistrictMapper
from pmauth.mappers.ModuleMapper import ModuleMapper
from pmauth.mappers.ContentTypeMapper import ContentTypeMapper
from pmauth.mappers.PermissionMapper import PermissionMapper
from pmauth.mappers.GroupMapper import GroupMapper
from pmauth.models import PMUser
from jtax.models import *
from jtax.modelforms.modelforms import *
from citizen.forms.forms import *
from dev1 import variables
import copy
from datetime import date, datetime, time, timedelta
from dateutil.relativedelta import relativedelta
from django.template.response import TemplateResponse
import calendar
from django.utils import timezone
import dateutil.parser
from django.db.models import Count, Q, F
from asset.models import *
from django.contrib import messages
import os
from django.conf import settings
from media.models import Media
from types import *
from decimal import Decimal
from admin.views import login
from jtax.mappers.PaymentMapper import PaymentMapper
from jtax.mappers.TaxMapper import TaxMapper

from django.forms import EmailField
from django.core.mail import EmailMessage
from property.models import *
from jtax.models import IncompletePayment
from common.util import CommonUtil
import json
from django.views.decorators.cache import cache_control
from jtax.shared_functions import *
from django.views.decorators.csrf import csrf_exempt
from django.core.context_processors import csrf

def access_content_type(request, content_type_name, action = None, content_type_name1 = None, obj_name = None, obj_id = None, part = None):
	"""
	This function direct request to the correspodding {module}_{contenttype}_default page
	"""
	if not request.session.get('user') or not type(request.session.get('user')) is PMUser:
		return login(request);

	#clear all the old messages
	storage = messages.get_messages(request)
	storage.used = True

	if content_type_name == 'tax':
		if not request.session['user'].has_content_type_by_name('tax','tax'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
		return tax_default(request, action, content_type_name1, obj_name, obj_id, part)

	raise Http404
	
	

def construction(request):
	#return HttpResponse('Unauthorized', status=401)
	raise Http404
	#return render_to_response('admin/construction.html', {}, context_instance=RequestContext(request))


def incomplete_payment_default(request, action=None, content_type_name1=None, obj_id=None):
	"""
	This funcion manages the following actions related to users. 1)add, 2)change, 3)delete 
	"""	

	if not request.session.get('user') or not type(request.session.get('user')) is PMUser:
		return login(request);

	records_in_page = 20
	page = 1
	if request.GET.get('page',None) != None and request.GET.get('page').isdigit():
		page = request.GET.get('page')

	user = request.session.get('user')

	if not action:
		# show incomplete payment default page
		if request.method != 'POST':
			payments = IncompletePayment.objects.filter(i_status='active').order_by('-date_time').select_related('user','district','sector','cell','village','business','subbusiness')
			if request.GET.get('print'):
				return PaymentMapper.generateIncompletePaymentPdf(payments)
			
			paginator = Paginator(payments, records_in_page)
			try:
				payment_list = paginator.page(page)
			except PageNotAnInteger:
				# If page is not an integer, deliver first page.
				payment_list = paginator.page(1)
			except EmptyPage:
				# If page is out of range (e.g. 9999), deliver last page of results.
				payment_list = paginator.page(paginator.num_pages)

			if payment_list and len(payment_list) > 0:
				for payment in payment_list:
					payment.tax_type_name = get_tax_type_display_name(payment.tax_type)
			search_incomplete_payment_form = incomplete_payment_search_form()

			LogMapper.createLog(request,user=user,action='search',search_message_all='view full Incomplete Payment list.')

			#search_incomplete_payment_form = None
			return render_to_response('tax/tax_tax_incomplete_payment_list.html', {\
								'payments':payment_list, 'search_incomplete_payment_form':search_incomplete_payment_form, 'action':'search','pagination_url':request.get_full_path().rsplit('?&page')[0] + '?'},
								context_instance=RequestContext(request))	
	elif action == 'search':
		search_incomplete_payment_form = incomplete_payment_search_form(request.GET)
		kwargs = {'i_status':'active'}
		payments = None
		payment_list = []		
		if search_incomplete_payment_form.is_valid():
			conditions = search_incomplete_payment_form.cleaned_data
			for key,value in conditions.iteritems():
				if value != None and str(value).strip() != '':
					if key=='id':
						try:
							kwargs['pk__exact'] = int(value.strip())
						except ValueError:
							pass
					if key=='sector':
						kwargs['sector__id'] = int(value.strip())
					elif key == 'parcel_id':
						kwargs['parcel_id'] = value.strip()
					elif key == 'filter_period_from':
						kwargs['date_time__gte'] = value
					elif key == 'filter_period_to':
						kwargs['date_time__lte'] = value
					elif key == 'user':
						continue
					else:
						kwargs[key + '__istartswith'] = value.strip()

			if conditions.has_key("user") and conditions['user']!='':
				names = str(conditions['user']).strip().split(' ')

				if len(names) == 1:
					payments = IncompletePayment.objects.filter(**kwargs).filter(Q(user__firstname__iexact = names[0])|Q(user__lastname__iexact = names[0])).order_by('-date_time').select_related('user','district','sector','cell','village','business','subbusiness')
				elif len(names) == 2:
					payments = IncompletePayment.objects.filter(**kwargs).filter(Q(user__firstname__iexact = names[0], user__lastname__iexact = names[1])|Q(user__firstname__iexact = names[1], user__lastname__iexact = names[0])).order_by('-date_time').select_related('user','district','sector','cell','village','business','subbusiness')
			else:
				payments = IncompletePayment.objects.filter(**kwargs).order_by('-date_time').select_related('user','district','sector','cell','village','business','subbusiness')


		if request.GET.get('print'):
			return PaymentMapper.generateIncompletePaymentPdf(payments)

		paginator = Paginator(payments, records_in_page)
		try:
			payment_list = paginator.page(page)
		except PageNotAnInteger:
			# If page is not an integer, deliver first page.
			payment_list = paginator.page(1)
		except EmptyPage:
			# If page is out of range (e.g. 9999), deliver last page of results.
			payment_list = paginator.page(paginator.num_pages)

		if payment_list and len(payment_list) > 0:
			for payment in payment_list:
				payment.tax_type_name = get_tax_type_display_name(payment.tax_type)

		LogMapper.createLog(request,user=user,action='search',search_object_class_name='IncompletePayment',search_conditions=conditions)

		return render_to_response('tax/tax_tax_incomplete_payment_list.html', {'payments':payment_list, 'search_incomplete_payment_form':search_incomplete_payment_form,'pagination_url':request.get_full_path().rsplit('&page')[0]},
						context_instance=RequestContext(request))
		
	elif action == 'add':
		# add incomplete payment +++
		if request.method == 'POST':
			form = IncompletePaymentModelForm(request.POST)
			if form.is_valid():
				incomplete_payment = form.save(request)
				try:
					if incomplete_payment.village:
						property = Property.objects.get(sector = incomplete_payment.sector, cell = incomplete_payment.cell, village= incomplete_payment.village, parcel_id  = incomplete_payment.parcel_id)
					else:
						property = Property.objects.get(sector = incomplete_payment.sector, cell = incomplete_payment.cell, parcel_id  = incomplete_payment.parcel_id)
				except Exception:
					property = None
				try:
					citizen = Citizen.objects.get(pk=incomplete_payment.citizen_id,i_status='active')
				except Exception:
					citizen = None
				LogMapper.createLog(request,user=user,object=incomplete_payment,action='add',property=property,business=incomplete_payment.business,subbusiness=incomplete_payment.subbusiness,citizen=citizen)
				return redirect('/admin/tax/incomplete_payment/')
			else:
				search_incomplete_payment_form = incomplete_payment_search_form()
				return render_to_response('tax/tax_tax_incomplete_payment_list.html', {'form':form, 'search_incomplete_payment_form':search_incomplete_payment_form,'action':'add'},
						context_instance=RequestContext(request))
		else:
			search_incomplete_payment_form = incomplete_payment_search_form()
			form = IncompletePaymentModelForm()
			return render_to_response('tax/tax_tax_incomplete_payment_list.html', {'form':form, 'search_incomplete_payment_form':search_incomplete_payment_form,'action':'add'},
						context_instance=RequestContext(request))			
	elif action == 'change':
		if obj_id != None:
			obj = get_object_or_404(IncompletePayment,pk=obj_id)
			form = IncompletePaymentModelForm(instance = obj)
			search_incomplete_payment_form = incomplete_payment_search_form()
			
			if request.method == 'POST':
				form = IncompletePaymentModelForm(request.POST, instance = obj)
				old_data = model_to_dict(obj)
				if form.is_valid():
					incomplete_payment = form.save(request)
					new_data = model_to_dict(incomplete_payment)
					try:
						if incomplete_payment.village:
							property = Property.objects.get(sector = incomplete_payment.sector, cell = incomplete_payment.cell, village= incomplete_payment.village, parcel_id  = incomplete_payment.parcel_id)
						else:
							property = Property.objects.get(sector = incomplete_payment.sector, cell = incomplete_payment.cell, parcel_id  = incomplete_payment.parcel_id)
					except Exception:
						property = None
					try:
						citizen = Citizen.objects.get(pk=incomplete_payment.citizen_id,i_status='active')
					except Exception:
						citizen = None
					LogMapper.createLog(request,user=user,object=incomplete_payment,old_data=old_data,new_data=new_data,action='change',property=property,business=incomplete_payment.business,subbusiness=incomplete_payment.subbusiness,citizen=citizen)
					return redirect('/admin/tax/incomplete_payment/')
				else:
					return render_to_response('tax/tax_tax_incomplete_payment_list.html', {'form':form,'search_incomplete_payment_form':search_incomplete_payment_form, 'action':'edit',},
						context_instance=RequestContext(request))
			else:
				return render_to_response('tax/tax_tax_incomplete_payment_list.html', {'form':form,'search_incomplete_payment_form':search_incomplete_payment_form, 'action':'edit',},
					context_instance=RequestContext(request))
	elif action == 'finalize':
		if obj_id != None:
			try:
				incomplete_payment = IncompletePayment.objects.get(pk = obj_id, i_status='active')
			except Exception:
				raise Http404
			medias = Media.objects.filter(incomplete_payment = incomplete_payment)
			
			if request.method != 'POST':
				form = None
				if incomplete_payment.tax_type == 'cleaning_fee':
					form = finalize_cleaning_fee_form(instance = incomplete_payment)
				elif incomplete_payment.tax_type == 'market_fee':
					form = finalize_market_fee_form(instance = incomplete_payment)
				elif incomplete_payment.tax_type == 'rental_income':
					form = finalize_rental_income_tax_form(instance = incomplete_payment)
				elif incomplete_payment.tax_type == 'fixed_asset':
					form = finalize_fixed_asset_tax_form(instance = incomplete_payment)
				elif incomplete_payment.tax_type == 'trading_license':
					form = finalize_trading_license_tax_form(instance = incomplete_payment)
				elif incomplete_payment.tax_type == 'land_lease_fee':
					form = finalize_land_lease_fee_form(instance = incomplete_payment)
				
				incomplete_payment = add_extra_info_to_incomplete_payment_for_invoince(incomplete_payment)
				return render_to_response('tax/tax_tax_incomplete_payment_invoice.html', {'form':form,'incomplete_payment':incomplete_payment,'media':medias,},
						context_instance=RequestContext(request))
			else:
				if incomplete_payment.tax_type == 'land_lease_fee':
					form = finalize_land_lease_fee_form(request.POST)
					if form.is_valid():
						incomplete_payment = IncompletePayment.objects.get(pk = incomplete_payment.id)						
						tax_amount = 0
						property = None
						if form.cleaned_data['village']:
							property = Property.objects.get(sector = incomplete_payment.sector, cell = incomplete_payment.cell, village= incomplete_payment.village, parcel_id  = incomplete_payment.parcel_id)
						else:
							property = Property.objects.get(sector = incomplete_payment.sector, cell = incomplete_payment.cell, parcel_id  = incomplete_payment.parcel_id)
						date_boundary = datetime.strptime('01/04/2013','%d/%m/%Y').date()
						base_amount = TaxMapper.get_base_amount_for_incomplete_payment(incomplete_payment, {'property':property,})
						late_fee = TaxMapper.get_late_fee_for_incomplete_payment(incomplete_payment, base_amount)

						#Create a jtax_fee record or update existing fee record
						period_from_wtz = timezone.make_aware(dateutil.parser.parse(incomplete_payment.period_from.strftime('%Y-%m-%d') + ' 00:00:00'), timezone.get_default_timezone())
						period_to_wtz = timezone.make_aware(dateutil.parser.parse(incomplete_payment.period_to.strftime('%Y-%m-%d') + ' 23:59:59'), timezone.get_default_timezone())
						fees = Fee.objects.filter(property=property,period_from = period_from_wtz,period_to=period_to_wtz,fee_type='land_lease',i_status='active')

						if fees:
							fee = fees[0]
							if fee.is_paid == True:
								form._errors['period_from'] = ["The tax applied for this period has already been paid, please re-check!!!"]
								incomplete_payment = add_extra_info_to_incomplete_payment_for_invoince(incomplete_payment)
								return render_to_response('tax/tax_tax_incomplete_payment_invoice.html', {'form':form,'incomplete_payment':incomplete_payment,'media':medias,},
														context_instance=RequestContext(request))
						else:
							fee = Fee()
							fee.property = property
							fee.period_from = period_from_wtz
							fee.period_to = period_to_wtz
							fee.currency = 'RWF'
							fee.fee_type='land_lease'
							fee.due_date = datetime(incomplete_payment.period_from.year,12,31,0,0,0).date()
							fee.i_status = 'active'

						if incomplete_payment.period_to < date_boundary or incomplete_payment.period_from < date_boundary:
							fee.amount = incomplete_payment.paid_amount
							fee.remaining_amount = 0
							fee.is_paid = True
						else:
							fee.amount = base_amount
							if base_amount + late_fee <= incomplete_payment.paid_amount:
								fee.is_paid=True
								fee.remaining_amount = 0
							else:
								fee.is_paid = False
								fee.remaining_amount = base_amount + late_fee - incomplete_payment.paid_amount 

						fee.date_time = datetime.now()
						fee.staff_id = request.session['user'].id
						fee.save()
						
						#Create a jtax_payfee record
						pay_fee = PayFee()
						pay_fee.fee = fee
						pay_fee.receipt_no = incomplete_payment.bank_receipt
						pay_fee.staff = request.session['user']
						pay_fee.amount = incomplete_payment.paid_amount
						pay_fee.bank = incomplete_payment.bank
						if incomplete_payment.note:
							pay_fee.note = incomplete_payment.note
						if incomplete_payment.sector_receipt:
							pay_fee.manual_receipt = incomplete_payment.sector_receipt
						pay_fee.i_status = 'active'
						if incomplete_payment.paid_date:
							pay_fee.paid_date = incomplete_payment.paid_date
						if late_fee:
							pay_fee.fine_amount = late_fee
						pay_fee.save()
						
						#Create media files for fee
						if medias:
							for media in medias:
								media.tags = 'tax|payment'
								media.tax_type = 'fee'
								media.tax_id = fee.id
								media.paymemnt_type = 'pay_fee'
								media.payment_id = pay_fee.id
								media.i_status = 'active'
								media.save()
						
						# set incomplete payment to be inactive
						incomplete_payment.i_status = 'inactive'
						incomplete_payment.save()

						try:
							citizen = Citizen.objects.get(pk=incomplete_payment.citizen_id,i_status='active')
						except Exception:
							citizen = None
						message = "finalized Incomplete Payment (ID: " + str(incomplete_payment.id) + ") into Land Lease payment (ReceiptID: " + PaymentMapper.generateInvoiceId('fee',pay_fee) + ")"
						LogMapper.createLog(request,user=user,object=pay_fee,action='add',message=message,property=fee.property,business=fee.business,subbusiness=fee.subbusiness,citizen=citizen)

						return redirect('/admin/tax/incomplete_payment/')
					else:
						incomplete_payment = add_extra_info_to_incomplete_payment_for_invoince(incomplete_payment)
						return render_to_response('tax/tax_tax_incomplete_payment_invoice.html', {'form':form,'incomplete_payment':incomplete_payment,'media':medias,},
												context_instance=RequestContext(request))
				elif incomplete_payment.tax_type == 'cleaning_fee':
					form = finalize_cleaning_fee_form(request.POST)
					if form.is_valid():
						incomplete_payment = IncompletePayment.objects.get(pk = incomplete_payment.id)
						tin =  form.cleaned_data['tin']
						paid_amount = int(form.cleaned_data['paid_amount'])
						period_from = form.cleaned_data['period_from']
						period_to = form.cleaned_data['period_to']
						bank = form.cleaned_data['bank']
						bank_receipt = form.cleaned_data['bank_receipt']
						date_boundary = datetime.strptime('01/04/2013','%d/%m/%Y').date()
						business = form.cleaned_data['business']
						subbusiness = form.cleaned_data['subbusiness']
						base_amount = TaxMapper.get_base_amount_for_incomplete_payment(incomplete_payment)
						if business:
							#Create a jtax_fee record or update existing fee record
							period_from_wtz = timezone.make_aware(dateutil.parser.parse(incomplete_payment.period_from.strftime('%Y-%m-%d') + ' 00:00:00'), timezone.get_default_timezone())
							period_to_wtz = timezone.make_aware(dateutil.parser.parse(incomplete_payment.period_to.strftime('%Y-%m-%d') + ' 23:59:59'), timezone.get_default_timezone())
							if subbusiness:
								fees = Fee.objects.filter(subbusiness=subbusiness,period_from = period_from_wtz,period_to=period_to_wtz,fee_type='cleaning',i_status='active')
							else:
								fees = Fee.objects.filter(business=business,period_from = period_from_wtz,period_to=period_to_wtz,fee_type='cleaning',i_status='active')

							if fees:
								fee = fees[0]
								if fee.is_paid == True:
									form._errors['period_from'] = ["The tax applied for this period has already been paid, please re-check!!!"]
									incomplete_payment = add_extra_info_to_incomplete_payment_for_invoince(incomplete_payment)
									return render_to_response('tax/tax_tax_incomplete_payment_invoice.html', {'form':form,'incomplete_payment':incomplete_payment,'media':medias,},
															context_instance=RequestContext(request))
							else:
								fee = Fee()
								if subbusiness:
									fee.subbusiness = subbusiness
								else:
									fee.business = business
								fee.period_from = period_from_wtz
								fee.period_to = period_to_wtz
								fee.currency = 'RWF'
								fee.fee_type='cleaning'
							
								period_from_date_time = datetime(period_from.year,period_from.month,period_from.day,0,0,0)
								period_from_date_time = period_from_date_time + relativedelta(days = +4)
								fee.due_date = period_from_date_time.date()
								
								fee.i_status = 'active'

							late_fee = TaxMapper.get_late_fee_for_incomplete_payment(incomplete_payment, base_amount)
							if period_to < date_boundary or period_from < date_boundary:
								fee.amount = paid_amount
								fee.is_paid = True
								fee.remaining_amount = 0
							else:
								fee.amount = base_amount
								if fee.amount + late_fee <=paid_amount:
									fee.is_paid=True
									fee.remaining_amount = 0
									#business.credit = paid_amount - fee.amount - late_fee
									#business.save()
								else:
									fee.is_paid = False
									fee.remaining_amount = fee.amount + late_fee - paid_amount									

							fee.date_time = datetime.now()
							fee.staff_id = request.session['user'].id
							fee.save()
							
							#Create a jtax_payfee record
							pay_fee = PayFee()
							pay_fee.business_id = business.id
							pay_fee.fee = fee
							pay_fee.receipt_no = bank_receipt
							pay_fee.staff = request.session['user']
							pay_fee.amount = paid_amount
							pay_fee.bank = bank
							if incomplete_payment.note:
								pay_fee.note = incomplete_payment.note
							if incomplete_payment.sector_receipt:
								pay_fee.manual_receipt = incomplete_payment.sector_receipt
							pay_fee.i_status = 'active'
							if incomplete_payment.paid_date:
								pay_fee.paid_date = incomplete_payment.paid_date
							if late_fee:
								pay_fee.fine_amount = late_fee 
							pay_fee.save()
							
							#Create media files for fee
							if medias:
								for media in medias:
									media.tags = 'tax|payment'
									media.tax_type = 'fee'
									media.tax_id = fee.id
									media.paymemnt_type = 'pay_fee'
									media.payment_id = pay_fee.id
									media.i_status = 'active'
									media.save()
							
							# set incomplete payment to be inactive
							incomplete_payment.i_status = 'inactive'
							incomplete_payment.save()

							try:
								citizen = Citizen.objects.get(pk=incomplete_payment.citizen_id,i_status='active')
							except Exception:
								citizen = None
							message = "finalized Incomplete Payment (ID: " + str(incomplete_payment.id)  + ") into Cleaning Fee payment (ReceiptID: " + PaymentMapper.generateInvoiceId('fee',pay_fee) + ")"
							LogMapper.createLog(request,user=user,object=pay_fee,action='add',message=message,property=fee.property,business=fee.business,subbusiness=fee.subbusiness,citizen=citizen)

							return redirect('/admin/tax/incomplete_payment/')
					else:

						incomplete_payment = add_extra_info_to_incomplete_payment_for_invoince(incomplete_payment)
						return render_to_response('tax/tax_tax_incomplete_payment_invoice.html', {'form':form,'incomplete_payment':incomplete_payment,'media':medias,},
												context_instance=RequestContext(request))

				elif incomplete_payment.tax_type == 'market_fee':
					form = finalize_market_fee_form(request.POST)
					if form.is_valid():
						incomplete_payment = IncompletePayment.objects.get(pk = incomplete_payment.id)
						tin =  form.cleaned_data['tin']
						paid_amount = int(form.cleaned_data['paid_amount'])
						period_from = form.cleaned_data['period_from']
						period_to = form.cleaned_data['period_to']
						bank = form.cleaned_data['bank']
						bank_receipt = form.cleaned_data['bank_receipt']
						date_boundary = datetime.strptime('01/04/2013','%d/%m/%Y').date()
						business = form.cleaned_data['business']
						subbusiness = form.cleaned_data['subbusiness']
						base_amount = TaxMapper.get_base_amount_for_incomplete_payment(incomplete_payment)
						if business:
							#Create a jtax_fee record or update existing fee record
							period_from_wtz = timezone.make_aware(dateutil.parser.parse(incomplete_payment.period_from.strftime('%Y-%m-%d') + ' 00:00:00'), timezone.get_default_timezone())
							period_to_wtz = timezone.make_aware(dateutil.parser.parse(incomplete_payment.period_to.strftime('%Y-%m-%d') + ' 23:59:59'), timezone.get_default_timezone())
							if subbusiness:
								fees = Fee.objects.filter(subbusiness=subbusiness,period_from = period_from_wtz,period_to=period_to_wtz,fee_type='market',i_status='active')
							else:
								fees = Fee.objects.filter(business=business,period_from = period_from_wtz,period_to=period_to_wtz,fee_type='market',i_status='active')

							if fees:
								fee = fees[0]
								if fee.is_paid == True:
									form._errors['period_from'] = ["The tax applied for this period has already been paid, please re-check!!!"]
									incomplete_payment = add_extra_info_to_incomplete_payment_for_invoince(incomplete_payment)
									return render_to_response('tax/tax_tax_incomplete_payment_invoice.html', {'form':form,'incomplete_payment':incomplete_payment,'media':medias,},
															context_instance=RequestContext(request))
							else:
								fee = Fee()
								if subbusiness:
									fee.subbusiness = subbusiness
								else:
									fee.business = business
								fee.period_from = period_from_wtz
								fee.period_to = period_to_wtz
								fee.currency = 'RWF'
								fee.fee_type='market'
							
								period_from_date_time = datetime(period_from.year,period_from.month,period_from.day,0,0,0)
								period_from_date_time = period_from_date_time + relativedelta(days = +4)
								fee.due_date = period_from_date_time.date()
								
								fee.i_status = 'active'

							late_fee = TaxMapper.get_late_fee_for_incomplete_payment(incomplete_payment, base_amount)
							if period_to < date_boundary or period_from < date_boundary:
								fee.amount = paid_amount
								fee.is_paid = True
								fee.remaining_amount = 0
							else:
								fee.amount = base_amount
								if fee.amount + late_fee <=paid_amount:
									fee.is_paid=True
									fee.remaining_amount = 0
									#business.credit = paid_amount - fee.amount - late_fee
									#business.save()
								else:
									fee.is_paid = False
									fee.remaining_amount = fee.amount + late_fee - paid_amount									

							fee.date_time = datetime.now()
							fee.staff_id = request.session['user'].id
							fee.save()
							
							#Create a jtax_payfee record
							pay_fee = PayFee()
							pay_fee.business_id = business.id
							pay_fee.fee = fee
							pay_fee.receipt_no = bank_receipt
							pay_fee.staff = request.session['user']
							pay_fee.amount = paid_amount
							pay_fee.bank = bank
							if incomplete_payment.note:
								pay_fee.note = incomplete_payment.note
							if incomplete_payment.sector_receipt:
								pay_fee.manual_receipt = incomplete_payment.sector_receipt
							pay_fee.i_status = 'active'
							if incomplete_payment.paid_date:
								pay_fee.paid_date = incomplete_payment.paid_date
							if late_fee:
								pay_fee.fine_amount = late_fee 
							pay_fee.save()
							
							#Create media files for fee
							if medias:
								for media in medias:
									media.tags = 'tax|payment'
									media.tax_type = 'fee'
									media.tax_id = fee.id
									media.paymemnt_type = 'pay_fee'
									media.payment_id = pay_fee.id
									media.i_status = 'active'
									media.save()
							
							# set incomplete payment to be inactive
							incomplete_payment.i_status = 'inactive'
							incomplete_payment.save()

							try:
								citizen = Citizen.objects.get(pk=incomplete_payment.citizen_id,i_status='active')
							except Exception:
								citizen = None
							message = "finalized Incomplete Payment (ID: " + str(incomplete_payment.id)  + ") into Market fee payment (ReceiptID: " + PaymentMapper.generateInvoiceId('fee',pay_fee) + ")"
							LogMapper.createLog(request,user=user,object=pay_fee,action='add',message=message,property=fee.property,business=fee.business,subbusiness=fee.subbusiness,citizen=citizen)

							return redirect('/admin/tax/incomplete_payment/')
					else:

						incomplete_payment = add_extra_info_to_incomplete_payment_for_invoince(incomplete_payment)
						return render_to_response('tax/tax_tax_incomplete_payment_invoice.html', {'form':form,'incomplete_payment':incomplete_payment,'media':medias,},
												context_instance=RequestContext(request))
				elif incomplete_payment.tax_type == 'rental_income':
					form = finalize_rental_income_tax_form(request.POST)
					if form.is_valid():
						incomplete_payment = IncompletePayment.objects.get(pk = incomplete_payment.id)
						rental_income = form.cleaned_data['sector']
						bank_interest_paid = form.cleaned_data['sector']
						late_fee_amount = 0
						
						property = None
						if form.cleaned_data['village']:
							property = Property.objects.get(sector = incomplete_payment.sector, cell = incomplete_payment.cell, village= incomplete_payment.village, parcel_id  = incomplete_payment.parcel_id)
						else:
							property = Property.objects.get(sector = incomplete_payment.sector, cell = incomplete_payment.cell, parcel_id  = incomplete_payment.parcel_id)
						base_amount = TaxMapper.get_base_amount_for_incomplete_payment(incomplete_payment, {'rental_income':rental_income,'bank_interest_paid':bank_interest_paid,}) 
						
						#Create a jtax_fee record or update existing fee record
						period_from_wtz = timezone.make_aware(dateutil.parser.parse(incomplete_payment.period_from.strftime('%Y-%m-%d') + ' 00:00:00'), timezone.get_default_timezone())
						period_to_wtz = timezone.make_aware(dateutil.parser.parse(incomplete_payment.period_to.strftime('%Y-%m-%d') + ' 23:59:59'), timezone.get_default_timezone())

						taxes = RentalIncomeTax.objects.filter(property=property,period_from = period_from_wtz,period_to=period_to_wtz,i_status='active')
						if taxes:
							tax_item = taxes[0]
							if tax_item.is_paid == True:
								form._errors['period_from'] = ["The tax applied for this period has already been paid, please re-check!!!"]
								incomplete_payment = add_extra_info_to_incomplete_payment_for_invoince(incomplete_payment)
								return render_to_response('tax/tax_tax_incomplete_payment_invoice.html', {'form':form,'incomplete_payment':incomplete_payment,'media':medias,},
														context_instance=RequestContext(request))
						else:
							tax_item = RentalIncomeTax()
							tax_item.currency = 'RWF'
							tax_item.period_from = period_from_wtz
							tax_item.period_to = period_to_wtz
							tax_item.due_date = datetime(incomplete_payment.period_to.year + 1,4,1,0,0,0).date()
							tax_item.property = property

						tax_item.date_time = datetime.now()
						tax_item.i_status = 'active'
						tax_item.submit_date = incomplete_payment.paid_date
						tax_item.amount = base_amount
						
						
						boundary_date = datetime(2013,4,1,0,0,0).date()
						if incomplete_payment.period_to < boundary_date or incomplete_payment.period_from < boundary_date:
							tax_item.is_paid = True
							tax_item.remaining_amount = 0
							tax_item.amount = incomplete_payment.paid_amount
						else:
							late_fee_amount = TaxMapper.get_late_fee_for_incomplete_payment(incomplete_payment, base_amount)
							if late_fee_amount + base_amount > incomplete_payment.paid_amount:
								tax_item.is_paid = False
								tax_item.remaining_amount = late_fee_amount + base_amount - incomplete_payment.paid_amount
							else:
								tax_item.is_paid = True
								tax_item.remaining_amount = 0

						tax_item.save()
						
						# create jtax_payrentalincometax record
						pay_tax_item = PayRentalIncomeTax()
						pay_tax_item.rental_income_tax = tax_item
						pay_tax_item.staff = request.session['user']
						pay_tax_item.amount = incomplete_payment.paid_amount
						pay_tax_item.receipt_no = incomplete_payment.bank_receipt
						pay_tax_item.bank = incomplete_payment.bank
						pay_tax_item.date_time = datetime.now()
						pay_tax_item.note = incomplete_payment.note
						pay_tax_item.i_status = 'active'
						pay_tax_item.paid_date = incomplete_payment.paid_date
						pay_tax_item.manual_receipt = incomplete_payment.sector_receipt
						pay_tax_item.fine_amount = late_fee_amount
						pay_tax_item.save()
						
						#Create media files for fee
						if medias:
							for media in medias:
								media.tags = 'tax|payment'
								media.tax_type = 'rental_income'
								media.tax_id = pay_tax_item.id
								media.paymemnt_type = 'pay_rental_income'
								media.payment_id = pay_tax_item.id
								media.i_status = 'active'
								media.save()
						
						# set incomplete payment to be inactive
						incomplete_payment.i_status = 'inactive'
						incomplete_payment.save()

						try:
							citizen = Citizen.objects.get(pk=incomplete_payment.citizen_id,i_status='active')
						except Exception:
							citizen = None
						message = "finalized Incomplete Payment (ID: " + str(incomplete_payment.id)  + ") into Rental Income Tax payment (ReceiptID: " + PaymentMapper.generateInvoiceId('rental_income',pay_tax_item) + ")"
						LogMapper.createLog(request,user=user,object=pay_tax_item,action='add',message=message,property=tax_item.property,citizen=citizen)

						return redirect('/admin/tax/incomplete_payment/')
					else:
						incomplete_payment = add_extra_info_to_incomplete_payment_for_invoince(incomplete_payment)
						return render_to_response('tax/tax_tax_incomplete_payment_invoice.html', {'form':form,'incomplete_payment':incomplete_payment,'media':medias,},
												context_instance=RequestContext(request))
				
				elif incomplete_payment.tax_type == 'fixed_asset':
					form = finalize_fixed_asset_tax_form(request.POST)
					if form.is_valid():
						declared_value = form.cleaned_data['declared_value']
						late_fee_amount = 0
						incomplete_payment = IncompletePayment.objects.get(pk = incomplete_payment.id)
						property = None
						if form.cleaned_data['village']:
							property = Property.objects.get(sector = incomplete_payment.sector, cell = incomplete_payment.cell, village= incomplete_payment.village, parcel_id  = incomplete_payment.parcel_id)
						else:
							property = Property.objects.get(sector = incomplete_payment.sector, cell = incomplete_payment.cell, parcel_id  = incomplete_payment.parcel_id)
						base_amount = TaxMapper.get_base_amount_for_incomplete_payment(incomplete_payment, {'declared_value':declared_value,}) 
						
						period_from_wtz = timezone.make_aware(dateutil.parser.parse(incomplete_payment.period_from.strftime('%Y-%m-%d') + ' 00:00:00'), timezone.get_default_timezone())
						period_to_wtz = timezone.make_aware(dateutil.parser.parse(incomplete_payment.period_to.strftime('%Y-%m-%d') + ' 23:59:59'), timezone.get_default_timezone())
						
						taxes = PropertyTaxItem.objects.filter(property=property,period_from = period_from_wtz,period_to=period_to_wtz,i_status='active')
						if taxes:
							tax_item = taxes[0]
							if tax_item.is_paid == True:
								form._errors['period_from'] = ["The tax applied for this period has already been paid, please re-check!!!"]
								incomplete_payment = add_extra_info_to_incomplete_payment_for_invoince(incomplete_payment)
								return render_to_response('tax/tax_tax_incomplete_payment_invoice.html', {'form':form,'incomplete_payment':incomplete_payment,'media':medias,},
														context_instance=RequestContext(request))
						else:
							tax_item = PropertyTaxItem()
							tax_item.currency = 'RWF'
							tax_item.period_from = period_from_wtz
							tax_item.period_to = period_to_wtz
							tax_item.due_date = datetime(incomplete_payment.period_to.year,4,1,0,0,0).date()
							tax_item.property = property

						tax_item.date_time = datetime.now()
						tax_item.i_status = 'active'
						tax_item.submit_date = incomplete_payment.paid_date
						tax_item.amount = base_amount

						boundary_date = datetime(2013,4,1,0,0,0).date()
						if incomplete_payment.period_to < boundary_date or incomplete_payment.period_from < boundary_date:
							tax_item.is_paid = True
							tax_item.remaining_amount = 0
							tax_item.amount = incomplete_payment.paid_amount
						else:
							late_fee_amount = TaxMapper.get_late_fee_for_incomplete_payment(incomplete_payment, base_amount)
							if late_fee_amount + base_amount > incomplete_payment.paid_amount:
								tax_item.is_paid = False
								tax_item.remaining_amount = late_fee_amount + base_amount - incomplete_payment.paid_amount 
							else:
								tax_item.is_paid = True
								tax_item.remaining_amount = 0
						tax_item.save()
						
						# create jtax_payrentalincometax record
						pay_tax_item = PayFixedAssetTax()
						pay_tax_item.property_tax_item = tax_item
						pay_tax_item.staff = request.session['user']
						pay_tax_item.amount = incomplete_payment.paid_amount
						pay_tax_item.receipt_no = incomplete_payment.bank_receipt
						pay_tax_item.bank = incomplete_payment.bank
						pay_tax_item.date_time = datetime.now()
						pay_tax_item.note = incomplete_payment.note
						pay_tax_item.i_status = 'active'
						pay_tax_item.paid_date = incomplete_payment.paid_date
						pay_tax_item.manual_receipt = incomplete_payment.sector_receipt
						pay_tax_item.fine_amount = late_fee_amount
						pay_tax_item.save()
						
						#Create media files for fee
						if medias:
							for media in medias:
								media.tags = 'tax|payment'
								media.tax_type = 'fixed_asset'
								media.tax_id = pay_tax_item.id
								media.paymemnt_type = 'pay_fixed_asset'
								media.payment_id = pay_tax_item.id
								media.i_status = 'active'
								media.save()
						
						# set incomplete payment to be inactive
						incomplete_payment.i_status = 'inactive'
						incomplete_payment.save()

						try:
							citizen = Citizen.objects.get(pk=incomplete_payment.citizen_id,i_status='active')
						except Exception:
							citizen = None
						message = "finalized Incomplete Payment (ID: " + str(incomplete_payment.id)  + ") into Fixed Asset tax payment (ReceiptID: " + PaymentMapper.generateInvoiceId('fixed_asset',pay_tax_item) + ")"
						LogMapper.createLog(request,user=user,object=pay_tax_item,action='add',message=message,property=tax_item.property,citizen=citizen)

						return redirect('/admin/tax/incomplete_payment/')
					else:
						incomplete_payment = add_extra_info_to_incomplete_payment_for_invoince(incomplete_payment)
						return render_to_response('tax/tax_tax_incomplete_payment_invoice.html', {'form':form,'incomplete_payment':incomplete_payment,'media':medias,},
												context_instance=RequestContext(request))
				elif incomplete_payment.tax_type == 'trading_license':
					form = finalize_trading_license_tax_form(request.POST)
					if form.is_valid():
						incomplete_payment = IncompletePayment.objects.get(pk = incomplete_payment.id)
						tin =  form.cleaned_data['tin']
						business = form.cleaned_data['business']
						subbusiness = form.cleaned_data['subbusiness']
						paid_amount = int(form.cleaned_data['paid_amount'])
						period_from = form.cleaned_data['period_from']
						period_to = form.cleaned_data['period_to']
						bank = form.cleaned_data['bank']
						bank_receipt = form.cleaned_data['bank_receipt']
						turnover = form.cleaned_data['turnover']
						date_boundary = datetime.strptime('01/04/2013','%d/%m/%Y').date()
						
						base_amount = TaxMapper.get_base_amount_for_incomplete_payment(incomplete_payment,{'turnover':turnover,})
						if business:

							period_from_wtz = timezone.make_aware(dateutil.parser.parse(incomplete_payment.period_from.strftime('%Y-%m-%d') + ' 00:00:00'), timezone.get_default_timezone())
							period_to_wtz = timezone.make_aware(dateutil.parser.parse(incomplete_payment.period_to.strftime('%Y-%m-%d') + ' 23:59:59'), timezone.get_default_timezone())
							if subbusiness:
								taxes = TradingLicenseTax.objects.filter(subbusiness=subbusiness,period_from = period_from_wtz,period_to=period_to_wtz,i_status='active')
							else:
								taxes = TradingLicenseTax.objects.filter(business=business,period_from = period_from_wtz,period_to=period_to_wtz,i_status='active')

							if taxes:
								tax_item = taxes[0]
								if tax_item.is_paid == True:
									form._errors['period_from'] = ["The tax applied for this period has already been paid, please re-check!!!"]
									incomplete_payment = add_extra_info_to_incomplete_payment_for_invoince(incomplete_payment)
									return render_to_response('tax/tax_tax_incomplete_payment_invoice.html', {'form':form,'incomplete_payment':incomplete_payment,'media':medias,},
															context_instance=RequestContext(request))
														
							else:
								tax_item = TradingLicenseTax()
								tax_item.period_from = period_from_wtz
								tax_item.period_to = period_to_wtz
								tax_item.currency = 'RWF'
								tax_item.due_date = datetime(period_from.year + 1,3,31,23,59,59).date()
								tax_item.i_status = 'active'
								#Create a jtax_fee record								
								if subbusiness:
									tax_item.subbusiness = subbusiness
								else:
									tax_item.business = business

							if period_to < date_boundary or period_from < date_boundary:
								tax_item.amount = paid_amount
								tax_item.remaining_amount = 0
								tax_item.is_paid = True
							else:
								tax_item.amount = base_amount
								if tax_item.amount <= paid_amount:
									tax_item.is_paid=True
									tax_item.remaining_amount = 0
									#business.credit = paid_amount - tax_item.amount
									#business.save()
								else:
									tax_item.is_paid = False
									tax_item.remaining_amount = tax_item.amount - paid_amount

							tax_item.date_time = datetime.now()
							tax_item.staff_id = request.session['user'].id
							tax_item.save()
							
							#Create a jtax_payfee record
							pay_tax_item = PayTradingLicenseTax()
							pay_tax_item.business_id = business.id
							pay_tax_item.trading_license_tax = tax_item
							pay_tax_item.receipt_no = bank_receipt
							pay_tax_item.staff = request.session['user']
							pay_tax_item.amount = paid_amount
							pay_tax_item.bank = bank
							if incomplete_payment.note:
								pay_tax_item.note = incomplete_payment.note
							if incomplete_payment.sector_receipt:
								pay_tax_item.manual_receipt = incomplete_payment.sector_receipt
							pay_tax_item.i_status = 'active'
							if incomplete_payment.paid_date:
								pay_tax_item.paid_date = incomplete_payment.paid_date
							pay_tax_item.save()
							
							
							#Create media files for fee
							if medias:
								for media in medias:
									media.tags = 'tax|payment'
									media.tax_type = 'trading_license'
									media.tax_id = tax_item.id
									media.paymemnt_type = 'pay_trading_license'
									media.payment_id = pay_tax_item.id
									media.i_status = 'active'
									media.save()
							
							# set incomplete payment to be inactive
							incomplete_payment.i_status = 'inactive'
							incomplete_payment.save()

							try:
								citizen = Citizen.objects.get(pk=incomplete_payment.citizen_id,i_status='active')
							except Exception:
								citizen = None
							message = "finalized Incomplete Payment (ID: " + str(incomplete_payment.id)  + ") into Trading License tax payment (ReceiptID: " + PaymentMapper.generateInvoiceId('trading_license',pay_tax_item) + ")"
							LogMapper.createLog(request,user=user,object=pay_tax_item,action='add',message=message,business=tax_item.business,subbusiness=tax_item.subbusiness,citizen=citizen)

							return redirect('/admin/tax/incomplete_payment/')
					else:

						incomplete_payment = add_extra_info_to_incomplete_payment_for_invoince(incomplete_payment)
						return render_to_response('tax/tax_tax_incomplete_payment_invoice.html', {'form':form,'incomplete_payment':incomplete_payment,'media':medias,},
												context_instance=RequestContext(request))
		else:
			raise Http404
	else:
		raise Http404


def pending_payment_default(request, action=None, content_type_name1=None, obj_id=None):
	"""
	This funcion manages the following actions related to users. 1)add, 2)change, 3)delete 
	"""	
	if not request.session.get('user') or not type(request.session.get('user')) is PMUser:
		return login(request);

	if not action or action == 'search':
		# show pending payment default page
		payments_found = []
		records_in_page = 20
		limit = 100

		if request.GET.get('submit_search',None) != None:
			search_pending_payment_form = pending_payment_search_form(request.GET)
			kwargs = {'i_status':'active'}
			pending_payments = None
			pagination_url = request.get_full_path().rsplit('?&page')[0]
			if search_pending_payment_form.is_valid():
				data = search_pending_payment_form.cleaned_data

				invoice_id = data['invoice_id']
				citizen_id = data['citizen_id']
				tin = data['tin']
				tax_type = data['tax_type']
				bank = data['bank']
				receipt_no = data['receipt_no']
				manual_receipt = data['manual_receipt']
				period_from = data['period_from']
				period_to = data['period_to']
				upi = data['upi']

				conditions = {}
				if invoice_id and invoice_id!='':
					tax_type_prefix = invoice_id[0:2]
					#case of multiple payments in 1 receipt
					if tax_type_prefix == 'MP':
						tax_type = 'cleaning_fee'
						multipay_receipt = get_object_or_404(MultipayReceipt,pk=invoice_id[2:])
						payment_relations = multipay_receipt.payment_relations.all()
						payment_ids = []
						if payment_relations:
							for i in payment_relations:
								payment_ids.append(i.payfee.id)
						conditions['payment_ids'] = payment_ids
					else:
						#normal single payment
						tax_type = variables.getValueByKey(variables.tax_and_fee_invoice_prefixes,tax_type_prefix)
						try:
							conditions['payment_id'] = int(invoice_id[2:])
						except Exception:
							#if entered invalid invoice id, set invalid payment_id condition to return empty result
							conditions['payment_id'] = -222222

				if citizen_id and citizen_id!='':
					conditions['citizen_id'] = citizen_id
				if upi and upi!='':
					conditions['upi'] = upi
				if tin and tin!='':
					conditions['tin'] = tin
				if tax_type:
					if tax_type in ['Land lease fee','Market fee','Cleaning fee']:
						conditions['fee_type'] = tax_type
				if bank and bank != '':
					conditions['bank'] = bank
				if receipt_no and receipt_no != '':
					conditions['receipt_no'] = receipt_no
				if manual_receipt and manual_receipt != '':
					conditions['manual_receipt'] = manual_receipt
				if period_from and period_from != '':
					#conditions['period_from'] = timezone.make_aware(period_from, timezone.get_default_timezone())
					conditions['period_from'] = timezone.make_aware(datetime.combine(period_from, time(0,0,0)), timezone.get_default_timezone())

				if period_to and period_to != '':
					#conditions['period_to'] = timezone.make_aware(period_to, timezone.get_default_timezone())
					conditions['period_to'] = timezone.make_aware(datetime.combine(period_to, time(23,59,59)), timezone.get_default_timezone())

				#only show active payments
				conditions['i_status'] = 'pending'

				tax_types_to_search = []
				if tax_type and tax_type!='':
					tax_types_to_search.append(tax_type)
				else:
					for c in tax_and_fee_types:
						tax_types_to_search.append(c[0])

				count = 0
				for tax_type_obj in tax_types_to_search:
					remaining_limit = limit - count
					if tax_type_obj == 'fixed_asset':
						payments = PayFixedAssetTaxMapper.getPayFixedAssetTaxByConditions(conditions, remaining_limit)
					elif tax_type_obj == 'rental_income':
						payments = PayRentalIncomeTaxMapper.getPayRentalIncomeTaxByConditions(conditions, remaining_limit)
					elif tax_type_obj == 'trading_license':
						payments = PayTradingLicenseTaxMapper.getPayTradingLicenseTaxByConditions(conditions, remaining_limit)						
					else:
						conditions_new = copy.deepcopy(conditions)
						conditions_new['fee_type'] = tax_type_obj
						payments = PayFeeMapper.getPayFeeByConditions(conditions_new, remaining_limit)

					count = count + len(payments)
					payments_found = payments_found + list(payments)
					#stop at the limit
					if count >= limit:
						break

				if payments_found and len(payments_found) > 0:
					page = 1
					if request.GET.get('page',None) != None:
						page = request.GET.get('page')

					paginator = Paginator(payments_found, records_in_page)
					try:
						pending_payments = paginator.page(page)
					except PageNotAnInteger:
						# If page is not an integer, deliver first page.
						pending_payments = paginator.page(1)
					except EmptyPage:
						# If page is out of range (e.g. 9999), deliver last page of results.
						pending_payments = paginator.page(paginator.num_pages)

					payments_found = formatPaymentsForDisplay(request,pending_payments.object_list)
		
		else:			
			pagination_url = request.get_full_path().rsplit('?&page')[0] + '?'
			search_pending_payment_form = pending_payment_search_form()
			payments_found = []
			pending_payments = PendingPayment.objects.filter(i_status='active')[0:limit]
			page = request.GET.get('page', 1)
			paginator = Paginator(pending_payments, records_in_page)
			try:
				pending_payments = paginator.page(page)
			except PageNotAnInteger:
				# If page is not an integer, deliver first page.
				pending_payments = paginator.page(1)
			except EmptyPage:
				# If page is out of range (e.g. 9999), deliver last page of results.
				pending_payments = paginator.page(paginator.num_pages)

			pending_payment_objects = pending_payments.object_list

			fixed_asset_ids = [ int(i.payment_id) for i in pending_payment_objects if i.tax_type == 'fixed_asset']
			rental_income_ids = [ int(i.payment_id) for i in pending_payment_objects if i.tax_type == 'rental_income']
			trading_license_ids = [ int(i.payment_id) for i in pending_payment_objects if i.tax_type == 'trading_license']
			fee_ids = [ int(i.payment_id) for i in pending_payment_objects if i.tax_type == 'fee']

			pay_fixed_asset_taxes = [i for i in PayFixedAssetTax.objects.filter(i_status='pending', id__in=fixed_asset_ids).select_related('property_tax_item','property_tax_item__property','property_tax_item__property__cell','staff')]
			pay_rental_income_taxes = [ i for i in PayRentalIncomeTax.objects.filter(i_status='pending', id__in=rental_income_ids).select_related('rental_income_tax','rental_income_tax__property','rental_income_tax__property__cell','staff')]
			pay_trading_license_taxes = [ i for i in PayTradingLicenseTax.objects.filter(i_status='pending', id__in=trading_license_ids).select_related('trading_license_tax','trading_license_tax__business','citizen','staff')]
			pay_fees = [ i for i in PayFee.objects.filter(i_status='pending', id__in=fee_ids).select_related('fee','fee__property','fee__property__cell','fee__business','citizen','staff')]

			payments_found = pay_fixed_asset_taxes + pay_rental_income_taxes + pay_trading_license_taxes + pay_fees
			for pf in payments_found:
				pending_payment = [ i for i in pending_payment_objects if int(i.payment_id) == pf.id][0]

			payments_found = formatPaymentsForDisplay(request, payments_found)
		return render_to_response('tax/tax_tax_pending_payment_list.html', {\
							'payments':payments_found, 'page':pending_payments, 'search_pending_payment_form':search_pending_payment_form, 'action':'search','pagination_url':pagination_url,'limit':limit },
							context_instance=RequestContext(request))			

	elif action == 'approve' or action == 'reject':
		if request.GET.get('type', None) != None and request.GET.get('id', None) != None:
			citizen = None
			business = None
			property = None
			subbusiness = None

			#remove pending payment 
			pending_payment = get_object_or_404(PendingPayment,tax_type=request.GET.get('type'),payment_id=request.GET.get('id'),i_status='active')
			if pending_payment.tax_type == 'fixed_asset':
				payment = get_object_or_404(PayFixedAssetTax,id=pending_payment.payment_id,i_status='pending')
				tax = get_object_or_404(PropertyTaxItem,id=pending_payment.tax_id,i_status='active')
				property = tax.property
			elif pending_payment.tax_type == 'rental_income':
				payment = get_object_or_404(PayRentalIncomeTax,id=pending_payment.payment_id,i_status='pending')
				tax = get_object_or_404(RentalIncomeTax,id=pending_payment.tax_id,i_status='active')
				property = tax.property
			elif pending_payment.tax_type == 'trading_license':
				payment = get_object_or_404(PayTradingLicenseTax,id=pending_payment.payment_id,i_status='pending')
				tax = get_object_or_404(TradingLicenseTax,id=pending_payment.tax_id,i_status='active')
				business = tax.business
				subbusiness = tax.subbusiness
			else:
				payment = get_object_or_404(PayFee,id=pending_payment.payment_id,i_status='pending')
				tax = get_object_or_404(Fee,id=pending_payment.tax_id,i_status='active')
				citizen = tax.citizen
				property = tax.property
				business = tax.business
				subbusiness = tax.subbusiness

			user = request.session.get('user')
			if payment.citizen_id:
				citizens = Citizen.objects.filter(pk=payment.citizen_id,i_status='active')
				if citizens:
					citizen = citizens[0]
			if action == 'approve':
				#if approve payment, set pending record to inactive,set payment status to active and update tax to paid
				pending_payment.i_status = 'inactive'
				pending_payment.save()
				
				payment.i_status = 'active'
				payment.note = payment.note + "\n Pending payment approved by " + user.username
				payment.save()

				tax.remaining_amount = 0
				tax.is_paid = True
				tax.save()

				#save log
				tax_name = TaxMapper.getTaxName(tax)
				message = "approved pending payment (" + PaymentMapper.generateInvoiceId(pending_payment.tax_type,payment) + ") " + tax_name + ".Reason: " + pending_payment.reason
				if pending_payment.note:
				   message = message + " (Note: " + pending_payment.note + ")"

				LogMapper.createLog(request,object=pending_payment,citizen=citizen,property=property,business=business,subbusiness=subbusiness,message= message,tax_type=pending_payment.tax_type,tax_id=tax.id,payment_type='pay_'+pending_payment.tax_type,payment_id=payment.id)
			elif action == 'reject':
				#if reject payment, set pending record and payment status to inactive
				pending_payment.i_status = 'inactive'
				pending_payment.save()
				payment.i_status = 'inactive'
				payment.save()

				#save log
				tax_name = TaxMapper.getTaxName(tax)
				message = "rejected pending payment (" + PaymentMapper.generateInvoiceId(pending_payment.tax_type,payment) + ") " + tax_name + ".Reason: " + pending_payment.reason
				if pending_payment.note:
				   message = message + " (Note: " + pending_payment.note + ")"
				LogMapper.createLog(request,object=pending_payment,citizen=citizen,property=property,business=business,subbusiness=subbusiness,message= message,tax_type=pending_payment.tax_type,tax_id=tax.id,payment_type='pay_'+pending_payment.tax_type,payment_id=payment.id)

			referer_url = request.META.get('HTTP_REFERER', None)
			if referer_url:
				return HttpResponseRedirect(referer_url)
			else:
				return HttpResponseRedirect('/admin/tax/pending_payment/')
		else:
			raise Http404		

	else:
		raise Http404


def manage_tax(request):
	if request.method != 'POST' and not request.GET.has_key("plot_id"):
		form = tax_search_property_declarevalue_form()
		return render_to_response('tax/tax_tax_managetax.html',{'form':form,},
							context_instance=RequestContext(request))
	else:
		plot_id = request.GET['plot_id']
		property = PropertyMapper.getPropertyByPlotId(plot_id)
		upi = property.getUPI()
		form = tax_search_property_declarevalue_form(initial={'upi':upi,'parcel_id':property.parcel_id,'cell':property.cell,'sector':property.sector.id,})
		return render_to_response('tax/tax_tax_managetax.html',{'form':form,'plot_id':plot_id,},
							context_instance=RequestContext(request))


def search(request):
	if request.method != 'POST':
		GET = request.GET
		if GET.has_key('page'):
			page = GET["page"]
			paginator = Paginator(request.session.get('properties'), 20)
			properties = paginator.page(page)
			property =properties[0]
			upi_prefix = Common.get_upi_prefix(property.upi)
			sector = property.sector
			new_properties = []
			for obj in properties.object_list:
				ownerships = OwnershipMapper.getCurrentOwnershipsByPropertyId(obj.id)
				all_owners = []
				phone = ''
				email = ''
				taxes = []
				if ownerships:
					for ownership in ownerships:
						all_owners.append(ownership.owner_citizen.getDisplayName())
						if phone == '' and ownership.owner_citizen.phone_1:
							phone = ownership.owner_citizen.phone_1
						if email == '' and ownership.owner_citizen.email:
							email = ownership.owner_citizen.email
				TaxMapper.generateTaxes(obj,request)

				# check whether rental income tax application to this property
				if obj.is_leasing:
					taxes.append('Rental income tax')
				if not obj.is_land_lease:
					fix_asset_tax_item = PropertyTaxItemMapper.getPropertyTaxItem(obj)
					if not fix_asset_tax_item.is_paid:
						taxes.append("Fixed asset tax")
				obj.all_owners = all_owners
				obj.taxes = taxes
				obj.phone = phone
				obj.email = email
				new_properties.append(obj)
			properties.object_list = new_properties
			geodata = PropertyMapper.getPropertyGeoData(properties.object_list)


			query_string = ''
			initials = {}
			if request.session['district']:
				initials['district'] = request.session['district']
				query_string = query_string + "&district=" + str(request.session['district'].id)
			if request.session['sector']:
				initials['sector'] = request.session['sector']
				query_string = query_string + "&sector=" + str(request.session['sector'].id)
			if request.session['cell']:
				initials['cell'] = request.session['cell']
				query_string = query_string + "&cell=" + str(request.session['cell'].id)
			#if request.session['village']:
			#	initials['village'] = request.session['village']
			#	query_string = query_string + "&village=" + request.session['village']
			if request.session['parcel_id']:
				initials['parcel_id'] = request.session['parcel_id']
				query_string = query_string + "&parcel_id=" + str(request.session['parcel_id'])
			if request.session['upi']:
				initials['upi'] = request.session['upi']
				query_string = query_string + "&upi=" + request.session['upi']
			if request.session['citizen_id']:
				initials['citizen_id'] = request.session['citizen_id']
				query_string = query_string + "&citizen_id=" + request.session['citizen_id']
			if request.session['has_ownership']:
				initials['has_ownership'] = request.session['has_ownership']
				query_string = query_string + "&has_ownership=" + request.session['has_ownership']

			form = tax_search_property_form(initial=initials)
			return render_to_response('tax/tax_tax_search.html', {'form':form, 'upi_prefix':upi_prefix, 'sector':sector, 'properties':properties,'geodata':geodata,'query_string':query_string},
								context_instance=RequestContext(request))
		else:
			form = tax_search_property_form(initial={"has_ownership":"all",})
			return render_to_response('tax/tax_tax_search.html',{'form':form,},
							context_instance=RequestContext(request))
	else:
		properties = []
		query_string = ""
		sector = None
		if request.POST.has_key('boundary'):
			query_string = "boundary="+request.POST['boundary']
			form = tax_search_property_form(initial={"has_ownership":"all",})
			boundary = request.POST['boundary']
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
					property.upi = PropertyMapper.getUPIByPropertyId(property.id)
					properties.append(property)
			if properties and len(properties) > 0:
				properties.sort(key=lambda x: (x.sector, x.parcel_id), reverse=False)
		else:
			form = tax_search_property_form(request.POST)
			if form.is_valid():
				district = form.cleaned_data['district']
				sector = form.cleaned_data['sector']
				#village = form.cleaned_data['village']
				parcel_id = form.cleaned_data['parcel_id']
				cell = form.cleaned_data['cell']
				#plot_id = form.cleaned_data['plot_id']
				upi = form.cleaned_data['upi']
				citizen_id = form.cleaned_data['citizen_id']
				has_ownership = form.cleaned_data['has_ownership']

				if district and district!='':
					district = District.objects.get(pk=district)
				request.session['district'] = district
				if sector and sector!="":
					sector = SectorMapper.getSectorById(sector)
				request.session['sector'] = sector
				#request.session['village'] = village

				if cell and cell!="":
					cell = CellMapper.getCellById(cell)
				request.session['cell'] = cell

				form = tax_search_property_form(initial={"district":district,"sector":sector,"cell":cell,"parcel_id":parcel_id,"citizen_id":citizen_id,"upi":upi,"has_ownership":has_ownership,})
				request.session['parcel_id'] = parcel_id
				#request.session['plot_id'] = plot_id
				request.session['upi'] = upi
				request.session['citizen_id'] = citizen_id
				request.session['has_ownership'] = has_ownership

				query_string = query_string + "has_ownership="+has_ownership;
				query_string = query_string + "&citizen_id="+citizen_id
				query_string = query_string + "&upi="+upi
				query_string = query_string + "&parcel_id="+str(parcel_id)
				#query_string = query_string + "&village="+village

				if district:
					query_string = query_string + "&district="+str(district.id)
				if sector:
					query_string = query_string + "&sector="+str(sector.id)
				if cell:
					query_string = query_string + "&cell="+str(cell.id)

				citizen = None
				error_message = None

				if citizen_id:
					citizen = CitizenMapper.getCitizenByCitizenId(citizen_id)
					if not citizen:
						error_message = "No citizen found!"
						return render_to_response('tax/tax_tax_search.html',{'form':form,'error_message':error_message},
								context_instance=RequestContext(request))
				#properties = PropertyMapper.getPropertiesByConditions({'plot_id':plot_id,'sector':sector,'village':village, 'cell':cell, 'parcel_id':parcel_id,'citizen':citizen,'has_ownership':has_ownership,})
				properties = PropertyMapper.getPropertiesByConditions({'upi':upi,'sector':sector, 'cell':cell,'parcel_id':parcel_id,'citizen':citizen,'has_ownership':has_ownership,})


		if properties is None or len(properties) == 0:
			error_message = "No property found!"
			return render_to_response('tax/tax_tax_search.html',{'form':form,'error_message':error_message,'query_string':query_string},
						context_instance=RequestContext(request))
		elif len(properties) == 1:
			property = properties[0]
			property.upi = PropertyMapper.getUPIByPropertyId(property.id)
			summaryInfo = TaxBusiness.getTaxSummary(property)
			geodata = PropertyMapper.getPropertyGeoData(property)
			declaredValues = DeclaredValueMapper.getCleanDeclaredValuesByProperty(property)
			initials = {}
			if request.session.has_key('district') and request.session['district'] and type(request.session['district'])==District:
				initials['district'] = request.session['district']
			if request.session.has_key('sector') and request.session['sector'] and type(request.session['sector'])==Sector:
				initials['sector'] = request.session['sector']
			#if request.session['village'] and request.session['village']!='':
			#	initials['village'] = request.session['village']
			#	query_string = query_string + "&village=" + request.session['village']
			if request.session.has_key('cell') and request.session['cell'] and request.session['cell']!='':
				initials['cell'] = request.session['cell']
			if request.session.has_key('parcel_id') and request.session['parcel_id'] and request.session['parcel_id']!='':
				initials['parcel_id'] = request.session['parcel_id']
			if request.session.has_key('upi') and request.session['upi'] and request.session['upi']!='':
				initials['upi'] = request.session['upi']
			if request.session.has_key('citizen_id') and request.session['citizen_id'] and request.session['citizen_id']!='':
				initials['citizen_id'] = request.session['citizen_id']
			if request.session.has_key('has_ownership') and request.session['has_ownership'] and request.session['has_ownership']!='':
				initials['has_ownership'] = request.session['has_ownership']
			form = tax_search_property_form(initial=initials)
			return render_to_response('tax/tax_tax_search.html', {'sector':sector, 'form':form,'declaredValues':declaredValues,'property':property, 'summary':summaryInfo,'geodata':geodata, 'query_string':query_string},
								context_instance=RequestContext(request))
		else:
			form = tax_search_property_form(initial={"has_ownership":"all",})
			request.session['properties'] = properties
			request.session['form'] = form
			paginator = Paginator(properties, 20)
			properties = paginator.page(1)
			property =properties[0]
			upi_prefix = Common.get_upi_prefix(property.upi)
			new_properties = []
			for obj in properties.object_list:
				ownerships = OwnershipMapper.getCurrentOwnershipsByPropertyId(obj.id)
				owners = []
				phone = ''
				email = ''
				taxes = []
				if ownerships:
					for ownership in ownerships:
						owners.append(ownership.owner_citizen.getDisplayName())
						if phone == '' and ownership.owner_citizen.phone_1:
							phone = ownership.owner_citizen.phone_1
						if email == '' and ownership.owner_citizen.email:
							email = ownership.owner_citizen.email
				TaxMapper.generateTaxes(obj,request)

				# check whether rental income tax application to this property
				if obj.is_leasing:
					taxes.append('Rental income tax')
				if not obj.is_land_lease:
					fix_asset_tax_item = PropertyTaxItemMapper.getPropertyTaxItem(obj)
					if not fix_asset_tax_item.is_paid:
						taxes.append("Fixed asset tax")


				obj.all_owners = owners
				obj.taxes = taxes
				obj.phone = phone
				obj.email = email
				new_properties.append(obj)


				#TaxMapper.generateTaxes(obj,request)
			properties.object_list = new_properties
			geodata = PropertyMapper.getPropertyGeoData(properties.object_list)
			return render_to_response('tax/tax_tax_search.html', {'sector':sector,'upi_prefix':upi_prefix, 'form':form,'properties':properties,'geodata':geodata,'query_string':query_string,},context_instance=RequestContext(request))
		return render_to_response('tax/tax_tax_search.html', {'form':form,},context_instance=RequestContext(request))


def verify_target(request, obj_name, obj_id, part):
	form = verify_target_for_pay_form()
	
	results = []
	if request.method == 'POST':
		POST = request.POST
		form = verify_target_for_pay_form(POST)		
		type = None
		
		if form.is_valid():
			if POST.has_key('pay_citizen_name'):
				type = 'citizen'
				conditions = {}
				conditions['citizen_id'] = form.cleaned_data['pay_citizen_id'].strip()
				conditions['name'] = form.cleaned_data['pay_citizen_name'].strip()
				citizen = None
				citizens =  CitizenMapper.getCitizensByConditions(conditions)

				if not citizens or len(citizens) == 0:
					message = "No citizen found! <a href='/admin/citizen/citizen/add_citizen/?redirect=admin/tax/tax/verify_target/'>Add a new citizen</a> now!"
					return render_to_response('tax/tax_tax_verifycitizen.html',{'form':form,'citizen_message':message,},
						context_instance=RequestContext(request))
				else:
					if len(citizens) > 1:
						results = citizens
						return render_to_response('tax/tax_tax_verifycitizen.html',{'form':form,'results':results,'type':type,},
							context_instance=RequestContext(request))
					else:
						citizen = citizens[0]
						return HttpResponseRedirect('/admin/tax/tax/citizen/' + str(citizen.id) + '/')

			elif POST.has_key('pay_tin'):
				type = 'business'
				tin = form.cleaned_data['pay_tin'].strip()
				name = form.cleaned_data['pay_business_name'].strip()
				owner_id = form.cleaned_data['pay_business_owner_ID'].strip()
				owner_name = form.cleaned_data['pay_business_owner_name'].strip()

				if tin != '':
					businesses = Business.objects.filter(tin__iexact=tin,i_status='active')
				else:
					conditions = {}
					if name!='':
						conditions['name'] = name
					if owner_id and owner_id != '':
						conditions['owner_id'] = owner_id
					if owner_name and owner_name != '':
						conditions['owner_name'] = owner_name

					businesses = BusinessMapper.getBusinessByConditions(conditions)

				if not businesses or len(businesses) == 0:
					message = "No business found! <a href='/admin/asset/business/add_business/?redirect=admin/tax/tax/verify_target/'>Add a new business</a> now!"
					return render_to_response('tax/tax_tax_verifycitizen.html',{'form':form,'business_message':message,},
						context_instance=RequestContext(request))
				else:
					if len(businesses) > 1:
						for i in businesses:
							tmp = {}
							tmp['name'] = i.name + " (TIN: " + i.tin + ")"
							tmp['link'] = '/admin/tax/tax/business/' + str(i.id)+ '/'
							results.append(tmp)
						return render_to_response('tax/tax_tax_verifycitizen.html',{'form':form,'results':results,'type':type,},
							context_instance=RequestContext(request))
					else:
						business = businesses[0]
						return HttpResponseRedirect('/admin/tax/tax/business/' + str(business.id) + '/')
			elif POST.has_key('pay_district'):
				type = 'property'
				upi = form.cleaned_data["pay_upi"]
				parcel_id = form.cleaned_data["pay_parcel_id"]
				cell = form.cleaned_data["pay_cell"]
				sector = form.cleaned_data["pay_sector"]
				district = form.cleaned_data["pay_district"]
				properties = []
				if district and district!="":
					district = int(district)
					district = DistrictMapper.getDistrictById(district)
				if sector and sector!="":
					sector = int(sector)
					sector = SectorMapper.getSectorById(sector)
				if cell and cell!="":
					cell = int(cell)
					cell = CellMapper.getCellById(cell)
				if upi:
					property = PropertyMapper.getPropertyByUPI(upi)
					if property:
						properties.append(property)
				else:
					properties = PropertyMapper.getPropertiesByConditions({'sector':sector,'cell':cell,'parcel_id':parcel_id,})
				
				form = verify_target_for_pay_form(initial={"pay_district":district,"pay_sector":sector,"pay_cell":cell,"pay_parcel_id":parcel_id,"pay_upi":upi,})
				if len(properties) == 0:
					message = "No property found! <a href='/admin/property/property/add_property/?redirect=admin/tax/tax/verify_target/'>Add a new property</a> now!"
					return render_to_response('tax/tax_tax_verifycitizen.html',{'form':form,'property_message':message,},
						context_instance=RequestContext(request))
				else:
					if len(properties) > 1:
						for i in properties:
							tmp = {}
							tmp['name'] = i.getDisplayName() + " (Plot ID: " + i.plot_id + ")"
							tmp['link'] = '/admin/tax/tax/property/' + str(i.id) + '/'
							results.append(tmp)
							return render_to_response('tax/tax_tax_verifycitizen.html',{'form':form,'results':results,'type':type,},
							context_instance=RequestContext(request))
					else:
						property = properties[0]
						return HttpResponseRedirect('/admin/tax/tax/property/' + str(property.id) + '/')
	return render_to_response('tax/tax_tax_verifycitizen.html',{'form':form,},context_instance=RequestContext(request))


def tax_business(request, obj_id, part):
	business = get_object_or_404(Business,id=obj_id)
	#set current citizen into session, clear out all other business/property session data
	if 'citizen' in request.session:
			del request.session['citizen']
	if 'business' in request.session:
			del request.session['business']
	if 'property' in request.session:
			del request.session['property']

	request.session['business'] = business
	TaxMapper.generateTaxes(business,request)
	if part == 'fees':
		request.session['tax_url']  = request.get_full_path()
		fee_summary = getFeeSummary(request, business)
		form = PayFeesForm()
		return render_to_response('tax/tax_tax_business_fees.html',{'business':business,'fees':fee_summary, 'form':form},context_instance=RequestContext(request))
	if part == 'miscellaneous_fees':
		return displayPayMiscellaneousFeePage(request, business)
	elif part == 'history':
		#historical_fees = Historical.objects.filter(business = business).order_by('-period_to')
		paid_taxes = []
		paid_fees = []
		trading_license_tax = TradingLicenseTax.objects.filter(business=business,is_paid=True,i_status__exact="active").order_by('date_time')
		if trading_license_tax:
			for i in trading_license_tax:
				last_payment = i.payments.order_by('-pk')[0]
				i.paid_date = last_payment.date_time
				i.type = 'Trading License Tax '+ str(i.period_to.year)
				if not i.remaining_amount:
					i.remaining_amount = 0
				staff = last_payment.staff
				if not staff:
					i.staff = None
				else:
					i.staff = staff.getFullName()
				i.receipt_no = PaymentMapper.generateInvoiceId('trading_license',last_payment)
				paid_taxes.append(i)		

		fees = Fee.objects.filter(business=business,is_paid=True,i_status__exact="active").order_by('date_time')
		if fees:
			for i in fees:
				last_payment = i.payments.order_by('-pk')[0]
				i.paid_date = last_payment.date_time
				i.type = i.fee_type.title() + ' Fee '
				
				staff = last_payment.staff
				if not staff:
					i.staff = None
				else:
					i.staff = staff.getFullName()

				if not i.remaining_amount:
					i.remaining_amount = 0
				i.receipt_no = PaymentMapper.generateInvoiceId('fee',last_payment)
				paid_fees.append(i)

		misc_fees = MiscellaneousFee.objects.filter(business=business,is_paid=True,i_status__exact="active").order_by('date_time')
		if misc_fees:
			for i in misc_fees:
				last_payment = i.payments.order_by('-pk')[0]
				i.paid_date = last_payment.date_time
				i.type = i.fee_type.replace("_"," ").title() + " - " + i.fee_sub_type.title()
				
				staff = last_payment.staff
				if not staff:
					i.staff = None
				else:
					i.staff = staff.getFullName()

				if not i.remaining_amount:
					i.remaining_amount = 0
				i.receipt_no = PaymentMapper.generateInvoiceId('misc_fee',last_payment)
				paid_fees.append(i)

		#order the result
		paid_taxes.sort(key=lambda x:x.date_time, reverse=True)
		paid_fees.sort(key=lambda x:x.date_time, reverse=True)

		return render_to_response('tax/tax_tax_business_history.html',{'business':business,'paid_taxes':paid_taxes,'fees':paid_fees,},
			context_instance=RequestContext(request))
	elif part == 'logs':
		form = LogSearchForm(initial={'business_id':business.id,})
		conditions = {}
		conditions['business']=business
		logs = []
		if request.method == 'POST':
			form = LogSearchForm(request.POST)
			if form.is_valid():
				username = form.cleaned_data['username']
				upi = form.cleaned_data['upi']
				period_from = form.cleaned_data['period_from']
				period_to = form.cleaned_data['period_to']
				logs = Log.objects.filter(username__icontains=username)
				if username is not None and username.strip() !='':
					conditions['username'] = username.strip()
				if upi is not None and upi.strip() !='':
					conditions['upi'] = upi.strip()
				if period_from is not None:
					conditions['period_from'] = timezone.make_aware(datetime.combine(period_from, time(0,0,0)), timezone.get_default_timezone())
				if period_to is not None:
					conditions['period_to'] = timezone.make_aware(datetime.combine(period_to, time(23,59,59)), timezone.get_default_timezone())
				LogMapper.createLog(request,action="search", search_object_class_name="log", search_conditions = {"username": username,'business_id':business.id,"period_from":period_from, "period_to":period_to})
		logs = LogMapper.getLogsByConditions(conditions)
		if logs:			
			logs = list(logs)
			logs.sort(key=lambda x:x.date_time, reverse=True)
			for log in logs:
				log.message=log.message.replace("User [","<span class='loguser'>User [")
				log.message=log.message.replace("User[","<span class='loguser'>User [")
				log.message=log.message.replace("Business [","<span class='logproperty'>Business [")
				log.message=log.message.replace("business [","<span class='logproperty'>business [")
				log.message=log.message.replace("Citizen [","<span class='logcitizen'>Citizen [")
				log.message=log.message.replace("citizen [","<span class='logcitizen'>Citizen [")
				log.message=log.message.replace("Group [","<span class='loggroup'>Group [")
				log.message=log.message.replace("group [","<span class='loggroup'>Group [")
				log.message=log.message.replace("]","]</span>")

		else:
			logs = []
		return render_to_response('tax/tax_tax_business_logs.html', {'business':business,'logs':logs, 'form':form},
							context_instance=RequestContext(request))
	elif part == 'owners':
		objs= BusinessMapper.getOwnersByBusinessID(business.id)
		return render_to_response('tax/tax_tax_business_owners.html',{'business':business,'ownerships':objs,},
			context_instance=RequestContext(request))
	elif part == 'edit_business':
		request.session['business_url']  = request.get_full_path()
		bus_subcategories_list = json.dumps(list(BusinessSubCategory.objects.values_list('pk','name','business_category')))
		if request.method == 'GET':
			form = BusinessForm(instance=business)
			media = MediaMapper.getMedia('business',business)
			return render_to_response('tax/tax_tax_business_editbusiness.html', {'business':business,'form':form, 'obj_id': business.id,'media':media, 'bus_subcategories_list':bus_subcategories_list},
							context_instance=RequestContext(request))
		else:
			old_data = model_to_dict(business)
			form = BusinessForm(request.POST, instance = business)
			if form.is_valid():
				business = form.save(request)
				if business.business_category:
					fees = business.fee_set.filter(fee_type='cleaning', submit_date__isnull=True)
					for fee in fees:
						fee.calc_tax()

				new_data = model_to_dict(business)
				LogMapper.createLog(request,object=business, old_data=old_data, new_data=new_data,business=business, action="change")
				success_message = 'Business updated successfully.'
				messages.success(request, success_message) 
				if request.GET.get('fee_redirect'):
					return HttpResponseRedirect(reverse("business_fees", args=[business.pk]))	

				return HttpResponseRedirect('/admin/tax/tax/business/%s/edit_business/' % business.pk)

		media = MediaMapper.getMedia('business',business)
		return render_to_response('tax/tax_tax_business_editbusiness.html', {'business':business,'form':form, 'obj_id': business.id,'media':media, 'bus_subcategories_list':bus_subcategories_list},
					context_instance=RequestContext(request))

	elif part == 'media':
		media = MediaMapper.getMedia('business',business)
		request.session['business_url'] = '/admin/tax/tax/business/'+ str(business.id) + '/media/'
		return render_to_response('tax/tax_tax_business_media.html', {'business': business,'media':media},context_instance=RequestContext(request))
	elif not part or part == 'taxes':
		request.session['tax_url']  = request.get_full_path()
		tax_summary = getTaxSummary(request)

		return render_to_response('tax/tax_tax_business_taxes.html',{'business':business,'taxes':tax_summary,},context_instance=RequestContext(request))


def tax_citizen(request, obj_id, part):
	citizen = get_object_or_404(Citizen,id=obj_id)
	#set current citizen into session, clear out all other business/property session data
	if 'citizen' in request.session:
			del request.session['citizen']
	if 'business' in request.session:
			del request.session['business']
	if 'property' in request.session:
			del request.session['property']

	request.session['citizen'] = citizen
	TaxMapper.generateTaxes(citizen,request)
	historical_fees = Historical.objects.filter(citizen = citizen).order_by('-period_to')
	if part == 'fees':
		request.session['tax_url']  = request.get_full_path()
		fee_summary = getFeeSummary(request, citizen)	
		return render_to_response('tax/tax_tax_citizen_fees.html',{'citizen':citizen,'fees':fee_summary,},context_instance=RequestContext(request))
	if part == 'miscellaneous_fees':
		return displayPayMiscellaneousFeePage(request, citizen)
	elif part == 'history':
		paid_taxes = []
		paid_fees = []
		property_ids = request.session.get('property_ids')
		if property_ids:
			for property_id in property_ids:
				try:
					property = Property.objects.get(pk=property_id,i_status='active')
				except Exception:
					continue
				fixed_asset_taxes = PropertyTaxItem.objects.filter(property=property,is_paid=True,i_status__exact="active").order_by('date_time')
				if fixed_asset_taxes:
					for i in fixed_asset_taxes:
						last_payment = i.payments.order_by('-pk')[0]
						i.paid_date = last_payment.date_time
						i.type = 'Fixed Asset Tax '+ str(i.due_date.year)
						if not i.remaining_amount:
							i.remaining_amount = 0
					
						staff = last_payment.staff
						if not staff:
							i.staff = None
						else:
							i.staff = staff.getFullName()
					
					
						if i.is_paid:
							i.is_paid = "Fully paid"
						else:
							if i.remaining_amount > 0 and i.remaining_amount < i.amount:
								i.is_paid = "Partially paid"
							else:
								i.is_paid = "Not paid"

						i.receipt_no = PaymentMapper.generateInvoiceId('fixed_asset',last_payment)
						paid_taxes.append(i)
				rental_income_taxes = RentalIncomeTax.objects.filter(property=property,is_paid=True,i_status__exact="active").order_by('date_time')
				if rental_income_taxes:
					for i in rental_income_taxes:
						last_payment = i.payments.order_by('-pk')[0]
						i.paid_date = last_payment.date_time
						i.type = 'Rental Income Tax '+ str(i.due_date.year)
						staff = last_payment.staff
						if not staff:
							i.staff = None
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

						i.receipt_no = PaymentMapper.generateInvoiceId('rental_income',last_payment)
						paid_taxes.append(i)
				fees = Fee.objects.filter(property=property,is_paid=True,i_status__exact="active").order_by('date_time')
				if fees:
					for i in fees:
						last_payment = i.payments.order_by('-pk')[0]
						i.paid_date = last_payment.date_time
						i.type = i.fee_type.title() + ' Fee '
						staff = last_payment.staff
						if not staff:
							i.staff = None
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
						i.receipt_no = PaymentMapper.generateInvoiceId('fee',last_payment)
						paid_fees.append(i)
				misc_fees = MiscellaneousFee.objects.filter(property=property,is_paid=True,i_status__exact="active").order_by('date_time')
				if misc_fees:
					for i in misc_fees:
						last_payment = i.payments.order_by('-pk')[0]
						i.paid_date = last_payment.date_time
						i.type = i.fee_type.replace("_"," ").title() + " - " + i.fee_sub_type.title()
				
						staff = last_payment.staff
						if not staff:
							i.staff = None
						else:
							i.staff = staff.getFullName()

						if not i.remaining_amount:
							i.remaining_amount = 0
						i.receipt_no = PaymentMapper.generateInvoiceId('misc_fee',last_payment)
						paid_fees.append(i)

		business_ids = request.session.get('business_ids')
		if business_ids:
			for business_id in business_ids:
				trading_license_tax = TradingLicenseTax.objects.filter(business=business_id,is_paid=True,i_status__exact="active").order_by('date_time')
				if trading_license_tax:
					for i in trading_license_tax:
						last_payment = i.payments.order_by('-pk')[0]
						i.paid_date = last_payment.date_time
						i.type = 'Trading License Tax '+ str(i.period_to.year)
						if not i.remaining_amount:
							i.remaining_amount = 0
						staff = last_payment.staff
						if not staff:
							i.staff = None
						else:
							i.staff = staff.getFullName()
						i.receipt_no = PaymentMapper.generateInvoiceId('trading_license',last_payment)
						paid_taxes.append(i)		
				fees = Fee.objects.filter(business=business_id,is_paid=True,i_status__exact="active").order_by('date_time')
				if fees:
					for i in fees:
						last_payment = i.payments.order_by('-pk')[0]
						i.paid_date = last_payment.date_time
						i.type = i.fee_type.title() + ' Fee '
						staff = last_payment.staff
						if not staff:
							i.staff = None
						else:
							i.staff = staff.getFullName()

						if not i.remaining_amount:
							i.remaining_amount = 0
						i.receipt_no = PaymentMapper.generateInvoiceId('fee',last_payment)
						paid_fees.append(i)

				misc_fees = MiscellaneousFee.objects.filter(business=business_id,is_paid=True,i_status__exact="active").order_by('date_time')
				if misc_fees:
					for i in misc_fees:
						last_payment = i.payments.order_by('-pk')[0]
						i.paid_date = last_payment.date_time
						i.type = i.fee_type.replace("_"," ").title() + " - " + i.fee_sub_type.title()
				
						staff = last_payment.staff
						if not staff:
							i.staff = None
						else:
							i.staff = staff.getFullName()

						if not i.remaining_amount:
							i.remaining_amount = 0
						i.receipt_no = PaymentMapper.generateInvoiceId('misc_fee',last_payment)
						paid_fees.append(i)

		#also show miscellaneous fees applied for this citizen
		misc_fees = MiscellaneousFee.objects.filter(citizen=citizen,is_paid=True,i_status__exact="active").order_by('date_time')
		if misc_fees:
			for i in misc_fees:
				last_payment = i.payments.order_by('-pk')[0]
				i.paid_date = last_payment.date_time
				i.type = i.fee_type.replace("_"," ").title() + " - " + i.fee_sub_type.title()
				
				staff = last_payment.staff
				if not staff:
					i.staff = None
				else:
					i.staff = staff.getFullName()

				if not i.remaining_amount:
					i.remaining_amount = 0

				i.receipt_no = PaymentMapper.generateInvoiceId('misc_fee',last_payment)
				paid_fees.append(i)
		fees = Fee.objects.filter(citizen=citizen,is_paid=True,i_status__exact="active").order_by('date_time')
		if fees:
			for i in fees:
				last_payment = i.payments.order_by('-pk')[0]
				i.paid_date = last_payment.date_time
				i.type = i.fee_type.title() + ' Fee '
				staff = last_payment.staff
				if not staff:
					i.staff = None
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
				i.receipt_no = PaymentMapper.generateInvoiceId('fee',last_payment)
				paid_fees.append(i)

		#order the result
		paid_taxes.sort(key=lambda x:x.date_time, reverse=True)
		paid_fees.sort(key=lambda x:x.date_time, reverse=True)

		return render_to_response('tax/tax_tax_citizen_history.html',{'citizen':citizen,'paid_taxes':paid_taxes,'fees':paid_fees,},
			context_instance=RequestContext(request))
	elif part == 'edit_citizen':
		if request.method == 'GET':
			form = CitizenChangeForm(instance = citizen, initial={'obj_id':citizen.id})
			photo_url = None
			if citizen.photo:
				photo_url = citizen.photo.url
			return render_to_response('tax/tax_tax_citizen_editcitizen.html', {'photo_url':photo_url,'citizen':citizen,'form':form,},
			context_instance=RequestContext(request))
		else:
			form = CitizenChangeForm(request.POST, request.FILES,instance = citizen)
			if form.is_valid():
				old_data = model_to_dict(citizen)
				form.save(request)
				citizen=CitizenMapper.getCitizenById(citizen.id)
				new_data = model_to_dict(citizen)
				LogMapper.createLog(request,object=citizen, old_data=old_data,citizen=citizen, new_data=new_data, action="change")
				return_url = "/admin/tax/tax/citizen/"+str(citizen.id)+"/"
				return redirect(return_url)
			else:
				return render_to_response('tax/tax_tax_citizen_editcitizen.html', {'citizen':citizen,'form':form,},
					context_instance=RequestContext(request))
	elif part == 'logs':
		form = LogSearchForm(initial={'citizen_id':citizen.citizen_id,})
		conditions = {}
		conditions['citizen']=citizen
		logs = []
		if request.method == 'POST':
			form = LogSearchForm(request.POST)
			if form.is_valid():
				username = form.cleaned_data['username']
				upi = form.cleaned_data['upi']
				citizen_id = form.cleaned_data['citizen_id']
				period_from = form.cleaned_data['period_from']
				period_to = form.cleaned_data['period_to']
				conditions = {}
				logs = Log.objects.filter(username__icontains=username)
				if username is not None and username.strip() !='':
					conditions['username'] = username.strip()
				if upi is not None and upi.strip() !='':
					conditions['upi'] = upi.strip()
				if period_from is not None:
					conditions['period_from'] = timezone.make_aware(datetime.combine(period_from, time(0,0,0)), timezone.get_default_timezone())
				if period_to is not None:
					conditions['period_to'] = timezone.make_aware(datetime.combine(period_to, time(23,59,59)), timezone.get_default_timezone())
				LogMapper.createLog(request,action="search", search_object_class_name="log", search_conditions = {"username": username,"upi":upi,'citizenid':citizen_id,"period_from":period_from, "period_to":period_to})
		logs = LogMapper.getLogsByConditions(conditions)
		if logs:			
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
				###### replace append upi to log #####
				if log.property:
					log.upi = log.property.getUPI()
				else:
					log.upi = None
		else:
			logs = []
		return render_to_response('tax/tax_tax_citizen_logs.html', {'citizen':citizen,'logs':logs, 'form':form},
							context_instance=RequestContext(request))
	elif part == 'media':
		media = MediaMapper.getMedia('citizen',citizen)
		request.session['citizen_url'] = '/admin/tax/tax/citizen/'+ str(citizen.id) + '/media/'
		return render_to_response('tax/tax_tax_citizen_media.html', {'citizen': citizen,'media':media},context_instance=RequestContext(request))

	elif not part or part == 'taxes':
		request.session['tax_url']  = request.get_full_path()
		tax_summary = getTaxSummary(request)

		return render_to_response('tax/tax_tax_citizen_taxes.html',{'citizen':citizen,'taxes':tax_summary,},context_instance=RequestContext(request))


def tax_property(request, obj_id, part):
	property = get_object_or_404(Property, id=obj_id)
	#set current citizen into session, clear out all other business/property session data
	if 'citizen' in request.session:
			del request.session['citizen']
	if 'business' in request.session:
			del request.session['business']
	if 'property' in request.session:
			del request.session['property']

	request.session['property'] = property
	TaxMapper.generateTaxes(property,request)

	request.session['tax_redirect'] = request.path_info

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
		if len(points_json) == 0:
			points_json = None
		return render_to_response('tax/tax_tax_property_map.html', {'property': property,'points':points_json,},
					context_instance=RequestContext(request))
	if part == 'fees':
		request.session['tax_url']  = request.get_full_path()
		fee_summary = getFeeSummary(request, property)
		return render_to_response('tax/tax_tax_property_fees.html',{'property':property,'fees':fee_summary,},context_instance=RequestContext(request))
	elif part == 'history':
		paid_taxes = []
		paid_fees = []
		fixed_asset_taxes = PropertyTaxItem.objects.filter(property=property,is_paid=True,i_status__exact="active").order_by('date_time')
		if fixed_asset_taxes:
			for i in fixed_asset_taxes:
				last_payment = i.payments.order_by('-pk')[0]
				i.paid_date = last_payment.date_time
				i.type = 'Fixed Asset Tax '+ str(i.due_date.year)
				if not i.remaining_amount:
					i.remaining_amount = 0
				
				staff = last_payment.staff
				if not staff:
					i.staff = None
				else:
					i.staff = staff.getFullName()
				
				if i.is_paid:
					i.is_paid = "Fully paid"
				else:
					if i.remaining_amount > 0 and i.remaining_amount < i.amount:
						i.is_paid = "Partially paid"
					else:
						i.is_paid = "Not paid"
				i.receipt_no = PaymentMapper.generateInvoiceId('fixed_asset',last_payment)
				paid_taxes.append(i)
		rental_income_taxes = RentalIncomeTax.objects.filter(property=property,is_paid=True,i_status__exact="active").order_by('date_time')
		if rental_income_taxes:
			for i in rental_income_taxes:
				last_payment = i.payments.order_by('-pk')[0]
				i.paid_date = last_payment.date_time
				i.type = 'Rental Income Tax '+ str(i.due_date.year)
				
				staff = last_payment.staff
				if not staff:
					i.staff = None
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
				i.receipt_no = PaymentMapper.generateInvoiceId('rental_income',last_payment)
				paid_taxes.append(i)
		fees = Fee.objects.filter(property=property,is_paid=True,i_status__exact="active").order_by('date_time')
		if fees:
			for i in fees:
				last_payment = i.payments.order_by('-pk')[0]
				i.paid_date = last_payment.date_time
				i.type = i.fee_type.title() + ' Fee '
				
				staff = last_payment.staff
				if not staff:
					i.staff = None
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
				i.receipt_no = PaymentMapper.generateInvoiceId('fee',last_payment)
				paid_fees.append(i)

		misc_fees = MiscellaneousFee.objects.filter(property=property,is_paid=True,i_status__exact="active").order_by('date_time')
		if misc_fees:
			for i in misc_fees:
				last_payment = i.payments.order_by('-pk')[0]
				i.paid_date = last_payment.date_time
				i.type = i.fee_type.replace("_"," ").title() + " - " + i.fee_sub_type.title()
				
				staff = last_payment.staff
				if not staff:
					i.staff = None
				else:
					i.staff = staff.getFullName()

				if not i.remaining_amount:
					i.remaining_amount = 0
				i.receipt_no = PaymentMapper.generateInvoiceId('misc_fee',last_payment)
				paid_fees.append(i)

		#order the result
		paid_taxes.sort(key=lambda x:x.date_time, reverse=True)
		paid_fees.sort(key=lambda x:x.date_time, reverse=True)

		return render_to_response('tax/tax_tax_property_history.html',{'property':property,'paid_taxes':paid_taxes,'fees':paid_fees},
			context_instance=RequestContext(request))
	elif part == 'media':
		media = MediaMapper.getMedia('property',property)
		request.session['property_url'] = '/admin/tax/tax/property/'+ str(property.id) + '/media/'
		return render_to_response('tax/tax_tax_property_media.html', {'property': property,'media':media},context_instance=RequestContext(request))
	elif part == 'logs':
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
		return render_to_response('tax/tax_tax_property_logs.html', {'property':property,'logs':logs, 'form':form},
							context_instance=RequestContext(request))


	elif not part or part == 'taxes':
		request.session['tax_url']  = request.get_full_path()
		tax_summary = getTaxSummary(request)
		return render_to_response('tax/tax_tax_property_taxes.html',{'property':property,'taxes':tax_summary,},context_instance=RequestContext(request))


def getFeeSummary(request, obj):
	fee_summary = []
	fees = Fee.objects.filter(is_paid=False, i_status='active')

	if type(obj) is Property:
		fees = fees.filter( property__pk=obj.pk )

	if type(obj) is Citizen:
		properties = obj.get_properties().values_list('pk',flat=True)
		fees = fees.filter( Q(citizen__pk=obj.pk) | Q(property__pk__in=properties))

	if type(obj) is SubBusiness:
		properties = obj.get_properties().values_list('pk',flat=True)
		fees = Fee.objects.filter(Q(subbusiness__pk=obj.pk) | Q(property__pk__in=properties))

	elif type(obj) is Business:
		properties = obj.get_properties().values_list('pk',flat=True)
		fees = Fee.objects.filter(Q(business__pk=obj.pk) | Q(subbusiness__business__pk=obj.pk) | Q(property__pk__in=properties))

	fees = fees.order_by('-pk')
	fee_summary = fee_summary + formatTaxesForDisplay(request,'fee',fees)
	return fee_summary


def getTaxSummary(request):
	tax_summary = []
	
	#start checking fixed asset taxes & rental income taxes
	property_ids = request.session.get('property_ids')
	if property_ids:
		fixed_asset_taxes = PropertyTaxItem.objects.filter(property__id__in=property_ids,is_paid=False,i_status='active').order_by('-due_date')
		tax_summary = tax_summary + formatTaxesForDisplay(request,'fixed_asset',fixed_asset_taxes)

		#start checking rental income taxes
		rental_income_taxes = RentalIncomeTax.objects.filter(property__id__in=property_ids,is_paid=False,i_status='active').order_by('-due_date')
		tax_summary = tax_summary + formatTaxesForDisplay(request,'rental_income',rental_income_taxes)		


	#start checking trading license taxes
	business_ids = request.session.get('business_ids')
	if business_ids:
		trading_license_taxes = TradingLicenseTax.objects.filter(is_paid=False,i_status='active').filter(Q(business__id__in=business_ids)|Q(subbusiness__business__id__in=business_ids)).order_by('-due_date')
		tax_summary = tax_summary + formatTaxesForDisplay(request,'trading_license',trading_license_taxes)

	return tax_summary


def formatTaxesForDisplay(request, type, taxes):
	list = []
	today = timezone.make_aware(datetime.combine(datetime.today(), time(0,0)), timezone.get_default_timezone())
	current_year = str(today.year)
	year_start = timezone.make_aware(dateutil.parser.parse(current_year + '-01-01 00:00:00'), timezone.get_default_timezone())
	year_end = timezone.make_aware(dateutil.parser.parse(current_year + '-12-31 23:59:59'), timezone.get_default_timezone())
	first_installment_due_date = timezone.make_aware(dateutil.parser.parse(current_year + '-03-31'), timezone.get_default_timezone())
	if taxes:
		for i in taxes:
			tax = {}
			tax['id'] = i.id
			tax['multi_pay'] = False
			tax['submit_date'] = i.submit_date
			details = calculatePaymentDetails(type,i)

			if i.is_paid:
				amount = int(i.amount)
			else:
				amount = details['amount']

			tax['is_paid'] = i.is_paid
			tax['amount'] = amount
			if type == 'fixed_asset':
				tax['name'] = 'Fixed Asset Tax ' + str(i.due_date.year)
				"""
				if amount == None:
					request.session['tax_redirect'] = request.path_info

					tax['prerequisite_link'] = '/admin/property/property/view_property/' + str(i.property.id) + '/declarevalues/?redirect=tax'
					tax['prerequisite_label'] = 'submit declared value'
				"""

			elif type == 'rental_income':
				tax['name'] = 'Rental Income Tax ' + str(i.due_date.year)

			elif type == 'trading_license':
				business = i.business
				tax['name'] = 'Trading License Tax '
				if i.due_date:
					tax['name'] = tax['name'] + str(Common.localizeDate(i.period_from).year)
					
				if i.subbusiness:
					tax['branch'] = i.subbusiness.branch
				else:
					tax['branch'] = 'Main'

			elif type == 'fee':
				if i.fee_type == 'misc_fee' and i.amount and not i.is_paid:
					tax['multi_pay'] = False
					tax['branch'] = None
					if i.citizen:
						tax['obj_id'] = i.citizen.id
					elif i.subbusiness:
						tax['obj_id'] = i.subbusiness.pk
					elif i.business:
						tax['obj_id'] = i.business.pk
					tax['name'] = i.name
				elif (i.fee_type == 'land_lease' and (i.property and i.property.is_land_lease or i.is_paid)) or (i.fee_type == 'cleaning' and ((i.business and not i.business.business_type == 'No premises' or i.is_paid) or (i.subbusiness and not i.subbusiness.business.business_type == 'No premises' or i.is_paid))) or (i.fee_type == 'market' and ((i.business and i.business.market_fee_applicable) or (i.subbusiness and i.subbusiness.business.market_fee_applicable))):
					tax['name'] = i.fee_type.replace('_',' ').title()
					if i.fee_type == 'land_lease':
						tax['name'] = tax['name'] + ' ' + str(i.due_date.year)
					tax['fee_type'] = i.fee_type

					if i.fee_type == 'cleaning' or i.fee_type == 'market':
						if i.subbusiness:
							tax['branch'] = i.subbusiness.branch
							tax['obj_id'] = i.subbusiness.business.id
						else:
							tax['branch'] = 'Main'
							tax['obj_id'] = i.business.id

						#only allow multiple payment for cleaning fee with existing amount atm
						if (i.amount or i.fee_type == 'market') and i.is_paid == False:
							tax['multi_pay'] = True
				else:
					continue

			#only allow set up payment installments for taxes/fees that cover the full year, and haven't been overdued, and current time less that the first installment due date

			#if i.is_paid==False and i.amount and i.amount > 0 and i.period_from == year_start and i.period_to == year_end and (not i.submit_details or i.submit_details.find("overdue_installment") < 0 ) :
			#	tax['installment_plan_link'] = '/admin/tax/tax/setup_installments/?type=' + type + '&id=' + str(i.id)

			tax['target'] = getTaxReference(type,i)

			#if tax has a pending payment, set pending_payment flag, otherwise set up action links
			pending_payments = PendingPayment.objects.filter(tax_type=type,tax_id=i.id,i_status='active')
			if pending_payments:
				tax['has_pending_payment'] = True
			else:
				tax['has_pending_payment'] = False

				#if there is no multi pay tax, display the view epay invoice & pay buttons
				if not tax['multi_pay']:
					tax['link'] = '/admin/tax/tax/pay_taxes/?type=' + type + '&id=' + str(i.id)
					#tax['upload_link'] = '/admin/tax/tax/upload_media/?type=fixed_asset&id=' + str(i.id)
					if not i.is_paid and i.amount:
						tax['epay_invoice_link'] = '/admin/tax/tax/generate_epayinvoice/?type=' + type + '&id=' + str(i.id)

					if (type != 'fee' or i.fee_type not in ('cleaning','market')):
						tax['submit_link'] = '/admin/tax/tax/submit_tax/?type=' + type + '&id=' + str(i.id)

			#set up receipt links if paid
			if i.is_paid:
				payments = i.payments.filter(i_status='active')
				receipt_links = []
				if payments:
					for payment in payments:
						receipt_links.append("/admin/tax/tax/generate_invoice/?type=" + type + "&id=" + str(payment.id))
				tax['receipt_links'] = receipt_links

			tax['past_payments_link'] = None
			if i.amount and i.remaining_amount != None and (i.remaining_amount < i.amount or i.is_paid == True or tax['has_pending_payment'] == True):
				tax['past_payments_link'] = '/admin/tax/tax/past_payments/?type=' + type + '&id=' + str(i.id)

			tax['due_date'] = i.due_date
			tax['currency'] = i.currency
			tax['payment_details'] = details
			media_tax_type = type
			if type == 'fee':
				media_tax_type = i.fee_type + '_fee'
			tax['medias'] = Media.objects.filter(tax_type__exact=media_tax_type,tax_id__exact=i.id,i_status='active')

			list.append(tax)
	return list


def formatPaymentsForDisplay(request,payments):
	payments_found = []
	fee_payments = []
	payment_ids = {'misc_fee':[],'fixed_asset':[],'trading_license':[],'rental_income':[],'fee':[]}
	pending_ids = []
	if payments:
		for payment in payments:
			payment_obj = {}

			payment_obj['id'] = payment.id
			upi = 'N/A'

			if type(payment) is PayFixedAssetTax:
				tax = payment.property_tax_item
				tax_type = 'fixed_asset'
				upi = tax.property.getUPI()		

			elif type(payment) is PayRentalIncomeTax:
				tax = payment.rental_income_tax
				tax_type = 'rental_income'
				upi = tax.property.getUPI()		

			elif type(payment) is PayTradingLicenseTax:
				tax = payment.trading_license_tax
				tax_type = 'trading_license'

			elif type(payment) is PayMiscellaneousFee:
				tax = payment.fee
				tax_type = 'misc_fee'
				if tax.property:
					upi = tax.property.getUPI()		
			else:
				tax = payment.fee
				tax_type = 'fee'
				if tax.property:
					upi = tax.property.getUPI()		
			payment_obj['type'] = tax_type.replace(" ","_")

			if (tax_type == 'fee' or tax_type == 'misc_fee') and tax.citizen:
				national_citizen_id = tax.citizen.citizen_id
			else:
				national_citizen_id = 'N/A'

			business_label = 'N/A'
			if tax_type == 'fee' or tax_type == 'misc_fee' or tax_type == 'trading_license':
				if tax.business:
					business = tax.business
					business_label = business.name + ' (TIN: ' + business.tin + ')'
				elif tax.subbusiness:
					business = tax.subbusiness.business
					business_label = business.name + ' (TIN: ' + business.tin + ')'	+ ' - ' + tax.subbusiness.branch 							

			if (type(tax) is Fee):
				if tax.fee_type == 'cleaning' or tax.fee_type == 'market':
					tax_name =  tax.fee_type.replace('_',' ').title() + ' Fee for period ' + str(Common.localizeDate(tax.period_from).strftime('%d/%m/%Y')) + ' - ' +  str(Common.localizeDate(tax.period_to).strftime('%d/%m/%Y'))
				else:
					tax_name =  tax.fee_type.replace('_',' ').title() + ' Fee for period ' + str(Common.localizeDate(tax.period_from).strftime('%d/%m/%Y')) + ' - ' +  str(Common.localizeDate(tax.period_to).strftime('%d/%m/%Y'))
			elif type(tax) is MiscellaneousFee:
				tax_name = tax.fee_type.replace('_',' ').title() + ' - ' + tax.fee_sub_type.title()
			else:
				tax_name = tax_type.replace('_',' ').title() + ' for period ' + str(Common.localizeDate(tax.period_from).strftime('%d/%m/%Y')) + ' - ' +  str(Common.localizeDate(tax.period_to).strftime('%d/%m/%Y'))

			payment_obj['tax_type'] = tax_type
			payment_obj['invoice_id'] = PaymentMapper.generateInvoiceId(tax_type.replace(" tax",'').replace(" ","_").lower(),payment)
			payment_obj['citizen_id'] = national_citizen_id
			payment_obj['business'] = business_label
			#payment_obj['plot_id'] = 'N/A'
			payment_obj['upi'] = upi
			payment_obj['tax_name'] = tax_name
			payment_obj['bank'] = variables.getFullBankName(payment.bank)
			payment_obj['receipt_no'] = payment.receipt_no
			payment_obj['manual_receipt'] = payment.manual_receipt
			payment_obj['paid_date'] = payment.paid_date
			payment_obj['date_time'] = payment.date_time
			payment_obj['amount'] = payment.amount
			payment_obj['amount_due'] = tax.amount
			payment_obj['note'] = payment.note
			payment_obj['status'] = payment.i_status
			#try:
			#	staff = last_payment.staff
			#except Exception:
			#	staff = None
			payment_obj['staff'] = payment.staff

			#getting receipt info for display 
			if type(tax) is MiscellaneousFee:
				payment_obj['receipt_link'] = '/admin/tax/tax/generate_invoice/?type=misc_fee' + '&id=' + str(payment_obj['id'])
			elif type(tax) is Fee:
				fee_payments.append(payment)
				payment_obj['receipt_link'] = '/admin/tax/tax/generate_invoice/?type=fee' + '&id=' + str(payment_obj['id'])
			else:
				payment_obj['receipt_link'] = '/admin/tax/tax/generate_invoice/?type=' + tax_type + '&id=' + str(payment_obj['id'])

			#save payment ids per tax type to mass fetching media later
			payment_ids[tax_type].append(payment.id)

			#save pending payment ids to mass fetching pending reason/note later
			if payment.i_status == 'pending':
				pending_ids.append(payment.id)

			payments_found.append(payment_obj)


	#start getting the media info for display, also overwrite the receipt links for multipaid payments
	medias = {}
	multipaid_receipt_links = {}
	multipaid_payment_ids = []

	#get the list of multitask relations that associated with the formatting payments
	receipts = MultipayReceipt.objects.filter(payment_relations__payfee__in=fee_payments,payment_relations__i_status__exact='active',i_status='active').distinct()

	if receipts:
		for i in receipts:
			temp_ids = []
			payment_relations = i.payment_relations.all().select_related('payfee')
						
			for relation in payment_relations:
				multipaid_receipt_links[relation.payfee.id] = '/admin/tax/tax/generate_multipayinvoice/?type=fee' + '&id=' + str(i.id)
				temp_ids.append(relation.payfee.id)
				multipaid_payment_ids.append(relation.payfee.id)
			multipaid_media = Media.objects.filter(payment_type__exact='pay_fee',payment_id__in=temp_ids)
			if temp_ids:
				for id in temp_ids:
					medias['fee_' + str(id)] = multipaid_media

	#get the normal payment medias
	for tax_type,list in payment_ids.items():
		if list:			
			temp_medias = Media.objects.filter(payment_type__exact='pay_' + tax_type,payment_id__in=list)
			if temp_medias:
				for i in temp_medias:
					if i.payment_id not in multipaid_payment_ids:
						if medias.has_key(tax_type +'_' + str(i.payment_id)):
							medias[tax_type + '_' + str(i.payment_id)].append(i)
						else:
							medias[tax_type + '_' + str(i.payment_id)] = [i]

	#get any pending reason/note if applicable
	pending_info = {}
	if pending_ids:
		pending_records = PendingPayment.objects.filter(payment_id__in=pending_ids,i_status='active')
		if pending_records:
			for i in pending_records:
				pending_info[i.tax_type + '_' + str(i.payment_id)] = {'reason':i.reason,'note':i.note}
		
	#append the found receipt links and media into the formated payment list
	if payments_found:
		for payment in payments_found:
			if payment['tax_type'] == 'fee' and multipaid_receipt_links.has_key(payment['id']):
				payment['receipt_link'] = multipaid_receipt_links[payment['id']]

			if medias.has_key(payment['tax_type'] + '_' + str(payment['id'])):
				payment['medias'] = medias[payment['tax_type'] + '_' + str(payment['id'])]

			if pending_info.has_key(payment['tax_type'] + '_' + str(payment['id'])):
				payment['pending_reason'] = pending_info[payment['tax_type'] + '_' + str(payment['id'])]['reason']
				payment['pending_note'] = pending_info[payment['tax_type'] + '_' + str(payment['id'])]['note']

	return payments_found

def getFeeCart(request):
	misc_payments = request.session.setdefault('misc_payment', {'total':0, 'payments':{}})
	total = 0
	for k,v in misc_payments['payments'].iteritems():
		total += v['subtotal']
	misc_payments['total'] = total
	json_data = json.dumps(misc_payments);
	request.session['misc_payment'] = misc_payments
	return HttpResponse(json_data, mimetype='application/json')


@csrf_exempt
def addFee(request):
	misc_payments = request.session.setdefault('misc_payment', {'total':0, 'payments':{}})
	qty = int(request.POST.get('qty', 0))
	pk = int(request.POST.get('pk', 0))
	setting = get_object_or_404(Setting, pk=pk)
	value = Decimal(setting.value)
	subtotal = float(Decimal(value * Decimal(qty)).quantize(Decimal('0.01')))
	if qty > 0:
		payment = misc_payments['payments'].setdefault(pk, { 'qty':qty, 'subtotal':subtotal, 'name':setting.sub_type,  'description':setting.description })
		payment['qty'] = qty
		payment['subtotal'] = subtotal
		payment['name'] = setting.sub_type
		payment['description'] = setting.description
	else:
		if misc_payments['payments'].get(pk):
			del(misc_payments['payments'][pk])
	return getFeeCart(request)


def payMiscFee(request):
	#display payment form

	if request.POST:
		pass
		#create payment objects from the session
		#create multipay record? 
		#delete the session


def clearMiscFees(request):
	request.session['misc_payment'] = { 'total':0, 'payments': {} }
	return request.get_full_path()


@csrf_exempt
def getMiscFees(request):
	district=request.GET.get('district')
	sector=request.GET.get('sector')
	cell=request.GET.get('cell')
	village=request.GET.get('village')
	fees = Setting.getFees(district, sector , cell, village)
	fees = fees.get(request.GET.get('category'))
	for fee_name, settings in fees.iteritems():
		fees[fee_name]['region'] = fees[fee_name]['region'].name
		fees[fee_name]['valid_from'] = None
		fees[fee_name]['value'] = float(fees[fee_name]['value'])
		misc_payment = request.session.get('misc_payment')
		if misc_payment:
			payments = misc_payment.get('payments')
			if payments.get(settings['pk']):
				fees[fee_name]['qty'] = payments.get(settings['pk']).get('qty')
			else:
				fees[fee_name]['qty'] = 0
		else:
			fee[fee_name]['qty'] = 0
	json_data = json.dumps(fees)
	return HttpResponse(json_data, mimetype='application/json')


def getDistricts(request):
	districts = list(District.objects.order_by('name').values_list('id','name'))
	districts = [(key, name.upper()) for (key, name) in districts]
	json_data = json.dumps(districts)
	return HttpResponse(json_data, mimetype='application/json')


@csrf_exempt
def getMiscFeeCategories(request):
	district=request.GET.get('district')
	sector=request.GET.get('sector')
	cell=request.GET.get('cell')
	village=request.GET.get('village')
	fees = Setting.getFees(district, sector, cell, village)
	if fees:
		categories = fees.keys()
	else:
		categories = None
	json_data = json.dumps(categories);
	return HttpResponse(json_data, mimetype='application/json')


@csrf_exempt
def submitMiscFee(request):
	business=None
	citizen=None
	misc_payments = request.session.setdefault('misc_payment', { 'total':0 , 'payments': {}} )
	citizen_pk = int(request.POST.get('citizen_pk'))
	business_pk = int(request.POST.get('business_pk'))
	if citizen_pk:
		citizen = Citizen.objects.get(pk=citizen_pk)
	elif business_pk:
		business = Business.objects.get(pk=business_pk)
	
	tz_date_from = timezone.now()
	date_from = tz_date_from.date()
	no_payments = len(misc_payments['payments'])
	for key, payment in misc_payments['payments'].iteritems():
		if 'month' in payment.setdefault('description',''):
			tz_date_to = tz_date_from + relativedelta(months=payment['qty'])
		elif 'year' or 'annual' in payment.setdefault('description'):
			tz_date_to = tz_date_from + relativedelta(years=1)
		date_to = tz_date_to.date()
		amount = payment['subtotal']
		name = payment['name']
		fee = Fee.objects.create(fee_type='misc_fee', amount=amount, remaining_amount=amount, currency='RWF', citizen=citizen, business=business, 
			name=name[:50], period_from = tz_date_from, period_to=tz_date_to, date_from=date_from, date_to=date_to, submit_date=timezone.now(), quantity=payment['qty'])
	request.session['misc_payment'] = {'total':0, 'payments':{}}
	if no_payments == 1:
		redirect_url = reverse('pay_fee', args=('fee', fee.pk))
	else:
		if citizen_pk:
			redirect_url = reverse('citizen_fees', args=(citizen_pk,))
		elif business_pk:
			redirect_url = reverse('business_fees', args=(business_pk,))
		elif property_pk:
			redirect_url = reverse('property_fees', args=(property_pk,))
	json_data = json.dumps(redirect_url);
	return HttpResponse(json_data, mimetype='application/json')


def miscFee(request, citizen_pk=None, business_pk=None):
	business = None
	citizen = None
	if citizen_pk:
		citizen = get_object_or_404(Citizen, pk=citizen_pk)
		template_type = 'citizen'
	if business_pk:
		business = get_object_or_404(Business, pk=business_pk)
		template_type = 'business'
		
	return render_to_response('tax/misc_fees.html',{ 'template_type':template_type, 'business':business, 'citizen':citizen }, context_instance=RequestContext(request))


def displayPayMiscellaneousFeePage(request, obj):
	business = None
	citizen = None
	property = None
	staff = request.session.get('user')
	staff_id = staff.id
	template_type = ''
	if type(obj) is Citizen:
		citizen = obj
		setting_name = 'citizen_miscellaneous_fee'
		template_type = 'citizen'
	elif type(obj) is Business:
		business = obj
		setting_name = 'business_miscellaneous_fee'
		template_type = 'business'
	#elif type(obj) is Property:
	#	property = obj

	form = PayMiscellaneousFeeForm()
	form.business = business
	form.citizen = citizen
	form.property = property
	#get list of miscellaneous fees available in the tax settings
	fee_types = TaxMapper.getTaxSetting(setting_name)

	if request.method == 'POST':
		form = PayMiscellaneousFeeForm(request.POST)
		data = request.POST
		#generate the miscellaneous fee item based on submitted info
		fee = MiscellaneousFee(amount=data['amount'],remaining_amount=data['amount'],fee_type=data['fee_type'],fee_sub_type=data['fee_sub_type'], business=business,citizen=citizen,property=property,currency='RWF',is_paid=False,staff_id=staff_id)
		fee.save()
		form.fee = fee
		
		#if only submit Tax information without Paying, calculate Tax Amount only
		if request.POST.get('submit',None) != None:
			fee.submit_date = timezone.make_aware(datetime.combine(datetime.today(), time(0,0)), timezone.get_default_timezone())
			fee.save()

			message = "add a submission for " + str(fee)
			LogMapper.createLog(request,object=fee,citizen=citizen,property=property,business=business,message= message,tax_type='misc_fee',tax_id=fee.id)
			if request.session.has_key('tax_url'):
				request.session['tax_url'] = request.session['tax_url'].replace("/fees/","/miscellaneous_fees/")
			#redirect to the receipt page
			return HttpResponseRedirect('/admin/tax/tax/generate_epayinvoice/?type=misc_fee' +  '&id=' + str(fee.id))
		#if Finalize (Pay Tax), add new Payment object etc
		else:
			if form.is_valid():
				payment = form.save(False)
				payment.business = business
				payment.citizen = citizen
				payment.fee = fee
				payment.staff = staff
				payment.save()

				fee.remaining_amount = 0
				fee.is_paid = True
				fee.save()
			
				message = "add a Payment of " + str(payment.amount) + fee.currency.title() + " for " + str(fee)
				LogMapper.createLog(request,object=fee,citizen=citizen,property=property,business=business,message= message,tax_type='misc_fee',tax_id=fee.id,payment_type='pay_misc_fee',payment_id=payment.id)
				if request.session.has_key('tax_url'):
					request.session['tax_url'] = request.session['tax_url'].replace("/fees/","/miscellaneous_fees/")
				#redirect to the receipt page
				return HttpResponseRedirect('/admin/tax/tax/generate_invoice/?type=misc_fee' + '&id=' + str(payment.id))

	#get list of submitted but unpaid miscellaneous fee:
	fees = MiscellaneousFee.objects.filter(business=business,citizen=citizen,property=property,i_status='active',is_paid=False)
	if fees:
		for i in fees:
			i.medias = 	Media.objects.filter(tax_type__exact='misc_fee',tax_id__exact=i.id,i_status='active')
			i.epay_invoice_link = '/admin/tax/tax/generate_epayinvoice/?type=misc_fee' +  '&id=' + str(i.id)

	return render_to_response('tax/tax_tax_paymiscellaneousfees.html',{'template_type':template_type,'business':business,'citizen':citizen,'property':property,'fees':fees,'fee_types':fee_types,'form':form},context_instance=RequestContext(request))



def payFixedAsset(request, id):

	tax = get_object_or_404(PropertyTaxItem, pk=id)
	if tax.amount is None:
		return HttpResponseRedirect(reverse('submit_fixed_asset', args=[id]))	
	
	if request.POST: #make the payment
		form = PayFixedAssetTaxForm(request.POST)
		if form.is_valid():
			payment = tax.calculatePayment(form.cleaned_data.get('paid_date', date.today()))
			payment_object = form.save(commit=False)
			payment_object.tax = tax
			payment_object.staff = request.session.get('user')
			payment_object.fine_amount = payment['late_fees'] + form.cleaned_data['fine']
			capital_amount = payment_object.amount - payment_object.fine_amount
			fee.remaining_amount = fee.remaining_amount - capital_amount
			if fee.remaining_amount < 0:
				fee.remaining_amount = 0
			if fee.remaining_amount == 0:
				fee.is_payed = True
			fee.save()
			payment_object.fine_description = "Late fee surcharge %s %s and late fee interest %s %s -%s" % (str(Common.formatCurrency(payment['surcharge'])), fee.currency.title(), str(Common.formatCurrency(payment['interest'])), fee.currency.title(), form.cleaned_data['fine_description'] )
			payment_object.save()
			# pay off installment
			TaxMapper.pay_installment(fee, capital_amount, paid_on=form.cleaned_data.get('paid_date'))
			redirect_url = '/admin/tax/tax/generate_invoice/?type=land_lease&id='+ str(payment_object.pk)
			return HttpResponseRedirect(redirect_url)
		else:
			payment = tax.calculatePayment()
	else:
		payment = fee.calculatePayment()	
		form = PayFixedAssetTaxForm(initial={'amount':payment['total_due']})
	
	return render_to_response('tax/paylandlease.html',{ 'form':form,'tax':fee,'payment':payment,
		'pending_payment_reasons':variables.pending_payment_reasons},
		context_instance=RequestContext(request))

def submitTaxPatch(request):
	id = request.GET.get('id')
	tax_type = request.GET.get('type')
	if tax_type == 'fee':
		fee = get_object_or_404(Fee, pk=id)
		if fee.fee_type == 'land_lease':
			return submitLandLease(request, id)
		else:
			return access_content_type(request,  'tax', action = 'pay', content_type_name1 = 'taxes')
	elif tax_type == 'rental_income':
			return submitRentalIncome(request, id)
	elif tax_type == 'trading_license':
		return submitTradingLicense(request, id)
	elif tax_type == 'fixed_asset':
		return submitFixedAssetTax(request, id)
	else:
		return access_content_type(request,  'tax', action = 'pay', content_type_name1 = 'taxes')


def processPayment(request):
	form = confirmPaymentForm(request.POST)
	if form.is_valid():
		fee_id = id = form.cleaned_data.get('fee_id')
		fee_type = form.cleaned_data.get('fee_type')

		if fee_type in ('fee', 'land_lease'):
			fee = get_object_or_404(Fee, pk=id)
		elif fee_type == 'fixed_asset':
			fee = get_object_or_404(PropertyTaxItem, pk=id)
		elif fee_type == 'trading_license':
			fee = get_object_or_404(TradingLicenseTax, pk=id)
		elif fee_type == 'rental_income':
			fee = get_object_or_404(RentalIncomeTax, pk=id)
		late_fees = form.cleaned_data.get('late_fees')

		posted = request.POST.copy()
		posted['i_status'] = 'active'
		form = paymentForm(fee)(posted)
		if form.is_valid():
			payment_object = form.save(commit=False)
			if fee_type in ('fee', 'land_lease'):
				payment_object.fee = fee
			elif fee_type == 'fixed_asset':
				payment_object.property_tax_item = fee
			elif fee_type == 'trading_license':
				payment_object.trading_license_tax = fee
			elif fee_type == 'rental_income':
				payment_object.rental_income_tax = fee
			
			if late_fees:
				if payment_object.fine_amount:
					payment_object.fine_description += " %s; " % str(Common.formatCurrency(payment_object.fine_amount))

				payment_object.fine_description += "Late fee %s %s" % (str(Common.formatCurrency(late_fees)), fee.currency.title())
				payment_object.fine_amount += late_fees

			payment_object.staff = request.session.get('user')
			payment_object.save()

			fee.remaining_amount = fee.get_remaining_amount()
			if fee.remaining_amount <= 0:
				fee.is_paid = True
			fee.save()
			citizen = None
			property = None
			business = None
			subbusiness = None
			if hasattr(fee,'citizen'):
				citizen = fee.citizen
			elif form.cleaned_data.get('citizen_id'): # set citizen as payer
				citizen = get_object_or_404(Citizen, pk=form.cleaned_data.get('citizen_id'))
			if hasattr(fee, 'property'):
				property = fee.property
			if hasattr(fee, 'business'):
				business = fee.business
			elif form.cleaned_data.get('business_id'): #set business as payer
				business = get_object_or_404(Business, pk=form.cleaned_data.get('business_id'))
			if hasattr(fee, 'subbusiness'):
				subbusiness = fee.subbusiness
			tax = fee
			message = "add a Payment of " + str(payment_object.amount) + tax.currency.title() + " for " + str(tax)
			LogMapper.createLog(request, object=tax, citizen=citizen, property=property, business=business, subbusiness=subbusiness, message= message, tax_type=tax.tax_type,tax_id=tax.id, payment_type='pay_' + tax.tax_type, payment_id=payment_object.id)
			redirect_url = "/admin/tax/tax/generate_invoice/?type=%s&id=%s" % ( fee_type, payment_object.pk)
			return HttpResponseRedirect(redirect_url)


def payFee(request, fee_type=None, id=None):
	if not id:
		id = request.GET.get('id')
	if not fee_type:
		fee_type = request.GET.get('type')
	business = None
	property = None
	citizen = None
	if fee_type in ('fee', 'land_lease'):
		fee = get_object_or_404(Fee, pk=id)
		if fee.fee_type == 'land_lease':
			fee_type = 'land_lease'
	elif fee_type == 'fixed_asset':
		fee = get_object_or_404(PropertyTaxItem, pk=id)
	elif fee_type == 'trading_license':
		fee = get_object_or_404(TradingLicenseTax, pk=id)
	elif fee_type == 'rental_income':
		fee = get_object_or_404(RentalIncomeTax, pk=id)

	if fee_type in ('land_lease', 'fixed_asset', 'rental_income'):
		template_type = 'property'
		property = fee.property
	elif fee_type == 'fee' and fee.citizen:
		template_type = 'citizen'
		citizen = fee.citizen
	elif fee_type == 'fee' and fee.business or fee_type == 'trading_license':
		template_type = 'business'
		business = fee.business

	if fee.is_paid and not fee.exempt:
		messages.add_message(request, messages.INFO, "This tax/fee has already been paid")
		if fee_type == 'fee' and 'land_lease' not in fee.fee_type:
			if template_type == 'property':
				return HttpResponseRedirect(reverse("property_fees", args=[property.pk]))	
			elif template_type == 'business':
				return HttpResponseRedirect(reverse("business_fees", args=[business.pk]))	
			elif template_type == 'citizen':
				return HttpResponseRedirect(reverse("citizen_fees", args=[citizen.pk]))	

		return HttpResponseRedirect(reverse("submit_%s" % fee_type, args=[id]))	

	if fee.amount is None or fee.submit_date is None:
		if fee_type == 'fee' and fee.fee_type in ('cleaning_fee','cleaning') and business:
			if not fee.submit_date:
				messages.add_message(request, messages.SUCCESS, "Confirm the 'business category' is set for this business and re-save to calculate cleaning fees.")
				return HttpResponseRedirect("/admin/tax/tax/business/%s/edit_business/?fee_redirect=1" % business.pk)
		else:
			messages.add_message(request, messages.INFO, "This tax/fee needs to be submitted.")
			return HttpResponseRedirect(reverse("submit_%s" % fee_type, args=[id]))	
	
	if request.POST:
		form = paymentForm(fee)(request.POST)
		if form.data.get('citizen_id'):
			citizen = Citizen.objects.get(pk=form.data.get('citizen_id'))
		elif form.data.get('business_id'):
			business = Business.objects.get(pk=form.data.get('business_id'))
		if form.is_valid():
			payment = fee.calculatePayment(form.cleaned_data.get('paid_date', date.today()), form.cleaned_data['amount'])
			
			# pay off installment
			#TaxMapper.pay_installment(fee, capital_amount, paid_on=form.cleaned_data.get('paid_date'))
			#redirect_url = "/admin/tax/tax/generate_invoice/?type=%s&id=%s" % ( fee_type, payment_object.pk)
			# return HttpResponseRedirect(redirect_url)
			form_data = request.POST.copy()
			capital_amount = form.cleaned_data['amount']
			bank_name = dict(variables.banks).get(form.cleaned_data['bank'])
			form_data['amount'] = capital_amount + form.cleaned_data['fine_amount'] + payment['late_fees']
			form_data['late_fees'] = payment['late_fees']
			form_data['fee_type'] = fee_type
			form_data['fee_id'] = id
			form = confirmPaymentForm(data=form_data)
			return TemplateResponse(request, 'tax/payment_confirm.html', {'template_type':template_type, 'tax':fee, 'form':form, 'payer':citizen or business, 'payment':payment, 'capital_amount':capital_amount, 'bank_name':bank_name, 'property':property, 'citizen':citizen, 'business':business })
		else:
			payment = fee.calculatePayment()
	else:
		payment = fee.calculatePayment()
		initial={'amount':payment['amount_due']}
		if business:
			initial['business_id'] = business.pk
			initial['payer_type'] = 'business'
		if citizen:
			initial['citizen_id'] = citizen.pk
			initial['payer_type'] = 'citizen'
		form = paymentForm(fee)(initial=initial)

	template = ("tax/pay%s.html" % fee_type).replace('_','')
	return render_to_response(template,{ 'form':form, 'property':property, 'citizen':citizen, 'business':business, 'tax':fee,'payment':payment, 'template_type':template_type,
		'pending_payment_reasons':variables.pending_payment_reasons},
		context_instance=RequestContext(request))


def payFees(request, id=None):
	fees = Fee.objects.filter(pk__in=request.POST.getlist('tax_id'))
	template_type = request.POST.get('template_type')
	# raise error message if no fees
	property = None
	citizen = None
	business = None

	if template_type == 'business':
		business = Business.objects.get(pk=request.POST.get('business_pk'))
	elif template_type == 'property':
		property = Property.objects.get(pk=request.POST.get('property_pk'))
	elif template_type == 'citizen':
		citizen = Citizen.objects.get(pk=request.POST.get('citizen_pk'))
	
	if request.POST.get('select'):
		# redirect back if no fees are selected
		form = PayFeesForm()
	else:
		form = PayFeesForm(request.POST)
		if form.is_valid():
			total_payment = late_fees = total_amount = 0

			for fee in fees:
				if not fee.amount:
					fee.calc_tax()
				fee.payment = fee.calculatePayment(form.cleaned_data.get('paid_date', date.today()))
				fee.payment['total'] = fee.payment['amount_due'] + fee.payment['late_fees']
				total_amount += fee.payment['amount_due']
				total_payment += (fee.payment['amount_due'] + fee.payment['late_fees'])
				late_fees += fee.payment['late_fees']

			if request.POST.get('confirm'): #confirmed, create payment
				mpr = MultipayReceipt(amount=total_payment, user=request.session.get('user'))
				mpr.save()
				for fee in fees:
					payfee = PayFee()
					if citizen:
						payfee.citizen_id = citizen.pk
					if business:
						payfee.business_id = business.pk
					payfee.staff = request.session.get('user')
					payfee.fee = fee
					payfee.amount = fee.payment['total']
					payfee.receipt_no=form.cleaned_data.get('receipt_no')
					payfee.bank=form.cleaned_data.get('bank')
					payfee.paid_date=form.cleaned_data.get('paid_on') or date.today()
					payfee.manual_receipt=form.cleaned_data.get('manual_receipt')
					payfee.fine_amount= fee.payment['late_fees']
					if payfee.fine_amount:
						payfee.fine_description = 'late fees'
					payfee.note=form.cleaned_data.get('note')
					payfee.save()
					fee.remaining_amount = 0
					fee.is_paid = True
					fee.save()
					mrpr = MultipayReceiptPaymentRelation(receipt=mpr, payfee=payfee)
					mrpr.save()
				return HttpResponseRedirect(reverse("multi_invoice", args=(mpr.pk, )))	

			# create payment objects and redirect to receipt
			return TemplateResponse(request, 'tax/pay_fees_confirm.html', {'template_type':template_type, 'fees':fees, 'form':form, 'payer':citizen or business, 'property':property, 'citizen':citizen, 'business':business, 'late_fees':late_fees, 'total_payment':total_payment, 'total_amount':total_amount })
		else:
			pass
			# form didn't validate

	return render_to_response('tax/pay_fees.html', { 'form':form, 'property':property, 'citizen':citizen, 'business':business, 'fees':fees, 'template_type':template_type},
		context_instance=RequestContext(request))


def submitRentalIncome(request, id):
	tax = get_object_or_404(RentalIncomeTax, pk=id)
	installments = tax.installments.all().order_by('due')
	payments = tax.payments.all().order_by('id')
	property = tax.property
	try:
		formula_data = tax.formuladata.formula_data
	except:
		formula_data = None

	if request.POST and request.POST.get('create_installments'):
		TaxMapper.generateInstallments(tax)
		messages.add_message(request, messages.INFO, "Installments have been created")
		return HttpResponseRedirect(request.META['HTTP_REFERER'])
	if request.POST and request.POST.get('delete_installments'):
		tax.installments.all().delete()
		messages.add_message(request, messages.INFO, "Installments have been deleted")
		return HttpResponseRedirect(request.META['HTTP_REFERER'])

	elif request.POST:
		form = RentalIncomeForm(request.POST)	
		if form.is_valid():
			tax.exempt = form.cleaned_data.get('exempt', 0)
			tax.months_deferred = request.POST.get('deferred', False)
			tax.staff = request.session.get('user')
			tax.declared_rental_income = form.cleaned_data.get('rental_income')
			tax.declared_bank_interest = form.cleaned_data.get('interest_paid')
			tax.submit_date = timezone.now()
			tax.save()
			tax.calc_tax()
			message = "add a submission for " + str(tax)
			LogMapper.createLog(request,object=tax,property=property,message= message,tax_type=tax.tax_type,tax_id=tax.id)
			messages.add_message(request, messages.INFO, "Rental Income Tax has been updated.")	
			return HttpResponseRedirect(request.META['HTTP_REFERER'])	
			#return HttpResponseRedirect('/admin/tax/tax/generate_epayinvoice/?type=land_lease&id=' + str(fee.id))
	else:
		initial = { 'exempt':tax.exempt, 'rental_income': tax.declared_rental_income, 'interest_paid':tax.declared_bank_interest, 'deferred':tax.months_deferred }
		form = RentalIncomeForm(initial=initial)

	return render_to_response('tax/submit_rental_income.html', { 'formula_data':formula_data, 'template_type':'property', 'property':property, 'form': form, 'tax':tax, 'payments': payments, 'installments':installments, 'tax_type':'rental_income' }, context_instance=RequestContext(request))


def submitTradingLicense(request, id):
	tax = get_object_or_404(TradingLicenseTax, pk=id)
	business = tax.business

	if tax.remaining_amount is None:
		tax.remaining_amount = 0
	if tax.amount is not None:
		paid_amount = tax.amount - tax.remaining_amount
	else:
		paid_amount = 0
	installments = tax.installments.all().order_by('due')
	payments = tax.payments.all().order_by('id')
	business = tax.business
	try:
		formula_data = tax.formuladata.formula_data
	except:
		formula_data = None
	activity_rates = variables.activities
	activity_descriptions = variables.activity_description

	if request.POST and request.POST.get('create_installments'):
		TaxMapper.generateInstallments(tax)
		messages.add_message(request, messages.INFO, "Installments have been created")
		return HttpResponseRedirect(request.META['HTTP_REFERER'])

	elif request.POST and request.POST.get('delete_installments'):
		tax.installments.all().delete()
		messages.add_message(request, messages.INFO, "Installments have been deleted")
		return HttpResponseRedirect(request.META['HTTP_REFERER'])

	elif request.POST:
		form = TradingLicenseForm(request.POST)
		if form.is_valid():
			business.vat_register = form.cleaned_data.get('vat_registered')
			business.tin = form.cleaned_data.get('tin')
			if not business.vat_register:
				activity_data = {}
				for activity, settings in variables.activities:
					for setting_name, rate in settings:
						units = form.cleaned_data.get("%s_%s" % (activity, setting_name), 0)
						if not units: continue
						activity_data["%s_%s" % (activity, setting_name)] = units
				tax.activity_data = pickle.dumps(activity_data).encode('base64')
			else:
				tax.turnover = form.cleaned_data.get('turnover', 0)

			business.save()
			tax.exempt = form.cleaned_data.get('exempt', 0)
			tax.months_deferred = request.POST.get('deferred', False)
			tax.staff = request.session.get('user')
			tax.submit_date = timezone.now()
			tax.save()
			tax.calc_tax()
			message = "add a submission for " + str(tax)
			LogMapper.createLog(request,object=tax,business=business,message= message,tax_type=tax.tax_type,tax_id=tax.id)
			
			redirect_url = '/admin/tax/tax/generate_epayinvoice/?type=fixed_asset&id='+ str(tax.id)
			messages.add_message(request, messages.INFO, "Trading License Tax has been updated.")	
			return HttpResponseRedirect(request.META['HTTP_REFERER'])	
			#return HttpResponseRedirect('/admin/tax/tax/generate_epayinvoice/?type=land_lease&id=' + str(fee.id))
	else:
		if not tax.turnover:
			tax.turnover = ''
		else:
			tax.turnover = str(int(tax.turnover))
		initial = { 'exempt': tax.exempt, 'deferred':tax.months_deferred, 'vat_registered':"Yes" if business.vat_register else "No", 'turnover':tax.turnover, 'tin':business.tin }
			
		if tax.activity_data:
			try:
				activity_data = pickle.loads(tax.activity_data.decode('base64'))
				initial.update(activity_data)		
			except:
				pass
	
		form = TradingLicenseForm(initial=initial)	
	
	return render_to_response('tax/submit_trading_license.html', { 'formula_data':formula_data, 'form': form, 'business':business, 'template_type':'business', 'tax':tax, 'tax_type':'trading_license', 'payments': payments, 'installments':installments, 'activity_rates':activity_rates, 'activity_desc':activity_descriptions }, context_instance=RequestContext(request))


def submitFixedAssetTax(request, id):
	tax = get_object_or_404(PropertyTaxItem, pk=id)
	if tax.remaining_amount is None:
		tax.remaining_amount = 0
	if tax.amount is not None:
		paid_amount = tax.amount - tax.remaining_amount
	else:
		paid_amount = 0
	installments = tax.installments.all().order_by('due')
	payments = tax.payments.all().order_by('id')
	property = tax.property
	try:
		formula_data = tax.formuladata.formula_data
	except:
		formula_data = None

	if request.POST and request.POST.get('create_installments'):
		TaxMapper.generateInstallments(tax)
		messages.add_message(request, messages.INFO, "Installments have been created")
		return HttpResponseRedirect(request.META['HTTP_REFERER'])

	elif request.POST and request.POST.get('delete_installments'):
		tax.installments.all().delete()
		messages.add_message(request, messages.INFO, "Installments have been deleted")
		return HttpResponseRedirect(request.META['HTTP_REFERER'])

	elif request.POST:
		form = FixedAssetForm(request.POST, property=property)

		if form.is_valid():
			land_use_types = form.cleaned_data.get('land_use_type')
			property.floor_count = form.cleaned_data.get('floor_count')
			property.floor_total_square_meters = form.cleaned_data.get('floor_total_square_meters')
			property.year_built = form.cleaned_data.get('year_built')

			property.land_use_types = tax.land_use_types = land_use_types
			
			tax.exempt = form.cleaned_data.get('exempt', 0)
			tax.staff = request.session.get('user')
			tax.months_deferred = request.POST.get('deferred', False)
			tax.submit_date = timezone.now()
			
			citizen_id=form.cleaned_data.get('declared_by')
			citizen = Citizen.objects.get(pk=citizen_id)
			
			residential_amount = form.cleaned_data.get('declared_residential_amount')
			commercial_amount = form.cleaned_data.get('declared_commercial_amount')
			agriculture_amount = form.cleaned_data.get('declared_agriculture_amount')
			total_declared_amount = residential_amount + commercial_amount + agriculture_amount
			declared_on = form.cleaned_data.get('declared_on')

			declared_value, created = DeclaredValue.objects.get_or_create(property=property, citizen=citizen, declared_on=declared_on,
					amount=total_declared_amount, residential_amount=residential_amount, 
					commercial_amount=commercial_amount, agriculture_amount=agriculture_amount, 
					user=request.session.get('user'), defaults=dict(date_time=datetime.now(), accepted='YE'))

			tax.declared_value = declared_value
			property.save()
			tax.calc_tax()
			message = "add a submission for " + str(tax)
			LogMapper.createLog(request,object=tax,property=property,message= message,tax_type=tax.tax_type,tax_id=tax.id)

			redirect_url = '/admin/tax/tax/generate_epayinvoice/?type=fixed_asset&id='+ str(tax.id)
			messages.add_message(request, messages.INFO, "Fixed Asset Tax has been updated")	
			return HttpResponseRedirect(request.META['HTTP_REFERER'])	
			#return HttpResponseRedirect('/admin/tax/tax/generate_epayinvoice/?type=land_lease&id=' + str(fee.id))
	else:
		initial = {'land_use_type':(tax.land_use_types.all() or property.land_use_types.all()), 'exempt':tax.exempt, 'deferred':tax.months_deferred  }
		declared_value = tax.declared_value or property.declaredValue
		initial['floor_count'] = property.floor_count
		initial['floor_total_square_meters'] = property.floor_total_square_meters
		initial['year_built'] = property.year_built
		if declared_value:
			initial['declared_value'] = declared_value.amount 
			initial['declared_residential_amount'] = declared_value.residential_amount
			initial['declared_commercial_amount'] = declared_value.commercial_amount
			initial['declared_agriculture_amount'] = declared_value.agriculture_amount
			if declared_value.declared_on:
				initial['declared_on'] = declared_value.declared_on.strftime(settings.DATE_INPUT_FORMAT)
			citizen = declared_value.citizen
			initial['declared_by'] = citizen.id
			if citizen.middle_name:
				citizen.first_name + ' ' + citizen.middle_name
			initial['declared_by_search'] = "%s %s" % (citizen.first_name, citizen.last_name)
		else:
			initial['declared_value'] = 0
			initial['declared_residential_amount'] = 0
			initial['declared_commercial_amount'] = 0
			initial['declared_agriculture_amount'] = 0

		form = FixedAssetForm(initial=initial, property=property)

	return render_to_response('tax/submit_fixed_asset.html', { 'formula_data':formula_data, 'template_type':'property', 'property':property, 'form': form, 'tax':tax, 'payments': payments, 'tax_type':'fixed_asset', 'installments':installments, 'date_from':tax.date_from, 'date_to':tax.date_to }, context_instance=RequestContext(request))


def submitLandLease(request, id, template_type='property'):
	fee = get_object_or_404(Fee, pk=id)
	installments = fee.get_installments()
	payments = fee.payments.all().order_by('id')
	property = fee.property
	try:
		formula_data = fee.formuladata.formula_data
	except:
		formula_data = None

	if request.POST and request.POST.get('create_installments'):
		TaxMapper.generateInstallments(fee)
		messages.add_message(request, messages.INFO, "Installments have been created")
		return HttpResponseRedirect(request.META['HTTP_REFERER'])

	elif request.POST and request.POST.get('delete_installments'):
		fee.installments.all().delete()
		fee.exempt = False
		fee.save()
		messages.add_message(request, messages.INFO, "Installments have been deleted")
		return HttpResponseRedirect(request.META['HTTP_REFERER'])

	elif request.POST:
		form = LandLeaseForm(request.POST)
		if form.is_valid():
			fee.land_lease_type = form.cleaned_data.get('land_lease_type')
			fee.exempt = form.cleaned_data.get('exempt', 0)
			fee.staff = request.session.get('user')
			fee.submit_date = timezone.now()
			fee.save()
			fee.calc_landlease()
			message = "add a submission for " + str(fee)
			LogMapper.createLog(request,object=fee,property=property,message= message,tax_type=fee.tax_type,tax_id=fee.id)
			redirect_url = '/admin/tax/tax/generate_epayinvoice/?type=land_lease&id='+ str(fee.id)
			messages.add_message(request, messages.INFO, "Land Lease Tax has been updated")	
			return HttpResponseRedirect(request.META['HTTP_REFERER'])
	else:
		initial = {'land_lease_type':fee.land_lease_type, 'exempt':fee.exempt }
		form = LandLeaseForm(initial=initial)

	return render_to_response('tax/submit_land_lease.html', { 'formula_data':formula_data, 'form': form, 'tax':fee, 'tax_type':'land_lease', 'payments': payments, 'property':fee.property, 'installments':installments, 'date_from':fee.date_from, 'date_to':fee.date_to, 'template_type':template_type }, context_instance=RequestContext(request))



def displayPayTaxPage(request, action, content_type_name1, obj_name, obj_id, part):
	GET = request.GET
	tax_type = GET['type']
	staff = request.session.get('user')
	citizen_id = None
	national_citizen_id = None
	file_list = None
	business_id = None
	citizen = None
	business = None
	subbusiness = None
	property = None
	formula_data = {}
	show_tax_url = '/admin/tax/tax/'

	if request.session.has_key('citizen') and request.session['citizen'] != None:
		citizen = request.session['citizen']
		national_citizen_id = citizen.citizen_id
		citizen_id = citizen.id
		show_tax_url = show_tax_url + 'citizen/' + str(citizen.id) + "/taxes/"

	if request.session.has_key('business') and request.session['business'] != None:
		business = request.session['business']
		business_id = business.id
		show_tax_url = show_tax_url + 'business/' + str(business.id) + "/taxes/"

	if request.session.has_key('property') and request.session['property'] != None:
		property = request.session['property']
		show_tax_url = show_tax_url + 'property/' + str(property.id) + "/taxes/"

	if tax_type == 'fixed_asset':
		tax = get_object_or_404(PropertyTaxItem,pk=GET['id'])
		reference = getTaxReference(tax_type, tax)
		tax_label = 'Fixed Asset Tax for ' + reference
		property = tax.property

		#get formula data to display to user				
		formula_data = getFormulaData(tax_type, tax, property)

		if request.method == 'POST':
			form = PayFixedAssetTaxForm(request.POST)
			form.citizen_id = citizen_id
			form.business_id = business_id
			form.property_tax_item = tax
		else:
			payment_amount = formula_data['final_amount']
			form = PayFixedAssetTaxForm(initial={"property_tax_item":tax,'amount':payment_amount,'citizen_id':citizen_id,'business_id':business_id})

	if tax_type == 'rental_income':
		tax = get_object_or_404(RentalIncomeTax,pk=GET['id'])
		reference = getTaxReference(tax_type, tax)
		tax_label = 'Rental Income Tax for ' + reference
		property = tax.property

		#get formula data to display to user				
		formula_data = getFormulaData(tax_type, tax, property)

		if request.method == 'POST':
			form = PayRentalIncomeTaxForm(request.POST)

			form.citizen_id = citizen_id
			form.business_id = business_id
			form.rental_income_tax = tax

		else:
			initial_values={"rental_income_tax":tax,'amount':formula_data['final_amount'],'citizen_id':citizen_id,'business_id':business_id}
			if formula_data.has_key('last_year_income'):
				initial_values['last_year_income'] = formula_data['last_year_income']
			if formula_data.has_key('bank_interest_paid'):
				initial_values['bank_interest_paid'] = formula_data['bank_interest_paid']
			if formula_data.has_key('fine_amount'):
				initial_values['fine_amount'] = formula_data['fine_amount']
			if formula_data.has_key('fine_description'):
				initial_values['fine_description'] = formula_data['fine_description']
			form = PayRentalIncomeTaxForm(initial=initial_values)

	if tax_type == 'trading_license':
		tax = get_object_or_404(TradingLicenseTax,pk=GET['id'])
		business = None
		subbusiness = None
		if tax.business:
			business = tax.business
		elif tax.subbusiness:
			subbusiness = tax.subbusiness
			business = tax.subbusiness.business
					
		business_id = business.id
		reference = getTaxReference(tax_type, tax)
		tax_label = 'Trading License Tax ' + reference
		formula_data = getFormulaData(tax_type, tax, business)

		if request.method == 'POST':
			form = PayTradingLicenseTaxForm(request.POST)
			form.citizen_id = citizen_id
			if subbusiness:
				form.subbusiness_id = subbusiness.id
			else:
				form.business_id = business_id
			form.trading_license_tax = tax
		else:
			if subbusiness:
				form = PayTradingLicenseTaxForm(initial={'trading_license_tax':tax,'amount':formula_data['final_amount'],'citizen_id':citizen_id,'subbusiness_id':subbusiness.id})
			else:
				form = PayTradingLicenseTaxForm(initial={'trading_license_tax':tax,'amount':formula_data['final_amount'],'citizen_id':citizen_id,'business_id':business_id})

	if tax_type == 'fee':
		tax = get_object_or_404(Fee,id=GET['id'])
		reference = getTaxReference(tax_type, tax)
		tax_label = tax.fee_type.replace("_"," ").title() + ' Fee ' + reference

		#get formula data to display to user
		if tax.fee_type == 'land_lease':
			property = tax.property
			formula_data = getFormulaData(tax_type,tax,property)
		elif tax.fee_type in ('cleaning','market'):
			business = tax.business
			if tax.subbusiness:
				subbusiness = tax.subbusiness
				if subbusiness.credit:
					tax.credit = subbusiness.credit
				else:
					tax.credit = 0
			else:
				if business.credit:
					tax.credit = business.credit
				else:
					tax_credit = 0
			formula_data = getFormulaData(tax_type,tax,business)

		if request.method == 'POST':
			form = PayFeeForm(request.POST)

			form.citizen_id = citizen_id
			form.business_id = business_id
		else:
			if formula_data.has_key('final_amount') and formula_data['final_amount'] > 0:
				form = PayFeeForm(initial={'final_tax_due':int(formula_data['final_amount']),'amount':int(formula_data['final_amount']),'fee':tax,'fee_type':tax.fee_type,'citizen_id':citizen_id,'business_id':business_id})
			else:
				form = PayFeeForm(initial={'fee':tax,'fee_type':tax.fee_type,'citizen_id':citizen_id,'business_id':business_id})

	#if tax already been paid, redirect back to the invoice page
	if tax.is_paid:
		if request.session.has_key('tax_url'):
			return HttpResponseRedirect(request.session['tax_url'])
		else:
			return HttpResponseRedirect("admin/tax/tax/verify_target/")

	if request.method == 'POST':
		fine_amount = 0
		late_fee_interest = 0
		late_fee_surcharge = 0
		
		#remove ',' out of submitted amount values
		if request.POST.get('fine_amount',None) != None and request.POST.get('fine_amount') != 0:
			fine_amount = Decimal(request.POST.get('fine_amount').replace(',',''))
		if request.POST.get('late_fee_surcharge',None) != None and request.POST.get('late_fee_surcharge') > 0:
			late_fee_interest = Decimal(request.POST.get('late_fee_interest').replace(',',''))
			late_fee_surcharge = Decimal(request.POST.get('late_fee_surcharge').replace(',',''))

		#if only submit Tax information without Paying, calculate Tax Amount only
		if (action == 'submit' and content_type_name1 == 'tax'):
			if request.POST.get('final_tax_due',None) != None and int(float(request.POST.get('final_tax_due'))) > 0 :

				tax.amount = int(float(request.POST.get('final_tax_due'))) - round(fine_amount + late_fee_interest + late_fee_surcharge)
				tax.remaining_amount = tax.amount

				tax.submit_date = timezone.now()
				tax.save()

				#also save the selected tax/fee settings into the DB for future taxes
				saveTaxDetails(tax_type,tax,request)
						
				message = "add a submission for " + str(tax)
				LogMapper.createLog(request,object=tax,citizen=citizen,property=property,business=business,subbusiness=subbusiness,message= message,tax_type=tax_type,tax_id=tax.id)

				#redirect to the receipt page
				return HttpResponseRedirect('/admin/tax/tax/generate_epayinvoice/?type=' + tax_type + '&id=' + str(tax.id))

		#if Finalize (Pay Tax), add new Payment object etc
		elif form.is_valid():
			#save payment - update fine if required
			payment = form.save(commit=False)
			payment.staff = staff

			#add the late fees into fines before save
			if late_fee_surcharge > 0:
				payment.fine_amount = fine_amount + late_fee_surcharge + late_fee_interest
				payment.fine_description = "Late fee surcharge (" + str(Common.formatCurrency(late_fee_surcharge)) + tax.currency.title() + " ) & late fee interest (" + str(Common.formatCurrency(late_fee_interest)) + tax.currency.title() + " ). " + form.cleaned_data['fine_description']	
			
			#if is a pending payment submit, set payment status to be pending, waiting for approval
			if form.cleaned_data['submit_pending'] and form.cleaned_data['submit_pending'] != '':
				payment.i_status = 'pending'
				payment.save()

				#start adding a pending payment record
				pending_record = PendingPayment(tax_type=tax_type,payment_id=payment.id,tax_id=tax.id,reason=form.cleaned_data['pending_reason'],note=form.cleaned_data['pending_note'],user=staff)
				pending_record.save()



				#set amount in tax if not exist - for Taxes with undefined amount (wont generated until user supplied information)
				if(tax.amount == None and form.cleaned_data['final_tax_due'] != None):
					tax.amount = int(float(form.cleaned_data['final_tax_due'])) - round(fine_amount + late_fee_interest + late_fee_surcharge)
					tax.remaining_amount = tax.amount

				tax.save()

				#also save the selected tax/fee settings into the DB for future taxes
				saveTaxDetails(tax_type,tax,request)
				message = "add a Pending Payment of " + str(payment.amount) + tax.currency.title() + " for " + str(tax)
	
				LogMapper.createLog(request,object=tax,citizen=citizen,property=property,business=business,subbusiness=subbusiness,message= message,tax_type=tax_type,tax_id=tax.id,payment_type='pay_' + tax_type,payment_id=payment.id)
				
				#redirect to result page to upload supporting documents		
				return HttpResponseRedirect("/admin/tax/tax/submit_pending/?type=" + tax_type + '&id=' + str(payment.id))

			#if is a normal payment, save payment with status active, also update the tax item details
			else:
				payment.save()

				#set amount in tax if not exist - for Taxes with undefined amount (wont generated until user supplied information)
				if(tax.amount == None and form.cleaned_data['final_tax_due'] != None):
					tax.amount = int(float(form.cleaned_data['final_tax_due'])) - round(fine_amount + late_fee_interest + late_fee_surcharge)
					tax.remaining_amount = tax.amount

				#update tax item to Paid if applicable
				payment_capital_amount = int(payment.amount) - round(fine_amount + late_fee_interest + late_fee_surcharge)

				# reduce installment if any
				# TaxMapper.pay_installment(tax, payment_capital_amount)

				if tax.remaining_amount:
					tax.remaining_amount = Decimal(tax.remaining_amount) - Decimal(payment_capital_amount)
				else:
					tax.remaining_amount = 0

				#put a check for overpaid amount
				if tax.remaining_amount < 0:
					tax.remaining_amount = 0


				"""
				##################################################################
				## Specified for cleaning fee credit...	Start
				##################################################################=			
				if	tax_type == 'fee' and tax.fee_type == 'cleaning':
					if tax.business:
						credit = 0
						business_entity = tax.business
						due_amount = float(request.POST['final_tax_due'])
						paid_amount = float(request.POST['amount'])

						if paid_amount > due_amount:
							if not business_entity.credit:
								business_entity.credit = 0
							business_entity.credit = business_entity.credit + paid_amount - due_amount
							tax.remaining_amount = 0
							business_entity.save()
						elif paid_amount < due_amount:
							if business_entity.credit:
								if business_entity.credit + paid_amount >= due_amount:
									business_entity.credit = business_entity.credit + paid_amount - due_amount
									tax.remaining_amount = 0
									business_entity.save()
								else:
									tax.remaining_amount = due_amount - business_entity.credit - paid_amount
									business_entity.credit = 0
									business_entity.save()
					elif tax.subbusiness:
						credit = 0
						subbusiness_entity = tax.subbusiness
						due_amount = float(request.POST['final_tax_due'])
						paid_amount = float(request.POST['amount'])

						if paid_amount > due_amount:
							if not subbusiness_entity.credit:
								subbusiness_entity.credit = 0
							subbusiness_entity.credit = subbusiness_entity.credit + paid_amount - due_amount
							tax.remaining_amount = 0
							subbusiness_entity.save()
						elif paid_amount < due_amount:
							if subbusiness_entity.credit:
								if subbusiness_entity.credit + paid_amount >= due_amount:
									subbusiness_entity.credit = subbusiness_entity.credit + paid_amount - due_amount
									tax.remaining_amount = 0
									subbusiness_entity.save()
								else:
									tax.remaining_amount = due_amount - subbusiness_entity.credit - paid_amount
									subbusiness_entity.credit = 0
									subbusiness_entity.save()
						
					
				##################################################################
				## Specified for cleaning fee credit ...	end
				##################################################################
				"""
			
				if tax.remaining_amount <= 0:
					tax.is_paid = True
				tax.save()

				#also save the selected tax/fee settings into the DB for future taxes
				saveTaxDetails(tax_type,tax,request)
				message = "add a Payment of " + str(payment.amount) + tax.currency.title() + " for " + str(tax)
	
				LogMapper.createLog(request,object=tax,citizen=citizen,property=property,business=business,subbusiness=subbusiness,message= message,tax_type=tax_type,tax_id=tax.id,payment_type='pay_' + tax_type,payment_id=payment.id)

				#redirect to the receipt page
				return HttpResponseRedirect('/admin/tax/tax/generate_invoice/?type=' + tax_type + '&id=' + str(payment.id))

	tax_year = None
	if tax.due_date:
		tax_year = tax.due_date.year

	if (action == 'submit' and content_type_name1 == 'tax'):
		html_template = 'tax/tax_tax_submittax.html'
	else:
		html_template = 'tax/tax_tax_paytax.html'
	return render_to_response(html_template,{'show_tax_url':show_tax_url,'tax_year':tax_year,'form':form,'tax_label':tax_label,'tax_type':tax_type,'tax':tax,'formula':formula_data,'file_list': file_list,'pending_payment_reasons':variables.pending_payment_reasons},
							context_instance=RequestContext(request))


def displayPayMultipleTaxesPage(request, action, content_type_name1, obj_name, obj_id, part):
	GET = request.GET
	tax_type = GET['type']
	staff = request.session.get('user')
	citizen = None
	business = None
	subbusiness = None
	property = None
	formula_data = {}
	show_tax_url = '/admin/tax/tax/'

	if request.session.has_key('citizen') and request.session['citizen'] != None:
		citizen = request.session['citizen']
		show_tax_url = show_tax_url + 'citizen/' + str(citizen.id) + "/taxes/"

	if request.session.has_key('business') and request.session['business'] != None:
		business = request.session['business']
		business_id = business.id
		show_tax_url = show_tax_url + 'business/' + str(business.id) + "/taxes/"

	if request.session.has_key('property') and request.session['property'] != None:
		property = request.session['property']
		show_tax_url = show_tax_url + 'property/' + str(property.id) + "/taxes/"

	#only allow pay multiple cleaning fees for 1 business/branch atm (prevent even the case of trying to play cleaning fee for main business & branch at the same time)
	taxes = Fee.objects.filter(id__in=GET['id'].split(','),i_status='active').order_by('period_from')

	if tax_type != 'fee' or not taxes or (taxes[0].subbusiness and taxes.filter(business__isnull=False).count() > 0) or (taxes[0].business and taxes.filter(subbusiness__isnull=False).count() > 0):
		raise Http404

	#if only 1 fee is selected, redirect to pay single fee page
	if taxes.count() == 1:
		return HttpResponseRedirect('/admin/tax/tax/pay_taxes/?type=' + tax_type + '&id=' + str(taxes[0].id))

	tax = taxes[0]
	if tax.business:
		business = tax.business
	else:
		business = tax.subbusiness.business
	months = []
	formula_list = {}
	formula_list['total'] = 0
	formula_list['list'] = []
	for tax in taxes:
		months.append(Common.localizeDate(tax.period_from).strftime('%b'))
	
		#if tax already been paid, redirect back to the invoice page
		if tax.is_paid:
			if request.session.has_key('tax_url'):
				return HttpResponseRedirect(request.session['tax_url'])
			else:
				return HttpResponseRedirect("admin/tax/tax/verify_target/")

		formula_data = getFormulaData(tax_type,tax,business)
		formula_data['tax_id'] = tax.id
		if formula_data.has_key('late_fee_interest_rate'):
			formula_list['late_fee_interest_rate'] = formula_data["late_fee_interest_rate"]
			formula_list['late_fee_surcharge_rate'] = formula_data["late_fee_surcharge_rate"]
			formula_list['late_fee_surcharge_max'] = formula_data["late_fee_surcharge_max"]
		formula_data['period'] = Common.localizeDate(tax.period_from).strftime('%b %Y')
		formula_data['currency'] = tax.currency
		formula_list['list'].append(formula_data)
		formula_list['total']= int(formula_list['total']) + int(formula_data['final_amount'])

	if request.method == 'POST':
		form = PayFeeForm(request.POST)
		form.citizen = citizen
		form.business = business
	else:
		if formula_list['total'] != 0:
			form = PayFeeForm(initial={'final_tax_due':int(formula_list['total']),'amount':int(formula_list['total']),'fee_type':tax.fee_type,'fee':tax,'citizen':citizen,'business':business})
		else:
			form = PayFeeForm(initial={'fee_type':tax.fee_type,'fee':tax,'citizen':citizen,'business':business})


	if request.method == 'POST':
		if form.is_valid():
			payment_data = form.save(commit=False)
			payment_data.staff = staff
			payment_ids = []

			#add multipay receipt record
			receipt = MultipayReceipt(amount=payment_data.amount,user=staff)
			receipt.save()

			#duplicate payment data for each tax item and save a payment per tax item
			for tax in taxes:
				#update tax item to Paid, also update the tax amount if is not defined
				if tax.amount == None and request.POST.get('fee_amount',None) != None:
					tax.amount = int(float(request.POST.get('fee_amount')))
				tax.remaining_amount = 0
				tax.is_paid = True
				tax.save()

				payment = payment_data
				payment.id = None
				payment.pk = None
				payment.fee = tax
				payment.fine_amount = 0
				payment.fine_description = ''
				payment.amount = tax.amount
				late_fee_interest = 0
				late_fee_surcharge = 0
				#print payment.fine_amount

				if request.POST.get('late_fee_surcharge_' + str(tax.id),None) != None and request.POST.get('late_fee_surcharge_' + str(tax.id)) > 0:
					late_fee_interest = int(request.POST.get('late_fee_interest_' + str(tax.id)))
					late_fee_surcharge = int(request.POST.get('late_fee_surcharge_' + str(tax.id)))

				#add the late fees into fines before save
				if late_fee_surcharge > 0:
					payment.amount = payment.amount + late_fee_surcharge + late_fee_interest
					payment.fine_amount = late_fee_surcharge + late_fee_interest
					payment.fine_description = "Late fee surcharge (" + str(Common.formatCurrency(late_fee_surcharge)) + tax.currency.title() + " ) & late fee interest (" + str(Common.formatCurrency(late_fee_interest)) + tax.currency.title() + " ). "

				payment.save()
				payment_ids.append(str(payment.id))

				#add link newly added payment with the multipay receipt
				relation = MultipayReceiptPaymentRelation(payfee=payment,receipt=receipt)
				relation.save()

						
				message = "add a Payment of " + str(payment.amount) + tax.currency.title() + " for " + str(tax)
				LogMapper.createLog(request,object=tax,citizen=citizen,property=property,business=business,message= message,tax_type=tax_type,tax_id=tax.id,payment_type='pay_' + tax_type,payment_id=payment.id)

			#redirect to the receipt page
			return HttpResponseRedirect('/admin/tax/tax/generate_multipayinvoice/?type=' + tax_type + '&id=' + str(receipt.id))
		else:
			pass
	tax_label = 'Pay multiple ' + taxes[0].fee_type.replace("_"," ").title() + ' Fee ' + '[TIN: ' + business.tin + '] for ' + ','.join(months) + ' ' + Common.localizeDate(taxes[0].period_from).strftime('%Y')
	tax_year = None
	if tax.due_date:
		tax_year = tax.due_date.year


	html_template = 'tax/tax_tax_paymultiple.html'
	return render_to_response(html_template,{'show_tax_url':show_tax_url,'tax_label':tax_label,'tax_year':tax_year,'form':form,'tax_type':tax_type,'tax':tax,'formula_list':formula_list},
							context_instance=RequestContext(request))


def displaySubmitPendingPage(request):
	GET = request.GET
	tax_type = GET['type']
	staff = request.session.get('user')
	tax_label = ''
	id = request.GET.get('id')
	national_citizen_id = None
	plot_id = None
	business_id = None
	property_id = None
	citizen_id = None
	citizen = None
	business = None
	property = None
	tax_url = None

	if tax_type == 'fixed_asset':
		payment = get_object_or_404(PayFixedAssetTax,pk=id,i_status='pending')
		tax = payment.property_tax_item
		property = tax.property
		property_id = property.id
		tax_label = 'Fixed Asset Tax for '

	elif tax_type == 'rental_income':
		payment = get_object_or_404(PayRentalIncomeTax,pk=id,i_status='pending')
		tax = payment.rental_income_tax
		property = tax.property
		property_id = property.id

	elif tax_type == 'trading_license':
		payment = get_object_or_404(PayTradingLicenseTax,pk=id,i_status='pending')
		tax = payment.trading_license_tax
		business = tax.business
		if tax.subbusiness:
			business = tax.subbusiness.business

	elif tax_type == 'misc_fee':
		payment = get_object_or_404(PayMiscellaneousFee,pk=id,i_status='pending')
		tax = payment.fee
		tax_label = 'Miscellaneous Fee'

		property = tax.property
		business = tax.business
		citizen = tax.citizen
		if tax.subbusiness:
			business = tax.subbusiness.business

	else:
		payment = get_object_or_404(PayFee,pk=id,i_status='pending')
		tax = payment.fee
		tax_label = 'Fee'

		property = tax.property
		business = tax.business
		if tax.subbusiness:
			business = tax.subbusiness.business

	if payment.citizen_id != None and payment.citizen_id != '':
		citizen = Citizen.objects.get(pk=payment.citizen_id)
	elif payment.business_id != None and payment.business_id != '':
		business = Business.objects.get(pk=payment.business_id)

	reference = getTaxReference(tax_type, tax)
	tax_label = tax_label + reference

	#get the list of support medias for this tax/fee if exist
	media = Media.objects.filter(tax_type__exact=tax_type,tax_id__exact=tax.id,i_status='active')

	#get current view taxes url in the session if exist
	if request.session.has_key('tax_url'):
		tax_url = request.session['tax_url']

	return render_to_response('tax/tax_tax_submit_pending.html',{'tax_url':tax_url,'tax_label':tax_label, 'media':media,'tax':tax,'payment':payment,'tax_type':tax_type,
													'business_id':business_id,'citizen_id':citizen_id,'property_id':property_id},
							context_instance=RequestContext(request))


def displayGenerateInvoicePage(request):
		GET = request.GET
		tax_type = GET['type']
		staff = request.session.get('user')
		tax_label = ''
		id = request.GET.get('id')
		national_citizen_id = None
		plot_id = None
		business_id = None
		property_id = None
		citizen_id = None
		citizen = None
		business = None
		property = None
		tax_url = None
		epay_no = None

		#also collect the sms/email contact belong to this citizen/businesss/property for receipt actions
		smsList = []
		emailList = []
		smsInputPairList = []
		emailInputPairList = []
		sendSmsList = None
		sendEmailList = None

		send_receipt_message = ''
		send_receipt_error = ''
		
		try:
			if tax_type == 'fixed_asset':
				payment = get_object_or_404(PayFixedAssetTax,pk=id,i_status='active')
				tax = payment.property_tax_item
				property = tax.property
				property_id = tax.property.id
				tax_label = 'Fixed Asset Tax for '

			elif tax_type == 'rental_income':
				payment = get_object_or_404(PayRentalIncomeTax,pk=id,i_status='active')
				tax = payment.rental_income_tax
				property = tax.property
				property_id = tax.property.id

			elif tax_type == 'trading_license':
				payment = get_object_or_404(PayTradingLicenseTax,pk=id,i_status='active')
				tax = payment.trading_license_tax
				business = tax.business
				if tax.subbusiness:
					business = tax.subbusiness.business

			elif tax_type == 'misc_fee':
				payment = get_object_or_404(PayMiscellaneousFee,pk=id,i_status='active')
				tax = payment.fee
				tax_label = 'Miscellaneous Fee'

				property = tax.property
				business = tax.business
				citizen = tax.citizen
				if tax.subbusiness:
					business = tax.subbusiness.business

			else:
				payment = get_object_or_404(PayFee,pk=id,i_status='active')
				tax = payment.fee
				tax_label = 'Fee'

				property = tax.property
				business = tax.business
				if tax.subbusiness:
					business = tax.subbusiness.business
		except Exception:
			raise Http404

		#if citizen == None and payment.citizen_id != None and payment.citizen_id != '':
		#	citizen = Citizen.objects.get(pk=payment.citizen_id)
		#elif business == None and payment.business_id != None and payment.business_id != '':
		#	business = Business.objects.get(pk=payment.business_id)
		if payment.citizen_id:
			citizen = Citizen.objects.get(pk=payment.citizen_id)
		elif payment.business_id:
			business = Business.objects.get(pk=payment.business_id)

		reference = getTaxReference(tax_type, tax)
		tax_label = tax_label + reference

		epay_no = PaymentMapper.generateEpayNo(tax_type, tax)
		#get the list of support medias for this tax/fee if exist
		media = Media.objects.filter(tax_type__exact=tax_type,tax_id__exact=tax.id,i_status='active')
		#get current view taxes url in the session if exist
		if request.session.has_key('tax_url'):
			tax_url = request.session['tax_url']

		#generate receipt
		receipt = None
		if citizen:
			national_citizen_id = citizen.citizen_id
			receipt = generateReceipt(tax_type, payment, tax, 'citizen',citizen)
			citizen_id = citizen.id

			if citizen.phone_1 != None and citizen.phone_1 != '' and citizen.phone_1 not in smsList:
				smsList.append(citizen.phone_1)
			if citizen.phone_2 != None and citizen.phone_2 != '' and citizen.phone_2 not in smsList:
				smsList.append(citizen.phone_2)
			if citizen.email != None and citizen.email != '' and citizen.email not in emailList:
				emailList.append(citizen.email)
		elif business:
			business_id = business.id
			receipt = generateReceipt(tax_type, payment, tax, 'business',business)

			if business.phone1 != None and business.phone1 != '' and business.phone1 not in smsList:
				smsList.append(business.phone1)
			if business.phone2 != None and business.phone2 != '' and business.phone2 not in smsList:
				smsList.append(business.phone2)
			if business.email != None and business.email != '' and business.email not in emailList:
				emailList.append(business.email)
		elif property:
			receipt = generateReceipt(tax_type, payment, tax, 'property',property)		
			#get owners of this property
			owners = property.owners.filter(i_status='active')
			if owners:
				for owner in owners:
					citizen = owner.owner_citizen
					if citizen:
						if citizen.phone_1 != '' and citizen.phone_1 not in smsList:
							smsList.append(citizen.phone_1)
						if citizen.phone_2 != '' and citizen.phone_2 not in smsList:
							smsList.append(citizen.phone_2)
						if citizen.email != '' and citizen.email not in emailList:
							emailList.append(citizen.email)
					business = owner.owner_business
					if business:
						if business.phone1 != None and business.phone1 != '' and business.phone1 not in smsList:
								smsList.append(business.phone1)
						if business.phone2 != None and business.phone2 != '' and business.phone2 not in smsList:
								smsList.append(business.phone2)
						if business.email != None and business.email != '' and business.email not in emailList:
								emailList.append(business.email)

		#send receipt if submited
		if request.POST.has_key('send_receipt'):
			invoice_id = PaymentMapper.generateInvoiceId(tax_type, payment)
			logSendSms = ''
			logSendEmail = ''
			errorEmailList = []
			errorSmsList = []
			sendSmsList = request.POST.getlist('send_sms_list[]')

			if sendSmsList:
				for i in sendSmsList:
					logSendSms += i.strip() + ','

			if request.POST.getlist('send_sms_input[]'):
				for i in request.POST.getlist('send_sms_input[]'):
					if i != '':
						sendSmsList.append(i.strip())

				#get matches of input sms & info to save to log later
				smsInputPairList = zip(request.POST.getlist('send_sms_input[]'),request.POST.getlist('send_sms_info_input[]'))
				for i, e in smsInputPairList:
					if i != '':
						logSendSms += i.strip() + ' [' + e.strip() + '],'

			sendEmailList = request.POST.getlist('send_email_list[]')
			if sendEmailList:
				for i in sendEmailList:
					logSendEmail += i.strip() + ','

			if request.POST.getlist('send_email_input[]') != '':
				inputList = request.POST.getlist('send_email_input[]');
				for i in inputList:
					if i != '':
						sendEmailList.append(i.strip())

				#get matches of input sms & info to save to log later
				emailInputPairList = zip(request.POST.getlist('send_email_input[]'),request.POST.getlist('send_email_info_input[]'))
				for i, e in emailInputPairList:
					if i != '':
						logSendEmail += i.strip() + ' [' + e.strip() + '],'


			if sendEmailList:
				for i in sendEmailList:
					try:
						EmailField().clean(i)
					except:
						errorEmailList.append(i)

			if sendSmsList:
				for i in sendSmsList:
					if not i.isdigit():
						errorSmsList.append(i)

			if errorSmsList:
				send_receipt_error = "The system can not send receipt to invalid sms: " + ','.join(errorSmsList)
			elif errorEmailList:
				send_receipt_error = "The system can not send receipt to invalid email addresses: " + ','.join(errorEmailList)
			else:

				if sendEmailList:
					subject = 'Receipt for ' + tax_label
					content = PaymentMapper.render_to_pdf(
								'tax/_receipt_template_pdf.html',
								{
									'pagesize':'A4',
									'receipt':receipt
								}
							).content

					attachment = {'name':'receipt.pdf','content':content,'mime':'application/pdf'}
					result = CommonUtil.sendEmail(subject,'','',sendEmailList,attachments=[attachment])
					if not result:
						send_receipt_error = "Error in sending email"

				if send_receipt_error == '' and sendSmsList:
					content = 'Receipt No: ' + str(invoice_id) + '. You have paid ' + str(payment.amount) + tax.currency + ' for ' + tax_type + ' of ' + tax_label
					response = CommonUtil.sendSms(content,sendSmsList)
					#message content need to be urlencoded
					if response.find('ERROR') >= 0:
						lines = response.split("\n")
						count = 0
						smsErrors = []
						for i in lines:
							if i.find('ERROR') >= 0:
								smsErrors.append(sendSmsList[count])
							count = count + 1
						send_receipt_error = "Error in sending sms to: " + ','.join(smsErrors)

				if send_receipt_error == '':
					send_receipt_message = "Receipt has been sent successfully!"
					#start log this
					log = ''
					if logSendSms != '':
						log += " by SMS to " + logSendSms
					if logSendEmail != '':
						log += " by email to " + logSendEmail

					log = 'Send Receipt (ID: ' + str(invoice_id) + ') for ' + tax_type + ' of ' + tax_label + log
						
					my_citizen = CitizenMapper.getCitizenByCitizenId(national_citizen_id)
					my_property = PropertyMapper.getPropertyByPlotId(plot_id)
					my_business = BusinessMapper.getBusinessesById(business_id)
					LogMapper.createLog(request,action="send receipt",citizen=my_citizen,property=my_property,business=my_business,message=log,tax_type=tax_type,tax_id=tax.id,payment_type='pay_' + tax_type,payment_id=payment.id)

		tablet_print_link = '/admin/tax/tax/generate_epayinvoice/?type=' + tax_type + '&id=' + id + '&tablet_printing=1'
		tablet_printing = False
		if GET.get('tablet_printing',None) != None:
			tablet_printing = True

		"""
		get property ownership info
		"""
		owner_info_string = None
		owners = []
		if property_id:
			ownerships = Ownership.objects.filter(asset_property = property, i_status = 'active')
			if ownerships:
				for ownership in ownerships:
					if ownership.owner_citizen:
						owners.append(ownership.owner_citizen.getDisplayName())
					elif ownership.owner_business:
						owners.append(ownership.owner_business.getDisplayName())
					elif ownership.owner_subbusiness:
						owners.append(ownership.owner_subbusiness.getDisplayName())
		owners_string = None
		if owners:
			owners_string = ','.join(owners)
		receipt['epay_no'] = epay_no


		return render_to_response('tax/tax_tax_invoice.html',{'tablet_printing':tablet_printing,'tablet_print_link':tablet_print_link,'tax_url':tax_url,'tax_label':tax_label,'receipt':receipt, 
														'smsList':smsList, 'emailList':emailList,'sendSmsList':sendSmsList,
														'sendEmailList':sendEmailList,'send_receipt_message':send_receipt_message,
														'send_receipt_error':send_receipt_error,'emailInputPairList':emailInputPairList,
														'smsInputPairList':smsInputPairList,'media':media,'tax':tax,'payment':payment,'tax_type':tax_type,
														'business_id':business_id,'citizen_id':citizen_id,'property_id':property_id,'owners_string':owners_string,},
								context_instance=RequestContext(request))

	
def displayGenerateEpayInvoicePage(request):
		GET = request.GET
		tax_type = GET['type']
		staff = request.session.get('user')
		tax_label = ''
		id = request.GET.get('id')
		national_citizen_id = None
		plot_id = None
		business_id = None
		property_id = None
		citizen_id = None
		citizen = None
		business = None
		property = None
		tax_url = None

		#also collect the sms/email contact belong to this citizen/businesss/property for receipt actions
		smsList = []
		emailList = []
		smsInputPairList = []
		emailInputPairList = []
		sendSmsList = None
		sendEmailList = None
		send_receipt_message = ''
		send_receipt_error = ''

		#get current view taxes url in the session if exist
		if request.session.has_key('tax_url'):
			tax_url = request.session['tax_url']
		
		try:
			if tax_type == 'fixed_asset':
				tax = get_object_or_404(PropertyTaxItem,pk=id)
				property = tax.property
				property_id = property.id
				tax_label = 'Fixed Asset Tax for '

			elif tax_type == 'rental_income':
				tax = get_object_or_404(RentalIncomeTax,pk=id)
				property = tax.property
				property_id = property.id

			elif tax_type == 'trading_license':
				tax = get_object_or_404(TradingLicenseTax,pk=id)
				business = tax.business
				if tax.subbusiness:
					business = tax.subbusiness.business

			elif tax_type == 'misc_fee':
				tax = get_object_or_404(MiscellaneousFee,pk=id)
				tax_label = 'Miscellaneous Fee'

				property = tax.property
				business = tax.business
				citizen = tax.citizen
				if tax.subbusiness:
					business = tax.subbusiness.business

			else:
				tax = get_object_or_404(Fee,pk=id)
				tax_label = 'Fee'

				property = tax.property
				business = tax.business
				citizen = tax.citizen
				if tax.subbusiness:
					business = tax.subbusiness.business
		except Exception:
			raise Http404

		reference = getTaxReference(tax_type, tax)
		tax_label = tax_label + reference

		#get the list of support medias for this tax/fee if exist
		media = Media.objects.filter(tax_type__exact=tax_type,tax_id__exact=tax.id,i_status='active')

		resubmit_url = None
		#only allow resubmit tax info for full unpaid taxes
		if tax.remaining_amount == tax.amount:
			resubmit_url = '/admin/tax/tax/submit_tax/?type=' + tax_type + '&id=' + str(tax.id)

		#generate receipt
		receipt = None

		if citizen:
			national_citizen_id = citizen.citizen_id
			receipt = generateEPayInvoice(tax_type, tax, 'citizen',citizen)
			citizen_id = citizen.id

			if citizen.phone_1 != None and citizen.phone_1 != '' and citizen.phone_1 not in smsList:
				smsList.append(citizen.phone_1)
			if citizen.phone_2 != None and citizen.phone_2 != '' and citizen.phone_2 not in smsList:
				smsList.append(citizen.phone_2)
			if citizen.email != None and citizen.email != '' and citizen.email not in emailList:
				emailList.append(citizen.email)
		elif business:
			business_id = business.id
			receipt = generateEPayInvoice(tax_type, tax, 'business',business)

			if business.phone1 != None and business.phone1 != '' and business.phone1 not in smsList:
				smsList.append(business.phone1)
			if business.phone2 != None and business.phone2 != '' and business.phone2 not in smsList:
				smsList.append(business.phone2)
			if business.email != None and business.email != '' and business.email not in emailList:
				emailList.append(business.email)
		elif property:
			receipt = generateEPayInvoice(tax_type, tax, 'property',property)
			#get owners of this property
			owners = property.owners.filter(i_status='active')
			if owners:
				for owner in owners:
					citizen = owner.owner_citizen
					if citizen:
						if citizen.phone_1 != '' and citizen.phone_1 not in smsList:
							smsList.append(citizen.phone_1)
						if citizen.phone_2 != '' and citizen.phone_2 not in smsList:
							smsList.append(citizen.phone_2)
						if citizen.email != '' and citizen.email not in emailList:
							emailList.append(citizen.email)
					business = owner.owner_business
					if business:
						if business.phone1 != None and business.phone1 != '' and business.phone1 not in smsList:
								smsList.append(business.phone1)
						if business.phone2 != None and business.phone2 != '' and business.phone2 not in smsList:
								smsList.append(business.phone2)
						if business.email != None and business.email != '' and business.email not in emailList:
								emailList.append(business.email)


		#send receipt if submited
		if request.POST.has_key('send_receipt'):
			epay_no = PaymentMapper.generateEpayNo(tax_type, tax)
			logSendSms = ''
			logSendEmail = ''
			errorEmailList = []
			errorSmsList = []
			sendSmsList = request.POST.getlist('send_sms_list[]')

			if sendSmsList:
				for i in sendSmsList:
					logSendSms += i.strip() + ','

			if request.POST.getlist('send_sms_input[]'):
				for i in request.POST.getlist('send_sms_input[]'):
					if i != '':
						sendSmsList.append(i.strip())

				#get matches of input sms & info to save to log later
				smsInputPairList = zip(request.POST.getlist('send_sms_input[]'),request.POST.getlist('send_sms_info_input[]'))
				for i, e in smsInputPairList:
					if i != '':
						logSendSms += i.strip() + ' [' + e.strip() + '],'

			sendEmailList = request.POST.getlist('send_email_list[]')
			if sendEmailList:
				for i in sendEmailList:
					logSendEmail += i.strip() + ','

			if request.POST.getlist('send_email_input[]') != '':
				inputList = request.POST.getlist('send_email_input[]');
				for i in inputList:
					if i != '':
						sendEmailList.append(i.strip())

				#get matches of input sms & info to save to log later
				emailInputPairList = zip(request.POST.getlist('send_email_input[]'),request.POST.getlist('send_email_info_input[]'))
				for i, e in emailInputPairList:
					if i != '':
						logSendEmail += i.strip() + ' [' + e.strip() + '],'


			if sendEmailList:
				for i in sendEmailList:
					try:
						EmailField().clean(i)
					except:
						errorEmailList.append(i)

			if sendSmsList:
				for i in sendSmsList:
					if not i.isdigit():
						errorSmsList.append(i)

			if errorSmsList:
				send_receipt_error = "The system can not send receipt to invalid sms: " + ','.join(errorSmsList)
			elif errorEmailList:
				send_receipt_error = "The system can not send receipt to invalid email addresses: " + ','.join(errorEmailList)
			else:

				if sendEmailList:
					subject = 'Receipt for ' + tax_label
					content = PaymentMapper.render_to_pdf(
								'tax/_epay_invoice_template_pdf.html',
								{
									'pagesize':'A4',
									'receipt':receipt
								}
							).content

					attachment = {'name':'epay_invoice.pdf','content':content,'mime':'application/pdf'}
					result = CommonUtil.sendEmail(subject,'','',sendEmailList,attachments=[attachment])
					if not result:
						send_receipt_error = "Error in sending email"

				if send_receipt_error == '' and sendSmsList:
					content = 'ePay Number: ' + str(epay_no) + '. You have submit information for ' + tax_type + ' of ' + tax_label
					response = CommonUtil.sendSms(content,sendSmsList)
					#message content need to be urlencoded
					if response.find('ERROR') >= 0:
						lines = response.split("\n")
						count = 0
						smsErrors = []
						for i in lines:
							if i.find('ERROR') >= 0:
								smsErrors.append(sendSmsList[count])
							count = count + 1
						send_receipt_error = "Error in sending sms to: " + ','.join(smsErrors)

				if send_receipt_error == '':
					send_receipt_message = "ePay Invoice has been sent successfully!"
					#start log this
					log = ''
					if logSendSms != '':
						log += " by SMS to " + logSendSms
					if logSendEmail != '':
						log += " by email to " + logSendEmail

					log = 'Send ePay Invoice (No. ' + str(epay_no) + ') for ' + tax_type + ' of ' + tax_label + log

					LogMapper.createLog(request,action="send receipt",citizen=citizen,property=property,business=business,message=log,tax_type=tax_type,tax_id=tax.id)

		tablet_print_link = '/admin/tax/tax/generate_epayinvoice/?type=' + tax_type + '&id=' + id + '&tablet_printing=1'
		tablet_printing = False
		if GET.get('tablet_printing',None) != None:
			tablet_printing = True

		owner_info_string = None
		owners = []
		if property_id:
			ownerships = Ownership.objects.filter(asset_property = property, i_status = 'active')
			if ownerships:
				for ownership in ownerships:
					if ownership.owner_citizen:
						owners.append(ownership.owner_citizen.getDisplayName())
					elif ownership.owner_business:
						owners.append(ownership.owner_business.getDisplayName())
					elif ownership.owner_subbusiness:
						owners.append(ownership.owner_subbusiness.getDisplayName())
		owners_string = None
		if owners:
			owners_string = ','.join(owners)
		#defer
		deferred_until = None
		if hasattr(tax,'months_deferred'):
			if tax.months_deferred:
				deferred_until = tax.due_date + relativedelta(months=tax.months_deferred)

		return render_to_response('tax/tax_tax_epayinvoice.html',{'tablet_printing':tablet_printing,'tablet_print_link':tablet_print_link,'resubmit_url':resubmit_url,'tax_url':tax_url,'tax_label':tax_label,'receipt':receipt, 
														'smsList':smsList, 'emailList':emailList,'sendSmsList':sendSmsList, 'deferred_until': deferred_until,
														'sendEmailList':sendEmailList,'send_receipt_message':send_receipt_message,
														'send_receipt_error':send_receipt_error,'emailInputPairList':emailInputPairList,
														'smsInputPairList':smsInputPairList,'media':media,'tax':tax,'tax_type':tax_type,
														'business_id':business_id,'citizen_id':citizen_id,'property_id':property_id, 'owners_string':owners_string,},
								context_instance=RequestContext(request))

# multi payments
def displayGenerateMultipayInvoicePage(request, id=None):
		tax_type = 'fee'
		GET = request.GET
		staff = request.session.get('user')
		tax_label = ''
		id = request.GET.get('id') or id
		business_id = None
		property_id = None
		citizen_id = None
		citizen = None
		business = None
		property = None
		tax_url = None
		#also collect the sms/email contact belong to this citizen/businesss/property for receipt actions
		smsList = []
		emailList = []
		smsInputPairList = []
		emailInputPairList = []
		sendSmsList = None
		sendEmailList = None

		send_receipt_message = ''
		send_receipt_error = ''

		#only allow pay multiple cleaning fees for 1 business/branch atm (prevent even the case of trying to play cleaning fee for main business & branch at the same time)
		multipay_receipt = get_object_or_404(MultipayReceipt,id=id,i_status='active')

		payment_relations = multipay_receipt.payment_relations.all()
		payments = []
		tax_ids = []
		if payment_relations:
			for i in payment_relations:
				payments.append(i.payfee)
				tax_ids.append(i.payfee.fee.id)
		payment = payments[0]
		tax = payment.fee
		tax_label = 'Fee'

		property = tax.property
		if property:
			property_id = property.pk

		business = tax.business
		if tax.subbusiness:
			business = tax.subbusiness.business

		if citizen == None and payment.citizen_id != None and payment.citizen_id != '':
			citizen = Citizen.objects.get(pk=payment.citizen_id)
		elif business == None and payment.business_id != None and payment.business_id != '':
			business = Business.objects.get(pk=payment.business_id)

		tax_label = 'Pay multiple ' + tax.fee_type.replace("_"," ").title()

		#get the list of support medias for this tax/fee if exist
		media = Media.objects.filter(tax_id__in=tax_ids,i_status='active')

		#get current view taxes url in the session if exist
		if request.session.has_key('tax_url'):
			tax_url = request.session['tax_url']

		#generate receipt
		receipt = None
		if citizen:
			national_citizen_id = citizen.citizen_id
			receipt = generateMultipayReceipt(payments, multipay_receipt, 'citizen',citizen)
			citizen_id = citizen.id

			if citizen.phone_1 != None and citizen.phone_1 != '' and citizen.phone_1 not in smsList:
				smsList.append(citizen.phone_1)
			if citizen.phone_2 != None and citizen.phone_2 != '' and citizen.phone_2 not in smsList:
				smsList.append(citizen.phone_2)
			if citizen.email != None and citizen.email != '' and citizen.email not in emailList:
				emailList.append(citizen.email)
		elif business:
			business_id = business.id
			receipt = generateMultipayReceipt(payments, multipay_receipt, 'business',business)

			if business.phone1 != None and business.phone1 != '' and business.phone1 not in smsList:
				smsList.append(business.phone1)
			if business.phone2 != None and business.phone2 != '' and business.phone2 not in smsList:
				smsList.append(business.phone2)
			if business.email != None and business.email != '' and business.email not in emailList:
				emailList.append(business.email)
		elif property:
			receipt = generateMultipayReceipt(payments, multipay_receipt, 'property',property)
			
			#get owners of this property
			owners = property.owners.filter(i_status='active')
			if owners:
				for owner in owners:
					citizen = owner.owner_citizen
					if citizen:
						if citizen.phone_1 != '' and citizen.phone_1 not in smsList:
							smsList.append(citizen.phone_1)
						if citizen.phone_2 != '' and citizen.phone_2 not in smsList:
							smsList.append(citizen.phone_2)
						if citizen.email != '' and citizen.email not in emailList:
							emailList.append(citizen.email)
					business = owner.owner_business
					if business:
						if business.phone1 != None and business.phone1 != '' and business.phone1 not in smsList:
								smsList.append(business.phone1)
						if business.phone2 != None and business.phone2 != '' and business.phone2 not in smsList:
								smsList.append(business.phone2)
						if business.email != None and business.email != '' and business.email not in emailList:
								emailList.append(business.email)

		#send receipt if submited
		if request.POST.has_key('send_receipt'):
			invoice_id = PaymentMapper.generateInvoiceId(tax_type, payment)
			logSendSms = ''
			logSendEmail = ''
			errorEmailList = []
			errorSmsList = []
			sendSmsList = request.POST.getlist('send_sms_list[]')

			if sendSmsList:
				for i in sendSmsList:
					logSendSms += i.strip() + ','

			if request.POST.getlist('send_sms_input[]'):
				for i in request.POST.getlist('send_sms_input[]'):
					if i != '':
						sendSmsList.append(i.strip())

				#get matches of input sms & info to save to log later
				smsInputPairList = zip(request.POST.getlist('send_sms_input[]'),request.POST.getlist('send_sms_info_input[]'))
				for i, e in smsInputPairList:
					if i != '':
						logSendSms += i.strip() + ' [' + e.strip() + '],'

			sendEmailList = request.POST.getlist('send_email_list[]')
			if sendEmailList:
				for i in sendEmailList:
					logSendEmail += i.strip() + ','

			if request.POST.getlist('send_email_input[]') != '':
				inputList = request.POST.getlist('send_email_input[]');
				for i in inputList:
					if i != '':
						sendEmailList.append(i.strip())

				#get matches of input sms & info to save to log later
				emailInputPairList = zip(request.POST.getlist('send_email_input[]'),request.POST.getlist('send_email_info_input[]'))
				for i, e in emailInputPairList:
					if i != '':
						logSendEmail += i.strip() + ' [' + e.strip() + '],'


			if sendEmailList:
				for i in sendEmailList:
					try:
						EmailField().clean(i)
					except:
						errorEmailList.append(i)

			if sendSmsList:
				for i in sendSmsList:
					if not i.isdigit():
						errorSmsList.append(i)

			if errorSmsList:
				send_receipt_error = "The system can not send receipt to invalid sms: " + ','.join(errorSmsList)
			elif errorEmailList:
				send_receipt_error = "The system can not send receipt to invalid email addresses: " + ','.join(errorEmailList)
			else:

				if sendEmailList:
					subject = 'Receipt for ' + tax_label
					content = PaymentMapper.render_to_pdf(
								'tax/_receipt_multipay_template_pdf.html',
								{
									'pagesize':'A4',
									'receipt':receipt
								}
							).content

					attachment = {'name':'receipt.pdf','content':content,'mime':'application/pdf'}
					result = CommonUtil.sendEmail(subject,'','',sendEmailList,attachments=[attachment])
					if not result:
						send_receipt_error = "Error in sending email"

				if send_receipt_error == '' and sendSmsList:
					content = 'Receipt No: ' + str(invoice_id) + '. You have paid ' + str(payment.amount) + tax.currency + ' for ' + tax_type + ' of ' + tax_label
					response = CommonUtil.sendSms(content,sendSmsList)
					#message content need to be urlencoded
					if response.find('ERROR') >= 0:
						lines = response.split("\n")
						count = 0
						smsErrors = []
						for i in lines:
							if i.find('ERROR') >= 0:
								smsErrors.append(sendSmsList[count])
							count = count + 1
						send_receipt_error = "Error in sending sms to: " + ','.join(smsErrors)

				if send_receipt_error == '':
					send_receipt_message = "Receipt has been sent successfully!"
					#start log this
					log = ''
					if logSendSms != '':
						log += " by SMS to " + logSendSms
					if logSendEmail != '':
						log += " by email to " + logSendEmail

					log = 'Send Receipt (ID: ' + str(invoice_id) + ') for ' + tax_type + ' of ' + tax_label + log
						
					LogMapper.createLog(request,action="send receipt",citizen=citizen,property=property,business=business,message=log,tax_type=tax_type,tax_id=tax.id,payment_type='pay_' + tax_type,payment_id=payment.id)

		tablet_print_link = '/admin/tax/tax/generate_multipayinvoice/?type=' + tax_type + '&id=' + id + '&tablet_printing=1'
		tablet_printing = False
		if GET.get('tablet_printing',None) != None:
			tablet_printing = True
		return render_to_response('tax/tax_tax_invoice_multipay.html',{'tablet_printing':tablet_printing,'tablet_print_link':tablet_print_link,'tax_url':tax_url,'tax_label':tax_label,'receipt':receipt, 
														'smsList':smsList, 'emailList':emailList,'sendSmsList':sendSmsList,
														'sendEmailList':sendEmailList,'send_receipt_message':send_receipt_message,
														'send_receipt_error':send_receipt_error,'emailInputPairList':emailInputPairList,
														'smsInputPairList':smsInputPairList,'media':media,'tax':tax,'payment':payment,'tax_type':tax_type,
														'business_id':business_id,'citizen_id':citizen_id,'property_id':property_id},
								context_instance=RequestContext(request))


def displayGenerateMultipayEpayInvoicePage(request):
		GET = request.GET
		tax_type = GET['type']
		staff = request.session.get('user')
		tax_label = ''
		id = request.GET.get('id')
		national_citizen_id = None
		plot_id = None
		business_id = None
		property_id = None
		citizen_id = None
		citizen = None
		business = None
		property = None
		tax_url = None

		#also collect the sms/email contact belong to this citizen/businesss/property for receipt actions
		smsList = []
		emailList = []
		smsInputPairList = []
		emailInputPairList = []
		sendSmsList = None
		sendEmailList = None
		send_receipt_message = ''
		send_receipt_error = ''

		#get current view taxes url in the session if exist
		if request.session.has_key('tax_url'):
			tax_url = request.session['tax_url']

		taxes = Fee.objects.filter(id__in=id.split(','),i_status='active')
		if tax_type != 'fee' or not taxes:
			raise Http404
		tax_label = 'Fee'
		tax = taxes[0]
		property = tax.property
		business = tax.business
		if tax.subbusiness:
			business = tax.subbusiness.business

		reference = getTaxReference(tax_type, tax)
		tax_label = tax_label + reference

		#get the list of support medias for this tax/fee if exist
		media = Media.objects.filter(tax_type__exact=tax_type,tax_id__exact=tax.id,i_status='active')

		#generate receipt
		receipt = None

		if citizen:
			national_citizen_id = citizen.citizen_id
			receipt = generateMultipayEPayInvoice(tax_type, taxes, 'citizen',citizen)
			citizen_id = citizen.id

			if citizen.phone_1 != None and citizen.phone_1 != '' and citizen.phone_1 not in smsList:
				smsList.append(citizen.phone_1)
			if citizen.phone_2 != None and citizen.phone_2 != '' and citizen.phone_2 not in smsList:
				smsList.append(citizen.phone_2)
			if citizen.email != None and citizen.email != '' and citizen.email not in emailList:
				emailList.append(citizen.email)
		elif business:
			business_id = business.id
			receipt = generateMultipayEPayInvoice(tax_type, taxes, 'business',business)

			if business.phone1 != None and business.phone1 != '' and business.phone1 not in smsList:
				smsList.append(business.phone1)
			if business.phone2 != None and business.phone2 != '' and business.phone2 not in smsList:
				smsList.append(business.phone2)
			if business.email != None and business.email != '' and business.email not in emailList:
				emailList.append(business.email)
		elif property:
			receipt = generateMultipayEPayInvoice(tax_type, taxes, 'property',property)

			#get owners of this property
			owners = property.owners.filter(i_status='active')
			if owners:
				for owner in owners:
					citizen = owner.owner_citizen
					if citizen:
						if citizen.phone_1 != '' and citizen.phone_1 not in smsList:
							smsList.append(citizen.phone_1)
						if citizen.phone_2 != '' and citizen.phone_2 not in smsList:
							smsList.append(citizen.phone_2)
						if citizen.email != '' and citizen.email not in emailList:
							emailList.append(citizen.email)
					business = owner.owner_business
					if business:
						if business.phone1 != None and business.phone1 != '' and business.phone1 not in smsList:
								smsList.append(business.phone1)
						if business.phone2 != None and business.phone2 != '' and business.phone2 not in smsList:
								smsList.append(business.phone2)
						if business.email != None and business.email != '' and business.email not in emailList:
								emailList.append(business.email)


		#send receipt if submited
		if request.POST.has_key('send_receipt'):
			epay_no = PaymentMapper.generateEpayNo(tax_type, tax)
			logSendSms = ''
			logSendEmail = ''
			errorEmailList = []
			errorSmsList = []
			sendSmsList = request.POST.getlist('send_sms_list[]')

			if sendSmsList:
				for i in sendSmsList:
					logSendSms += i.strip() + ','

			if request.POST.getlist('send_sms_input[]'):
				for i in request.POST.getlist('send_sms_input[]'):
					if i != '':
						sendSmsList.append(i.strip())

				#get matches of input sms & info to save to log later
				smsInputPairList = zip(request.POST.getlist('send_sms_input[]'),request.POST.getlist('send_sms_info_input[]'))
				for i, e in smsInputPairList:
					if i != '':
						logSendSms += i.strip() + ' [' + e.strip() + '],'

			sendEmailList = request.POST.getlist('send_email_list[]')
			if sendEmailList:
				for i in sendEmailList:
					logSendEmail += i.strip() + ','

			if request.POST.getlist('send_email_input[]') != '':
				inputList = request.POST.getlist('send_email_input[]');
				for i in inputList:
					if i != '':
						sendEmailList.append(i.strip())

				#get matches of input sms & info to save to log later
				emailInputPairList = zip(request.POST.getlist('send_email_input[]'),request.POST.getlist('send_email_info_input[]'))
				for i, e in emailInputPairList:
					if i != '':
						logSendEmail += i.strip() + ' [' + e.strip() + '],'


			if sendEmailList:
				for i in sendEmailList:
					try:
						EmailField().clean(i)
					except:
						errorEmailList.append(i)

			if sendSmsList:
				for i in sendSmsList:
					if not i.isdigit():
						errorSmsList.append(i)

			if errorSmsList:
				send_receipt_error = "The system can not send receipt to invalid sms: " + ','.join(errorSmsList)
			elif errorEmailList:
				send_receipt_error = "The system can not send receipt to invalid email addresses: " + ','.join(errorEmailList)
			else:

				if sendEmailList:
					subject = 'Receipt for ' + tax_label
					content = PaymentMapper.render_to_pdf(
								'tax/_epay_invoice_template_pdf.html',
								{
									'pagesize':'A4',
									'receipt':receipt
								}
							).content

					attachment = {'name':'epay_invoice.pdf','content':content,'mime':'application/pdf'}
					result = CommonUtil.sendEmail(subject,'','',sendEmailList,attachments=[attachment])
					if not result:
						send_receipt_error = "Error in sending email"

				if send_receipt_error == '' and sendSmsList:
					content = 'ePay Number: ' + str(epay_no) + '. You have submit information for ' + tax_type + ' of ' + tax_label
					response = CommonUtil.sendSms(content,sendSmsList)
					#message content need to be urlencoded
					if response.find('ERROR') >= 0:
						lines = response.split("\n")
						count = 0
						smsErrors = []
						for i in lines:
							if i.find('ERROR') >= 0:
								smsErrors.append(sendSmsList[count])
							count = count + 1
						send_receipt_error = "Error in sending sms to: " + ','.join(smsErrors)

				if send_receipt_error == '':
					send_receipt_message = "ePay Invoice has been sent successfully!"
					#start log this
					log = ''
					if logSendSms != '':
						log += " by SMS to " + logSendSms
					if logSendEmail != '':
						log += " by email to " + logSendEmail

					log = 'Send ePay Invoice (No. ' + str(epay_no) + ') for ' + tax_type + ' of ' + tax_label + log

					LogMapper.createLog(request,action="send receipt",citizen=citizen,property=property,business=business,message=log,tax_type=tax_type,tax_id=tax.id)

		tablet_print_link = '/admin/tax/tax/generate_epayinvoice/?type=' + tax_type + '&id=' + id + '&tablet_printing=1'
		tablet_printing = False
		if GET.get('tablet_printing',None) != None:
			tablet_printing = True

		owner_info_string = None
		owners = []
		if property_id:
			ownerships = Ownership.objects.filter(asset_property = property, i_status = 'active')
			if ownerships:
				for ownership in ownerships:
					if ownership.owner_citizen:
						owners.append(ownership.owner_citizen.getDisplayName())
					elif ownership.owner_business:
						owners.append(ownership.owner_business.getDisplayName())
					elif ownership.owner_subbusiness:
						owners.append(ownership.owner_subbusiness.getDisplayName())
		owners_string = None
		if owners:
			owners_string = ','.join(owners)
		#defer
		deferred_until = None
		if hasattr(tax,'months_deferred'):
			if tax.months_deferred:
				deferred_until = tax.due_date + relativedelta(months=tax.months_deferred)
		return render_to_response('tax/tax_tax_epayinvoice.html',{'tablet_printing':tablet_printing,'tablet_print_link':tablet_print_link,'tax_url':tax_url,'tax_label':tax_label,'receipt':receipt, 
														'smsList':smsList, 'emailList':emailList,'sendSmsList':sendSmsList, 'deferred_until':deferred_until,
														'sendEmailList':sendEmailList,'send_receipt_message':send_receipt_message,
														'send_receipt_error':send_receipt_error,'emailInputPairList':emailInputPairList,
														'smsInputPairList':smsInputPairList,'media':media,'tax':tax,'tax_type':tax_type,
														'business_id':business_id,'citizen_id':citizen_id,'property_id':property_id, 'owners_string':owners_string,},
								context_instance=RequestContext(request))


def displayPaymentSearchPage(request):

	if request.GET.get('search',None) == None and request.GET.get('export_pdf',None) == None:
		form = payment_search_form()
		return render_to_response('tax/tax_tax_paymentsearch.html',{'form':form,'default':True},
									context_instance=RequestContext(request))
	else:
		form = payment_search_form(request.GET)
		if not form.is_valid():
			return render_to_response('tax/tax_tax_paymentsearch.html',{'form':form,'default':True},
									context_instance=RequestContext(request))
		else:
			invoice_id = form.cleaned_data['invoice_id']
			citizen_id = form.cleaned_data['citizen_id']
			tin = form.cleaned_data['tin']
			upi = form.cleaned_data['upi']
			tax_type = form.cleaned_data['tax_type']
			bank = form.cleaned_data['bank']
			receipt_no = form.cleaned_data['receipt_no']
			manual_receipt = form.cleaned_data['manual_receipt']
			period_from = form.cleaned_data['period_from']
			period_to = form.cleaned_data['period_to']

			conditions = {}
			if invoice_id and invoice_id!='':
				tax_type_prefix = invoice_id[0:2]
				#case of multiple payments in 1 receipt
				if tax_type_prefix == 'MP':
					tax_type = 'cleaning_fee'
					multipay_receipt = get_object_or_404(MultipayReceipt,pk=invoice_id[2:])
					payment_relations = multipay_receipt.payment_relations.all()
					payment_ids = []
					if payment_relations:
						for i in payment_relations:
							payment_ids.append(i.payfee.id)
					conditions['payment_ids'] = payment_ids
				else:
				#normal single payment
					tax_type = variables.getValueByKey(variables.tax_and_fee_invoice_prefixes,tax_type_prefix)
					if tax_type:					
						try:
							conditions['payment_id'] = int(invoice_id[2:])
						except Exception:
							#if entered invalid invoice id, set invalid payment_id condition to return empty result
							conditions['payment_id'] = -222222
					else:
						#if entered invalid invoice id, set invalid payment_id condition to return empty result
						conditions['payment_id'] = -222222


			if citizen_id and citizen_id!='':
				conditions['citizen_id'] = citizen_id
			if upi and upi!='':
				conditions['upi'] = upi
			if tin and tin!='':
				conditions['tin'] = tin
			if tax_type:
				if tax_type in ['Land lease fee','Market fee','Cleaning fee']:
					conditions['fee_type'] = tax_type
			if bank and bank != '':
				conditions['bank'] = bank
			if receipt_no and receipt_no != '':
				conditions['receipt_no'] = receipt_no
			if manual_receipt and manual_receipt != '':
				conditions['manual_receipt'] = manual_receipt
			if period_from and period_from != '':
				#conditions['period_from'] = timezone.make_aware(period_from, timezone.get_default_timezone())
				conditions['period_from'] = timezone.make_aware(datetime.combine(period_from, time(0,0,0)), timezone.get_default_timezone())

			if period_to and period_to != '':
				#conditions['period_to'] = timezone.make_aware(period_to, timezone.get_default_timezone())
				conditions['period_to'] = timezone.make_aware(datetime.combine(period_to, time(23,59,59)), timezone.get_default_timezone())

			#only show active payments
			conditions['i_status'] = 'active'

			payments_found = []
			tax_types_to_search = []
			if tax_type and tax_type!='':
				tax_types_to_search.append(tax_type)
			else:
				for c in tax_and_fee_types:
					tax_types_to_search.append(c[0])

			limit = 100
			exceed_limit = False
			records_in_page = 20
			exporting = None

			if request.GET.get('export_pdf',None) != None:
				exporting = 'pdf'

			count = 0
			for tax_type_obj in tax_types_to_search:
				remaining_limit = limit - count
				if tax_type_obj == 'fixed_asset':
					payments = PayFixedAssetTaxMapper.getPayFixedAssetTaxByConditions(conditions, remaining_limit)
				elif tax_type_obj == 'rental_income':
					payments = PayRentalIncomeTaxMapper.getPayRentalIncomeTaxByConditions(conditions, remaining_limit)
				elif tax_type_obj == 'trading_license':
					payments = PayTradingLicenseTaxMapper.getPayTradingLicenseTaxByConditions(conditions, remaining_limit)						
				else:
					conditions_new = copy.deepcopy(conditions)
					conditions_new['fee_type'] = tax_type_obj
					payments = PayFeeMapper.getPayFeeByConditions(conditions_new, remaining_limit)

				count = count + len(payments)
				payments_found = payments_found	+ list(payments)
				if count > limit:
					exceed_limit = True
					break
						

			if payments_found and exceed_limit == False and len(payments_found) > 0:
				#payments_found.sort(key=lambda x:x['paid_date'], reverse = True)
				page = 1
				if request.GET.get('page',None) != None:
					page = request.GET.get('page')

				paginator = Paginator(payments_found, records_in_page)
				try:
					payments_found = paginator.page(page)
				except PageNotAnInteger:
					# If page is not an integer, deliver first page.
					payments_found = paginator.page(1)
				except EmptyPage:
					# If page is out of range (e.g. 9999), deliver last page of results.
					payments_found = paginator.page(paginator.num_pages)

				#format paginated result
				payments_found.object_list = formatPaymentsForDisplay(request,payments_found.object_list)		

			if exporting == 'pdf':
				return PaymentMapper.generatePaymentPdf(payments_found)
			#elif exporting == 'print':

			else:
				return render_to_response('tax/tax_tax_paymentsearch.html',{'form':form,'payments':payments_found,'exceed_limit':exceed_limit,'limit':limit,'pagination_url':request.get_full_path().rsplit('&page')[0] },
									context_instance=RequestContext(request))


def displayPaymentReversePage(request):
	GET = request.GET
	type = GET['type'].replace("_tax","")
	id = GET['id']
	form = payment_reverse_form()
	payment = None
	show_tax_link = '/admin/tax/tax/'
	national_citizen_id = None
	file_list = []
	property = None
	citizen = None
	business = None
	multi_payments = None
	receipt = None
	months = []
	if type == 'fixed_asset':
		payment = get_object_or_404(PayFixedAssetTax,pk=id,i_status='active')
		tax = payment.property_tax_item
		property = tax.property

	elif type == 'rental_income':
		payment = get_object_or_404(PayRentalIncomeTax,pk=id,i_status='active')
		tax = payment.rental_income_tax
		property = tax.property

	elif type == 'trading_license':
		payment = get_object_or_404(PayTradingLicenseTax,pk=id,i_status='active')
		tax = payment.trading_license_tax
		business_id = tax.business_id
		if tax.subbusiness:
			business_id = tax.subbusiness.business.id
	elif type == 'misc_fee':
		payment = get_object_or_404(PayMiscellaneousFee,pk=id,i_status='active')
		tax = payment.fee
	else:
		payment = get_object_or_404(PayFee,pk=id,i_status='active')
		tax = payment.fee
		#if payment is associated with multipay receipt, get all the associated payments
		receipt_relations = payment.receipt_relations.all()
		if receipt_relations:
			multi_payments = []
			receipt = receipt_relations[0].receipt
			payment_relations = receipt.payment_relations.all()
			for i in payment_relations:
				multi_payments.append(i.payfee)
				months.append(Common.localizeDate(i.payfee.fee.period_from).strftime('%b'))
			
	if multi_payments:
		type_label = 'Multiple Payments for ' + type.replace("_"," ").title() + ' for ' + ', '.join(months) + ' ' + Common.localizeDate(multi_payments[0].fee.period_from).strftime('%Y')
		amount = receipt.amount
	else:
		type_label = type.replace("_"," ").title()
		amount = payment.amount

	reference = getTaxReference(type, tax)

	if payment.citizen_id != None:
		citizen = get_object_or_404(Citizen,pk=payment.citizen_id)
		national_citizen_id = citizen.citizen_id
		citizen_id = citizen.id
		show_tax_link = show_tax_link + 'citizen/' + str(citizen_id) + "/taxes/"
	elif payment.business_id != None:
		show_tax_link = show_tax_link + 'business/' + str(payment.business_id) + "/taxes/"
	elif property:				
		show_tax_link = show_tax_link + 'property/' + str(property.id) + "/taxes/"

	payment_staff = payment.staff
	now = timezone.make_aware(datetime.now(), timezone.get_default_timezone())
	staff = request.session.get('user')
	if request.method == "POST":
		form = payment_reverse_form(request.POST)
		file_valid = True

		if request.FILES != None:
			file_list = zip( request.FILES.getlist('media_urls'), request.POST.getlist('media_titles'), request.POST.getlist('media_descs'))
			#validate file
			for file, title, desc in file_list:
				if file.size > variables.MAX_UPLOAD_SIZE:
					messages.error(request, 'File upload exceeded the maximum limit of ' + str(int(variables.MAX_UPLOAD_SIZE / 1048576.0)) + 'Mb')
					file_valid = False
					break;

		if form.is_valid() and file_valid:
			reason = form.cleaned_data['reason']
			log = "Rolled back " + type_label + " payment on " + str(now.strftime('%Y/%m/%d %H:%M:%S')) + ".\n" + "Reason: " + reason
			note = "Rolled back " + type_label + " payment on " + str(now.strftime('%Y/%m/%d %H:%M:%S')) + " by " + staff.firstname + ' ' + staff.lastname + ".\n" + "Reason: " + reason
			if multi_payments:
				#change status of payment to inactive, and reverse the tax item to not paid for ALL taxes/payments associated with this multipay receipt
				for payment in multi_payments:
					tax = payment.fee
					payment.i_status = 'inactive'
					if payment.note == None or payment.note == '':
						payment.note = log
					else:
						payment.note = payment.note + "\n" + log

					payment.save()

					tax.is_paid = False
					if tax.remaining_amount:
						tax.remaining_amount = tax.remaining_amount + payment.amount
						#put a check in case of overpaid
						if tax.remaining_amount > tax.amount:
							tax.remaining_amount = tax.amount
					tax.save()

				#also deactivate the multipay receipt 
				receipt.i_status = 'inactive'
				receipt.save()
			else:
				#change status of payment to inactive, and reverse the tax item to not paid
				payment.i_status = 'inactive'
				if payment.note == None or payment.note == '':
					payment.note = note
				else:
					payment.note = payment.note + "\n" + note

				payment.save()


				tax.is_paid = False
				if tax.remaining_amount:
					tax.remaining_amount = tax.remaining_amount + payment.amount
					#put a check in case of overpaid
					if tax.remaining_amount > tax.amount:
						tax.remaining_amount = tax.amount
				else:
					tax.remaining_amount = tax.amount
				tax.save()

			
			# reverse any installments
			installments = tax.installments.filter(paid_on = payment.paid_date)
			if installments:
				installment = installments[0]
				installment.paid = installment.paid - amount
				if installment.paid <= 0:
					installment.paid = 0
					paid_on = None
					installment.save()

			#start upload file & create media record
			if request.FILES != None:
				tax_folder = 'tax/' + type + '/'
				if os.path.exists(settings.MEDIA_ROOT + tax_folder) == False:
					os.mkdir(settings.MEDIA_ROOT + tax_folder)

				media_folder = tax_folder +  str(tax.id) + '/'
				if os.path.exists(settings.MEDIA_ROOT + media_folder) == False:
					os.mkdir(settings.MEDIA_ROOT + media_folder)

				now = str(datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))
				for file, title, desc in file_list:

					file_info = file.name.split('.')
					file_name = file_info[0] + '_' + now + '.' + file_info[1]
					file_path = media_folder + file_name
					with open(settings.MEDIA_ROOT + file_path, 'wb+') as destination:
						for chunk in file.chunks():
							destination.write(chunk)

					tags = 'tax|payment'

					media = Media(tags=tags,title=title,description=desc,file_name=file_name,path=file_path,file_type=file.content_type,
									file_size=file.size,citizen=citizen,business=business,property=property,
									tax_type=type,tax_id=tax.id,payment_type='pay_'+type,payment_id=payment.id,user_id=staff.id)
					media.save()
			#save the log
			LogMapper.createLog(request,object=payment,action="change",citizen=citizen,property=property,business=business,message=log,payment_type='pay_'+type,payment_id=payment.id,tax_type=type,tax_id=tax.id)

			#show success roll back page
			return render_to_response('tax/tax_tax_paymentreverse.html',{'success':True,'show_tax_link':show_tax_link},
										context_instance=RequestContext(request))

	return render_to_response('tax/tax_tax_paymentreverse.html',{'form':form,'tax':tax,'staff':payment_staff,'reference':reference,'type':type_label,'payment':payment,'amount':amount,'file_list': file_list,'multi_payments':multi_payments},
								context_instance=RequestContext(request))


def displayTaxSettingPage(request):
	settings_label = 'Default Tax Settings'
	district = None
	sector = None
	invalid_setting_ids = []
	if request.GET.get('district_id',None) != None and request.GET.get('district_id') != '':
		try:
			district = District.objects.get(pk=int(request.GET.get('district_id')))
			settings_label = district.name.title() + ' Tax Settings'
			if request.GET.get('sector_id',None) != None and request.GET.get('sector_id') != '':
				sector = Sector.objects.get(pk=int(request.GET.get('sector_id')))
				settings_label = district.name.title() + ' - ' + sector.name.title() + ' Tax Settings'
		except Exception: 
			raise Http404

	if request.method == 'POST' and request.POST.get('save_settings',None) != None:
		valid_from = datetime.strptime(request.POST['valid_from'],'%d/%m/%Y')

		postSettings = zip( request.POST.getlist('ids[]'), request.POST.getlist('values[]'))
		#validate settings first before save
		if postSettings:
			is_valid = True
			for id, value in postSettings:
				if value == None or value == "":
					is_valid = False
					invalid_setting_ids.append(int(id))

			if is_valid:
				logs = []
				today = date.today()

				for id, value in postSettings:
					result = Setting.objects.filter(pk__exact=id,i_status="active")
					if result:
						setting = result[0]
						#if is using the default setting list, create a new setting record specific for the selected district & sector
						if district != None and setting.district == None:
							if '_rate' in setting.setting_name:
								value = Decimal(value.strip())/100

							newSetting = Setting(tax_fee_name=setting.tax_fee_name,setting_name=setting.setting_name,description=setting.description,district=district,sector=sector)
							newSetting.sub_type = setting.sub_type
							newSetting.valid_from = datetime.strftime(valid_from,'%Y-%m-%d')
							newSetting.value = value

							newSetting.save()

							logMessage = "- " + setting.tax_fee_name.replace("_"," ").title() + "'s " + setting.setting_name.replace("_"," ").title()
							if setting.sub_type != "":
								logMessage = logMessage + " sub item '" + setting.sub_type.replace("_"," ").title() + "'"
							logMessage = logMessage + " from [" + str(setting.value) + "] to [" + str(newSetting.value) + "]"
							logs.append(logMessage)

						else:
							setting_changed = False
							#if is a rate setting (%), convert it to decimal number before check / save
							if '_rate' in setting.setting_name:
								value = Decimal(value.strip())/100
								if Decimal(setting.value) != Decimal(value):
									setting_changed = True
							elif str(setting.value) != str(value):
								setting_changed = True

							#check if there is a change in the setting value
							if setting_changed:
								#if this change happned on the same day as last change valid_from, just update the existing one
								if setting.valid_from == valid_from.date():
									setting.value = value
									setting.save()
								else:
									#if this change happened on another day, then save the new setting & set old one valid_to date
									newSetting = Setting(tax_fee_name=setting.tax_fee_name,setting_name=setting.setting_name,description=setting.description,district=district,sector=sector)
									newSetting.sub_type = setting.sub_type
									newSetting.valid_from = datetime.strftime(valid_from,'%Y-%m-%d')
									newSetting.value = value

									newSetting.save()

									#update old setting								
									if valid_from.date() > setting.valid_from:
										setting.valid_to = datetime.strftime(valid_from - timedelta(days=1),'%Y-%m-%d')
									else:
										setting.valid_to = setting.valid_from
									#setting.i_status = 'inactive'
									setting.save()			

								logMessage = "- " + setting.tax_fee_name.replace("_"," ").title() + "'s " + setting.setting_name.replace("_"," ").title()
								if setting.sub_type != "":
									logMessage = logMessage + " sub item '" + setting.sub_type.replace("_"," ").title() + "'"
								logMessage = logMessage + " from [" + str(setting.value) + "] to [" + str(value) + "]"
								logs.append(logMessage)

				if logs:
					messages.success(request, 'New settings have been saved.')
					#save the log
					LogMapper.createLog(request,action="change",message=" updated " + settings_label + ": \r\n" + ("\r\n").join(logs))
			else:
				messages.error(request, 'Invalid setting value. Please check your input.')

	form = tax_setting_search_form(initial={'district':district,'sector':sector})
	mySettings = []

	#get list of settings 
	if district:
		mySettings = Setting.objects.filter(Q(valid_from__lte=datetime.today(),i_status='active')|Q(valid_to__gte=datetime.today()),district=district,sector=sector).order_by("valid_from","tax_fee_name","setting_name","sub_type")
		
	#load default settings if no setting found for the selected filters
	if not mySettings:
		mySettings = Setting.objects.filter(Q(valid_from__lte=datetime.today(),i_status='active')|Q(valid_to__gte=datetime.today()),district=None,sector=None).order_by("valid_from","tax_fee_name","setting_name","sub_type")

	list = {}
	if mySettings:
		for i in mySettings:
			tax_fee_name = i.tax_fee_name.replace("_",' ').title()
			setting_name = i.setting_name.replace("_",' ').title()
			if list.has_key(tax_fee_name):
				temp = list[tax_fee_name]
			else:
				temp = {}

			if i.sub_type != None and i.sub_type != '':
				if temp.has_key(setting_name):
					setting_list = temp[setting_name]['value']
				else:
					setting_list = []

				setting_list.append({'sub_type':i.sub_type,'value':i.value,'id':i.id})
				temp[setting_name] = {'description':i.description,'value':setting_list,'type':'list','valid_from':i.valid_from,'valid_to':i.valid_to}

			elif '_rate' in i.setting_name:
				temp[setting_name] = {'id':i.id,'description':i.description,'value':str(Decimal(i.value)*100),'type':'rate','valid_from':i.valid_from,'valid_to':i.valid_to}
			else:
				temp[setting_name] = {'id':i.id,'description':i.description,'value':i.value,'type':'','valid_from':i.valid_from,'valid_to':i.valid_to}

			list[tax_fee_name] = temp
	else:
		list = None
		invalid_setting_ids = None


	return render_to_response('tax/tax_tax_settings.html',{'settings_label':settings_label,'list':list,'invalid_setting_ids':invalid_setting_ids,'form':form},
								context_instance=RequestContext(request))


def setupInstallments(request):
	GET = request.GET
	type = GET['type']
	id = GET['id']
	if type == 'fixed_asset':
		tax = get_object_or_404(PropertyTaxItem,id=GET['id'],is_paid=False,i_status='active',remaining_amount=F('amount'))
	if type == 'trading_license':
		tax = get_object_or_404(TradingLicenseTax,id=GET['id'],is_paid=False,i_status='active',remaining_amount=F('amount'))
	if type == 'rental_income':
		tax = get_object_or_404(RentalIncomeTax,id=GET['id'],is_paid=False,i_status='active',remaining_amount=F('amount'))
	if type == 'fee':
		tax = get_object_or_404(Fee,id=GET['id'],is_paid=False,i_status='active',remaining_amount=F('amount'))
		fee_type = tax.fee_type
	today = timezone.make_aware(datetime.combine(datetime.today(), time(0,0)), timezone.get_default_timezone())
	now = timezone.make_aware(datetime.now(), timezone.get_default_timezone())
	current_year = str(today.year)
	year_start = timezone.make_aware(dateutil.parser.parse(current_year + '-01-01 00:00:00'), timezone.get_default_timezone())
	year_end = timezone.make_aware(dateutil.parser.parse(current_year + '-12-31 23:59:59'), timezone.get_default_timezone())

	#ensure this is a full yearly tax
	if tax.period_from != year_start or tax.period_to != year_end:
		raise Http404

	#set up period for 4 installments - due date will be the last date of that period

	periods = [['01-01','03-31'],
			['04-01','06-30'],
			['07-01','09-30'],
			['10-01','12-31']]

	#amount for each installments is 25%
	amount = round(tax.amount / 100 * 25)
	staff = request.session.get('user')

	#update tax attribute to be the first installments tax item
	tax.period_from = timezone.make_aware(dateutil.parser.parse(current_year + '-' + periods[0][0] + ' 00:00:00'), timezone.get_default_timezone()) 
	tax.period_to = timezone.make_aware(dateutil.parser.parse(current_year + '-' + periods[0][1] + ' 23:59:59'), timezone.get_default_timezone()) 
	tax.due_date = current_year + '-' + periods[0][1]
	tax.amount = amount
	tax.remaining_amount = amount
	tax.submit_date = today
	tax.submit_details = json.dumps({'installment':1})
	tax.save()

	#add the remaining 3 installments tax item
	del periods[0]
	count = 2
	for i in periods:
		period_from = timezone.make_aware(dateutil.parser.parse(current_year + '-' + i[0] + ' 00:00:00'), timezone.get_default_timezone()) 
		period_to = timezone.make_aware(dateutil.parser.parse(current_year + '-' + i[1] + ' 23:59:59'), timezone.get_default_timezone()) 
		due_date = current_year + '-' + i[1]

		if type == 'fixed_asset':
			tax = PropertyTaxItem(submit_date=today,submit_details=json.dumps({'installment':count}),amount=amount,remaining_amount=amount,property=tax.property,currency=tax.currency,period_from=period_from,period_to=period_to,due_date=due_date,date_time=now,is_paid=False,staff_id=staff.id)
		if type == 'trading_license':
			tax = TradingLicenseTax(submit_date=today,submit_details=json.dumps({'installment':count}),amount=amount,remaining_amount=amount,business=tax.business,subbusiness=tax.subbusiness,currency=tax.currency,period_from=period_from,period_to=period_to,due_date=due_date,date_time=now,is_paid=False,staff_id=staff.id)
		if type == 'rental_income':
			tax = RentalIncomeTax(submit_date=today,submit_details=json.dumps({'installment':count}),amount=amount,remaining_amount=amount,property=tax.property,currency=tax.currency,period_from=period_from,period_to=period_to,due_date=due_date,date_time=now,is_paid=False,staff_id=staff.id)
		if type == 'fee':
			tax = Fee(submit_date=today,submit_details=json.dumps({'installment':count}),amount=amount,remaining_amount=amount,fee_type=fee_type,property=tax.property,currency=tax.currency,period_from=period_from,period_to=period_to,due_date=due_date,date_time=now,is_paid=False,staff_id=staff.id)
		tax.save()
		count = count + 1
	#"/admin/tax/tax/property/" + str(tax.property.id) + "/fees/"
	return redirect(request.META.get('HTTP_REFERER'))


@cache_control(no_cache=True, must_revalidate=True, no_store=True)
def tax_default(request, action, content_type_name1, obj_name, obj_id, part):
	"""
	"""
	
	if not action and not obj_name:
		user = request.session.get('user')
		module = ModuleMapper.getModuleByName("tax")
		content_type = ContentTypeMapper.getContentTypeByModuleAndName('tax', module)
		actions = user.getActionsByContentTypeWithLink(content_type)
		return render_to_response('tax/tax_tax_default.html', {\
							 'permissions':actions},
							  context_instance=RequestContext(request))
	elif action == 'search':
		return search(request)
	elif action == 'manage':
		return manage_tax(request)
	elif action == 'incomplete' and content_type_name1 == 'payment':
		return incomplete_payment_default(request)
	elif action == 'verify' and content_type_name1 == 'target':
		return verify_target(request, obj_name, obj_id, part)
	elif obj_name == "citizen" and obj_id:
		return tax_citizen(request,obj_id, part)
	elif obj_name == "business" and obj_id:
		return tax_business(request,obj_id, part)
	elif obj_name == "property" and obj_id:
		return tax_property(request,obj_id, part)

	elif (action == 'pay' and content_type_name1 == 'taxes') or (action == 'submit' and content_type_name1 == 'tax') :

		if request.GET.get('type',None) != None and request.GET.get('id',None) != None:
			tax_type = request.GET['type']
			if tax_type!='fee' and  not request.session['user'].has_tax_type_by_name(tax_type):
				return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
			elif tax_type == 'fee':
				tax = get_object_or_404(Fee,id=request.GET['id'])
				if not request.session['user'].has_tax_type_by_name(tax.fee_type):
					return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
			return displayPayTaxPage(request, action, content_type_name1, obj_name, obj_id, part)
		else:
			raise Http404

	elif (action == 'paymultiple' and content_type_name1 == 'taxes'):
		#Atm, only allow pay multiple for fees and full amount pay only for now
		if request.GET.get('type',None) != None and request.GET.get('id',None) != None and request.GET.get('type') == 'fee':
			tax_type = request.GET['type']
			if tax_type!='fee' and  not request.session['user'].has_tax_type_by_name(tax_type):
				return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
			elif tax_type == 'fee':
				taxes = Fee.objects.filter(id__in=request.GET['id'].split(','),i_status='active')
				if taxes:
					for i in taxes:
						if not request.session['user'].has_tax_type_by_name(i.fee_type):
							return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
				else:
					raise Http404
			return displayPayMultipleTaxesPage(request, action, content_type_name1, obj_name, obj_id, part)
		else:
			raise Http404

	elif action == 'generate' and content_type_name1 == 'invoice':
		if request.GET.get('type',None) != None and request.GET.get('id',None) != None:
			return displayGenerateInvoicePage(request)
		else:
			raise Http404

	elif action == 'generate' and content_type_name1 == 'multipayinvoice':
		if request.GET.get('type',None) != None and request.GET.get('id', None) != None:
			return displayGenerateMultipayInvoicePage(request)
		else:
			raise Http404

	elif action == 'generate' and content_type_name1 == 'epayinvoice':
		if request.GET.get('type',None) != None and request.GET.get('id',None) != None:
			return displayGenerateEpayInvoicePage(request)
		else:
			raise Http404

	elif action == 'generate' and content_type_name1 == 'multipayepayinvoice':
		if request.GET.get('type',None) != None and request.GET.get('id',None) != None:
			return displayGenerateMultipayEpayInvoicePage(request)
		else:
			raise Http404

	elif action == 'payment' and content_type_name1 == 'search':
		return displayPaymentSearchPage(request)

	elif action == 'payment' and content_type_name1 == 'reverse':
		if request.GET.get('type',None) != None and request.GET.get('id',None) != None:
			return displayPaymentReversePage(request)
		else:
			raise Http404

	elif action == 'setup' and content_type_name1 == 'installments':
		if request.GET.get('type',None) != None and request.GET.get('id',None) != None:
			return setupInstallments(request)
		else:
			raise Http404

	elif action == 'submit' and content_type_name1 == 'pending':
		if request.GET.get('type',None) != None and request.GET.get('id',None) != None:
			return displaySubmitPendingPage(request)
		else:
			raise Http404

	elif action == 'past' and content_type_name1 == 'payments':
		if request.GET.get('type',None) != None and request.GET.get('id',None) != None:
			GET = request.GET
			id = GET['id']
			tax_type = GET['type']

			if tax_type == 'fixed_asset':
				payments = PayFixedAssetTax.objects.filter(property_tax_item_id__exact=id,i_status='active')

			elif tax_type == 'rental_income':
				payments = PayRentalIncomeTax.objects.filter(rental_income_tax_id__exact=id,i_status='active')

			elif tax_type == 'trading_license':
				payments = PayTradingLicenseTax.objects.filter(trading_license_tax_id__exact=id,i_status='active')

			else:
				tax = get_object_or_404(Fee,pk=id)
				#show installment payments if this tax is generated from an failed overdue_installment
				if tax.fee_type == 'land_lease' and tax.submit_details and tax.submit_details.find("overdue_installment") >= 0:
					details = json.loads(tax.submit_details)
					payments = PayFee.objects.filter(fee_id__in=details['paid_installments'],i_status='active')
				else:
					payments = PayFee.objects.filter(fee_id__exact=id,i_status='active')

			payments_found = []
			if payments and len(payments) > 0:
				for payment in payments:
					payment_obj = {}
					payment_obj['invoice_id'] = PaymentMapper.generateInvoiceId(tax_type,payment)
					payment_obj['bank'] = variables.getFullBankName(payment.bank)
					payment_obj['receipt_no'] = payment.receipt_no
					payment_obj['paid_date'] = payment.paid_date
					payment_obj['date_time'] = payment.date_time
					payment_obj['capital_amount'] = payment.amount - ( payment.fine_amount or 0 )
					payment_obj['fine_amount'] = payment.fine_amount
					payment_obj['fine_description'] = payment.fine_description
					payment_obj['amount'] = payment.amount
					payment_obj['currency'] = 'RWF'
					payment_obj['note'] = payment.note
					payment_obj['status'] = payment.i_status
					payment_obj['staff'] = payment.staff

					payments_found.append(payment_obj)

			return render_to_response('tax/tax_tax_pastpayments.html',{'payments':payments_found},
										context_instance=RequestContext(request))

		else:
			raise Http404

	elif action == 'change' and content_type_name1 == 'settings':
		return displayTaxSettingPage(request)
	elif action =='viewfee' and content_type_name1 =='settings':
		return viewFeeSettingPage(request)
	elif action =='viewtax' and content_type_name1 =='settings':
		return viewTaxSettingPage(request)

	elif action == 'update' and content_type_name1 == 'taxes':
		if request.GET.get('type',None) != None and request.GET.get('type') in ['business','property'] and request.GET.get('id',None) != None:
			GET = request.GET
			type = request.GET.get('type')
			id = request.GET.get('id')
			update_all = False
			if GET.get('all',None) != None:
				update_all = True
			TaxMapper.updateTaxesOnDetailsChanged(type,id,update_all)
			return redirect("/admin/tax/tax/" + type + "/" + id + "/fees/")
		else:
			raise Http404
	else:
		raise Http404

		
"""
get formula data to display the tax amount calculation process to user
"""
def getFormulaData(type, tax, model):
	data = {}
	paymentDetails = calculatePaymentDetails(type, tax)
	settingFilters = {}
	fixedAssetSettings = None
	if type == 'fixed_asset':
		if tax.property and tax.property.sector and tax.property.sector != None:
			settingFilters['sector'] = tax.property.sector
			if tax.property.sector.district:
				settingFilters['district'] = tax.property.sector.district

		fixedAssetSettings = TaxMapper.getTaxSetting('fixed_asset_tax', settingFilters)

		#only start setting up formula data for taxes that havent been paid partially yet
		if paymentDetails['past_payment_amount'] == 0:
			data['purpose'] = model.land_use_type

			if data['purpose'] == 'Residential':
				data['taxable_amount_formula'] = 'Latest Declared Value - ' + fixedAssetSettings['residential_deduction']
			else:
				data['taxable_amount_formula'] = 'Latest Declared Value'

			declared_value = DeclaredValueMapper.getDeclaredValueByProperty(model)
			if declared_value:
				data['declared_value'] = declared_value.amount

				if data['purpose'] == 'Residential':
					if data['declared_value']:
						data['taxable_amount'] =  float(data['declared_value']) - float(fixedAssetSettings['residential_deduction'])
						
				else:
					data['taxable_amount'] = data['declared_value']
			else:
				data['taxable_amount'] = None

			if data['taxable_amount']:
				data['tax_due'] = int(round(float(data['taxable_amount'])) * float(fixedAssetSettings['tax_rate']))
				data['remaining_amount'] = int(round(float(data['tax_due']) - float(paymentDetails['past_payment_amount'])))

				#get partial tax amount if tax doesnt' cover full year
				if paymentDetails.has_key('partial_percent'):
					data['remaining_amount'] = data['remaining_amount'] * paymentDetails['partial_percent'] / 100

				data['partial_tax'] = round(data['remaining_amount'] )

				if paymentDetails['late_fee_surcharge']:
					data['final_amount'] = round(float(data['remaining_amount']) +  float(paymentDetails['late_fee_interest']) + float(paymentDetails['late_fee_surcharge']))
				else:
					data['final_amount'] = round(data['remaining_amount'])
			else:
				data['tax_due'] = 0
				data['taxable_amount'] = 0
				data['remaining_amount'] = 0
				data['final_amount'] = 0

		else:
			data['final_amount'] = paymentDetails['amount']

		data.update(paymentDetails)

	elif type == 'rental_income':
		settingFilters = {}
		if tax.property and tax.property.sector and tax.property.sector != None:
			settingFilters['sector'] = tax.property.sector
			if tax.property.sector.district:
				settingFilters['district'] = tax.property.sector.district
		#data['final_amount'] = payment
		if tax.amount:
			data['past_payment_amount'] = tax.amount - tax.remaining_amount
			data['final_amount'] = tax.remaining_amount
		else:
			data['past_payment_amount'] = 0
			data['final_amount'] = 0

		'''
		#check if there is tax settings has been changed within this tax period
		changed_dates = TaxMapper.getTaxChangeList('rental_income_tax',tax.period_from,tax.period_to,settingFilters)
		tax_settings = []
		print changed_dates
		print '========'
		if changed_dates:
			for i in changed_dates:
				settings = TaxMapper.getTaxSetting('rental_income_tax',settingFilters,None,i['valid_from'],i['valid_to'])
				if i['valid_from'] < tax.period_from:
					settings['from'] = tax.period_from
				else:
					settings['from'] = i['valid_from']
				if i['valid_to'] == None or i['valid_to'] > tax.period_to:
					settings['to'] = tax.period_to
				else:
					settings['to'] = i['valid_to']
	
				settings['rate_with_bank_interest_percentage'] = float(settings['rate_with_bank_interest'])*100
				settings['rate_percentage'] = float(settings['rate'])*100
				#reformat tax ranges
				if settings['tax_ranges']:
					for k,v in settings['tax_ranges'].items():
						if k.startswith('0-'):
							settings['range_limit_1'] = k.replace('0-','')
							settings['range_percentage_1'] = float(v)*100
						elif k.startswith('>'):
							settings['range_limit_2'] = k.replace('>','')
							settings['range_percentage_3'] = float(v)*100
						elif '-' in k:
							settings['range_percentage_2'] = float(v)*100
				tax_settings.append(settings)
		data['tax_settings'] = tax_settings
		print tax_settings
		print data
		print '======='
		'''

		settings = TaxMapper.getTaxSetting('rental_income_tax',settingFilters)
		settings['rate_with_bank_interest_percentage'] = float(settings['rate_with_bank_interest'])*100
		settings['rate_percentage'] = float(settings['rate'])*100
		#reformat tax ranges
		if settings['tax_ranges']:
			for k,v in settings['tax_ranges'].items():
				if k.startswith('0-'):
					settings['range_limit_1'] = k.replace('0-','')
					settings['range_percentage_1'] = float(v)*100
				elif k.startswith('>'):
					settings['range_limit_2'] = k.replace('>','')
					settings['range_percentage_3'] = float(v)*100
				elif '-' in k:
					settings['range_percentage_2'] = float(v)*100
		data.update(settings)

	elif type == 'trading_license':
		#load submission info from previous tax submit
		data['sum_activity_tax'] = 0
		if tax.amount:
			data['past_payment_amount'] = tax.amount - tax.remaining_amount
			data['final_amount'] = tax.remaining_amount
			data['sum_activity_tax'] = tax.amount
		else:
			data['past_payment_amount'] = 0
			data['final_amount'] = 0

		
		data.update(paymentDetails)
		#fetch list of yearly turnover from tax settings if is VAT registered business
		if model.vat_register:
			settingFilters = {}
			if model.sector and model.sector != None:
				settingFilters['sector'] = model.sector
				if model.sector.district:
					settingFilters['district'] = model.sector.district
			settings = TaxMapper.getTaxSetting('trading_license_tax',settingFilters)
			data['yearly_turnover_tax'] = settings['business_yearly_turnover_and_tax_matches']

	elif type == 'fee':
		fee = 0

		if tax.fee_type == 'land_lease':
			settingFilters = {}
			if tax.property and tax.property.sector and tax.property.sector != None:
				settingFilters['sector'] = tax.property.sector
				if tax.property.sector.district:
					settingFilters['district'] = tax.property.sector.district
			sub_type_select = None
			size_type = None
			if model.land_lease_type:
				sub_type_select = model.land_lease_type
			if model.land_lease_type != 'Agriculture':
				size = model.size_sqm			
				size_type = 'sqm'
			elif model.size_hectare:
				size = model.size_hectare		
				size_type = 'hectare'	

			if not size:
				size = 0

			rates = TaxMapper.getTaxSetting('land_lease_fee',settingFilters,'area_and_fee_matches')
			label = variables.getValueByKey(variables.land_lease_types,sub_type_select)
			rate = 0

			if rates.has_key(label):
				rate = rates[label]
				fee = round(float(rate) * float(size),-3)

			data['sub_types'] = variables.land_lease_types
			data['sub_type_select'] = sub_type_select
			data['rates'] = rates
			data['rate'] = rate
			data['size'] = int(size)
			data['size_type'] = size_type
			data['fee'] = int(fee)
		elif tax.fee_type == 'cleaning':
			area_type = None
			fee = 0
			sub_type_select = None
			if tax.subbusiness:
				business = tax.subbusiness.business
			else:
				business = tax.business

			if business and business.sector and business.sector != None:
				settingFilters['sector'] = business.sector
				if business.sector.district:
					settingFilters['district'] = business.sector.district
			if business.area_type:
				data['area_type'] = business.area_type
			else:
				data['area_type_list'] = variables.area_types
			if business.business_type:
				data['business_type'] = business.business_type
			else:
				data['business_type_list'] = variables.business_types

			data['fee_matches'] = TaxMapper.getTaxSetting('cleaning_fee',settingFilters,'fee_matches')
			if business.area_type and business.area_type != '' and business.business_type and business.business_type != '':
				match = business.area_type + '-' + business.business_type
				for match_type,rate in data['fee_matches'].iteritems():
					if match_type == match:
						fee = rate
						#recalculate payment details with this fee
						paymentDetails = calculatePaymentDetails(type, tax, fee)
			else:
				fee = 0

		data.update(paymentDetails)

		data['past_payment_amount'] = 0
		data['final_amount'] = 0
		if fee != 0:
			data['final_amount'] = fee
			data['amount'] = fee
		elif data['amount']:
			data['final_amount'] = data['amount']

	#load submit details data into Formula list
	if tax.submit_details and tax.submit_details != '':
		data.update(json.loads(tax.submit_details))

	if  data.has_key('late_fee_month') and data['late_fee_month']:
		if type == 'fixed_asset':
			data['late_fee_interest_formula'] = str(float(fixedAssetSettings["late_fee_interest_rate"])*100) + '% * Late Month Count * Tax Due'
			data['late_fee_surcharge_formula'] = str(float(fixedAssetSettings["late_fee_surcharge_rate"])*100) + '% * Tax Due (not exceeding ' + str(fixedAssetSettings["late_fee_surcharge_max"]) + 'Rwf)'
			data['tax_rate_label'] = str(float(fixedAssetSettings['tax_rate']) * 100) + '%'
			data['tax_rate'] = float(fixedAssetSettings['tax_rate'])
			data['late_fee_interest_rate'] = fixedAssetSettings["late_fee_interest_rate"]
			data['late_fee_surcharge_rate'] = fixedAssetSettings["late_fee_surcharge_rate"]
			data['late_fee_surcharge_max'] = fixedAssetSettings["late_fee_surcharge_max"]

		else:
			feeSettings = TaxMapper.getTaxSetting('general_fee',settingFilters)
			data['final_amount'] = int(round(float(data['final_amount']) + float(data['late_fee_interest']) + float(data['late_fee_surcharge'])))
			data['late_fee_interest_formula'] = str(float(feeSettings["late_fee_interest_rate"])*100) + '% * Late Month Count * Fee Due'
			data['late_fee_surcharge_formula'] = str(float(feeSettings["late_fee_surcharge_rate"])*100) + '% * Fee Due (not exceeding ' + str(feeSettings["late_fee_surcharge_max"]) + 'Rwf)'
			data['late_fee_interest_rate'] = feeSettings["late_fee_interest_rate"]
			data['late_fee_surcharge_rate'] = feeSettings["late_fee_surcharge_rate"]
			data['late_fee_surcharge_max'] = feeSettings["late_fee_surcharge_max"]

	if  data.has_key('fine_amount') and data['fine_amount']:
		data['final_amount'] = int(round(float(data['final_amount']) + float(data['fine_amount'])))

	for k,v in data.iteritems():
		if v == None or v == '':
			data[k] = 0

	return data


def saveTaxDetails(tax_type, tax, request):
	details = {}
	if tax.submit_details and tax.submit_details != '':
		details = json.loads(tax.submit_details)

	if tax_type == 'fixed_asset':
		pass	
	elif tax_type == 'rental_income':
		if request.POST.get('last_year_income',None) != None:
			details['last_year_income'] = request.POST.get('last_year_income')
		if request.POST.get('bank_interest_paid',None) != None:
			details['bank_interest_paid'] = request.POST.get('bank_interest_paid')		

	elif tax_type == 'trading_license':
		if request.POST.get('yearly_turnover',None) != None:
			details['yearly_turnover'] = request.POST.get('yearly_turnover')
		elif request.POST.get('sum_activity_tax',None) != None:
			details['sum_activity_tax'] = request.POST.get('sum_activity_tax')

	if tax_type == 'fee':
		if tax.fee_type == 'land_lease' and request.POST.get('land_lease_size',None) != None and request.POST.get('land_lease_size') != '' :
			property = tax.property
			property.land_lease_type = request.POST.get('land_lease_type')
			if property.land_lease_type  == 'Agriculture':
				property.size_hectare = request.POST.get('land_lease_size')	
			else:
				property.size_sqm = request.POST.get('land_lease_size')
			property.save()

		elif tax.fee_type == 'cleaning':
			if tax.business:
				business = tax.business
			elif tax.subbusiness:
				business = tax.subbusiness.business

			if request.POST.get('area_type',None) != None and request.POST.get('area_type') != '':
				business.area_type = request.POST.get('area_type')
			if request.POST.get('business_type',None) != None and request.POST.get('business_type') != '':
				business.business_type = request.POST.get('business_type')
			business.save()

	if request.POST.get('fine_amount',None) != None and int(request.POST.get('fine_amount')) != 0:
		details['fine_amount'] = request.POST.get('fine_amount')
	if request.POST.get('fine_description',None) != None and request.POST.get('fine_description') != '':
		details['fine_description'] = request.POST.get('fine_description')

	if details:
		tax.submit_details = json.dumps(details)
		tax.save()					


def getTaxReference(tax_type,tax):
	reference = ''
	if tax_type == 'fixed_asset' or tax_type == 'rental_income':
		property = tax.property
		if property:
			if PropertyMapper.getUPIByPropertyId(property.id):
				reference = '[UPI:' + PropertyMapper.getUPIByPropertyId(property.id) + '] ' + property.getDisplayName()
			else:
				reference = property.getDisplayName()

		reference = reference + ' From ' + '  ' + Common.localizeDate(tax.period_from).strftime('%d/%m/%Y') + ' - ' + Common.localizeDate(tax.period_to).strftime('%d/%m/%Y')

	elif tax_type == 'trading_license':
		if tax.business:
			reference = '[TIN:' + tax.business.tin + '] ' + tax.business.name + ' From ' + "  " + Common.localizeDate(tax.period_from).strftime('%d/%m/%Y') + ' - ' + Common.localizeDate(tax.period_to).strftime('%d/%m/%Y')
		elif tax.subbusiness:
			business = tax.subbusiness.business
			reference = '[TIN:' + business.tin + '] ' + business.name + '(Branch:' + tax.subbusiness.branch+')' + ' From ' + "  " + Common.localizeDate(tax.period_from).strftime('%d/%m/%Y') + ' - ' + Common.localizeDate(tax.period_to).strftime('%d/%m/%Y')

	elif tax_type == 'misc_fee':
		reference = tax.fee_type.replace("_"," ").title() + ' - ' + tax.fee_sub_type
	elif tax_type == 'fee' or tax_type.endswith("_fee"):
		if tax.fee_type == 'land_lease':
			property = tax.property
			if property:
				if property.getUPI():
					reference = "[UPI: " + property.getUPI() + "] " + property.getDisplayName()
				else:
					reference = property.getDisplayName()

			if tax.submit_details and tax.submit_details.find('"installment"') >= 0:
				details = json.loads(tax.submit_details)
				reference = ' ' + Common.localizeDate(tax.period_from).strftime('%Y') + ' - Installment No.' + str(details['installment']) + ' for ' + reference 
			elif tax.submit_details and tax.submit_details.find('"overdue_installment"') >= 0:
				details = json.loads(tax.submit_details)
				reference = ' ' + Common.localizeDate(tax.period_from).strftime('%Y') + ' - Cover the remaining Tax Amount of Cancelled Payment Installments Plan due to overdue for ' + reference 
			else:
				reference = 'From ' + Common.localizeDate(tax.period_from).strftime('%d/%m/%Y') + ' - ' + Common.localizeDate(tax.period_to).strftime('%d/%m/%Y') + ' for ' + reference 

		elif tax.fee_type == 'cleaning' or tax.fee_type == 'market':
			if tax.business:
				reference = '[TIN: ' + tax.business.tin + '] ' + tax.business.name + ' for ' + Common.localizeDate(tax.period_from).strftime('%b %Y')
			elif tax.subbusiness:
				business = tax.subbusiness.business
				reference = '[TIN: ' + business.tin + '] ' + business.name + ' (Branch: ' + tax.subbusiness.branch + ') for ' + Common.localizeDate(tax.period_from).strftime('%b %Y')
	return reference


def calculateLateFee(type,tax, manual_tax_amount = None):
	today = timezone.make_aware(datetime.combine(datetime.today(), time(0,0)), timezone.get_default_timezone())
	late_fee = 0

	installment = TaxMapper.next_outstanding_installment(tax)
	if installment: 
		if installment.due >= date.today(): # installment is not late
			return 0
		else:
			tax.due_date = installment.due


	#check if this is overdue, to apply a late fee for Taxes / fee that have a due date
	if type != 'misc_fee' and tax.due_date != None and datetime.date(today) > tax.due_date:
		late_fee = {}
		late_fee_interest = 0
		late_fee_surcharge = 0
		month_late = 0
		amount = None

		if tax.remaining_amount:
			amount = tax.remaining_amount
		elif manual_tax_amount:
			amount = manual_tax_amount

		if type == 'fixed_asset':
			settingFilters = {}
			if tax.property and tax.property.sector and tax.property.sector != None:
				settingFilters['sector'] = tax.property.sector
				if tax.property.sector.district:
					settingFilters['district'] = tax.property.sector.district
			fixedAssetSettings = TaxMapper.getTaxSetting('fixed_asset_tax', settingFilters)

			#get the late time in months
			month1 = today.month
			month2 = tax.due_date.month
			if( month2 > month1):
				month_late = (month1 - month2) + 12
			else:
				month_late = month1 - month2

			if amount:
				late_fee_interest = (float(fixedAssetSettings['late_fee_interest_rate']) * month_late) * float(amount)
				late_fee_surcharge = float(fixedAssetSettings['late_fee_surcharge_rate']) * float(amount)
				if late_fee_surcharge > float(fixedAssetSettings["late_fee_surcharge_max"]):
					late_fee_surcharge = float(fixedAssetSettings["late_fee_surcharge_max"])

		elif type == 'fee':
			if tax.fee_type == 'land_lease':
				settingFilters = {}
				if tax.property and tax.property.sector and tax.property.sector != None:
					settingFilters['sector'] = tax.property.sector
					if tax.property.sector.district:
						settingFilters['district'] = tax.property.sector.district
			elif tax.fee_type == 'cleaning':
				settingFilters = {}
				if tax.business and tax.business.sector and tax.business.sector != None:
					settingFilters['sector'] = tax.business.sector
					if tax.business.sector.district:
						settingFilters['district'] = tax.business.sector.district
			else:
				settingFilters = None
			feeSettings = TaxMapper.getTaxSetting('general_fee', settingFilters)

			#get the late time in months
			month1 = today.month
			month2 = tax.due_date.month
			if( month2 > month1):
				month_late = (month1 - month2) + 12
			else:
				month_late = month1 - month2

			#even if 1 date late, round it to full month late
			if tax.due_date.day < today.day:
				month_late = month_late + 1

			if amount:
				late_fee_interest = (float(feeSettings['late_fee_interest_rate']) * month_late) * float(amount)
				late_fee_surcharge = float(feeSettings['late_fee_surcharge_rate']) * float(amount)
				if late_fee_surcharge > float(feeSettings["late_fee_surcharge_max"]):
					late_fee_surcharge = float(feeSettings["late_fee_surcharge_max"])

		late_fee['interest'] = int(round(late_fee_interest,0))
		late_fee['surcharge'] = int(round(late_fee_surcharge,0))
		late_fee['month_late'] = month_late

	return late_fee


def calculatePaymentDetails(type, tax, manual_tax_amount = None):
	amount = 0
	details = {}
	late_fee = None

	if tax.amount:
		remaining_amount = 0
		if tax.remaining_amount and tax.remaining_amount != None:
			remaining_amount = tax.remaining_amount
			past_payment_amount = tax.amount - remaining_amount
		else:
			past_payment_amount = 0
		amount = float(remaining_amount)
		late_fee = calculateLateFee(type, tax)
	elif manual_tax_amount:
		past_payment_amount = 0
		amount = manual_tax_amount
		late_fee = calculateLateFee(type, tax, manual_tax_amount)
	else:
		amount = TaxMapper.calculateTax(tax)
		late_fee = calculateLateFee(type, tax)
		past_payment_amount = 0

	if late_fee:
		details['late_fee_interest'] = late_fee['interest']
		details['late_fee_surcharge'] = late_fee['surcharge']
		details['late_fee_month'] = late_fee['month_late']
	else:
		details['late_fee_interest'] = 0
		details['late_fee_surcharge'] = 0
		details['late_fee_month'] = 0

	#check if this is a full tax or partial tax (only include portion of the annual tax/fee)
	#exclude cleaning-fee which is monthly paid
	if type != 'fee' or tax.fee_type != 'cleaning':
		current_year = str(datetime.today().year)
		#localize period_from & to before checking
		period_from = Common.localize(tax.period_from)
		period_to = Common.localize(tax.period_to)
		year_start = timezone.make_aware(dateutil.parser.parse(str(period_from.year) + '-01-01 00:00:00'), timezone.get_default_timezone())
		year_end = timezone.make_aware(dateutil.parser.parse(str(period_to.year) + '-12-31 23:59:59'), timezone.get_default_timezone())

		if (not tax.submit_details or not tax.submit_details.find('installment') >= 0 ) and (amount == tax.remaining_amount or amount == 0 )and (period_from > year_start or period_to < year_end):
			#get total days in this year
			dayCountInYear =Common.getDaysInYear(period_from.year)
			#get total days this tax cover
			timeDiff = period_to - period_from

			taxDays = timeDiff.days
			details['year_days'] = dayCountInYear
			details['tax_days'] = taxDays
			details['partial_percent'] = round(1.0 * taxDays/dayCountInYear,2) * 100

	details['amount'] = amount
	details['past_payment_amount'] = round(past_payment_amount)
	details['due_date'] = tax.due_date
	return details


def generateMultipayReceipt(payments, multipay_receipt, type, model):
	tax_type = 'fee'
	receipt = {}
	receipt['paid_at'] = str(payments[0].bank)
	receipt['paid_date'] = payments[0].paid_date

	#get payer info
	if type == 'citizen':
		payer = { 'name': model.getDisplayName(), 'address': model.address, 'idString':'Citizen ID: ' + model.citizen_id }
	elif type == 'business':
		payer = { 'name': model.name, 'address': model.address, 'idString':'TIN/RRA: ' + model.tin }
	elif type == 'property':
		payer = { 'name': model.getUPI(), 'address': model.getDisplayName, 'idString':''}

	receipt['payer'] = payer

	taxes = []
	for payment in payments:
		tax = payment.fee
		#get remaining tax amount
		remaining_amount = int(tax.remaining_amount)

		if payment.fine_amount:
			payment_without_fines = payment.amount - payment.fine_amount
		else:
			payment_without_fines = payment.amount
		payment_capital_part = int(payment_without_fines)
		#get all late fees incurred
		#late_fee = calculateLateFee(tax_type, tax)
		#print late_fee
		#print '======='
		#if late_fee:
		#	late_fees = []
		#	if late_fee['interest'] > 0:
		#		late_fee_record = { 'name': 'Late Fee Interest', 'reference': '', 'invoice_no': '', 'bank_receipt': '', 'amount': late_fee['interest'], 'currency': tax.currency}
		#		late_fees.append(late_fee_record)
		#	if late_fee['surcharge'] > 0:
		#		late_fee_record = { 'name': 'Late Fee Surcharge', 'reference': '', 'invoice_no': '', 'bank_receipt': '', 'amount': late_fee['surcharge'], 'currency': tax.currency}
		#		late_fees.append(late_fee_record)

		#	receipt['late_fees'] = late_fees
		#	payment_capital_part = round(Decimal(payment_without_fines) - Decimal(late_fee['interest']) - Decimal(late_fee['surcharge']),2)


		#append actual tax amount
		#get id for this invoice
		invoice_id = PaymentMapper.generateInvoiceId(tax_type, payment)

		if tax_type == 'fee':
			tax_record = { 'name': tax.fee_type.replace("_"," ").title() + ' Fee', 'period': Common.localizeDate(tax.period_from).strftime('%b %Y'), 'reference': getTaxReference(tax_type, tax), 'manual_receipt':payment.manual_receipt, 'invoice_no': invoice_id, 'bank_receipt': payment.receipt_no, 'amount': payment_capital_part, 'currency': tax.currency}
		else:
			tax_record = { 'name': tax_type.replace("_"," ").title(),'period': Common.localizeDate(tax.period_from).strftime('%b %Y'), 'reference': getTaxReference(tax_type, tax), 'manual_receipt':payment.manual_receipt, 'invoice_no': invoice_id, 'bank_receipt': payment.receipt_no, 'amount': payment_capital_part, 'currency': tax.currency}
		taxes.append(tax_record)

		#append fines - if exists
		if payment.fine_amount > 0:
			tax_record = { 'name': 'Fines', 'reference': payment.fine_description,'period': Common.localizeDate(tax.period_from).strftime('%b %Y'), 'manual_receipt':payment.manual_receipt, 'invoice_no': invoice_id, 'bank_receipt': payment.receipt_no, 'amount': int(payment.fine_amount), 'currency': tax.currency }
			taxes.append(tax_record)

	receipt['taxes'] = taxes
	#set multipay invoice id to use multipay receipt object id with 'MP' marking
	receipt['invoice_no'] = 'MP' + str(multipay_receipt.id)
	receipt['bank_receipt'] = payments[0].receipt_no
	receipt['manual_receipt'] = payments[0].manual_receipt
	receipt['total'] = int(multipay_receipt.amount)

	#check for any pending future payments for this payer, limit to 2 months only
	receipt['future_payments'] = getUpcomingTaxes(type,model)

	return receipt


def generateMultipayEPayInvoice(tax_type, tax_list, type, model):
	#testing testing testing
	receipt = {}

	#get payer info
	if type == 'citizen':
		payer = { 'name': model.getDisplayName(), 'address': model.address, 'idString':'Citizen ID: ' + model.citizen_id }
	elif type == 'business':
		payer = { 'name': model.name, 'address': model.address, 'idString':'TIN/RRA: ' + model.tin }
	elif type == 'property':
		payer = { 'name': model.getUPI(), 'address': model.getDisplayName, 'idString':''}

	receipt['payer'] = payer

	total = 0
	taxes = []

	if tax_list:
		for tax in tax_list:
			#get remaining tax amount
			if tax.remaining_amount:
				remaining_amount = int(tax.remaining_amount)
			else:
				#update to dynamically generate tax amount on the spot to always implement latest taxes/fees rates
				remaining_amount = TaxMapper.calculateTax(tax)

			#if there is no remaining amount - raise 404
			if remaining_amount == None:
				raise Http404 

			record_name = tax.fee_type.replace("_"," ").title()
			amount = remaining_amount
			#get all late fees incurred
			late_fee = calculateLateFee(tax_type, tax)
			#print late_fee
			#print '======='
			if late_fee:
				record_name = record_name + ' (with Late Fee)'
				amount = int(round(amount + Decimal(late_fee['interest']) + Decimal(late_fee['surcharge']),2))

			total = total + amount

			#append actual tax amount
			tax_record = { 'name': record_name, 'reference': getTaxReference(tax_type, tax),'amount': amount, 'currency': tax.currency}
			taxes.append(tax_record)
	
	receipt['total'] = int(total)


	#append fines - if exists
	tax = tax_list[0]
	if tax.submit_details and tax.submit_details.find('fine_description') >= 0:
		details = json.loads(tax.submit_details)
		if int(details['fine_amount']) >0:
			tax_record = { 'name': 'Fines', 'reference': details['fine_description'], 'amount': details['fine_amount'], 'currency': tax.currency }
			taxes.append(tax_record)
			receipt['total'] = int(round(receipt['total'] + Decimal(details['fine_amount']),2))

	receipt['taxes'] = taxes

	#get ePay Number for this invoice
	epay_no = PaymentMapper.generateEpayNo(tax_type, tax)
	receipt['epay_no'] = epay_no

	#check for any pending future payments for this payer, limit to 2 months only
	receipt['future_payments'] = getUpcomingTaxes(type,model)

	return receipt


def generateEPayInvoiceOld(tax_type, tax, type, model):
	#testing testing testing
	receipt = {}
	receipt['submit_date'] = tax.submit_date
	if tax_type != 'misc_fee':
		receipt['due_date'] = tax.due_date
	
	#get ePay Number for this invoice
	epay_no = PaymentMapper.generateEpayNo(tax_type, tax)
	receipt['epay_no'] = epay_no

	#get payer info
	if type == 'citizen':
		payer = { 'name': model.getDisplayName(), 'address': model.address, 'idString':'Citizen ID: ' + model.citizen_id }
	elif type == 'business':
		payer = { 'name': model.name, 'address': model.address, 'idString':'TIN/RRA: ' + model.tin }
	elif type == 'property':
		payer = { 'name': model.getUPI(), 'address': model.getDisplayName, 'idString':''}

	receipt['payer'] = payer

	#get remaining tax amount
	if tax.remaining_amount:
		remaining_amount = int(tax.remaining_amount)
	else:
		#update to dynamically generate tax amount on the spot to always implement latest taxes/fees rates
		remaining_amount = TaxMapper.calculateTax(tax)

	#if there is no remaining amount - raise 404
	if remaining_amount == None:
		raise Http404 

	receipt['total'] = int(remaining_amount)
	taxes = []

	#get all late fees incurred
	late_fee = calculateLateFee(tax_type, tax)
	#print late_fee
	#print '======='
	if late_fee:
		late_fees = []
		if late_fee['interest'] > 0:
			late_fee_record = { 'name': 'Late Fee Interest', 'reference': '', 'invoice_no': '', 'bank_receipt': '', 'amount': late_fee['interest'], 'currency': tax.currency}
			late_fees.append(late_fee_record)
		if late_fee['surcharge'] > 0:
			late_fee_record = { 'name': 'Late Fee Surcharge', 'reference': '', 'invoice_no': '', 'bank_receipt': '', 'amount': late_fee['surcharge'], 'currency': tax.currency}
			late_fees.append(late_fee_record)

		receipt['late_fees'] = late_fees
		receipt['total'] = receipt['total'] + Decimal(late_fee['interest']) + Decimal(late_fee['surcharge'])

	#append actual tax amount
	if tax_type == 'fee':
		tax_record = { 'name': tax.fee_type.replace("_"," ").title(), 'reference': getTaxReference(tax_type, tax),'amount': remaining_amount, 'currency': tax.currency}
	elif tax_type == 'misc_fee':
		tax_record = { 'name': tax.fee_type.replace("_"," ").title(), 'reference': tax.fee_sub_type.title(),'amount': remaining_amount, 'currency': tax.currency}
	else:
		tax_record = { 'name': tax_type.replace("_"," ").title(), 'reference': getTaxReference(tax_type, tax),'amount': remaining_amount, 'currency': tax.currency}
	taxes.append(tax_record)

	#append fines - if exists
	if tax.submit_details and tax.submit_details.find('fine_description') >= 0:
		details = json.loads(tax.submit_details)
		if int(details['fine_amount']) >0:
			tax_record = { 'name': 'Fines', 'reference': details['fine_description'], 'amount': details['fine_amount'], 'currency': tax.currency }
			taxes.append(tax_record)
			receipt['total'] = int(round(receipt['total'] + Decimal(details['fine_amount']),2))

	receipt['taxes'] = taxes

	#check for any pending future payments for this payer, limit to 2 months only
	receipt['future_payments'] = getUpcomingTaxes(type,model)

	return receipt


def generateReceipt(tax_type, payment, tax, type, model):
	
	receipt = {}
	receipt['paid_at'] = str(payment.bank)
	if receipt['paid_at']:
		for bank in variables.banks:
			if bank[0] == receipt['paid_at']:
				receipt['paid_at'] = bank[1]
				break
	receipt['paid_date'] = payment.paid_date

	#get payer info
	if type == 'citizen':
		payer = { 'name': model.getDisplayName(), 'address': model.address, 'idString':'Citizen ID: ' + model.citizen_id }
	elif type == 'business':
		payer = { 'name': model.name, 'address': model.address, 'idString':'TIN/RRA: ' + model.tin }
	elif type == 'property':
		payer = { 'name': model.getUPI(), 'address': model.getDisplayName, 'idString':''}

	receipt['payer'] = payer

	taxes = []
	if payment.fine_amount:
		payment_without_fines = payment.amount - payment.fine_amount
	else:
		payment_without_fines = payment.amount
	payment_capital_part = int(payment_without_fines)
	#get all late fees incurred
	#late_fee = calculateLateFee(tax_type, tax)
	#print late_fee
	#print '======='
	#if late_fee:
	#	late_fees = []
	#	if late_fee['interest'] > 0:
	#		late_fee_record = { 'name': 'Late Fee Interest', 'reference': '', 'invoice_no': '', 'bank_receipt': '', 'amount': late_fee['interest'], 'currency': tax.currency}
	#		late_fees.append(late_fee_record)
	#	if late_fee['surcharge'] > 0:
	#		late_fee_record = { 'name': 'Late Fee Surcharge', 'reference': '', 'invoice_no': '', 'bank_receipt': '', 'amount': late_fee['surcharge'], 'currency': tax.currency}
	#		late_fees.append(late_fee_record)

	#	receipt['late_fees'] = late_fees
	#	payment_capital_part = round(Decimal(payment_without_fines) - Decimal(late_fee['interest']) - Decimal(late_fee['surcharge']),2)

	receipt['total'] = int(payment.amount)

	if receipt['total'] == 0 and tax_type == 'fixed_asset':
		latestDeclaredValue = DeclaredValueMapper.getDeclaredValueByProperty(tax.property)
		receipt['note'] = 'Property declared value ( '+ str(latestDeclaredValue.amount) + ' ' + tax.currency.title()  + ' ) is within the tax-free threshold, so no tax amount due.'  

	#append actual tax amount
	#get id for this invoice
	invoice_id = PaymentMapper.generateInvoiceId(tax_type, payment)

	if tax_type == 'fee':
		tax_record = { 'name': tax.name or tax.fee_type.replace("_"," ").title(), 'reference': getTaxReference(tax_type, tax), 'manual_receipt':payment.manual_receipt or '', 'invoice_no': invoice_id, 'bank_receipt': payment.receipt_no, 'amount': payment_capital_part, 'currency': tax.currency}
	elif tax_type == 'misc_fee':
		tax_record = { 'name': tax.fee_type.replace("_"," ").title(), 'reference': tax.fee_sub_type.title(),'manual_receipt':payment.manual_receipt or '', 'invoice_no': invoice_id, 'bank_receipt': payment.receipt_no, 'amount': payment_capital_part, 'currency': tax.currency}
	else:
		tax_record = { 'name': tax_type.replace("_"," ").title(), 'reference': getTaxReference(tax_type, tax), 'manual_receipt':payment.manual_receipt or '', 'invoice_no': invoice_id, 'bank_receipt': payment.receipt_no, 'amount': payment_capital_part, 'currency': tax.currency}
	taxes.append(tax_record)

	#append fines - if exists
	if payment.fine_amount > 0:
		tax_record = { 'name': 'Fines', 'reference': payment.fine_description, 'manual_receipt':payment.manual_receipt, 'invoice_no': invoice_id, 'bank_receipt': payment.receipt_no, 'amount': int(payment.fine_amount), 'currency': tax.currency }
		taxes.append(tax_record)

	receipt['taxes'] = taxes

	payment = tax.calculatePayment()
	receipt['installments'] = tax.get_installments()

	remaining_amount = tax.amount - payment['amount_paid']
	receipt['total_outstanding'] = remaining_amount + payment['late_fees']
	#check for any pending future payments for this payer, limit to 2 months only
	receipt['future_payments'] = getUpcomingTaxes(type,model)
	return receipt


def generateEPayInvoice(tax_type, tax, type, model):
	#testing testing testing
	receipt = {}
	receipt['submit_date'] = tax.submit_date
	if tax_type != 'misc_fee':
		receipt['due_date'] = tax.due_date
	
	#get ePay Number for this invoice
	epay_no = PaymentMapper.generateEpayNo(tax_type, tax)
	receipt['epay_no'] = epay_no

	#get payer info
	if type == 'citizen':
		payer = { 'name': model.getDisplayName(), 'address': model.address, 'idString':'Citizen ID: ' + model.citizen_id }
	elif type == 'business':
		payer = { 'name': model.name, 'address': model.address, 'idString':'TIN/RRA: ' + model.tin }
	elif type == 'property':
		payer = { 'name': model.getUPI(), 'address': model.getDisplayName, 'idString':''}

	receipt['payer'] = payer
	taxes = []

	#get all late fees incurred
	payment = tax.calculatePayment()
	total = 0
	late_fees = []
	if payment['late_fees']:
		if payment['interest'] > 0:
			late_fee_record = { 'name': 'Late Fee Interest', 'reference': '', 'invoice_no': '', 'bank_receipt': '', 'amount': payment['interest'], 'currency': tax.currency}
			late_fees.append(late_fee_record)
		if payment['surcharge'] > 0:
			late_fee_record = { 'name': 'Late Fee Surcharge', 'reference': '', 'invoice_no': '', 'bank_receipt': '', 'amount': payment['surcharge'], 'currency': tax.currency}
			late_fees.append(late_fee_record)

	if tax_type == 'fee':
		tax_record = { 'name': tax.name or tax.fee_type.replace("_"," ").title(), 'reference': getTaxReference(tax_type, tax),'amount': (tax.amount or 0), 'currency': tax.currency}
	elif tax_type == 'misc_fee':
		tax_record = { 'name': tax.fee_type.replace("_"," ").title(), 'reference': tax.fee_sub_type.title(),'amount': (tax.amount or 0), 'currency': tax.currency}
	else:
		tax_record = { 'name': tax_type.replace("_"," ").title(), 'reference': getTaxReference(tax_type, tax),'amount': (tax.amount or 0), 'currency': tax.currency}
	taxes.append(tax_record)

	receipt['late_fees'] = late_fees
	receipt['total'] = ( tax.amount or 0 ) + payment['late_fees']
	remaining_amount = (tax.amount or 0 ) - payment['amount_paid']
	receipt['total_outstanding'] = remaining_amount + payment['late_fees']

	#append fines - if exists
	"""
	if tax.submit_details and tax.submit_details.find('fine_description') >= 0:
		details = json.loads(tax.submit_details)
		if int(details['fine_amount']) >0:
			tax_record = { 'name': 'Fines', 'reference': details['fine_description'], 'amount': details['fine_amount'], 'currency': tax.currency }
			taxes.append(tax_record)
			receipt['total'] = int(round(receipt['total'] + Decimal(details['fine_amount']),2))
	"""
	receipt['taxes'] = taxes

	#check for any pending future payments for this payer, limit to 2 months only

	receipt['installments'] = tax.get_installments()
	receipt['future_payments'] = getUpcomingTaxes(type,model)

	return receipt


def getUpcomingTaxes(type, model):
	today = timezone.make_aware(datetime.combine(datetime.today(), time(0,0)), timezone.get_default_timezone())
	current_year = str(today.year)
	#year_start = timezone.make_aware(dateutil.parser.parse(current_year + '-01-01 00:00:00'), timezone.get_default_timezone())
	#year_end = timezone.make_aware(dateutil.parser.parse(current_year + '-12-31 23:59:59'), timezone.get_default_timezone())
	start = datetime(today.year,today.month,today.day,23,59,59)
	day_upcoming = today + relativedelta(days=60)
	end = datetime(day_upcoming.year,day_upcoming.month,day_upcoming.day,0,0,0)
	date_range = (start,end)

	upcoming_taxes = []
	if type == 'citizen':
		ownerships = Ownership.objects.filter(owner_citizen=model,asset_business__isnull=False)
		if ownerships:
			for ownership in ownerships:
				if ownership.asset_property:
					property = ownership.asset_property
					#get unpaid pending fixed asset taxes
					taxes = PropertyTaxItem.objects.filter(due_date__range=date_range,i_status='active',is_paid=False, property=property)
					if taxes:
						for tax in taxes:
							reference = getTaxReference('fixed_asset', tax)
							tax_record = { 'due_date':tax.due_date,'name':'Fixed Asset - ' + reference, 'amount': tax.remaining_amount, 'currency': tax.currency}
							upcoming_taxes.append(tax_record)

					#get unpaid pending rental income taxes
					taxes = RentalIncomeTax.objects.filter(due_date__range=date_range,i_status='active',is_paid=False, property=property)
					if taxes:
						for tax in taxes:
							reference = getTaxReference('rental_income', tax)
							tax_record = { 'due_date':tax.due_date,'name':'Rental Income - ' + reference, 'amount': tax.remaining_amount, 'currency': tax.currency}
							upcoming_taxes.append(tax_record)
				elif ownership.asset_business:
					#if there is no Trading License Tax Item for this business in the current year, add a new Trading License Tax
					business = ownership.asset_business
					taxes = TradingLicenseTax.objects.filter(due_date__range=date_range,i_status='active',is_paid=False,business__exact=business)
					if taxes:
						for tax in taxes:
							reference = getTaxReference('trading_license', tax)
							tax_record = { 'due_date':tax.due_date,'name':'Trading License - ' + reference, 'amount': tax.remaining_amount, 'currency': tax.currency}
							upcoming_taxes.append(tax_record)

		#start checking fees
		fees = Fee.objects.filter(due_date__range=date_range,i_status='active',is_paid=False, citizen = model)
		if fees:
			for fee in fees:
				reference = getTaxReference(fee.fee_type, tax)
				tax_record = { 'due_date':tax.due_date,'name': fee.fee_type.replace("_"," ").title() + ' fee for ' + Common.localizeDate(fee.period_from).strftime('%b %Y'), 'amount': tax.remaining_amount, 'currency': tax.currency}
				upcoming_taxes.append(tax_record)
	elif type == 'business':
		#checking trading license tax for this business
		taxes = TradingLicenseTax.objects.filter(due_date__range=date_range,i_status='active',is_paid=False,business=model)
		if taxes:
			for tax in taxes:
				reference = getTaxReference('trading_license', tax)
				tax_record = { 'due_date':tax.due_date,'name':'Trading License - ' + reference, 'amount': tax.remaining_amount, 'currency': tax.currency}
				upcoming_taxes.append(tax_record)
		#start checking fees
		fees = Fee.objects.filter(due_date__range=date_range,i_status='active',is_paid=False, business = model)
		if fees:
			for fee in fees:
				reference = getTaxReference(fee.fee_type, fee)
				tax_record = { 'due_date':fee.due_date,'name': fee.fee_type.replace("_"," ").title() + ' fee for ' + Common.localizeDate(fee.period_from).strftime('%b %Y'), 'amount': fee.remaining_amount, 'currency': fee.currency}
				upcoming_taxes.append(tax_record)
	elif type == 'property':
		#get unpaid pending fixed asset taxes
		taxes = PropertyTaxItem.objects.filter(due_date__range=date_range,i_status='active',is_paid=False, property=model)
		if taxes:
			for tax in taxes:
				reference = getTaxReference('fixed_asset', tax)
				tax_record = { 'due_date':tax.due_date,'name':'Fixed Asset - ' + reference, 'amount': tax.remaining_amount, 'currency': tax.currency}
				upcoming_taxes.append(tax_record)

		#get unpaid pending rental income taxes
		taxes = RentalIncomeTax.objects.filter(due_date__range=date_range,i_status='active',is_paid=False, property=model)
		if taxes:
			for tax in taxes:
				reference = getTaxReference('rental_income', tax)
				tax_record = { 'due_date':tax.due_date,'name':'Rental Income - ' + reference, 'amount': tax.remaining_amount, 'currency': tax.currency}
				upcoming_taxes.append(tax_record)

		#start checking fees
		fees = Fee.objects.filter(due_date__range=date_range,i_status='active',is_paid=False, property = model)
		if fees:
			for fee in fees:
				reference = getTaxReference(fee.fee_type, fee)
				tax_record = { 'due_date':fee.due_date,'name': fee.fee_type.replace("_"," ").title() + ' fee for ' + Common.localizeDate(fee.period_from).strftime('%b %Y'), 'amount': fee.remaining_amount, 'currency': fee.currency}
				upcoming_taxes.append(tax_record)

	return upcoming_taxes


@csrf_exempt
def update_installment_date(request):
	id = request.POST.get('id')
	due = dateutil.parser.parse(request.POST.get('due_date'))
	installment = get_object_or_404(Installment, pk=id)
	installment.due = due
	installment.save()
	json_data = json.dumps({'due_date':request.POST.get('due_date') });
	return HttpResponse(json_data, mimetype='application/json')

def viewFeeSettingPage(request):
	settings_label = 'Default Fee Settings'
	district = None
	sector = None
	cell=None
	village=None
	invalid_setting_ids = []
	fee_type=[]
	list={}
	c = {}
	conditions=dict()
	graph_title=""
	c.update(csrf(request))
	if request.method=='GET':
		form = fee_view_search_form(request)
	elif request.method=='POST':
		
		if request.POST.has_key('district') and request.POST['district']<>"":			
			district = request.POST['district']
			conditions['district'] = district
			graph_title=graph_title+" "+DistrictMapper.getById(district).name+" "
		if request.POST.has_key('sector') and request.POST['sector']<>"":
			sector = request.POST['sector']
			conditions['sector'] = sector
			graph_title=graph_title+" "+SectorMapper.getById(sector).name+" "
		if request.POST.has_key('cell') and request.POST['cell']<>"":
			cell=request.POST['cell']
			conditions['cell']=cell
		if request.POST.has_key('village') and request.POST['village']<>"":
			village=request.POST['village']
			conditions['village']=village
		mySettings=TaxMapper.getFeeSettingList(conditions ={'district':district,'sector':sector,'cell':cell, 'village':village})
		form = fee_view_search_form(request, request.POST)
		if mySettings:
			for i in mySettings:
				tax_fee_name = i.tax_fee_name.replace("_",' ').title()
				setting_name = i.setting_name.replace("_",' ').title()
				if list.has_key(tax_fee_name):
					temp = list[tax_fee_name]
				else:
					temp = {}
	
				if i.sub_type != None and i.sub_type != '':
					if temp.has_key(setting_name):
						setting_list = temp[setting_name]['value']
					else:
						setting_list = []
					setting_list.append({'sub_type':i.sub_type,'value':i.value,'id':i.id})
					temp[setting_name] = {'description':i.description,'value':setting_list,'type':'list','valid_from':i.valid_from,'valid_to':i.valid_to}	
				elif '_rate' in i.setting_name:
					temp[setting_name] = {'id':i.id,'description':i.description,'value':str(Decimal(i.value)*100),'type':'rate','valid_from':i.valid_from,'valid_to':i.valid_to}
				else:
					temp[setting_name] = {'id':i.id,'description':i.description,'value':i.value,'type':'','valid_from':i.valid_from,'valid_to':i.valid_to}
	
				list[tax_fee_name] = temp	
		else:
			list = None
			invalid_setting_ids = None

	return render_to_response('tax/tax_fee_view.html',{'settings_label':settings_label,'list':list,'invalid_setting_ids':invalid_setting_ids,'form':form, 'csrf':c},
								context_instance=RequestContext(request))


def viewTaxSettingPage(request):
	settings_label = 'Default Fee Settings'
	district = None
	sector = None
	cell=None
	village=None
	invalid_setting_ids = []
	fee_type=[]
	list={}
	c = {}
	conditions=dict()
	graph_title=""
	c.update(csrf(request))
	if request.method=='GET':
		form = fee_view_search_form(request)
	elif request.method=='POST':
		
		if request.POST.has_key('district') and request.POST['district']<>"":			
			district = request.POST['district']
			conditions['district'] = district
			graph_title=graph_title+" "+DistrictMapper.getById(district).name+" "
		if request.POST.has_key('sector') and request.POST['sector']<>"":
			sector = request.POST['sector']
			conditions['sector'] = sector
			graph_title=graph_title+" "+SectorMapper.getById(sector).name+" "
		if request.POST.has_key('cell') and request.POST['cell']<>"":
			cell=request.POST['cell']
			conditions['cell']=cell
		if request.POST.has_key('village') and request.POST['village']<>"":
			village=request.POST['village']
			conditions['village']=village
		mySettings=TaxMapper.getTaxSettingList(conditions ={'district':district,'sector':sector,'cell':cell, 'village':village})
		form = fee_view_search_form(request, request.POST)
		if mySettings:
			for i in mySettings:
				tax_fee_name = i.tax_fee_name.replace("_",' ').title()
				setting_name = i.setting_name.replace("_",' ').title()
				if list.has_key(tax_fee_name):
					temp = list[tax_fee_name]
				else:
					temp = {}
	
				if i.sub_type != None and i.sub_type != '':
					if temp.has_key(setting_name):
						setting_list = temp[setting_name]['value']
					else:
						setting_list = []
					setting_list.append({'sub_type':i.sub_type,'value':i.value,'id':i.id})
					temp[setting_name] = {'description':i.description,'value':setting_list,'type':'list','valid_from':i.valid_from,'valid_to':i.valid_to}	
				elif '_rate' in i.setting_name:
					temp[setting_name] = {'id':i.id,'description':i.description,'value':str(Decimal(i.value)*100),'type':'rate','valid_from':i.valid_from,'valid_to':i.valid_to}
				else:
					temp[setting_name] = {'id':i.id,'description':i.description,'value':i.value,'type':'','valid_from':i.valid_from,'valid_to':i.valid_to}
	
				list[tax_fee_name] = temp	
		else:
			list = None
			invalid_setting_ids = None

	return render_to_response('tax/tax_tax_view.html',{'settings_label':settings_label,'list':list,'invalid_setting_ids':invalid_setting_ids,'form':form, 'csrf':c},
								context_instance=RequestContext(request))



# def viewTaxSettingPage(request):
# 	ettings_label = 'Default Tax Settings'
# 	district = None
# 	sector = None
# 	cell=None
# 	village=None
# 	invalid_setting_ids = []
# 	fee_type=[]
# 	list={}
# 	c = {}
# 	conditions=dict()
# 	graph_title=""
