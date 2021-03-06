from collect.forms import EpayForm, CollectionGroupForm, RegistrationForm, CollectorForm, BusinessForm
from crud.forms import CitizenForm, BusinessForm, UtilityForm, FeeForm, NewPaymentForm, \
	AccountUtilityForm, ContactForm, PaymentForm, form_for_model, \
	MediaForm, NewFeeCollectionForm, AccountNoteForm, CollectionForm, RegionForm, \
	NewLocationForm, LocationForm, \
	RegionalCollectionForm, AddAccountDates, UserForm, NewUserForm, CollectionUpdateForm,\
	BankDepositForm, LoginForm, NewAccountHolderForm, DistrictForm, SectorForm,\
	CellForm, VillageForm, RateForm, AccountForm, RegionReportForm, SearchForm, MakePaymentForm, ReceiptBookForm, NewAccountForm
from crud.models import Account, Contact, AccountPayment, Media,\
	 AccountHolder, AccountFee, AccountNote, Utility, Collection, Profile,\
	  Log, BankDeposit, CurrentOutstanding, ReceiptBook, Business, split_upi
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from calendar import monthrange
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
from djqscsv import render_to_csv_response, generate_filename
from random import randint
from taxplus.models import District, Sector, Cell, Village, Citizen, Category, CategoryChoice, Property, Rate
import csv
import json
import collections
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from PIL import Image
import PIL
import os
from django.db import IntegrityError
import zipfile
import djqscsv
from StringIO import StringIO
import json
from django.core import serializers





def admin_check(user):
    return (user.groups.filter(name__in=['staff', 'Staff']) or user.is_superuser)


def logout(request):
    auth_logout(request)
    return HttpResponseRedirect(reverse('index'))

def login(request):
	if request.method == 'POST':
		form = LoginForm(request.POST)
		if form.is_valid():
			username = request.POST.get('username')
			password = request.POST.get('password')
			user = authenticate(username=username, password=password)
			if user is not None:
				if user.is_active:
					auth_login(request, user)
					next = request.GET.get('next')
					if next:
						return HttpResponseRedirect(next)
					if user.groups.filter(name='Staff') or user.is_superuser:
						return HttpResponseRedirect(reverse('index'))
					elif user.groups.filter(name='Collector').exists():
						return HttpResponseRedirect(reverse('collector_index'))
					else:
						messages.error(request, "Invalid Permission")
				else:
					messages.error(request, "Account has been disabled")
			else:
				messages.error(request, "Invalid login")
	else:
		form = LoginForm()
	return render(request, 'admin/login.html', {'form':form})


@user_passes_test(admin_check)
def index(request):
	return general_roster(request)


@user_passes_test(admin_check)
def select_fees(request):
	return TemplateResponse(request, 'crud/select_fees.html')



@user_passes_test(admin_check)
def select_account_holder(request, pk):
	fee_type = get_object_or_404(ContentType, pk=pk)
	request.session['fee_type'] = {'id':id, 'name':fee_type.name}
	return TemplateResponse(request, 'crud/select_fees.html')



@user_passes_test(admin_check)
def new_citizen_account(request):
	if request.method == 'POST':
		form= CitizenForm(request.POST)
		if form.is_valid():
			duplicate = form.cleaned_data.get('duplicate')
			if duplicate:
				form = CitizenForm(request.POST, instance=duplicate)
				if form.is_valid():
					citizen = form.save()
				else:
					return TemplateResponse(request, 'crud/base_form.html', {'form':form, 'heading':'New Citizen Account'})
			else:
				citizen = form.save()

			#create an account
			account = Account.objects.create(start_date=form.cleaned_data.get('start_date'), name=citizen.name)
			AccountHolder.objects.create(account=account, holder=citizen)
			messages.success(request, 'New Citizen Account created')
			return HttpResponseRedirect(reverse('add_account_utility', args=[account.pk]))
	else:
		form = CitizenForm()

	return TemplateResponse(request, 'crud/base_form.html', {'form':form, 'heading':'New Citizen Account'})


@user_passes_test(admin_check)
def new_business_account(request):
	if request.method == 'POST':
		form= BusinessForm(request.POST)
		if form.is_valid():
			duplicate = form.cleaned_data.get('duplicate')
			if duplicate:
				form = BusinessForm(request.POST, instance=duplicate)
				if form.is_valid():
					business = form.save(commit=False)
				else:
					return TemplateResponse(request, 'crud/base_form.html', {'form':form, 'heading':'New Business Account'})
			else:
				business = form.save(commit=False)
				business.vat_register = False
				business.market_fee_applicable = False
			lat = form.cleaned_data.get('lat')
			lon = form.cleaned_data.get('lon')
			if lat and lon:
				business.location = Point(lat, lon)
			business.save()
			#create an account
			account = Account.objects.create(start_date=form.cleaned_data.get('date_started'), name=business.name)
			AccountHolder.objects.create(account=account, holder=business)
			messages.success(request, 'New Business Account created')
			return HttpResponseRedirect(reverse('add_account_utility', args=[account.pk]))
	else:
		form = BusinessForm()

	return TemplateResponse(request, 'crud/base_form.html', {'form':form, 'heading':'New Business Account'})


@user_passes_test(admin_check)
def account(request, pk):
	account = get_object_or_404(Account, pk=pk)
	return TemplateResponse(request, 'crud/account.html', {'account':account})

@user_passes_test(admin_check)
def new_account_fee(request, pk):
	account = get_object_or_404(Account, pk=pk)
	if request.method == 'POST':
		form= FeeForm(request.POST, account=account)
		if form.is_valid():
			account_fee = form.save(commit=False)
			account_fee.account = account
			account_fee.user = request.user
			account_fee.save()
			messages.success(request, 'New Fee Created')
			return HttpResponseRedirect(reverse('account_fees', args=[pk]))
	else:
		form = FeeForm(account=account)

	return TemplateResponse(request, 'crud/new_fee_account.html', {'account':account, 'form':form})


