from django.template.response import TemplateResponse 
from django.shortcuts import HttpResponseRedirect
from jtax.models import PayFee, Fee
from property.models import District, Sector, Cell
from datetime import date
import json
from taxplus.forms import SearchForm, DebtorsForm
from django.db.models import Q, Sum
import csv
from django.http import HttpResponse



def cleaning_audit_csv(payments, includes):
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename="cleaning_fee_audit.csv"'
	writer = csv.writer(response)
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
				row.append(p.fee.subbusiness.name)
			else:
				row.append(p.fee.business.name)	
		
		if 'Cell' in includes:
			if p.fee.subbusiness and p.fee.subbusiness.business.cell:
				row.append(p.fee.subbusiness.business.cell.name)
			elif p.fee.business and p.fee.business.cell:
				row.append(p.fee.business.cell.name)
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
			payments = PayFee.objects.filter(fee__fee_type='cleaning', date_time__gte=form.cleaned_data['date_from'], date_time__lte=form.cleaned_data['date_to']).select_related('fee', 'fee__business', 'staff').order_by('date_time')
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
				return cleaning_audit_csv(payments, form.cleaned_data.get('include_fields'))

	else:
		form = SearchForm()

	return TemplateResponse(request, 'tax/cleaning_fee_audit.html', { 'payments':None, 'form':form, })



def cleaning_debtors(request):
	user = request.session.get('user')
	if not user or not user.superuser:
		return HttpResponseRedirect('/')
	fees = Fee.objects.none()
	totals = {}
	include_fields = []
	if request.method == 'POST':
		form = DebtorsForm(request.POST)
		if form.is_valid():
			include_fields = form.cleaned_data['include_fields']

			as_at = form.cleaned_data['as_at']
			fees = Fee.objects.filter(fee_type='cleaning', remaining_amount__gt=0, i_status='active', due_date__lt=form.cleaned_data['as_at']).select_related('business').order_by('date_time')
			if form.cleaned_data['sector']:
				fees = fees.filter(Q(business__sector=form.cleaned_data['sector'])| Q(subbusiness__sector=form.cleaned_data['sector']))
			if form.cleaned_data['cell']:
				fees = fees.filter(Q(business__cell=form.cleaned_data['cell']) | Q(subbusiness__cell=form.cleaned_data['cell']))
			totals['amount'] = fees.aggregate(Sum('amount'))['amount__sum']
			totals['remaining'] = fees.filter(remaining_amount__gte=0).aggregate(Sum('remaining_amount'))['remaining_amount__sum']

			for fee in fees:
				if (as_at - fee.due_date).days >= 365:
					fee.late_year = fee.remaining_amount
				elif (as_at - fee.due_date).days >= 120:
					fee.late_half_year = fee.remaining_amount
				elif (as_at - fee.due_date).days >= 90:
					fee.late_quarter_year = fee.remaining_amount
				elif (as_at - fee.due_date).days >= 30:
					fee.late_month = fee.remaining_amount
				else:
					fee.late = fee.remaining_amount


			if request.POST.get('web_button') or not fees:
				return TemplateResponse(request, 'tax/cleaning_fee_debtors.html', { 'fees':fees, 'form':form, 'totals':totals, 'include_fields':include_fields })
			else: # csv
				return cleaning_audit_csv(fees, form.cleaned_data.get('include_fields'))

	else:
		form = DebtorsForm()

	return TemplateResponse(request, 'tax/cleaning_fee_debtors.html', { 'fees':None, 'form':form, })