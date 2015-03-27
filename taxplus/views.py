#from property.models import District, Sector, Cell
from datetime import date
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.core.urlresolvers import reverse
from django.db.models import Q, Sum
from django.forms.models import modelformset_factory
from django.http import HttpResponse, Http404
from django.shortcuts import HttpResponseRedirect, render_to_response, get_object_or_404, redirect
from django.template.response import TemplateResponse
from jtax.models import PayFee, Fee
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from taxplus.forms import PaymentForm, PayFeesForm, TitleForm
from taxplus.forms import SearchForm, DebtorsForm, MergeBusinessForm, BusinessForm, BusinessFormRegion, MessageBatchForm, PaymentSearchForm
from taxplus.management.commands.generate_invoices import generate_invoice
from taxplus.models import *
from dev1.ThreadLocal import Log
import csv
import json

def csv_data(rows, values_list, filename, preamble=None):
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="%s"' % filename
	writer = csv.writer(response)
	rows = rows.values_list(*values_list)
	if preamble:
		for k, v in preamble.iteritems():
			writer.writerow([k,v])
		writer.writerow([])

	writer.writerow(values_list)
	for r in rows:
		row = []
		for item in r:
			if isinstance(item, datetime):
				item = item.strftime('%d/%m/%Y %H:%M')

			elif isinstance(item, date):
				item = item.strftime('%d/%m/%Y')

			if isinstance(item, basestring):
				row.append(item.encode('utf-8'))

			elif item is None:
				row.append('')

			else:
				row.append(item)

		writer.writerow(row)

	return response


@login_required
def leases(request, pk):
	prop = get_object_or_404(Property, pk=pk)
	Log.log(target=prop, message="view leases")
	#TitleFormSet = modelformset_factory(PropertyTitle, form=TitleForm, extra=0)
	titles = PropertyTitle.objects.filter(prop=prop).order_by('-date_from')
	"""
	if request.method == 'POST':
		titleformset = TitleFormSet(request.POST)
		if titleformset.is_valid():
			user = PMUser.objects.get(pk=request.session.get('user').pk)
			Log.objects.create(property=prop, user = user, message='Property Titles updated')
			titleformset.save()
			for title in titles:
				title.calc_taxes()
			messages.success(request, 'Land leases updated')
			return HttpResponseRedirect(reverse('property_leases', args=[prop.pk]))
	else:
		#for title in titles:
		#	title.calc_taxes()
		titleformset = TitleFormSet(queryset=titles)
	"""
	return TemplateResponse(request, 'tax/property_leases.html', { 'property':prop, 'titles':titles })


@login_required
def edit_lease(request, pk):
	lease = get_object_or_404(PropertyTitle, pk=pk)
	if request.method == 'POST':
		if request.POST.get('payer_type'):
			payer_type = request.POST.get('payer_type')
			citizen_id = request.POST.get('citizen_id')
			business_id = request.POST.get('business_id')
			if payer_type == 'citizen' and citizen_id:
				citizen = get_object_or_404(Citizen, pk=citizen_id)
				ownership, created = Ownership.objects.get_or_create(asset_property=lease.prop, owner_citizen=citizen, defaults=dict(date_started=lease.date_from, date_ended=lease.date_to, prop_title=lease))
				messages.success(request, 'leaser %s added' % citizen)
				return HttpResponseRedirect(reverse('edit_lease', args=[lease.pk]))

			elif payer_type == 'business' and business_id:
				business = get_object_or_404(Business, pk=business_id)
				ownership, created = Ownership.objects.get_or_create(asset_property=lease.prop, owner_business=business, defaults=dict(date_started=lease.date_from, date_ended=lease.date_to, prop_title=lease))
				messages.success(request, 'leaser %s added' % business)
				return HttpResponseRedirect(reverse('edit_lease', args=[lease.pk]))

			else:
				messages.warning(request, 'could not add leaser')
				form = TitleForm(instance=lease)

		if request.POST.get('remove_leasers'):
				Log.log(message='remove leasers', target=lease.prop, target2=lease)
				delete_ownership = request.POST.getlist('ownership_id')
				if delete_ownership:
					Ownership.objects.filter(id__in=delete_ownership).delete()
				return HttpResponseRedirect(reverse('edit_lease', args=[lease.pk]))
		else:
			form = TitleForm(request.POST, instance=lease)
			if form.is_valid():
				form.save()
				Log.log('lease updated', target2=lease, target=lease.prop)
				lease.calc_taxes()
				messages.success(request, 'Land lease updated')
				return HttpResponseRedirect(reverse('property_leases', args=[lease.prop.pk]))
	else:
		Log.log(message='view lease to edit', target=lease.prop, target2=lease)
		form = TitleForm(instance=lease)

	return TemplateResponse(request, 'tax/property_lease.html', { 'property':lease.prop, 'lease':lease, 'form':form})