@user_passes_test(admin_check)
def new_account_utility(request, pk):
	account = get_object_or_404(Account, pk=pk)
	if request.method == "POST":
		form= NewFeeForm(request.POST)
		if form.is_valid():
			utility_form_class = form_for_model(form.cleaned_data.get('fee_type').code)
			form = utility_form_class(request.POST, auto=form.cleaned_data.get('auto'),district=form.cleaned_data.get('district'))
			if form.is_valid():
				fee = form.save(commit=False, user=request.user, account=account)
				fee.account = account
				fee.user = request.user
				fee.save()
				messages.success(request, 'New Fee Created')
				return HttpResponseRedirect(reverse('account_fees', args=[pk]))
	else:
		form = NewFeeForm()
		return TemplateResponse(request, 'crud/new_fee_account.html', {'account':account, 'form':form})

	return TemplateResponse(request, 'crud/new_account_utility.html', {'account':account, 'form':form})


@user_passes_test(admin_check)
def new_account_payment(request, pk):
	account = get_object_or_404(Account, pk=pk)
	if request.method == 'POST':
		form= NewPaymentForm(request.POST)
		if form.is_valid():
			messages.success(request, 'New Payment Created')
			return HttpResponseRedirect(reverse('account', args=[pk]))
	else:
		form = NewPaymentForm()

	return TemplateResponse(request, 'crud/new_fee_account.html', {'account':account, 'form':form})

@user_passes_test(admin_check)
def recent_accounts(request):
	accounts = Account.objects.all().order_by('-pk')[:50]
	return TemplateResponse(request, 'crud/accounts.html', {'accounts':accounts})


@user_passes_test(admin_check)
def recent_utilities(request, utility_type):
	utilities = Utility.objects.filter(utility_type__code=utility_type).order_by('-pk')[:50]

	return TemplateResponse(request, 'crud/recent_utilities.html', {'utilities':utilities})


@user_passes_test(admin_check)
def account_fees(request,pk):
	account = get_object_or_404(Account, pk=pk)
	fees = AccountFee.objects.filter(account=account).order_by('-pk')
	return TemplateResponse(request, 'crud/fees.html', {'account':account, 'fees':fees})


@user_passes_test(admin_check)
def update_account(request, pk):
	if request.method == 'POST':
		form= BusinessForm(request.POST)
		if form.is_valid():
			business = form.save(commit=False)
			account = Account.objects.create(holder=business, name=business.name)
			messages.success(request, 'New Business Account created')
	else:
		form = BusinessForm()

	return TemplateResponse(request, 'crud/new_account.html', {'form':form})


@user_passes_test(admin_check)
def account_select(request):
	return TemplateResponse(request, 'crud/account_select.html', {})


@user_passes_test(admin_check)
def new_location(request):
	if request.method == 'POST':
		form = NewLocationForm(request.POST)
		if form.is_valid():
				current_accounts = Account.objects.filter(utilities__village=form.cleaned_data.get('village'), utilities__utility_type=form.cleaned_data.get('utility_type'))
				initial_data = form.cleaned_data
				initial_data['name'] = "%s %s" % (initial_data.get('village'), initial_data.get('utility_type'))
				form = LocationForm(initial=initial_data)
				return TemplateResponse(request, 'crud/new_location.html', {'form':form, 'heading':'Add a new %s location in %s village' % ( initial_data.get('utility_type'), initial_data.get('village')), 'current_accounts':current_accounts})
	else:
		form = NewLocationForm()
	return TemplateResponse(request, 'crud/base_form.html', {'form':form, 'heading':'Add a new Account' })


@user_passes_test(admin_check)
def new_location_post(request):
	"""
	add a new location
	"""
	if request.method == 'POST':
		form = LocationForm(request.POST)
		if form.is_valid():
			utility = form.save()
			account = Account(start_date=form.cleaned_data.get('start_date'), name=form.cleaned_data.get('name'))
			account.save()
			account.utilities.add(utility)
			messages.success(request, 'New Account created')
			return HttpResponseRedirect(reverse('account', args=[account.pk]))
	else:
		return HttpResponseRedirect(reverse('new_location'))
	return TemplateResponse(request, 'crud/new_location.html', {'form':form, 'heading':'Add a new %s in %s village' % (form.cleaned_data.get('utility_type'), form.cleaned_data.get('village'))})


@user_passes_test(admin_check)
def account_contacts(request,pk):
	account = get_object_or_404(Account, pk=pk)
	contacts = Contact.objects.filter(account=account).order_by('-pk')

	return TemplateResponse(request, 'crud/contacts.html', {'account':account, 'contacts':contacts})


@user_passes_test(admin_check)
def new_contact(request, pk):
	account = get_object_or_404(Account, pk=pk)
	if request.method == 'POST':
		form= ContactForm(request.POST)
		if form.is_valid():
			contact = form.save(commit=False)
			contact.account = account
			contact.save()
			return HttpResponseRedirect(reverse('account_contacts', args=[account.pk]))
	else:
		form = ContactForm()

	return TemplateResponse(request, 'crud/form.html', {'account':account, 'form':form, 'heading':'New Contact'})


@user_passes_test(admin_check)
def account_payments(request,pk):
	account = get_object_or_404(Account, pk=pk)
	payments = BankDeposit.objects.filter(account=account).order_by('-pk')

	return TemplateResponse(request, 'crud/payments.html', {'account':account, 'payments':payments})



@user_passes_test(admin_check)
def new_payment(request, pk):
	account = get_object_or_404(Account,pk=pk)
	searchform = SearchForm()
	if request.method == 'POST':
		form = MakePaymentForm(request.POST)
		if form.is_valid():
			fee_type = form.cleaned_data.get('fee_type')
			current_fees = AccountFee.objects.filter(fee_type=fee_type, account=account, closed__isnull=True)
			if not current_fees:
				messages.warning(request, "Warning: There is no active %s for this account" % fee_type)
			bank_deposit = form.save(commit=False)
			bank_deposit.account = account
			bank_deposit.user = request.user
			bank_deposit.save()
			messages.success(request, "Payment created successfully")
			return HttpResponseRedirect(reverse('account_payments', args=[pk]))

	else:
		form = MakePaymentForm()

	return TemplateResponse(request, 'crud/new_payment.html', {'account':account, 'form':form})


