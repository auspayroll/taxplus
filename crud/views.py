from collect.forms import EpayForm, CollectionGroupForm, RegistrationForm, CollectorForm, BusinessForm
from crud.forms import CitizenForm, BusinessForm, UtilityForm, FeeForm, NewPaymentForm, \
	AccountUtilityForm, ContactForm, PaymentForm, form_for_model, \
	MediaForm, NewFeeCollectionForm, AccountNoteForm, CollectionForm, RegionForm, NewMarketForm, MarketForm, AddUtilityRegionForm
from crud.models import Account, Contact, AccountPayment, Media,\
	 AccountHolder, AccountFee, AccountNote, Utility, Collection
from datetime import date
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.geos import Point
from django.core.mail import send_mail
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.db.models import Q, Sum
from django.forms.models import modelformset_factory
from django.http import HttpResponse, Http404
from django.shortcuts import HttpResponseRedirect, render_to_response, get_object_or_404, redirect
from django.template.response import TemplateResponse
from djqscsv import render_to_csv_response
from random import randint
from taxplus.models import District, Sector, Cell, Village, Business, Citizen, CategoryChoice, Property
import csv
import json



@login_required
def index(request):
	return districts(request)


@login_required
def select_fees(request):
	return TemplateResponse(request, 'crud/select_fees.html')



@login_required
def select_account_holder(request, pk):
	fee_type = get_object_or_404(ContentType, pk=pk)
	request.session['fee_type'] = {'id':id, 'name':fee_type.name}
	return TemplateResponse(request, 'crud/select_fees.html')



@login_required
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


@login_required
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


@login_required
def account(request, pk):
	account = get_object_or_404(Account, pk=pk)
	return TemplateResponse(request, 'crud/account.html', {'account':account})

@login_required
def new_account_fee(request, pk):
	account = get_object_or_404(Account, pk=pk)
	if request.method == 'POST':
		form= FeeForm(request.POST)
		if form.is_valid():
			account_fee = form.save(commit=False)
			account_fee.account = account
			account_fee.user = request.user
			account_fee.save()
			messages.success(request, 'New Fee Created')
			return HttpResponseRedirect(reverse('account_fees', args=[pk]))
	else:
		form = FeeForm()

	return TemplateResponse(request, 'crud/new_fee_account.html', {'account':account, 'form':form})


@login_required
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


@login_required
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

@login_required
def recent_accounts(request):
	accounts = Account.objects.all().order_by('-pk')[:50]
	return TemplateResponse(request, 'crud/accounts.html', {'accounts':accounts})


@login_required
def recent_utilities(request, utility_type):
	utilities = Utility.objects.filter(utility_type__code=utility_type).order_by('-pk')[:50]

	return TemplateResponse(request, 'crud/recent_utilities.html', {'utilities':utilities})


@login_required
def account_fees(request,pk):
	account = get_object_or_404(Account, pk=pk)
	fees = AccountFee.objects.filter(account=account).order_by('-pk')
	return TemplateResponse(request, 'crud/fees.html', {'account':account, 'fees':fees})


@login_required
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


@login_required
def account_select(request):
	return TemplateResponse(request, 'crud/account_select.html', {})


@login_required
def new_market(request, utility_type='market'):
	if request.method == 'POST':
		form = NewMarketForm(request.POST)
		if form.is_valid():
				current_accounts = Account.objects.filter(utilities__village=form.cleaned_data.get('village'), utilities__utility_type=form.cleaned_data.get('utility_type'))
				initial_data = form.cleaned_data
				initial_data['name'] = "%s %s" % (initial_data.get('village'), initial_data.get('utility_type'))
				form = MarketForm(initial=initial_data)
				return TemplateResponse(request, 'crud/new_market.html', {'form':form, 'heading':'Add a new %s Location in %s village' % ( initial_data.get('utility_type'), initial_data.get('village')), 'current_accounts':current_accounts})
	else:
		utility_type  = CategoryChoice.objects.get(category__code='utility_type', code=utility_type)
		form = NewMarketForm(initial={'utility_type':utility_type})
	return TemplateResponse(request, 'crud/base_form.html', {'form':form, 'heading':'Add a new %s' % utility_type })


@login_required
def new_market_post(request):
	"""
	add a new market location
	"""
	if request.method == 'POST':
		form = MarketForm(request.POST)
		if form.is_valid():
			village = form.cleaned_data.get('village')
			utility = form.save()
			account = Account(name=utility.name, start_date=form.cleaned_data.get('start_date'))
			account.save()
			account.utilities.add(utility)
			messages.success(request, 'New Market site created')
			return HttpResponseRedirect(reverse('account', args=[account.pk]))
	else:
		return HttpResponseRedirect(reverse('new_market'))
	return TemplateResponse(request, 'crud/new_market.html', {'form':form, 'heading':'Add a new %s in %s village' % (form.cleaned_data.get('utility_type'), form.cleaned_data.get('village'))})