@login_required
def new_lease(request, pk):
	prop = get_object_or_404(Property, pk=pk)
	if request.method == 'POST':
		form = TitleForm(request.POST)
		if form.is_valid():
			lease = form.save(commit=False)
			lease.status = CategoryChoice.objects.get(code='active', category__code='status')
			lease.prop = prop
			lease.set_hash_key()
			lease.save()
			lease.calc_taxes()
			Log.log(message='Lease created', target=prop, target2=lease)
			messages.success(request, 'Land lease created')
			return HttpResponseRedirect(reverse('edit_lease', args=[lease.pk]))
	else:
		Log.log(message='New Lease Form', target=prop)
		form = TitleForm()

	return TemplateResponse(request, 'tax/new_lease.html', { 'property':prop, 'form':form})



def merge_business(request):
	form = None
	businesses = Business.objects.filter(pk__in=[int(pk) for pk in request.POST.getlist('business')])
	if request.POST.get('merge'):
		form = MergeBusinessForm(request.POST, businesses=businesses)
		if form.is_valid():
			business = form.save()
			business.merge(businesses)
			Log.log(message="Business merge", target=business)
			success_message = 'Business merged successfully. <a href="%s">%s</a> ' % (reverse('business_fees', args=[business.pk]), business)
			messages.success(request, success_message)
			Duplicate.objects.filter(business1=business, business2__in=businesses).update(status=0)
			return HttpResponseRedirect(reverse('duplicates'))
	else:
		form = MergeBusinessForm(businesses=businesses)

	return TemplateResponse(request, 'asset/business/merge_business.html', { 'form':form, 'businesses':businesses })



def cleaning_audit_csv(payments, criteria):
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="cleaning_fee_audit.csv"'
	writer = csv.writer(response)
	fee_type = criteria.get('fee_type')
	if fee_type == 'land_lease':
		writer.writerow(['LAND LEASE FEE AUDIT REPORT'])
	else:
		writer.writerow(['CLEANING FEE AUDIT REPORT'])

	if criteria.get('district'):
		writer.writerow(['District:', criteria.get('district').name] )
	if criteria.get('sector'):
		writer.writerow(['Sector:', criteria.get('sector').name] )
	if criteria.get('cell'):
		writer.writerow(['Cell:', criteria.get('cell').name] )
	if criteria.get('village'):
		writer.writerow(['Village:', criteria.get('village').name] )
	writer.writerow(['Date from:', criteria.get('date_from').strftime('%d %B %Y')] )
	writer.writerow(['Date to:', criteria.get('date_to').strftime('%d %B %Y')] )
	writer.writerow([])
	header = []
	header.append('Payment Amount')
	header.append('Month/Year')

	if fee_type == 'land_lease':
		header.append('Property')
	else:
		header.append('Business')

	header.append('Cell')

	header.append('Fines')

	header.append('Sector Receipt')

	header.append('Bank')

	header.append('Bank Receipt')

	header.append('Total Fee Amount')

	header.append('Remaining Amount')

	header.append('User')


	writer.writerow(header)

	for p in payments:
		row = []
		row.append(p.amount)
		row.append(p.fee.date_from.strftime('%b/%Y'))

		if fee_type == 'land_lease':
			row.append(p.fee.prop.__unicode__().encode('utf-8'))

		elif fee_type == 'cleaning':
			row.append(p.fee.business.name.encode('utf-8'))
		else:
			row.append('')

		if fee_type == 'cleaning':
			if p.fee.business and p.fee.business.cell:
				row.append(p.fee.business.cell.name.encode('utf-8'))
			else:
				row.append('')

		elif fee_type == 'land_lease':
			if p.fee.prop and p.fee.prop.village:
				row.append(p.fee.prop.village.cell.name.encode('utf-8'))

			elif p.fee.prop and p.fee.prop.cell:
				row.append(p.fee.prop.cell.name.encode('utf-8'))

			else:
				row.append('')

		row.append(p.fine_amount or '0.00')
		row.append(p.manual_receipt.encode('utf-8') or '')
		row.append(p.bank or '')
		row.append(p.receipt_no.encode('utf-8') or '')

		row.append(p.fee.amount or '')
		row.append(p.fee.remaining_amount)
		if p.staff:
			row.append("%s %s" % (p.staff.username, p.date_time.strftime('%d/%m/%y')))
		else:
			row.append(p.date_time.strftime('%d/%m/%y'))

		writer.writerow(row)

	return response