"""
@user_passes_test(admin_check)
def new_payment(request, pk):
	account = get_object_or_404(Account, pk=pk)
	collections = Collection.objects.filter(account=account, deposit__isnull=True)
	if request.method == 'POST':
		collection_ids = request.POST.getlist('collection_id')
		collection_instances = Collection.objects.filter(pk__in=collection_ids)
		form= BankDepositForm(request.POST)
		if form.is_valid():
			payment = form.save(commit=False)
			payment.account = account
			payment.user = request.user
			payment.save()
			if collection_instances:
				collection_instances.update(deposit=payment)
				payment.amount = reduce(lambda x,y:x+y, [c.amount for c in collection_instances])
				payment.save()
				if account.period_ending and payment.date_banked > account.period_ending or not account.period_ending:
					account.transactions(update=True, period_ending=payment.date_banked)
				else:
					account.transactions(update=True)
			messages.success(request, 'New Payment created')
			return HttpResponseRedirect(reverse('account_transactions', args=[account.pk]))
	else:
		form = BankDepositForm()

	return TemplateResponse(request, 'crud/new_payment.html', {'account':account, 'form':form, 'heading':'New Account Payment'})
"""


@user_passes_test(admin_check)
def account_media(request,pk):
	account = get_object_or_404(Account, pk=pk)
	media = [media for media in Media.objects.filter(account=account).order_by('-pk') if os.path.isfile(media.item.path)]
	return TemplateResponse(request, 'crud/media.html', {'account':account, 'media':media})


@user_passes_test(admin_check)
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
			return HttpResponseRedirect(reverse('account_media', args=[account.pk]))
	else:
		form = MediaForm()

	return TemplateResponse(request, 'crud/mediaform.html', {'account':account, 'form':form, 'heading':'New Media'})


@user_passes_test(admin_check)
def new_fee_collection(request, pk):
	account = get_object_or_404(Account, pk=pk)
	if request.method == 'POST':
		form = CollectionForm(request.POST, request.FILES, account=account)
		if form.is_valid():
			payment = form.save(commit=False)
			payment.account = account
			payment.user = request.user
			payment.collector = request.user
			payment.save()
			uploaded_file = form.cleaned_data.get('file_upload')
			if uploaded_file:
				Media.objects.create(account=account, user=request.user, item=uploaded_file, record=payment)
			messages.success(request, 'New Collection created')
			return HttpResponseRedirect(reverse('new_payment', args=[account.pk]))
	else:
		form = CollectionForm(account=account)

	return TemplateResponse(request, 'crud/form.html', {'account':account, 'form':form, 'heading':'New Collection', 'heading2':'Bank Details'})


@user_passes_test(admin_check)
def fee_collections(request,pk):
	account = get_object_or_404(Account, pk=pk)
	collections = Collection.objects.filter(account=account).order_by('-pk')
	return TemplateResponse(request, 'crud/collections.html', {'account':account, 'collections':collections})


@user_passes_test(admin_check)
def account_holders(request,pk):
	account = get_object_or_404(Account, pk=pk)
	holders = AccountHolder.objects.filter(account=account).order_by('-pk')
	if request.method == 'POST':
		form = NewAccountHolder(request.POST)
		if form.is_valid():
			pass
	else:
		form = NewAccountHolderForm()
	return TemplateResponse(request, 'crud/holders.html', {'account':account, 'holders':holders, 'form':form})


@user_passes_test(admin_check)
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
			return HttpResponseRedirect(reverse('account_notes', args=[account.pk]))
	else:
		form = AccountNoteForm()

	return TemplateResponse(request, 'crud/form.html', {'account':account, 'form':form, 'heading':'New Account Note'})


@user_passes_test(admin_check)
def account_notes(request,pk):
	account = get_object_or_404(Account, pk=pk)
	notes = AccountNote.objects.filter(account=account).order_by('-pk')
	return TemplateResponse(request, 'crud/notes.html', {'account':account, 'notes':notes})


@user_passes_test(admin_check)
def add_account_utility(request, pk):
	account = get_object_or_404(Account, pk=pk)
	if request.method == 'POST':
		form= AccountUtilityForm(request.POST)
		if form.is_valid():
			if form.cleaned_data.get('utility_type') == 'property':
				utility, created = Property.objects.get_or_create(upi=form.cleaned_data.get('identifier') )
			else:
				utility, created = Utility.objects.get_or_create(utility_type=form.cleaned_data.get('utility_type'), identifier=form.cleaned_data.get('identifier'))
			account.utility = utility
			account.save()
			messages.success(request, 'New utility added')
			return HttpResponseRedirect(reverse('account_fees', args=[account.pk]))
	else:
		form = AccountUtilityForm()

	return TemplateResponse(request, 'crud/form.html', {'account':account, 'form':form, 'heading':'Add Utility/Site'})


@user_passes_test(admin_check)
def update_utility(request, pk):
	utility = get_object_or_404(Utility, pk=pk)
	if request.method == 'POST':
		form= UtilityForm(request.POST, instance=utility)
		if form.is_valid():
			form.save()
			messages.success(request, 'Utility updated')
			return HttpResponseRedirect(reverse('utilities_type',args=[utility.utility_type.code]))
	else:
		form = UtilityForm(instance=utility)

	return TemplateResponse(request, 'crud/update_utility.html', {'account':account, 'form':form, 'heading':'Update Utility/Site'})


@user_passes_test(admin_check)
def utilities(request, utility_type=None):
	if request.method == 'POST':
		form= UtilityForm(request.POST)
		if form.is_valid():
			utility = form.save()
			messages.success(request, 'New utility added')
			return HttpResponseRedirect(reverse('utilities_type',args=[utility.utility_type.code]))
	else:
		form = UtilityForm()

	if utility_type:
		utilities = Utility.objects.filter(utility_type__code=utility_type).order_by('-pk')
	else:
		utilities = Utility.objects.all().order_by('-pk')[:50]

	return TemplateResponse(request, 'crud/add_utility.html', {'form':form, 'heading':'Add Utility/Site', })


