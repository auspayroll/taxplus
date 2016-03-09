from .forms import CitizenForm, BusinessForm, UtilityForm, FeeForm, NewPaymentForm, \
	AccountUtilityForm, ContactForm, PaymentForm, form_for_model, \
	MediaForm, NewFeeCollectionForm, AccountNoteForm, CollectionForm, RegionForm, \
	NewLocationForm, LocationForm, AddUtilityRegionForm, \
	RegionalCollectionForm, AddAccountDates, UserForm, NewUserForm, CollectionUpdateForm, BankDepositForm, LoginForm
from crud.models import Account, Contact, AccountPayment, Media,\
	 AccountHolder, AccountFee, AccountNote, Utility, Collection
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test, user_passes_test
from django.contrib.auth.models import User, Group
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import Point
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.db.models import Q, Sum
from django.forms.models import modelformset_factory
from django.http import HttpResponse, Http404
from django.shortcuts import HttpResponseRedirect, render_to_response, get_object_or_404, redirect, render
from django.template.response import TemplateResponse
from djqscsv import render_to_csv_response
from random import randint
from taxplus.models import District, Sector, Cell, Village, Business, Citizen, Category, CategoryChoice, Property
import csv
import json
import collections



def collector_check(user):
    return (user.groups.filter(name__in=['Collector','collector', 'staff', 'Staff']) or user.is_staff or user.is_superuser)


def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse('index'))

def login(request):
	if request.method == 'POST':
		form = LoginForm(request.POST)
		if form.is_valid():
			username = request.POST['username']
			password = request.POST['password']
			user = authenticate(username=username, password=password)
			if user is not None:
				if user.is_active:
					auth_login(request, user)
					return HttpResponseRedirect(reverse('collector_index'))
				else:
					messages.error(request, "Account has been disabled")
			else:
				messages.error(request, "Invalid login")
	else:
		form = LoginForm()
	return render(request, 'admin/login.html', {'form':form})


@user_passes_test(collector_check)
def index(request):
	return collector_roster(request)


@user_passes_test(collector_check)
def account(request, pk):
	account = get_object_or_404(Account, pk=pk)
	return TemplateResponse(request, 'collector/account.html', {'account':account})


@user_passes_test(collector_check)
def account_contacts(request,pk):
	account = get_object_or_404(Account, pk=pk)
	contacts = Contact.objects.filter(account=account).order_by('-pk')
	return TemplateResponse(request, 'collector/contacts.html', {'account':account, 'contacts':contacts})


@user_passes_test(collector_check)
def new_contact(request, pk):
	account = get_object_or_404(Account, pk=pk)
	if request.method == 'POST':
		form= ContactForm(request.POST)
		if form.is_valid():
			contact = form.save(commit=False)
			contact.account = account
			contact.save()
			return HttpResponseRedirect(reverse('collector_account_contacts', args=[account.pk]))
	else:
		form = ContactForm()

	return TemplateResponse(request, 'collector/form.html', {'account':account, 'form':form, 'heading':'New Contact'})


@user_passes_test(collector_check)
def account_media(request,pk):
	account = get_object_or_404(Account, pk=pk)
	media = Media.objects.filter(account=account).order_by('-pk')
	return TemplateResponse(request, 'collector/media.html', {'account':account, 'media':media})


@user_passes_test(collector_check)
def new_media(request, pk):
	account = get_object_or_404(Account, pk=pk)
	if request.method == 'POST':
		form= MediaForm(request.POST, request.FILES)
		if form.is_valid():
			media = form.save(commit=False)
			media.account = account
			media.user = request.user
			media.save()
			messages.success(request, 'New Media created')
			return HttpResponseRedirect(reverse('collector_account_media', args=[account.pk]))
	else:
		form = MediaForm()

	return TemplateResponse(request, 'collector/mediaform.html', {'account':account, 'form':form, 'heading':'New Media'})


@user_passes_test(collector_check)
def new_fee_collection(request, pk):
	account = get_object_or_404(Account, pk=pk)
	if request.method == 'POST':
		form = CollectionForm(request.POST, request.FILES, account=account)
		form2 = BankDepositForm(request.POST)
		if form.is_valid() and form2.is_valid():
			payment = form.save(commit=False)
			payment.account = account
			payment.user = request.user
			payment.collector = request.user
			if form2.not_empty:
				deposit =  form2.save(commit=False)
				deposit.amount = payment.amount
				deposit.user = request.user
				deposit.save()
				messages.success(request, 'New Bank deposit created')
				payment.deposit = deposit
			payment.save()
			uploaded_file = form.cleaned_data.get('file_upload')
			if uploaded_file:
				Media.objects.create(account=account, user=request.user, item=uploaded_file, record=payment)
			messages.success(request, 'New Collection created')
			return HttpResponseRedirect(reverse('collector_fee_collections', args=[account.pk]))
	else:
		form = CollectionForm(account=account)
		form2 = BankDepositForm()

	return TemplateResponse(request, 'collector/form.html', {'account':account, 'form':form, 'form2':form2, 'heading':'New Collection', 'heading2':'Bank Details'})


@user_passes_test(collector_check)
def fee_collections(request,pk):
	account = get_object_or_404(Account, pk=pk)
	collections = Collection.objects.filter(account=account, collector=request.user).order_by('-pk')
	return TemplateResponse(request, 'collector/collections.html', {'account':account, 'collections':collections})