@login_required
def cleaning_audit(request):
	user = request.session.get('user')
	payments = PayFee.objects.none()
	totals = {}
	include_fields = []
	if request.method == 'POST':
		form = SearchForm(request.POST)
		if form.is_valid():
			fee_type = form.cleaned_data['fee_type']
			payments = PayFee.objects.filter(status__code='active', fee__status__code='active', fee__category__code=fee_type, paid_date__gte=form.cleaned_data['date_from'], paid_date__lte=form.cleaned_data['date_to'])
			if form.cleaned_data['village']:
				if fee_type == 'cleaning':
					payments = payments.filter(fee__business__village=form.cleaned_data['village'])
				else:
					payments = payments.filter(fee__prop__village=form.cleaned_data['village'])

			elif form.cleaned_data['cell']:
				if fee_type == 'cleaning':
					payments = payments.filter(fee__business__cell=form.cleaned_data['cell'])
				else:
					payments = payments.filter(fee__prop__cell=form.cleaned_data['cell'])

			elif form.cleaned_data['sector']:
				if fee_type == 'cleaning':
					payments = payments.filter(fee__business__sector=form.cleaned_data['sector'])
				else:
					payments = payments.filter(fee__prop__sector=form.cleaned_data['sector'])


			if fee_type == 'cleaning':
				payments = payments.select_related('fee', 'fee__business', 'staff', 'receipt', 'fee__business__cell', 'fee__business__village', 'fee__business__village__cell').order_by('date_time')
			else:
				payments = payments.select_related('fee', 'fee__prop', 'staff', 'receipt', 'fee__prop__village', 'fee__prop__village__cell').order_by('date_time')

			totals['payment'] = payments.aggregate(Sum('amount'))['amount__sum']
			totals['fee'] = payments.aggregate(Sum('fee__amount'))['fee__amount__sum']
			totals['remaining'] = payments.filter(fee__remaining_amount__gte=0).aggregate(Sum('fee__remaining_amount'))['fee__remaining_amount__sum']
			totals['fines'] = payments.aggregate(Sum('fine_amount'))['fine_amount__sum']

			if request.POST.get('web_button') or not payments:
				return TemplateResponse(request, 'tax/cleaning_fee_audit.html', { 'payments':payments, 'form':form, 'totals':totals })
			else: # csv
				return cleaning_audit_csv(payments, form.cleaned_data)

	else:
		form = SearchForm()

	return TemplateResponse(request, 'tax/cleaning_fee_audit.html', { 'payments':None, 'form':form, })