@user_passes_test(admin_check)
def districts(request):
	districts = District.objects.all().order_by('name')
	return TemplateResponse(request, 'crud/districts.html', {'districts':districts, })

@user_passes_test(admin_check)
def district(request, pk):
	district = get_object_or_404(District, pk=pk)
	sectors = Sector.objects.filter(district=district)
	return TemplateResponse(request, 'crud/district.html', {'district':district, 'sectors':sectors, })

@user_passes_test(admin_check)
def sector(request, pk):
	sector = get_object_or_404(Sector, pk=pk)
	recent_collections = Collection.objects.filter(utility__sector=sector).order_by('-id')
	cells = Cell.objects.filter(sector=sector)
	return TemplateResponse(request, 'crud/sector.html', {'sector':sector, 'cells':cells, 'recent_collections':recent_collections})

@user_passes_test(admin_check)
def cell(request, pk):
	cell = get_object_or_404(Cell, pk=pk)
	villages = Village.objects.filter(cell=cell)
	return TemplateResponse(request, 'crud/cell.html', {'cell':cell, 'villages':villages})

@user_passes_test(admin_check)
def village(request, pk):
	village = get_object_or_404(Village, pk=pk)
	accounts = Account.objects.filter(Q(utilities__village=village) | Q(account_fees__prop__village=village)).prefetch_related('account_fees').order_by('-id')
	recent_collections = Collection.objects.filter(account__in=accounts).order_by('-id')[:100]
	return TemplateResponse(request, 'crud/village.html', {'village':village, 'accounts':accounts, 'recent_collections':recent_collections })


@user_passes_test(admin_check)
def recent_collections(request):
	recent_collections = Collection.objects.filter(amount__gt=0).order_by('-id')[:100]
	return TemplateResponse(request, 'crud/recent_collections.html', {'recent_collections':recent_collections })

@user_passes_test(admin_check)
def add_village_utility(request, pk):
	village = get_object_or_404(Village, pk=pk)
	form = NewLocationForm(initial={'village':village, 'cell':village.cell, 'sector':village.cell.sector, 'district':village.cell.sector.district})
	return TemplateResponse(request, 'crud/base_form.html', {'form':form, 'heading':'Add a new Account' })



@user_passes_test(admin_check)
def sector_collection(request, pk):
	sector = get_object_or_404(Sector, pk=pk)
	recent_collections = Collection.objects.filter(utility__sector=sector).order_by('-id')
	utility_type, created = CategoryChoice.objects.get_or_create(category__code='utility_type', code='sector', defaults=dict(category=Category.objects.get(code='utility_type')))
	utility, updated = Utility.objects.update_or_create(sector=sector, cell=None, village=None, utility_type=utility_type,
		defaults=dict(district=sector.district, sector=sector, identifier=sector.code))

	if created:
		account = Account(start_date=date.today(), name=utility)
		account.save()
		account.utilities.add(utility)
	else:
		accounts = Account.objects.filter(utilities=utility)
		if accounts:
			account = accounts[0]
		else:
			account = Account(start_date=date.today(), name=utility)
			account.save()
			account.utilities.add(utility)

	if request.method == 'POST':
		form = RegionalCollectionForm(request.POST)
		if form.is_valid():
			collection = form.save(commit=False)
			collection.account = account
			collection.utility = utility
			collection.user = request.user
			collection.save()
			messages.success(request, 'New collection added')
			return HttpResponseRedirect(reverse('sector_collection',args=[sector.pk]))
	else:
		form = RegionalCollectionForm()

	return TemplateResponse(request, 'crud/sector.html', {'sector':sector, 'form':form, 'recent_collections':recent_collections})


@user_passes_test(admin_check)
def edit_collection(request, pk):
	collection = get_object_or_404(Collection, pk=pk)
	account = collection.account
	if request.method == 'POST':
		form= CollectionUpdateForm(request.POST, request.FILES, instance=collection, initial={'next':request.GET.get('next')})
		if form.is_valid():
			collection = form.save(commit=False)
			uploaded_file = form.cleaned_data.get('file_upload')
			if uploaded_file:
				Media.objects.create(account=collection.account, user=request.user, item=uploaded_file, record=collection)
			messages.success(request, 'Collection update')
			next = form.cleaned_data.get('next')
			if next:
				return HttpResponseRedirect(next)
			else:
				return HttpResponseRedirect(reverse('fee_collections',args=[collection.account.pk]))
	else:
		form = CollectionUpdateForm(instance=collection, initial={'next':request.GET.get('next')})

	return TemplateResponse(request, 'crud/form.html', {'account':account, 'form':form, 'heading':'Edit Collection', 'heading2':'Banking Details' })

@user_passes_test(admin_check)
def add_account_dates(request, pk):
	account = get_object_or_404(Account, pk=pk)
	if request.method == 'POST':
		form = AddAccountDates(request.POST, account=account)
		if form.is_valid():
			collections = {}
			collector = form.cleaned_data.get('collector')
			fee_type = form.cleaned_data.get('fee_type')
			utility = form.cleaned_data.get('utility')
			dates = form.cleaned_data.get('dates')
			cycle = form.cleaned_data.get('cycle')
			for d in dates:
				collection = Collection.objects.create(account=account, date_from=d, date_to=d,
						collector=collector, user=request.user, no_collections=0, fee_type=fee_type, utility=utility)

			messages.success(request, '%d new collections created' % len(dates))
			return HttpResponseRedirect(reverse('fee_collections', args=[account.pk]))

	else:
		form = AddAccountDates(account=account)
	return TemplateResponse(request, 'crud/add_account_dates.html', {'account':account, 'form':form})


@user_passes_test(admin_check)
def users(request):
	users = User.objects.all().order_by('-is_active', 'first_name', '-id')
	return TemplateResponse(request, 'crud/users.html', {'users':users})



