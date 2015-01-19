from django.template.response import TemplateResponse
from django.shortcuts import HttpResponseRedirect, render_to_response, get_object_or_404, redirect
from jtax.models import PayFee, Fee
from property.models import District, Sector, Cell
from datetime import date
import json
from taxplus.forms import SearchForm, DebtorsForm, MergeBusinessForm
from django.db.models import Q, Sum
import csv
from django.http import HttpResponse
from dateutil.relativedelta import relativedelta
from taxplus.models import *
from django.contrib.auth.decorators import login_required
from taxplus.forms import PaymentForm, PayFeesForm, TitleForm
from django.contrib import messages
from django.core.urlresolvers import reverse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from taxplus.management.commands.generate_invoices import generate_invoice
from django.forms.models import modelformset_factory



@login_required
def leases(request, pk):
	prop = get_object_or_404(Property, pk=pk)
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
				delete_ownership = request.POST.getlist('ownership_id')
				if delete_ownership:
					Ownership.objects.filter(id__in=delete_ownership).delete()
				return HttpResponseRedirect(reverse('edit_lease', args=[lease.pk]))
		else:
			form = TitleForm(request.POST, instance=lease)
			if form.is_valid():
				form.save()
				lease.calc_taxes()
				user = PMUser.objects.get(pk=request.session.get('user').pk)
				Log.objects.create(property=lease.prop, user = user, message='Property Title %s updated. Date from: %s, Date to %s' % (lease.pk, lease.date_from, lease.date_to))
				messages.success(request, 'Land lease updated')
				return HttpResponseRedirect(reverse('property_leases', args=[lease.prop.pk]))
	else:
		form = TitleForm(instance=lease)

	return TemplateResponse(request, 'tax/property_lease.html', { 'property':lease.prop, 'lease':lease, 'form':form})


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
			user = PMUser.objects.get(pk=request.session.get('user').pk)
			Log.objects.create(property=lease.prop, user = user, message='Property Title %s updated from: %s to %s' % (lease.pk, lease.date_from, lease.date_to))
			messages.success(request, 'Land lease created')
			return HttpResponseRedirect(reverse('edit_lease', args=[lease.pk]))
	else:
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
	return TemplateResponse(request, 'asset/business/duplicates.html', { 'businesses':businesses })


@login_required
def merge_preview(request, pk):
	business = get_object_or_404(Business,pk=pk)
	duplicates = Duplicate.objects.filter(business1=business)
	return TemplateResponse(request, 'asset/business/merge_preview.html', { 'business':business, 'duplicates':duplicates })


@login_required
def property_fees(request, pk):
	prop = get_object_or_404(Property, pk=pk)
	fees = prop.property_fees.filter(status__code='active')
	payments = PayFee.objects.filter(fee__in=fees)
	return TemplateResponse(request, 'tax/tax_tax_property_fees.html', { 'property':prop, 'fees':fees, 'payments':payments })


@login_required
def business_fees(request, pk):
	business = get_object_or_404(Business, pk=pk)
	fees = business.business_fees.filter(amount__gt=0)
	payments = PayFee.objects.filter(fee__in=fees)
	return TemplateResponse(request, 'tax/business_fees_new.html', { 'business':business, 'fees':fees, 'payments':payments  })


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
					return HttpResponseRedirect(reverse('property_fees', args=[fee.prop_id]))
				elif fee.business_id:
					return HttpResponseRedirect(reverse('business_fees', args=[fee.business_id]))

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

				payment_receipt = process_payment(amount = amount, payment_date=d.get('paid_date'), citizen_id=citizen_id, business_id=business_id,
					payer_name=d.get('payer_name'), sector_receipt=d.get('sector_receipt'),
					bank_receipt=d.get('bank_receipt'), bank=d.get('bank'), staff_id=user.pk, fee=fees)

				#redirect to receipt
				return HttpResponseRedirect(reverse('tax_receipt', args=(payment_receipt.pk,)))

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


def property_media(request, pk):
	prop = get_object_or_404(Property, pk=pk)
	media = Media.objects.filter(property=prop)
	return TemplateResponse(request, "tax/tax_tax_property_media.html", { 'property':prop, 'media':media  })



