from property.models import District, Sector, Cell
from datetime import date
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.db.models import Q, Sum
from django.forms.models import modelformset_factory
from django.http import HttpResponse, Http404
from django.shortcuts import HttpResponseRedirect, render_to_response, get_object_or_404, redirect
from django.template.response import TemplateResponse
from collect.models import Epay
from collect.forms import EpayForm
import csv
import json



def register_collector(request):
	pass


def register_collection_group(request):
	pass

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
def addEpay(request):
	if request.method == 'POST':
		epayform= EpayForm(request.POST)
		if epayform.is_valid():
			user = PMUser.objects.get(pk=request.session.get('user').pk)
			Log.objects.create(user = user, message='Epays added')
			epayform.save()
			messages.success(request, 'Land leases updated')
			return HttpResponseRedirect(reverse('add_pay', args=[prop.pk]))
	else:
		epayform = EpayForm()
	return TemplateResponse(request, 'collect/add_epay.html', { 'epayform':epayform,})