def user_list_json(request, pk=None):
    pay_load = {}
    users = User.objects.all()
    start = int(request.GET.get("start", 0))
    length = int(request.GET.get("length", 25))

    totalUsers = users.count()
    search = request.GET.get('search[value]')
    if search:
        users = users.filter(Q(username__icontains=search) | Q(email__icontains=search))
        pay_load['recordsTotal'] = pay_load['recordsFiltered'] = users.count()
    else:
        pay_load['recordsTotal'] = pay_load['recordsFiltered'] = totalUsers


    pay_load["draw"] = request.GET.get('draw')
    pay_load["data"] = [dict(i) for i in users.values('id', 'username', 'first_name', 'last_name')[start:(start+length)]]
    for user in pay_load['data']:
    	user['edit_link'] = "<a href=\"%s\">Edit</a>" % reverse('edit_user', args = (user['id'],))
    pay_load = json.dumps(pay_load)
    return HttpResponse(pay_load, content_type="application/json")


def log_list_json(request, pk=None):
    pay_load = {}
    logs = Log.objects.all()
    if pk:
        user = get_object_or_404(User, pk=pk)
        logs = logs.filter(user=user)

    start = int(request.GET.get("start", 0))
    length = int(request.GET.get("length", 25))

    totalLogs = logs.count()
    search = request.GET.get('search[value]')
    if search:
        logs = logs.filter(Q(username__icontains=search) | Q(email__icontains=search))
        pay_load['recordsTotal'] = pay_load['recordsFiltered'] = users.count()
    else:
        pay_load['recordsTotal'] = pay_load['recordsFiltered'] = totalLogs

    logs = logs.order_by('-id')

    pay_load["draw"] = request.GET.get('draw')
    pay_load["data"] = []
    for log in logs[start:(start+length)]:
    	data = {}
    	data["id"] = log.pk
    	data["user"] = '<a href="%s">%s</a>' % (reverse('edit_user',args=[log.user.pk,]),log.user.username)
    	data['time'] = log.created.strftime('%I:%M %p')
    	data['created'] = log.created.strftime('%d-%m-%Y')
    	data['request_ip'] = log.request_ip or '-'
    	if log.account:
    		data['account'] = '<a href="%s">%s : %s</a>' % (reverse('account',args=[log.account.pk]), log.account.pk, log.account.name )
    	else:
    		data['account'] = '-'
    	if log.instance:
    		data['instance'] = "%s : %s " % (ContentType.objects.get_for_model(log.instance), log.instance)
    	else:
    		data['instance'] = ''
    	changes_as_html = log.changes_as_html
    	if 'Logged in' in changes_as_html:
    		data['changes'] = changes_as_html
    	else:
    		data['changes'] = "<a href=\"\"  class=\"show_changes btn btn-default\">View</a> <div style=\"display:none;\" class=\"changes\">"+changes_as_html+"</div>"
    	pay_load["data"].append(data)

    pay_load = json.dumps(pay_load)
    return HttpResponse(pay_load, content_type="application/json")


@user_passes_test(admin_check)
def register_user(request):
	if request.method == 'POST':
		form = NewUserForm(request.POST, request.FILES)
		if form.is_valid():
			email = form.cleaned_data.get('email')
			password = form.cleaned_data.get('password')
			username = form.cleaned_data.get('username')
			user = User.objects.create_user(username, email, password)
			user.last_name = form.cleaned_data.get('last_name')
			user.first_name = form.cleaned_data.get('first_name')
			user.is_active = form.cleaned_data.get('is_active')
			user.save()
			Profile.objects.create(user=user, registration_no=form.cleaned_data.get('registration_no'), phone=form.cleaned_data.get('phone'), photo=form.cleaned_data.get('photo'))
			groups = form.cleaned_data.get('groups')
			for g in groups:
				user.groups.add(g)
			messages.success(request, 'New user created. Username: %s , Password: %s . Please record this in a safe place.' % (user.username, password))
			return HttpResponseRedirect(reverse('register_user'))

	else:
		form = NewUserForm()
	return TemplateResponse(request, 'crud/user_form.html', {'form':form, 'heading':'Register New User'})


@user_passes_test(admin_check)
def edit_user(request, pk):
	user = get_object_or_404(User, pk=pk)
	if request.method == 'POST':
		form = UserForm(request.POST, request.FILES, instance=user)
		if form.is_valid():
			try:
				user = form.save()
			except IntegrityError:
				messages.error(request, 'Username %s already exists' % form.cleaned_data.get('username'))
			else:
				if hasattr(user,'profile'):
					user.profile.registration_no = form.cleaned_data.get('registration_no')
					user.profile.phone = form.cleaned_data.get('phone')
					user.profile.save()
					profile = user.profile
				else:
					profile = Profile.objects.create(user=user, registration_no = form.cleaned_data.get('registration_no'), phone=form.cleaned_data.get('phone'))

				if form.cleaned_data.get('photo'):
					profile.photo = form.cleaned_data.get('photo')
					profile.save()
					#im=Image.open(profile.photo.path)
					#im.thumbnail([320,320], Image.ANTIALIAS)
					#im.save(profile.photo.path, quality=100)

				if form.cleaned_data.get('reset_password'):
					raw_password = form.cleaned_data.get('raw_password')
					user.set_password(raw_password)
					user.save()
					messages.success(request, 'User password reset to %s . Please record this in a safe place.' % raw_password)

				messages.success(request, 'User updated')
				return HttpResponseRedirect(reverse('users'))
	else:
		form = UserForm(instance=user)
	return TemplateResponse(request, 'crud/user_form.html', {'form':form, 'heading':'Update User %s' % user.username})


@user_passes_test(admin_check)
def edit_location(request, pk):
	location = get_object_or_404(Utility, pk=pk)
	if request.method == 'POST':
		form = UtilityForm(request.POST, instance=location)
		if form.is_valid():
			form.save()
			messages.success(request, 'Location/Site updated')
			return HttpResponseRedirect(reverse('edit_location', args=[pk]))
	else:
		form = UtilityForm(instance=location)
	return TemplateResponse(request, 'crud/base_form.html', {'form':form, 'heading':'Update Location/Site', 'instance':location})


@user_passes_test(admin_check)
def recent_locations(request):
	locations = Utility.objects.exclude(utility_type__code__in=['sector', 'district', 'cell', 'village']).order_by('-id')[:100]
	return TemplateResponse(request, 'crud/locations.html', {'locations':locations})


