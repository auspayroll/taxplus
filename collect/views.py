from taxplus.models import Sector
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
from collect.models import Epay, CollectionGroup, Collector, Epay, EpayBatch
from collect.forms import EpayForm, CollectionGroupForm, RegistrationForm, CollectorForm
import csv
import json
from random import randint
from django.contrib.auth.models import User
from django.core.mail import send_mail
from djqscsv import render_to_csv_response


def epay_batch_csv(request, pk):
  qs = Epay.objects.filter(batch__pk=pk).values('alt', 'batch__pk', 'batch__sector__name', 'batch__sector__code', 'batch__sector__district__name', 'collector__user__first_name', 'collector__user__last_name', 'collector__registration_no', 'collector__collection_group__name')
  return render_to_csv_response(qs, field_header_map={'alt':'epay', 'collector__user__first_name': 'collector_first_name', 'batch__sector__name':'sector', 'batch__sector__district__name':'district', 'batch__pk':'batch_no', 'batch__sector__code':'sector_code',
  	'collector__user__last_name':'collector_last_name', 'collector__registration_no':'collector_registration', 'collector__collection_group__name':'collector_group'})


def epay_batch(request, pk):
  batch = get_object_or_404(EpayBatch, pk=pk)
  epays = Epay.objects.filter(batch__pk=pk)
  return TemplateResponse(request, 'collect/epays.html', { 'epays':epays, 'group':batch.collection_group})


@login_required
def index(request):
	return TemplateResponse(request, 'collect/readme.html')

@login_required
def addEpay(request):
	if request.method == 'POST':
		epayform= EpayForm(request.POST)
		if epayform.is_valid():
			group = epayform.cleaned_data.get('collection_group')
			success = group.allocate_epays(epayform.cleaned_data.get('number'), sector=epayform.cleaned_data.get('sector'), user=request.user)
			if success:
				messages.success(request, '%s EPays generated' % epayform.cleaned_data.get('number'))
				return HttpResponseRedirect(reverse('groups'))
			else:
				messages.error(request,'Failed to add Epays')
	else:
		epayform = EpayForm()
	return TemplateResponse(request, 'collect/add_epay.html', { 'epayform':epayform,})



@login_required
def register(request):
	if request.method == 'POST':
		form= RegistrationForm(request.POST)
		if form.is_valid():
			email = form.cleaned_data['email']
			if email:
				username = email
			else:
				username = form.cleaned_data['first_name'][0]  + form.cleaned_data['last_name'][:5]  + str(randint(100, 999))
			username = username.lower()
			password = User.objects.make_random_password()
			user = User.objects.create_user(username, email=email, password=password, first_name=form.cleaned_data.get('first_name'), last_name=form.cleaned_data.get('last_name'))
			if user:
				messages.success(request, 'New User added. Username: %s, password: %s' % (username, password))
				collector = Collector.objects.create(user=user, collection_group=form.cleaned_data.get('collection_group'))

				if email:
					messages.success(request, 'Password emailed to %s' % email)
				else:
					messages.warning(request, 'No email sent. Write down this password:%s in a safe place:' % (password))
			else:
				message.error(request, 'Failed to create user')
			return HttpResponseRedirect(reverse('register'))
	else:
		form = RegistrationForm()
	return TemplateResponse(request, 'collect/register.html', { 'form':form,})


@login_required
def collector(request, pk):
	coll = get_object_or_404(Collector, pk=pk)
	user = coll.user
	if request.method == 'POST':
		form = CollectorForm(request.POST, instance=coll)
		if form.data.get('submit') == 'Reset Password':
			password = User.objects.make_random_password()
			user.set_password(password)
			user.save()
			messages.success(request, 'Password has been reset to %s' % password)
			return HttpResponseRedirect(reverse('collector', args=[coll.pk]))
		else:
			if form.is_valid():
				user.first_name = form.cleaned_data.get('first_name')
				user.last_name = form.cleaned_data.get('last_name')
				user.is_active = form.cleaned_data.get('active')
				user.save()
				form.save()
				messages.success(request, 'User updated')
				return HttpResponseRedirect(reverse('collector', args=[coll.pk]))
	else:
		form = CollectorForm(instance=coll, initial={'first_name':user.first_name, 'last_name':user.last_name, 'active':user.is_active})
	return TemplateResponse(request, 'collect/collector.html', { 'form':form, 'collector':coll})


@login_required
def groups(request):
	groups = CollectionGroup.objects.all()
	return TemplateResponse(request, 'collect/groups.html', { 'groups':groups,})


@login_required
def collectors(request, pk):
	group = get_object_or_404(CollectionGroup, pk=pk)
	collectors = Collector.objects.filter(collection_group=group)
	return TemplateResponse(request, 'collect/collectors.html', { 'group': group, 'collectors':collectors,})


@login_required
def logs(request):
	logs = EpayBatch.objects.all().order_by('-created')
	return TemplateResponse(request, 'collect/logs.html', { 'logs':logs,})

@login_required
def group_epays(request, pk, status=0):
	group = get_object_or_404(CollectionGroup, pk=pk)
	epays = Epay.objects.filter(collector__collection_group=group)
	if status == 1:
		epays = epays.filter(used=True)
	elif status ==2:
		epays = epays.filter(used=False)
	epays = epays.order_by('-pk')
	return TemplateResponse(request, 'collect/epays.html', { 'group': group, 'epays':epays,})

@login_required
def addCollectionGroup(request):
	if request.method == 'POST':
		form= CollectionGroupForm(request.POST)
		if form.is_valid():
			form.save()
			messages.success(request, 'Collection Group saved')
			return HttpResponseRedirect(reverse('groups'))
	else:
		form = CollectionGroupForm()
	return TemplateResponse(request, 'collect/add_collection_group.html', { 'form':form,})


@login_required
def editGroup(request, pk):
	group = get_object_or_404(CollectionGroup, pk=pk)
	if request.method == 'POST':
		form= CollectionGroupForm(request.POST, instance=group)
		if form.is_valid():
			form.save()
			messages.success(request, 'Collection Group created')
			return HttpResponseRedirect(reverse('add_collection_group'))
	else:
		form = CollectionGroupForm(instance=group)
	return TemplateResponse(request, 'collect/add_collection_group.html', { 'form':form,})