def cleaning_debtors_csv(report, line_items, criteria={}, th=None, totals={}):
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="cleaning_fee_debtors.csv"'
	writer = csv.writer(response)
	writer.writerow(['CLEANING FEE DEBTORS REPORT'])
	if criteria.get('district'):
		writer.writerow(['District:', criteria.get('district').name] )
	if criteria.get('sector'):
		writer.writerow(['Sector:', criteria.get('sector').name] )
	if criteria.get('cell'):
		writer.writerow(['Cell:', criteria.get('cell').name] )
	if criteria.get('village'):
		writer.writerow(['Village:', criteria.get('village').name] )
	writer.writerow(['Report as at:', report.as_at.strftime('%d %B %Y')])

	writer.writerow([])
	header = []
	header.append('Business')
	header.append('Phone')
	header.append('Address')
	header.append(th[0])
	header.append(th[1])
	header.append(th[3])
	header.append(th[6])
	header.append(th[12])

	writer.writerow(header)

	for l in line_items:
		row = []

		row.append(l.business.name.encode('utf-8'))

		if l.business.phone1:
			row.append(l.business.phone1.encode('utf-8'))
		else:
			row.append(l.business.phone2.encode('utf-8') or '')

		row.append(l.business.address or '')
		row.append(l.month)
		row.append(l.month_1)
		row.append(l.month_3)
		row.append(l.month_6)
		row.append(l.month_12)

		writer.writerow(row)

	return response


@login_required
def cleaning_debtors(request):
	user = request.session.get('user')
	if not user or not user.superuser:
		return HttpResponseRedirect('/')
	fees = Fee.objects.none()
	totals = {}
	#include_fields = []
	if request.method == 'POST':
		form = DebtorsForm(request.POST)
		if form.is_valid():
			#include_fields = form.cleaned_data['include_fields']

			debtors_report = get_object_or_404(DebtorsReport, fee_type='cleaning')
			line_items = DebtorsReportLine.objects.filter(report=debtors_report).select_related('business').order_by('business__name')
			      #['amount__sum']
			if form.cleaned_data['sector']:
				line_items = line_items.filter(Q(business__sector=form.cleaned_data['sector'])| Q(subbusiness__sector=form.cleaned_data['sector']))
			if form.cleaned_data['cell']:
				line_items = line_items.filter(Q(business__cell=form.cleaned_data['cell']) | Q(subbusiness__cell=form.cleaned_data['cell']))

			totals = line_items.aggregate(month=Sum('month'), month_1=Sum('month_1'), month_3=Sum('month_3'), month_6=Sum('month_6'), month_12=Sum('month_12'))
			totals['total'] = (totals.get('month') or 0) + (totals.get('month_1') or 0) + \
				(totals.get('month_3') or 0) + (totals.get('month_6') or 0) + (totals.get('month_12') or 0)

			th = {}
			th[0] = debtors_report.as_at.strftime("Due 5-%b-%Y")
			th[1] = (debtors_report.as_at - relativedelta(months=1)).strftime("5-%b-%Y")
			th[3] = (debtors_report.as_at - relativedelta(months=3)).strftime("5-%b-%Y")
			th[6] = (debtors_report.as_at - relativedelta(months=6)).strftime("5-%b-%Y")
			th[12] = (debtors_report.as_at - relativedelta(months=12)).strftime("5-%b-%Y")

			if request.POST.get('web_button') or not line_items:
				return TemplateResponse(request, 'tax/cleaning_fee_debtors.html', { 'report':debtors_report, 'line_items':line_items, 'form':form, 'th':th, 'totals':totals })
			else: # csv
				return cleaning_debtors_csv(debtors_report, line_items, form.cleaned_data, th, totals)
	else:
		form = DebtorsForm()

	return TemplateResponse(request, 'tax/cleaning_fee_debtors.html', { 'businesses':None, 'form':form, })


@login_required
def duplicates(request):
	businesses =  Business.objects.filter(duplicates__isnull=False, duplicates__status=1).distinct()
	Log.log(message='view duplicates')
	return TemplateResponse(request, 'asset/business/duplicates.html', { 'businesses':businesses })

@login_required
def merge_preview(request, pk):
	business = get_object_or_404(Business,pk=pk)
	duplicates = Duplicate.objects.filter(business1=business)
	Log.log(message='merge preview', target=business)
	return TemplateResponse(request, 'asset/business/merge_preview.html', { 'business':business, 'duplicates':duplicates })

@login_required
def property_fees(request, pk):
	prop = get_object_or_404(Property, pk=pk)
	fees = prop.property_fees.filter(status__code='active')
	payments = PayFee.objects.filter(fee__prop=prop, receipt__status__code='active')
	Log.log(target=prop, message='view fees')
	return TemplateResponse(request, 'tax/tax_tax_property_fees.html', { 'property':prop, 'fees':fees, 'payments':payments })