@user_passes_test(admin_check)
def district_roster(request, pk, blocks=0):
	try:
		blocks = int(blocks)
	except:
		raise Http404
	block_length = 14 # days
	district = get_object_or_404(District, pk=pk)
	#end_of_month = monthrange(date.today().year, date.today().month)[1]
	start_date = date.today() + timedelta(days=blocks*block_length)
	next_block = blocks + 1
	last_block = blocks - 1
	dates = [start_date + timedelta(days=i) for i in range(14)]
	collectionz = [ c for c in Collection.objects.filter(date_from__lte=dates[-1], date_to__gte=dates[0]).filter(Q(utility__sector__district=district) | Q(utility__village__cell__sector__district=district) | Q(utility__cell__sector__district=district))]
	date_dict = collections.OrderedDict()
	for d in dates:
		date_dict[d] = [ c for c in collectionz if c.date_to == d ]
	return TemplateResponse(request, 'crud/roster.html', {'dates':date_dict,
		'district':district, 'next_block':next_block, 'last_block':last_block, 'heading':'%s district roster' % district})


@user_passes_test(admin_check)
def general_roster(request, blocks=0):
	districts = District.objects.all().order_by('name')
	return TemplateResponse(request, 'crud/general_roster.html', {'districts':districts, 'heading':'General Roster'})


@user_passes_test(admin_check)
def district_update(request, pk):
	district = get_object_or_404(District, pk=pk)
	if request.method == 'POST':
		form = DistrictForm(request.POST, instance=district)
		if form.is_valid():
			form.save()
			messages.success(request,'District has been updated')
			return HttpResponseRedirect(reverse('district', args=[district.pk]))
	else:
		form = DistrictForm(instance=district)
	return render(request, 'crud/district_update.html', {'form':form, 'district':district})


@user_passes_test(admin_check)
def sector_update(request, pk):
	sector = get_object_or_404(Sector, pk=pk)
	if request.method == 'POST':
		form = SectorForm(request.POST, instance=sector)
		if form.is_valid():
			form.save()
			messages.success(request,'Sector has been updated')
			return HttpResponseRedirect(reverse('sector', args=[sectors.pk]))
	else:
		form = SectorForm(instance=sector)
	return render(request, 'crud/sector_update.html', {'form':form, 'sector':sector})


@user_passes_test(admin_check)
def cell_update(request, pk):
	cell = get_object_or_404(Cell, pk=pk)
	if request.method == 'POST':
		form = CellForm(request.POST, instance=cell)
		if form.is_valid():
			form.save()
			messages.success(request,'Cell has been updated')
			return HttpResponseRedirect(reverse('cell', args=[cell.pk]))
	else:
		form = CellForm(instance=cell)
		return render(request, 'crud/cell_update.html', {'form':form, 'cell':cell})



@user_passes_test(admin_check)
def village_update(request, pk):
	village = get_object_or_404(Village, pk=pk)
	if request.method == 'POST':
		form = VillageForm(request.POST, instance=village)
		if form.is_valid():
			form.save()
			messages.success(request,'Village has been updated')
			return HttpResponseRedirect(reverse('village', args=[village.pk]))
	else:
		form = VillageForm(instance=village)
		return render(request, 'crud/village_update.html', {'form':form, 'village':village})


@user_passes_test(admin_check)
def sector_rates(request, pk):
	sector = get_object_or_404(Sector, pk=pk)
	rates = Rate.objects.filter(Q(sector=sector) | Q(village__cell__sector=sector)).order_by('category', '-date_from')
	return render(request, 'crud/sector_rates.html', {'sector':sector, 'rates':rates})


@user_passes_test(admin_check)
def village_rates(request, pk):
	village = get_object_or_404(Village, pk=pk)
	rates = village.rate_set.all().order_by('-date_from')
	return render(request, 'crud/village_rates.html', {'village':village, 'rates':rates})

@user_passes_test(admin_check)
def rate_update(request, pk):
	rate = get_object_or_404(Rate, pk=pk)
	if request.method == 'POST':
		form = RateForm(request.POST, instance=rate)
		if form.is_valid():
			form.save()
			messages.success(request,'Rate has been updated')
			next = request.POST.get('next')
			if next:
				return HttpResponseRedirect(next)
	else:
		form = RateForm(instance=rate, initial={'next':request.GET.get('next')})
		return render(request, 'crud/rate_update.html', {'form':form, 'rate':rate})

@user_passes_test(admin_check)
def recent_logs(request):
	recent_logs = Log.objects.all().order_by('-id')[:100]
	return TemplateResponse(request, 'crud/recent_logs.html', {'logs':recent_logs })

@user_passes_test(admin_check)
def account_logs(request, pk):
	account = get_object_or_404(Account,pk=pk)
	logs = Log.objects.filter(account=account).order_by('-id')
	return TemplateResponse(request, 'crud/account_logs.html', {'account':account,  'logs':logs })

@user_passes_test(admin_check)
def user_logs(request, pk):
	user = get_object_or_404(User,pk=pk)
	logs = Log.objects.filter(user=user).order_by('-id')
	return TemplateResponse(request, 'crud/user_logs.html', {'user':user,  'logs':logs })

@user_passes_test(admin_check)
def edit_account(request, pk):
	account = get_object_or_404(Account, pk=pk)
	if request.method == 'POST':
		form = AccountForm(request.POST, instance=account)
		if form.is_valid():
			form.save()
			messages.success(request,'Account has been updated')
			next = request.POST.get('next')
			if next:
				return HttpResponseRedirect(next)
			else:
				return HttpResponseRedirect(reverse('account', args=[account.pk]))

	form = AccountForm(instance=account, initial={'next':request.GET.get('next')})
	return render(request, 'crud/form.html', {'form':form, 'account':account})


@user_passes_test(admin_check)
def account_archive_transactions(request, pk):
	account = get_object_or_404(Account,pk=pk)
	transactions, fees = account.transactions(update=False)
	return TemplateResponse(request, 'crud/account_transactions.html', {'account':account, 'transactions':transactions, 'fees':fees})


