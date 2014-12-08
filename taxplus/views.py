from django.template.response import TemplateResponse
from django.shortcuts import HttpResponseRedirect, render_to_response, get_object_or_404, redirect
from jtax.models import PayFee, Fee
from property.models import District, Sector, Cell
from datetime import date
import json
from taxplus.forms import SearchForm, DebtorsForm
from django.db.models import Q, Sum
import csv
from django.http import HttpResponse
from asset.models import Business, Duplicate
from dateutil.relativedelta import relativedelta
from taxplus.models import *
from django.contrib.auth.decorators import login_required
from taxplus.forms import PaymentForm, PayFeesForm
from django.contrib import messages
from django.core.urlresolvers import reverse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from taxplus.management.commands.generate_invoices import generate_invoice



def cleaning_audit_csv(payments, includes, criteria={}):
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

	if 'Cell' in includes:
		header.append('Cell')

	if 'Fines' in includes:
		header.append('Fines')

	if 'Receipt' in includes:
		header.append('Sector Receipt')

	if 'Bank' in includes:
		header.append('Bank')

	if 'Bank Receipt' in includes:
		header.append('Bank Receipt')

	if 'User' in includes:
		header.append('User')

	if 'Timestamp' in includes:
		header.append('Timestamp')

	if 'Total Fee Amount' in includes:
		header.append('Total Fee Amount')

	if 'Remaining Fee Amount' in includes:
		header.append('Remaining Amount')

	writer.writerow(header)

	for p in payments:
		row = []
		row.append(p.amount)
		row.append(p.fee.date_from.strftime('%b/%Y'))

		if fee_type == 'land_lease':
			row.append(p.fee.prop.__unicode__().encode('utf-8'))
		else:
			row.append('')
			#row.append(p.fee.business.name.encode('utf-8'))

		if 'Cell' in includes and fee_type == 'cleaning':
			if p.fee.business and p.fee.business.cell:
				row.append(p.fee.business.cell.name.encode('utf-8'))
			else:
				row.append('')

		elif 'Cell' in includes and fee_type == 'land_lease':
			if p.fee.prop and p.fee.prop.village:
				row.append(p.fee.prop.village.cell.name.encode('utf-8'))

			elif p.fee.prop and p.fee.prop.cell:
				row.append(p.fee.prop.cell.name.encode('utf-8'))

			else:
				row.append('')

		if 'Fines' in includes:
			row.append(p.fine_amount or '0.00')

		if 'Receipt' in includes:
			row.append(p.manual_receipt.encode('utf-8') or '')

		if 'Bank' in includes:
			row.append(p.bank or '')

		if 'Bank Receipt' in includes:
			row.append(p.receipt_no.encode('utf-8') or '')

		if 'User' in includes and p.staff:
			row.append(p.staff.username or '')
		else:
			row.append('')

		if 'Timestamp' in includes:
			row.append(p.date_time or '')

		if 'Total Fee Amount' in includes:
			row.append(p.fee.amount or '')

		if 'Remaining Fee Amount' in includes:
			row.append(p.fee.remaining_amount or '')

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
	rows = Duplicate.objects.filter(status=1).order_by('-similarity').select_related('business1','business2')
	return TemplateResponse(request, 'asset/business/duplicates.html', { 'rows':rows })


@login_required
def property_fees(request, pk):
	prop = get_object_or_404(Property, pk=pk)
	fees = prop.property_fees.filter(amount__gt=0)
	for fee in fees:
		fee.adjust_payments()
	return TemplateResponse(request, 'tax/tax_tax_property_fees.html', { 'property':prop, 'fees':fees })


@login_required
def business_fees(request, pk):
	business = get_object_or_404(Business, pk=pk)
	fees = business.business_fees.filter(amount__gt=0)
	for fee in fees:
		fee.adjust_payments()
	return TemplateResponse(request, 'tax/business_fees.html', { 'business':business, 'fees':fees })


@login_required
def payLandLease(request, pk=None):
	business_id = None
	citizen_id = None
	fee = get_object_or_404(Fee, pk=pk)
	penalty, interest = fee.calc_penalty(date.today())
	total = fee.remaining_amount + penalty + interest
	payer_name = ''

	if fee.remaining_amount == 0:
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
				fee.process_payment(payment_date=d.get('paid_date'), citizen_id=citizen_id, business_id=business_id, sector_receipt=d.get('sector_receipt'), \
					bank_receipt=d.get('bank_receipt'), payment_amount=d.get('amount'), staff_id=user.pk, bank=d.get('bank'), payer_name=payer_name)
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


	return TemplateResponse(request, "tax/paylandlease.html", { 'form':form, 'property':fee.prop,
		'tax':fee, 'payer_name':payer_name })


@login_required
def paySelectedFees(request):
	pay_fees = [ int(pk) for pk in request.POST.getlist('pay_fee')]
	fees = Fee.objects.filter(pk__in=pay_fees)
	total = 0
	if request.POST:
		form = PayFeesForm(request.POST)

		if form.is_valid():
			citizen_id = None
			business_id = None
			payer_type = form.cleaned_data.get('payer_type')
			if payer_type == 'citizen':
				citizen_id = form.cleaned_data.get('citizen_id')
				if citizen_id:
					citizen = Citizen.objects.get(pk=citizen_id)
				payer_name = form.cleaned_data.get('payer_name')

			elif payer_type == 'business':
				business_id = form.cleaned_data.get('business_id')
				if business_id:
					business = Business.objects.get(pk=business_id)
				payer_name = form.cleaned_data.get('payer_name')

			if request.POST.get('process_payment'): #process payment
				d = form.cleaned_data
				user = request.session.get('user')
				payment_receipt = Fee.process_payments(payment_date=d.get('paid_date'), citizen_id=citizen_id, business_id=business_id,
					payer_name=d.get('payer_name'), sector_receipt=d.get('sector_receipt'),
					bank_receipt=d.get('bank_receipt'), bank=d.get('bank'), staff_id=user.pk, fee_ids=pay_fees)
				#redirect to receipt
				payFee = PayFee.objects.filter(receipt=payment_receipt)[0]
				return HttpResponseRedirect('/admin/tax/tax/generate_invoice/?type=fee&id=%s' % payFee.pk)

		else:
			pass
	else:
		initial = {'paid_date':date.today().strftime('%d/%m/%Y')}
		form = PayFeesForm(initial=initial)


	if hasattr(form,'cleaned_data'):
		paid_date = form.cleaned_data.get('paid_date')
	else:
		paid_date = date.today()
	for fee in fees:
		penalty, interest = fee.calc_penalty(paid_date)
		fee.penalty = penalty
		fee.interest = interest
		fee.total = fee.remaining_amount + penalty + interest
		total += fee.total


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



