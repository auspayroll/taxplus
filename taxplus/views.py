from django.template.response import TemplateResponse 
from django.shortcuts import HttpResponseRedirect
from jtax.models import PayFee
from property.models import District, Sector, Cell
from datetime import date
import json
from taxplus.forms import SearchForm
from django.db.models import Q, Sum






def cleaning_audit(request):
	user = request.session.get('user')
	if not user or not user.superuser:
		return HttpResponseRedirect('/')
	date_from = date(2000,1,1)
	date_to = date(2014,12,24)
	payments = PayFee.objects.none()
	totals = {}
	include_fields = []
	if request.method == 'POST':
		form = SearchForm(request.POST)
		if form.is_valid():
			include_fields = form.cleaned_data['include_fields']
			payments = PayFee.objects.filter(fee__fee_type='cleaning', fee__date_from__gte=form.cleaned_data['date_from'], fee__date_to__lte=form.cleaned_data['date_to']).select_related('fee', 'fee__business', 'staff').order_by('date_time')
			if form.cleaned_data['sector']:
				payments = payments.filter(Q(fee__business__sector=form.cleaned_data['sector'])| Q(fee__subbusiness__sector=form.cleaned_data['sector']))
			if form.cleaned_data['cell']:
				payments = payments.filter(Q(fee__business__cell=form.cleaned_data['cell']) | Q(fee__subbusiness__cell=form.cleaned_data['cell']))
			totals['payment'] = payments.aggregate(Sum('amount'))['amount__sum']
			totals['fee'] = payments.aggregate(Sum('fee__amount'))['fee__amount__sum']
			totals['remaining'] = payments.aggregate(Sum('fee__remaining_amount'))['fee__remaining_amount__sum']
			totals['fines'] = payments.aggregate(Sum('fine_amount'))['fine_amount__sum']
	else:
		form = SearchForm()
	return TemplateResponse(request, 'tax/cleaning_fee_audit.html', { 'payments':payments, 'form':form, 'include_fields':include_fields, 'totals':totals })