@user_passes_test(admin_check)
def account_transactions(request, pk):
	account = get_object_or_404(Account,pk=pk)
	transactions, fees = account.current_transactions()
	return TemplateResponse(request, 'crud/account_transactions.html', {'account':account, 'transactions':transactions, 'fees':fees})


@user_passes_test(admin_check)
def fee_items_report(request, district_pk=None, sector_pk=None,  cell_pk=None, village_pk=None, fee_type_pk=None, web=False):
	filename = ''
	#af = AccountFee.objects.filter(balance__gt=0, closed__isnull=True).select_related('account', 'fee_type')
	af = AccountFee.objects.filter(balance__gt=0, closed__isnull=True).\
		values('account_id', 'account__name', 'account__citizen_id', 'account__tin','upi', 'account__phone','account__email', 'fee_type__name').\
		annotate(balance=Sum('balance'), overdue=Sum('overdue')).order_by('-balance')

	if int(fee_type_pk):
		fee_type = get_object_or_404(CategoryChoice, id=fee_type_pk)
		af = af.filter(fee_type=fee_type)
		filename += "%s " % fee_type.name

	if int(village_pk):
		village = get_object_or_404(Village, pk=village_pk)
		af = af.filter(village=village)
		filename += "%s village " % village

	elif int(cell_pk):
		cell = get_object_or_404(Cell, pk=cell_pk)
		af = af.filter(cell=cell)
		filename += "%s cell " % cell

	elif int(sector_pk):
		sector = get_object_or_404(Sector, pk=sector_pk)
		af = af.filter(sector=sector)
		filename += "%s sector " % sector

	elif int(district_pk):
		district = get_object_or_404(District, pk=district_pk)
		af = af.filter(sector__district=district)
		filename += "%s district " % district

	af = af.order_by('-balance')
	if web:
		af = af[:101]
	if filename:
		filename += '.csv'
	else:
		filename = generate_filename(af, append_datestamp=True)

	if web:
		return TemplateResponse(request, 'crud/fee_items_report.html', {'account_fees':af})
	else:
		buff = StringIO()
		af = af.values('account_id', 'account__name', 'account__phone', 'account__tin', 'account__citizen_id', 'upi', 'account__email', 'fee_type__name', 'balance', 'overdue' )
		djqscsv.write_csv(af, buff, field_header_map={'account_id': 'Account Number', 'account__name':'Account Name', 'account__phone':'Account Phone', 'account__email':'Account Email', 'fee_type__name':'Fee Type'})
		buff.seek(0)
		#render_to_csv_response(af, filename=filename, field_header_map={'id': 'Account Number', 'account__name':'Account Name', 'account__phone':'Account Phone', 'account__email':'Account Email', 'fee_type__name':'Fee Type'})
		response = HttpResponse(content_type='application/zip')
		response['Content-Disposition'] = 'attachment; filename=%s.zip' % filename
		zf = zipfile.ZipFile(response, mode='w', compression=zipfile.ZIP_DEFLATED)
		zf.writestr(filename, buff.read())

		return response




@user_passes_test(admin_check)
def region_report(request):
	region = []
	sub_regions = []
	regions = []
	if request.method == 'POST':
		form = RegionReportForm(request.POST)
		if form.is_valid():
			village = form.cleaned_data.get('village')
			cell = form.cleaned_data.get('cell')
			sector = form.cleaned_data.get('sector')
			district = form.cleaned_data.get('district')
			fee_type = form.cleaned_data.get('fee_type')
			if fee_type:
				region = CurrentOutstanding.objects.filter(fee_type=fee_type)
				sub_regions = CurrentOutstanding.objects.filter(fee_type=fee_type)
			else:
				region = CurrentOutstanding.objects.all()
				sub_regions = CurrentOutstanding.objects.all()

			if village:
				region = region.filter(village=village)
				sub_regions = []

			elif cell:
				region = region.filter(cell=cell)
				sub_regions = sub_regions.filter(village__cell=cell)

			elif sector:
				region = region.filter(sector=sector)
				sub_regions = sub_regions.filter(cell__sector=sector)

			elif district:
				region = region.filter(district=district)
				sub_regions = sub_regions.filter(sector__district=district)
			else:
				region = region.filter(district__isnull=False)
				sub_regions = []

			regions = [r for r in region] + [r for r in sub_regions]

	else:
		form = RegionReportForm()

	return TemplateResponse(request, 'crud/region_report.html', {'form':form, 'regions':regions,})


@user_passes_test(admin_check)
def search(request):
	r = []
	results = []
	if request.method == 'POST':
		form = SearchForm(request.POST)
		if form.is_valid():
			category = form.cleaned_data.get('category')
			search_for = form.cleaned_data.get('search_for')
			if category == 'TIN':
				r = r + [a for a in Account.objects.filter(tin__icontains=search_for)]
			elif category == 'phone':
				r = r + [a for a in Account.objects.filter(phone__icontains=search_for)]
				r = r + [a for a in Profile.objects.filter(phone__icontains=search_for)]
			elif category == 'Account Name':
				r = r + [a for a in Account.objects.filter(name__icontains=search_for)]
			elif category == 'citizen_id':
				r = r + [a for a in Account.objects.filter(citizen_id__icontains=search_for)]
			elif category == 'upi':
				cell, parcel_id = split_upi(search_for)
				accounts = Account.objects.filter(account_fees__cell=cell, account_fees__parcel_id=parcel_id).distinct()
				prop = Property.objects.filter(cell=cell, parcel_id=parcel_id)
				r = r + [a for a in accounts]
				r = r + [a for a in prop]
			elif category == 'account_id':
				try:
					account  = Account.objects.get(pk=search_for)
				except Account.DoesNotExist:
					r = []
				else:
					return HttpResponseRedirect(reverse('account', args=[account.pk]))

	else:
		form = SearchForm(initial={'category':'Account Name'})

	for m in r:
		results.append([ContentType.objects.get_for_model(m), m])

	return render(request, 'crud/search_form.html', {'form':form, 'results':results})