@login_required
def property_map(request, pk):
	prop = get_object_or_404(Property, pk=pk)
	Log.log(target=prop, message='view map')
	return TemplateResponse(request, 'tax/property_details.html', { 'property':prop, })

@login_required
def property_payments(request, pk):
	prop = get_object_or_404(Property, pk=pk)
	Log.log(target=prop, message='view payments')
	payments = PaymentReceipt.objects.filter(receipt_payments__fee__prop=prop, status__code='active').distinct().order_by('date_time')
	return TemplateResponse(request, 'tax/property_payments.html', { 'property':prop, 'payments':payments })

@login_required
def business_fees(request, pk):
	business = get_object_or_404(Business, pk=pk)
	fees = business.business_fees.filter(status__code='active')
	Log.log(target=business, message='view fees')
	payments = PayFee.objects.filter(fee__business=business, receipt__status__code='active')
	return TemplateResponse(request, 'tax/business_fees_new.html', { 'business':business, 'fees':fees, 'payments':payments  })

@login_required
def business_payments(request, pk):
	business = get_object_or_404(Business, pk=pk)
	payments = PaymentReceipt.objects.filter(receipt_payments__fee__business=business, status__code='active').distinct().order_by('date_time')
	Log.log(target=business, message='view payments')
	return TemplateResponse(request, 'tax/business_payments.html', { 'business':business, 'payments':payments })

@login_required
def payFee(request, pk=None):
	business_id = None
	citizen_id = None
	fees = Fee.objects.filter(pk=pk)
	fee = fees[0]
	payer_name = ''

	if fee.total_due <= 0:
		messages.add_message(request, messages.INFO, "This tax/fee has already been paid")
		#return HttpResponseRedirect(request.META['HTTP_REFERER'])

	if request.POST:
		form = PaymentForm(request.POST, fee=fee)

		if form.is_valid():

			payer_type = form.cleaned_data.get('payer_type')
			payer_name = form.cleaned_data.get('payer_name')
			payer = None

			if payer_type == 'citizen':
				citizen_id = form.cleaned_data.get('citizen_id')

			elif payer_type == 'business':
				business_id = form.cleaned_data.get('business_id')


			if not request.POST.get('process_payment'):
				pass
			else:
				d = form.cleaned_data
				user = request.session.get('user')
				process_payment(payment_date=d.get('paid_date'), citizen_id=citizen_id, business_id=business_id, sector_receipt=d.get('sector_receipt'), \
					bank_receipt=d.get('bank_receipt'), payment_amount=d.get('amount'), staff_id=user.pk, bank=d.get('bank'), payer_name=payer_name, fees=fees)
				messages.success(request, "Payment successful")
				if fee.prop_id:
					return HttpResponseRedirect(reverse('property_payments', args=[fee.prop_id]))
				elif fee.business_id:
					return HttpResponseRedirect(reverse('business_payments', args=[fee.business_id]))

		else:
			pass
	else:
		initial={'amount':fee.total_due}
		form = PaymentForm(initial=initial, fee=fee)


	return TemplateResponse(request, "tax/pay_fee.html", { 'form':form, 'property':fee.prop,
		'tax':fee, 'payer_name':payer_name })

@login_required
def payment_receipt(request, id):
	receipt = get_object_or_404(PaymentReceipt, pk=id)
	prop = None
	business = None
	for payfee in receipt.receipt_payments.all():
		prop = payfee.fee.prop
		if prop:
			break;
		business = payfee.fee.business
		if business:
			break;

	Log.log(message='view receipt', target=(business or property), target2=receipt)
	media = Media.objects.filter(Q(receipt=receipt) | Q(payfee__receipt=receipt) )
	return TemplateResponse(request, 'tax/tax_tax_invoice_multipay.html', {'receipt':receipt, 'media':media, 'property': prop, 'business': business})