@user_passes_test(collector_check)
def account_holders(request,pk):
	account = get_object_or_404(Account, pk=pk)
	holders = AccountHolder.objects.filter(account=account).order_by('-pk')
	return TemplateResponse(request, 'collector/holders.html', {'account':account, 'holders':holders})


@user_passes_test(collector_check)
def new_account_note(request, pk):
	account = get_object_or_404(Account, pk=pk)
	if request.method == 'POST':
		form= AccountNoteForm(request.POST)
		if form.is_valid():
			note = form.save(commit=False)
			note.account=account
			note.user=request.user
			note.save()
			messages.success(request, 'New Account note created')
			return HttpResponseRedirect(reverse('collector_account_notes', args=[account.pk]))
	else:
		form = AccountNoteForm()

	return TemplateResponse(request, 'collector/form.html', {'account':account, 'form':form, 'heading':'New Account Note'})


@user_passes_test(collector_check)
def account_notes(request,pk):
	account = get_object_or_404(Account, pk=pk)
	notes = AccountNote.objects.filter(account=account).order_by('-pk')
	return TemplateResponse(request, 'collector/notes.html', {'account':account, 'notes':notes})



@user_passes_test(collector_check)
def districts(request):
	districts = District.objects.all().order_by('name')
	return TemplateResponse(request, 'collector/districts.html', {'districts':districts, })

@user_passes_test(collector_check)
def district(request, pk):
	district = get_object_or_404(District, pk=pk)
	sectors = Sector.objects.filter(district=district)
	return TemplateResponse(request, 'collector/district.html', {'district':district, 'sectors':sectors, })

@user_passes_test(collector_check)
def sector(request, pk):
	sector = get_object_or_404(Sector, pk=pk)
	recent_collections = Collection.objects.filter(utility__sector=sector, collector=request.user).order_by('-id')
	cells = Cell.objects.filter(sector=sector)
	return TemplateResponse(request, 'collector/sector.html', {'sector':sector, 'cells':cells, 'recent_collections':recent_collections})

@user_passes_test(collector_check)
def cell(request, pk):
	cell = get_object_or_404(Cell, pk=pk)
	villages = Village.objects.filter(cell=cell)
	return TemplateResponse(request, 'collector/cell.html', {'cell':cell, 'villages':villages})

@user_passes_test(collector_check)
def village(request, pk):
	village = get_object_or_404(Village, pk=pk)
	recent_collections = Collection.objects.filter(account__in=accounts, collector=equest.user).order_by('-id')[:100]
	return TemplateResponse(request, 'collector/village.html', {'village':village, 'accounts':accounts, 'recent_collections':recent_collections })


@user_passes_test(collector_check)
def recent_collections(request):
	recent_collections = Collection.objects.filter(collector=request.user, amount__gt=0).order_by('-id')[:100]
	return TemplateResponse(request, 'collector/recent_collections.html', {'recent_collections':recent_collections })




@user_passes_test(collector_check)
def edit_collection(request, pk):
	collection = get_object_or_404(Collection, pk=pk, collector=request.user)
	if request.method == 'POST':
		form= CollectionUpdateForm(request.POST, request.FILES, instance=collection)
		if collection.deposit:
			form2 = BankDepositForm(request.POST, instance=collection.deposit)
		else:
			form2 = BankDepositForm(request.POST)
		if form.is_valid() and form2.is_valid():
			collection = form.save(commit=False)
			if not collection.deposit and form2.not_empty: #create a new deposit
				deposit =  form2.save(commit=False)
				deposit.amount = collection.amount
				deposit.user = request.user
				deposit.save()
				messages.success(request, 'New Bank deposit created')
				collection.deposit = deposit

			elif collection.deposit and form2.not_empty:
				form2.save() # collection record and not empty, update as normal
				messages.success(request, 'New Bank deposit updated')
			elif collection.deposit and not form2.not_empty:
				pass # there is deposit record but the form is empty, should be invalid
			elif not collection.deposit and not form2.not_empty:
				pass # no deposit record, form is empty, do nothing

			collection.save()
			uploaded_file = form.cleaned_data.get('file_upload')
			if uploaded_file:
				Media.objects.create(account=collection.account, user=request.user, item=uploaded_file, record=collection)
			messages.success(request, 'Collection update')

			return HttpResponseRedirect(reverse('collector_fee_collections',args=[collection.account.pk]))
	else:
		form = CollectionUpdateForm(instance=collection)
		if collection.deposit:
			form2 = BankDepositForm(instance=collection.deposit)
		else:
			form2 = BankDepositForm()

	return TemplateResponse(request, 'collector/base_form.html', {'form':form, 'form2':form2, 'heading':'Edit Collection', 'heading2':'Banking Details' })


@user_passes_test(collector_check)
def collector_roster(request, blocks=0):
	try:
		blocks = int(blocks)
	except:
		raise Http404
	block_length = 14 # days
	#end_of_month = monthrange(date.today().year, date.today().month)[1]
	start_date = date.today() + timedelta(days=blocks*block_length)
	next_block = blocks + 1
	last_block = blocks - 1
	dates = [start_date + timedelta(days=i) for i in range(14)]
	collectionz = [ c for c in Collection.objects.filter(collector=request.user, date_from__lte=dates[-1], date_to__gte=dates[0])]
	date_dict = collections.OrderedDict()
	for d in dates:
		date_dict[d] = [ c for c in collectionz if c.date_to == d ]
	return TemplateResponse(request, 'collector/general_roster.html', {'dates':date_dict,
		 'next_block':next_block, 'last_block':last_block, 'heading':'General Roster'})