@user_passes_test(admin_check)
def make_payment(request, pk):
	account = get_object_or_404(Account,pk=pk)
	searchform = SearchForm()
	if request.method == 'POST':
		form = MakePaymentForm(request.POST)
		if form.is_valid():
			fee_type = form.cleaned_data.get('fee_type')
			current_fees = AccountFee.objects.filter(fee_type=fee_type, account=account, closed__isnull=True)
			if not current_fees:
				messages.warning(request, "Warning: There is no active %s for this account" % fee_type)
			bank_deposit = form.save(commit=False)
			bank_deposit.account = account
			bank_deposit.user = request.user
			bank_deposit.save()
			messages.success(request, "Payment created successfully")
			return HttpResponseRedirect(reverse('make_payment', args=[pk]))

	else:
		form = MakePaymentForm()

	return render(request, 'crud/make_payment.html', {'form':form, 'searchform':searchform, 'account':account })


@user_passes_test(admin_check)
def receipt_book_add(request):
	if request.method == 'POST':
		form = ReceiptBookForm(request.POST)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect(reverse('receipt_books'))
	else:
		form = ReceiptBookForm()

	return render(request, 'crud/base_form.html', {'form':form, 'heading':'New Receipt Book'})


@user_passes_test(admin_check)
def receipt_book_update(request, pk):
	receipt_book = get_object_or_404(ReceiptBook,pk=pk)
	if request.method == 'POST':
		form = ReceiptBookForm(request.POST, instance=receipt_book)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect(reverse('receipt_books'))
	else:
		form = ReceiptBookForm(instance=receipt_book)

	return render(request, 'crud/base_form.html', {'form':form})


@user_passes_test(admin_check)
def receipt_books(request):
	receipt_books = ReceiptBook.objects.all().order_by('id')
	return render(request, 'crud/receipt_books.html', {'receipt_books':receipt_books })


@user_passes_test(admin_check)
def receipt_payments(request,pk):
	receipt_book = get_object_or_404(ReceiptBook, pk=pk)
	payments = BankDeposit.objects.filter(receipt_book=receipt_book, status__code='active').order_by('-pk')
	return TemplateResponse(request, 'crud/receipt_payments.html', {'receipt_book':receipt_book, 'payments':payments})


@user_passes_test(admin_check)
def new_account(request):
	matches = []
	if request.method == 'POST':
		form = NewAccountForm(request.POST)
		if form.is_valid():
			cd = form.cleaned_data
			tin = cd.get('tin')
			citizen_id = cd.get('citizen_id')
			phone = cd.get('phone')
			name = cd.get('name')
			district = cd.get('district')
			sector = cd.get('sector')
			cell = cd.get('cell')
			village = cd.get('village')
			parcel_id = cd.get('parcel_id')
			if not request.POST.get('confirm'):
				filt = Q(name__icontains=name)
				words = name.split(' ')
				if len(words) > 1:
					for w in words:
						if len(w) < 4: #eliminate common words/articles
							continue
						filt |= Q(name__icontains=w)

				if tin:
					filt |= Q(tin=tin)
				if citizen_id:
					filt |= Q(citizen_id=citizen_id)
				if phone:
					filt |= Q(phone=phone)
				if cell and parcel_id:
					filt |= Q(account_fees__cell=cell, account_fees__parcel_id=parcel_id)
				matches = Account.objects.filter(filt).distinct()[:70]

				if not matches:
					if village:
						matches = Account.objects.filter(Q(village=village) | Q(account_fees__village=village)).distinct()[:50]
					elif cell:
						matches = Account.objects.filter(Q(cell=cell) | Q(account_fees__cell=cell)).distinct()[:30]
					elif sector:
						matches = Account.objects.filter(Q(sector=sector) | Q(account_fees=sector)).distinct()[:30]


			if not matches or request.POST.get('confirm'): #create the account
				account = Account.objects.create(name=name, start_date=cd.get('start_date'), parcel_id=cd.get('parcel_id'), village=village, cell=cell, sector=sector, district=district,
					phone=phone, citizen_id=citizen_id, tin=tin, period_ending=date.today())
				messages.success(request, "New Account %s created" % account.pk)
				if tin: #create / link business
					businesses = Business.objects.filter(tin=tin)
					if not businesses:
						business=Business.objects.create(name=name, tin=tin, phone1=phone, date_started=cd.get('start_date'), village=village, cell=cell,
							district=district, sector=sector)
					else:
						business = businesses[0]
						business.phone1 = phone or business.phone1
						business.district = district or business.district
						business.sector = sector or business.sector
						business.cell = cell or business.cell
						business.village = village or business.village
						business.save()
					AccountHolder.objects.create(account=account, holder=business)
				if citizen_id: # create / link citizen
					citizens = Citizen.objects.filter(citizen_id=citizen_id)
					if not citizens:
						citizen = Citizen.objects.create(first_name=cd.get('citizen_first_name'), last_name=cd.get('citizen_last_name'), date_of_birth=cd.get('citizen_dob'), citizen_id=citizen_id)
					else:
						citizen = citizens[0]
						citizen.phone_1 = phone or citizen.phone_1
						citizen.date_of_birth = cd.get('dob') or citizen.date_of_birth
						citizen.first_name = cd.get('citizen_first_name') or citizen.first_name
						citizen.last_name = cd.get('ctizen_last_name') or citizen.last_name
						citizen.save()
					AccountHolder.objects.create(account=account, holder=citizen)

				fee_type = cd.get('fee_type')
				if fee_type: #create fee
					if fee_type == 'cleaning':
						period = 12
					else:
						period = 1
					from_date = date(date.today().year, 1,1 )
					to_date = date(date.today().year, 12, 31)
					AccountFee.objects.create(account=account, from_date=from_date, to_date=to_date, fee_type=cd.get('fee_type'), parcel_id=cd.get('parcel_id'), district=district,\
						sector=sector, cell=cell, village=village, period=period, fee_subtype=cd.get('fee_subtype'))

					account.transactions(update=True)

				return HttpResponseRedirect(reverse('account', args=[account.pk]))
	else:
		form = NewAccountForm()

	return render(request, 'crud/new_account.html', {'form':form, 'matches':matches})