@login_required
def paySelectedFees(request):
	pay_fees = [ int(pk) for pk in request.POST.getlist('pay_fee')]
	fees = Fee.objects.filter(pk__in=pay_fees).order_by('due_date')
	total = 0
	for fee in fees:
		total += fee.total_due
	if request.POST:
		form = PayFeesForm(request.POST)

		if form.is_valid():
			citizen_id = None
			business_id = None
			payer_type = form.cleaned_data.get('payer_type')
			payer_name = form.cleaned_data.get('payer_name')
			citizen_id = form.cleaned_data.get('citizen_id')
			business_id = form.cleaned_data.get('business_id')

			if request.POST.get('process_payment'): #process payment
				d = form.cleaned_data
				user = request.session.get('user')
				amount = form.cleaned_data['amount']

				payment_receipt = process_payment(payment_amount = amount, payment_date=d.get('paid_date'), citizen_id=citizen_id, business_id=business_id,
					payer_name=d.get('payer_name'), sector_receipt=d.get('sector_receipt'),
					bank_receipt=d.get('bank_receipt'), bank=d.get('bank'), staff_id=user.pk, fees=fees)

				fee = fees[0]
				messages.success(request, "Payment successful")
				#redirect to payments screen
				if fee.prop:
					return HttpResponseRedirect(reverse('property_payments', args=[fee.prop.pk]))
				elif fee.business_id:
					return HttpResponseRedirect(reverse('business_payments', args=[fee.business_id]))

		else:
			pass
	else:
		initial = {'paid_date':date.today().strftime('%d/%m/%Y')}
		form = PayFeesForm(initial=initial)


	return TemplateResponse(request, "tax/payfees.html", { 'form':form, 'fees':fees, 'total':total  })


def property_invoice(request, pk):
	title = get_object_or_404(PropertyTitle, pk=pk)
	response = HttpResponse(content_type='application/pdf')
	response['Content-Disposition'] = 'attachment; filename="invoice.pdf"'
	p = canvas.Canvas(response, pagesize=A4)
	generate_invoice(canvas=p, pagesize=A4, title=title)
	Log.log(message='view invoice', target=title.prop, target2=title)
	return response


@login_required
def get_property_invoice(request, pk):
	return property_invoice(request, pk)


def mobile_invoice(request, key):
	try:
		pk, hash_key = key.split('_')
	except:
		raise Http404

	title = get_object_or_404(PropertyTitle, pk=pk, hash_key=hash_key)
	return property_invoice(request, title.pk)

def mobile_invoice_landing(request, key):
	try:
		pk, hash_key = key.split('_')
	except:
		raise Http404

	title = get_object_or_404(PropertyTitle, pk=pk, hash_key=hash_key)
	return render_to_response('common/mobile_invoice.html', {'title':title, 'key':key})

@login_required
def property_media(request, pk):
	prop = get_object_or_404(Property, pk=pk)
	media = Media.objects.filter(property=prop)
	Log.log(message='view media', target=prop)
	return TemplateResponse(request, "tax/tax_tax_property_media.html", { 'property':prop, 'media':media  })

@user_passes_test(lambda u: u.is_superuser)
def reverse_payments(request):
	delete_payments = request.POST.getlist('reverse_payment')
	user = PMUser.objects.get(pk=request.session.get('user').pk)
	if delete_payments:
		inactive = CategoryChoice.objects.get(category__code='status', code='inactive')
		receipts = PaymentReceipt.objects.filter(id__in=delete_payments)
		for receipt in receipts:
			receipt.reverse(user=user)
			messages.success(request, 'Payment of %s reversed' % receipt.amount)
	business_id = request.POST.get('business_id')
	prop_id = request.POST.get('property_id')
	if business_id:
		business = get_object_or_404(Business, pk=business_id)
		business.adjust_payments()
	if prop_id:
		prop = get_object_or_404(Property, pk=prop_id)
		prop.adjust_payments()

	return HttpResponseRedirect(request.META['HTTP_REFERER'])

def payment_reverse(request): #deprecated payments reverse from jtax
	raise Http404