@login_required
def account_contacts(request,pk):
	account = get_object_or_404(Account, pk=pk)
	contacts = Contact.objects.filter(account=account).order_by('-pk')

	return TemplateResponse(request, 'crud/contacts.html', {'account':account, 'contacts':contacts})


@login_required
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


@login_required
def account_payments(request,pk):
	account = get_object_or_404(Account, pk=pk)
	payments = AccountPayment.objects.filter(account=account).order_by('-pk')

	return TemplateResponse(request, 'crud/payments.html', {'account':account, 'payments':payments})


@login_required
def new_payment(request, pk):
	account = get_object_or_404(Account, pk=pk)
	if request.method == 'POST':
		form= PaymentForm(request.POST)
		if form.is_valid():
			payment = form.save(commit=False)
			payment.account = account
			payment.user = request.user
			payment.save()
			messages.success(request, 'New Payment created')
			return HttpResponseRedirect(reverse('account_payments', args=[account.pk]))
	else:
		form = PaymentForm()

	return TemplateResponse(request, 'crud/form.html', {'account':account, 'form':form, 'heading':'New Account Payment'})


@login_required
def account_media(request,pk):
	account = get_object_or_404(Account, pk=pk)
	media = Media.objects.filter(account=account).order_by('-pk')
	return TemplateResponse(request, 'crud/media.html', {'account':account, 'media':media})


@login_required
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


@login_required
def new_fee_collection(request, pk):
	account = get_object_or_404(Account, pk=pk)
	if request.method == 'POST':
		form= CollectionForm(request.POST, account=account)
		if form.is_valid():
			payment = form.save(commit=False)
			payment.account = account
			payment.user = request.user
			payment.save()
			messages.success(request, 'New Collection created')
			return HttpResponseRedirect(reverse('fee_collections', args=[account.pk]))
	else:
		form = CollectionForm(account=account)

	return TemplateResponse(request, 'crud/form.html', {'account':account, 'form':form, 'heading':'New Collection'})


@login_required
def fee_collections(request,pk):
	account = get_object_or_404(Account, pk=pk)
	collections = Collection.objects.filter(account=account).order_by('-pk')
	return TemplateResponse(request, 'crud/collections.html', {'account':account, 'collections':collections})


@login_required
def account_holders(request,pk):
	account = get_object_or_404(Account, pk=pk)
	holders = AccountHolder.objects.filter(account=account).order_by('-pk')
	return TemplateResponse(request, 'crud/holders.html', {'account':account, 'holders':holders})



@login_required
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


@login_required
def account_notes(request,pk):
	account = get_object_or_404(Account, pk=pk)
	notes = AccountNote.objects.filter(account=account).order_by('-pk')
	return TemplateResponse(request, 'crud/notes.html', {'account':account, 'notes':notes})


@login_required
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


@login_required
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

@login_required
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

@login_required
def districts(request):
	districts = District.objects.all().order_by('name')
	return TemplateResponse(request, 'crud/districts.html', {'districts':districts, })

@login_required
def district(request, pk):
	district = get_object_or_404(District, pk=pk)
	sectors = Sector.objects.filter(district=district)
	return TemplateResponse(request, 'crud/district.html', {'district':district, 'sectors':sectors, })

@login_required
def sector(request, pk):
	sector = get_object_or_404(Sector, pk=pk)
	cells = Cell.objects.filter(sector=sector)
	return TemplateResponse(request, 'crud/sector.html', {'sector':sector, 'cells':cells, })

@login_required
def cell(request, pk):
	cell = get_object_or_404(Cell, pk=pk)
	villages = Village.objects.filter(cell=cell)
	return TemplateResponse(request, 'crud/cell.html', {'cell':cell, 'villages':villages})

@login_required
def village(request, pk):
	village = get_object_or_404(Village, pk=pk)
	accounts = Account.objects.filter(utilities__village=village).order_by('-id')
	recent_collections = Collection.objects.filter(account__in=accounts).order_by('-id')[:100]
	return TemplateResponse(request, 'crud/village.html', {'village':village, 'accounts':accounts, 'recent_collections':recent_collections })


@login_required
def recent_collections(request):
	recent_collections = Collection.objects.all().order_by('-id')[:100]
	return TemplateResponse(request, 'crud/recent_collections.html', {'recent_collections':recent_collections })

@login_required
def add_village_utility(request, pk):
	village = get_object_or_404(Village, pk=pk)
	if request.method == 'POST':
		form= AddUtilityRegionForm(request.POST)
		if form.is_valid():
			utility = form.save() #custom form save method has commit= False
			utility.village = village
			utility.cell = village.cell
			utility.sector = village.cell.sector
			utility.district = village.cell.sector.district
			utility.save()
			account = Account(name=utility.name, start_date=form.cleaned_data.get('start_date'))
			account.save()
			account.utilities.add(utility)
			messages.success(request, 'New utility added')
			return HttpResponseRedirect(reverse('village',args=[village.pk]))
	else:
		form = AddUtilityRegionForm()

	return TemplateResponse(request, 'crud/village_utility.html', {'village':village, 'form':form, })
