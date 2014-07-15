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



def cleaning_audit_csv(payments, includes, criteria={}):
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="cleaning_fee_audit.csv"'
	writer = csv.writer(response)
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

	if 'Business Name' in includes:
		header.append('Business Name')

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

		if 'Business Name' in includes:
			if p.fee.subbusiness:
				row.append(p.fee.subbusiness.name.encode('utf-8'))
			else:
				row.append(p.fee.business.name.encode('utf-8'))	
		
		if 'Cell' in includes:
			if p.fee.subbusiness and p.fee.subbusiness.business.cell:
				row.append(p.fee.subbusiness.business.cell.name.encode('utf-8'))
			elif p.fee.business and p.fee.business.cell:
				row.append(p.fee.business.cell.name.encode('utf-8'))
			else:
				row.append('')

		if 'Fines' in includes:
			row.append(p.fine_amount or '0.00')

		if 'Receipt' in includes:
			row.append(p.manual_receipt or '')

		if 'Bank' in includes:
			row.append(p.bank or '')

		if 'Bank Receipt' in includes:
			row.append(p.receipt_no or '')

		if 'User' in includes:
			row.append(p.staff.username or '')

		if 'Timestamp' in includes:
			row.append(p.date_time or '')

		if 'Total Fee Amount' in includes:
			row.append(p.fee.amount or '')

		if 'Remaining Fee Amount' in includes:
			row.append(p.fee.remaining_amount or '')

		writer.writerow(row)

	return response


def cleaning_audit(request):
	user = request.session.get('user')
	if not user or not user.superuser:
		return HttpResponseRedirect('/')
	payments = PayFee.objects.none()
	totals = {}
	include_fields = []
	if request.method == 'POST':
		form = SearchForm(request.POST)
		if form.is_valid():
			include_fields = form.cleaned_data['include_fields']
			payments = PayFee.objects.filter(i_status='active', fee__fee_type='cleaning', date_time__gte=form.cleaned_data['date_from'], date_time__lte=form.cleaned_data['date_to']).select_related('fee', 'fee__business', 'staff').order_by('date_time')
			if form.cleaned_data['sector']:
				payments = payments.filter(Q(fee__business__sector=form.cleaned_data['sector'])| Q(fee__subbusiness__sector=form.cleaned_data['sector']))
			if form.cleaned_data['cell']:
				payments = payments.filter(Q(fee__business__cell=form.cleaned_data['cell']) | Q(fee__subbusiness__cell=form.cleaned_data['cell']))
			totals['payment'] = payments.aggregate(Sum('amount'))['amount__sum']
			totals['fee'] = payments.aggregate(Sum('fee__amount'))['fee__amount__sum']
			totals['remaining'] = payments.filter(fee__remaining_amount__gte=0).aggregate(Sum('fee__remaining_amount'))['fee__remaining_amount__sum']
			totals['fines'] = payments.aggregate(Sum('fine_amount'))['fine_amount__sum']

			if request.POST.get('web_button') or not payments:
				return TemplateResponse(request, 'tax/cleaning_fee_audit.html', { 'payments':payments, 'form':form, 'include_fields':include_fields, 'totals':totals })
			else: # csv
				return cleaning_audit_csv(payments, form.cleaned_data.get('include_fields'), form.cleaned_data)

	else:
		form = SearchForm()

	return TemplateResponse(request, 'tax/cleaning_fee_audit.html', { 'payments':None, 'form':form, })



def cleaning_debtors_csv(report, line_items, criteria={}, th=None):
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
			if form.cleaned_data['sector']:
				line_items = line_items.filter(Q(business__sector=form.cleaned_data['sector'])| Q(subbusiness__sector=form.cleaned_data['sector']))
			if form.cleaned_data['cell']:
				line_items = line_items.filter(Q(business__cell=form.cleaned_data['cell']) | Q(subbusiness__cell=form.cleaned_data['cell']))

			th = {}
			th[0] = date.today().strftime("5-%b-%Y")
			th[1] = (date.today() - relativedelta(months=1)).strftime("5-%b-%Y")
			th[3] = (date.today() - relativedelta(months=3)).strftime("5-%b-%Y")
			th[6] = (date.today() - relativedelta(months=6)).strftime("5-%b-%Y")
			th[12] = (date.today() - relativedelta(months=12)).strftime("5-%b-%Y")
			if request.POST.get('web_button') or not line_items:
				return TemplateResponse(request, 'tax/cleaning_fee_debtors.html', { 'report':debtors_report, 'line_items':line_items, 'form':form, 'th':th })
			else: # csv
				return cleaning_debtors_csv(debtors_report, line_items, form.cleaned_data, th)
	else:
		form = DebtorsForm()

	return TemplateResponse(request, 'tax/cleaning_fee_debtors.html', { 'businesses':None, 'form':form, })



def duplicates(request):
	rows = Duplicate.objects.filter(status=1).order_by('-similarity').select_related('business1','business2')
	return TemplateResponse(request, 'asset/business/duplicates.html', { 'rows':rows })