@login_required
def business_update(request, pk):
	business = get_object_or_404(Business, pk=pk)
	if request.method == 'POST':
		form = BusinessForm(request.POST, instance=business)
		if form.is_valid():
			form.save()
			business.reset_fees()
			business.calc_taxes()
			business.adjust_payments()
			#add a log message
			Log.log(message='business updated', target=business)
			messages.success(request, "Update successful")
			return HttpResponseRedirect(reverse('business_update', args=[business.pk]))
		else:
			messages.error(request, "there was a form error")
	else:
		form = BusinessForm(instance=business)

	return TemplateResponse(request, "tax/update_business.html", { 'business':business, 'form':form })

@login_required
def business_update_region(request, pk):
	business = get_object_or_404(Business, pk=pk)
	if request.method == 'POST':
		form = BusinessFormRegion(request.POST, instance=business)
		if form.is_valid():
			form.save()
			business.calc_taxes()
			business.reset_fees()
			business.adjust_payments()
			#add a log message
			messages.success(request, "Update successful")
			return HttpResponseRedirect(reverse('business_update_region', args=[business.pk]))
		else:
			messages.error(request, "there was a form error")
	else:
		form = BusinessFormRegion(instance=business)

	return TemplateResponse(request, "tax/update_business.html", { 'business':business, 'form':form })

@login_required
def message_batches(request):
	batches = MessageBatch.objects.all().select_related('district', 'sector', 'cell', 'village', 'staff')
	Log.log(message='view message batches')
	return TemplateResponse(request, "tax/message_batches.html", { 'batches':batches })

@login_required
def new_business_message_batch(request):
	if request.method == 'POST':
		form = MessageBatchForm(request.POST)
		if form.is_valid():
			batch = MessageBatch.objects.create(message=form.cleaned_data['message'], district=form.cleaned_data['district'], \
				sector=form.cleaned_data['sector'], cell=form.cleaned_data['cell'], \
				village=form.cleaned_data['village'], staff=request.user, message_type=form.cleaned_data['message_type'])
			batch.generate_messages()
			messages.success(request, "%s messages created" % batch.count)
			return HttpResponseRedirect(reverse('message_batches'))
		else:
			messages.error(request, "there was a form error")
	else:
		form = MessageBatchForm()

	return TemplateResponse(request, "tax/new_message_batch.html", { 'form':form })

@login_required
def batch_messages(request, pk, csv=None):
	batch = get_object_or_404(MessageBatch, pk=pk)
	messages = batch.batch_messages.all().select_related('citizen', 'business')
	if csv:
		batch.exported = datetime.now()
		batch.save()
		if batch.message_type == 1:
			return csv_data(messages, values_list=('message','phone','business__name'), filename='messages.csv', preamble=None)
		else:
			return csv_data(messages, values_list=('citizen__first_name',\
				'citizen__middle_name', 'citizen__last_name', 'citizen__citizen_id', 'message', 'phone'), filename='messages.csv', preamble=None)
	else:
		return TemplateResponse(request, "tax/batch_messages.html", { 'batch':batch, 'batch_messages':messages })

@login_required
def payment_search(request):
	if request.method == 'POST':
		form = PaymentSearchForm(request.POST)
		if form.is_valid():
			receipts = PaymentReceipt.objects.filter(Q(bank_receipt__icontains=form.cleaned_data.get('search_string')) | Q(sector_receipt__icontains=form.cleaned_data.get('search_string')))
			if form.cleaned_data.get('date_from'):
				receipts  = receipts.filter(date_time__gte=form.cleaned_data.get('date_from'))

			if form.cleaned_data.get('date_to'):
				receipts  = receipts.filter(date_time__lte=form.cleaned_data.get('date_to'))

			Log.log(message='Payment search')
			return TemplateResponse(request, "tax/payment_search.html", { 'form':form, 'payments':receipts })
		else:
			messages.error(request, "there was a form error")
	else:
		form = PaymentSearchForm()

	return TemplateResponse(request, "tax/payment_search.html", { 'form':form })

@login_required
def to_fee_from_payment_search(request, pk):
	receipt = get_object_or_404(PaymentReceipt, pk=pk)
	payments = receipt.receipt_payments.all()
	fee = payments[0].fee
	if fee.prop_id:
		return HttpResponseRedirect(reverse('property_payments', args=[fee.prop_id]))
	elif fee.business_id:
		return HttpResponseRedirect(reverse('business_payments', args=[fee.business_id]))








