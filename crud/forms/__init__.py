from django import forms
from django.contrib.contenttypes.models import ContentType
from taxplus.models import Business, Citizen, District, Sector, Property, CategoryChoice, Cell, District, Village
from crud.models import AccountPayment, CleaningFee, TowerFee, QuarryFee,\
 Contact, AccountPayment, Media, AccountFee, Utility, AccountNote, Collection, BankDeposit
from django.contrib.gis.geos import Point
from collections import OrderedDict
from django.contrib.auth.models import User, Group

import html5.forms.widgets as html5_widgets
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.core.validators import RegexValidator
import re
from datetime import date
from dateutil import parser

from django.core.exceptions import ValidationError


fee_auto_choices = [(0,'Add as one-off fee'),(12,'Auto generate fees every month'),(4,'Auto generate fees every quarter'),
(52,'Auto generate fees every week'),(1,'Auto generate fees every year')]
fee_auto_choices = [('','I will specify the amount'),(1,'Automatically calculate the amount')]


fee_defaults = {'tower':'tower', 'property':'land_lease', 'quarry':'quarry', 'market':'market', 'cemetery':'cemetery', 'sign':'sign'}
regional_fees = {'marriage':'marriage'}


class LoginForm(forms.Form):
	username = forms.CharField()
	password = forms.CharField(widget=forms.PasswordInput())


class FormExtra(forms.Form):
	def field_clean(self, field_name):
		try:
			field = self.fields.get(field_name)
			value = field.widget.value_from_datadict(self.data, self.files, self.add_prefix(field_name))
			if value is None:
				return None
			value = field.clean(value)
			self.cleaned_data[field_name] = value
			return value
		except ValidationError as e:
			self.add_error(field_name, e)
			return None


class ContactForm(forms.ModelForm):
	class Meta:
		model = Contact
		fields = ('first_name','last_name','phone','email')


class PaymentForm(forms.ModelForm):
	class Meta:
		model = AccountPayment
		fields = ('payment_date','receipt_no','amount')

	payment_date = forms.DateField(widget=html5_widgets.DateInput, initial=date.today())



class CollectionForm(forms.ModelForm):
	class Meta:
		model = Collection
		fields = ('utility', 'fee_type', 'date_from','date_to','receipt_no','amount', 'no_collections')

	date_from = forms.DateField(widget=html5_widgets.DateInput, initial=date.today())
	date_to = forms.DateField(widget=html5_widgets.DateInput, initial=date.today())
	file_upload = forms.FileField(required=False)

	def __init__(self, *args, **kwargs):
		account = kwargs.pop('account')
		super(CollectionForm, self).__init__(*args, **kwargs)
		if account:
			utilities = account.utilities.all()
			self.fields['utility'].queryset=utilities
			self.fields['utility'].empty_label = None
			self.fields['fee_type'].empty_label = None
			#set the default fee type
			if utilities:
				default_fee_code = fee_defaults.get(utilities[0].utility_type.code)
				if default_fee_code:
					self.fields['fee_type'].initial = CategoryChoice.objects.get(code=default_fee_code, category__code='fee_type')
		else:
			self.fields['utility'].queryset=Utility.objects.none()


class CollectionUpdateForm(forms.ModelForm):
	class Meta:
		model = Collection
		fields = ('utility', 'fee_type', 'collector', 'date_from','date_to','receipt_no','amount', 'no_collections')

	date_from = forms.DateField(widget=html5_widgets.DateInput, initial=date.today())
	date_to = forms.DateField(widget=html5_widgets.DateInput, initial=date.today())
	file_upload = forms.FileField(required=False)
	collector = forms.ModelChoiceField( help_text='allocated collector can be assigned later', required=False, queryset=User.objects.filter(is_active=True, groups__name='Collector'))
	next = forms.CharField(required=False, widget=forms.HiddenInput())

	def __init__(self, *args, **kwargs):
		super(CollectionUpdateForm, self).__init__(*args, **kwargs)
		self.fields['utility'].queryset=self.instance.account.utilities.all()
		self.fields['fee_type'].empty_label = None

class RegionalCollectionForm(forms.ModelForm):
	class Meta:
		model = Collection
		fields = ('fee_type', 'date_from','date_to','receipt_no','amount', 'no_collections')

	date_from = forms.DateField(widget=html5_widgets.DateInput, initial=date.today())
	date_to = forms.DateField(widget=html5_widgets.DateInput, initial=date.today())
	fee_type = forms.ModelChoiceField(queryset=CategoryChoice.objects.filter(category__code='fee_type', code__in=regional_fees))


class AccountUtilityForm(forms.Form):
	utility_type = forms.ModelChoiceField(queryset=CategoryChoice.objects.filter(category__code='utility_type'), label='Location type')
	identifier = forms.CharField(max_length=30, label="Unique Identifer", help_text="Unique Identifer")


class RegionForm(FormExtra):
	district = forms.ModelChoiceField(queryset=District.objects.all().order_by('name'))
	sector = forms.ModelChoiceField(queryset=Sector.objects.none(), required=False)
	cell = forms.ModelChoiceField(queryset=Cell.objects.none(), required=False)
	village = forms.ModelChoiceField(queryset=Village.objects.none(), required=False)

	def clean(self, *args, **kwargs):
		try:
			self._errors.pop('sector')
		except KeyError:
			pass

		try:
			self._errors.pop('cell')
		except KeyError:
			pass

		try:
			self._errors.pop('village')
		except KeyError:
			pass

		district = self.cleaned_data.get('district')
		self.fields['sector'].queryset = Sector.objects.filter(district=district)
		sector  = self.field_clean('sector')
		if sector:
			self.fields['cell'].queryset = Cell.objects.filter(sector=sector)

		cell = self.field_clean('cell')
		if cell:
			self.fields['village'].queryset = Village.objects.filter(cell=cell)
		village = self.field_clean('village')
		cleaned_data = super(RegionForm, self).clean(*args, **kwargs)
		return cleaned_data


class UtilityForm(forms.ModelForm, RegionForm):
	class Meta:
		model = Utility
		fields = ('utility_type', 'identifier', 'upi', 'district', 'sector', 'cell', 'village')

	utility_type = forms.ModelChoiceField(queryset=CategoryChoice.objects.filter(category__code='utility_type'), label='Location type')
	identifier = forms.CharField(max_length=30, label="Unique Identifer", help_text="Market ID, Quarry ID etc.", required=False)
	lat = forms.FloatField(required=False, min_value=-90, max_value=90, label='Latitude')
	lon = forms.FloatField(required=False, min_value=-180, max_value=180, label='Longitude')

	def __init__(self, *args, **kwargs):
		super(UtilityForm, self).__init__(*args, **kwargs)
		if self.instance and self.instance.location:
			self.fields['lat'].initial = self.instance.location.coords[0]
			self.fields['lon'].initial = self.instance.location.coords[1]


	def clean(self, *args, **kwargs):
		RegionForm.clean(self, *args, **kwargs)
		return super(UtilityForm, self).clean(*args, **kwargs)


	def save(self, *args, **kwargs):
		utility = super(UtilityForm, self).save(commit=False, *args, **kwargs)
		lat = self.cleaned_data.get('lat')
		lon = self.cleaned_data.get('lon')
		if lat and lon:
			utility.location = Point(lat, lon)
		utility.save()
		return utility


class NewLocationForm(RegionForm):
	def __init__(self, *args, **kwargs):
		super(NewLocationForm, self).__init__(*args, **kwargs)
		fields = self.fields
		self.fields = OrderedDict({'utility_type': forms.ModelChoiceField(queryset=CategoryChoice.objects.filter(category__code='utility_type').exclude(code__in=['property','district','sector','cell','village']), label='Location type')})
		self.fields.update(fields)

class AddUtilityRegionForm(forms.ModelForm):
	class Meta:
		model = Utility
		fields = ('utility_type', 'identifier', 'upi')

	utility_type = forms.ModelChoiceField(queryset=CategoryChoice.objects.filter(category__code='utility_type').exclude(code='property'), label='Location type')
	identifier = forms.CharField(max_length=30, label="Unique Identifer", help_text="Market ID, Quarry ID etc.", required=False)
	lat = forms.FloatField(required=False, min_value=-90, max_value=90, label='Latitude')
	lon = forms.FloatField(required=False, min_value=-180, max_value=180, label='Longitude')
	start_date = forms.DateField(widget=html5_widgets.DateInput, initial=date.today())


	def save(self, *args, **kwargs):
		utility = super(AddUtilityRegionForm, self).save(commit=False, *args, **kwargs)
		lat = self.cleaned_data.get('lat')
		lon = self.cleaned_data.get('lon')
		if lat and lon:
			utility.location = Point(lat, lon)
		return utility

class LocationForm(UtilityForm):
	start_date = forms.DateField(widget=html5_widgets.DateInput, initial=date.today())
	def __init__(self, *args, **kwargs):
		super(LocationForm, self).__init__(*args, **kwargs)
		self.fields['utility_type'].widget = forms.HiddenInput()
		self.fields['district'].widget = forms.HiddenInput()
		self.fields['identifier'].help_text = 'optional'
		self.fields['sector'].widget = forms.HiddenInput()
		self.fields['cell'].widget = forms.HiddenInput()
		self.fields['village'].widget = forms.HiddenInput()
		self.fields['identifier'].label = "Unique Identifer"



class NewFeeForm(forms.Form):
	fee_type = forms.ModelChoiceField(queryset=CategoryChoice.objects.filter(category__code='fee_type'))
	auto = forms.BooleanField(label="Auto-calculate fee" , help_text="Uncheck to specify amount", required=False)
	district = forms.ModelChoiceField(queryset=District.objects.all().order_by('name'))


class AccountNoteForm(forms.ModelForm):
	class Meta:
		model = AccountNote
		fields = ['text']

	text = forms.CharField(label='Note',widget=forms.Textarea, help_text='')

class NewFeeCollectionForm(forms.ModelForm):
	class Meta:
		model = AccountFee
		fields = ['fee_type', 'from_date', 'to_date', 'quantity', 'amount']

	from_date = forms.DateField(widget=html5_widgets.DateInput)
	to_date = forms.DateField(widget=html5_widgets.DateInput)
	quantity = forms.IntegerField(label="No. of collections taken", min_value=0)
	amount = forms.DecimalField(label='Total Collected Amount', min_value=0, decimal_places=2)
	receipt_no = forms.CharField(widget=forms.Textarea, label="Receipt numbers", help_text="separate multiple receipts with comma eg. N1234, F4343, ... ")
	identifier = forms.CharField(label='Unique Identifier', required=False, max_length=30, help_text="Eg. Market ID, Quarry ID etc.")
	lat = forms.FloatField(required=False, min_value=-90, max_value=90, label='Latitude')
	lon = forms.FloatField(required=False, min_value=-180, max_value=180, label='Longitude')

	def save(self, account, user, *args, **kwargs):
		account_fee = super(NewFeeCollectionForm, self).save(commit=False,*args, **kwargs)
		account_fee.account = account
		account_fee.user = user
		account_fee.is_paid = True
		account_fee.principle_paid = self.cleaned_data.get('amount')

		#create utility
		if self.cleaned_data.get('identifier'):
			utility, created = Utility.objects.get_or_create(identifier=self.cleaned_data.get('identifier'),
				utility_type=self.cleaned_data.get('fee_type'))
			lat = self.cleaned_data.get('lat')
			lon = self.cleaned_data.get('lon')
			if lat and lon:
				utility.location = Point(lat, lon)
				utility.save()
				account_fee.utility = utility

		account_fee.save()

		# create a payment
		account_payment = AccountPayment(payment_date=self.cleaned_data.get('to_date'),
			account=account, amount=self.cleaned_data.get('amount'),
			no_collections=self.cleaned_data.get('quantity',1), receipt_no=self.cleaned_data.get('receipt_no'))
		account_payment.user = user
		account_payment.fee = account_fee
		account_payment.save()

		return account_fee



class MediaForm(forms.ModelForm):
	class Meta:
		model = Media
		fields = ('title','item')



class FeeForm(forms.ModelForm):
	class Meta:
		model = AccountFee
		fields = ['fee_type',  'period', 'from_date', 'auto', 'amount', 'due_date']

	auto = forms.BooleanField(label="Auto-calculate fee" , help_text="Uncheck to specify amount", required=False)
	from_date = forms.DateField(widget=html5_widgets.DateInput, label="Start fee on")
	due_date = forms.DateField(widget=html5_widgets.DateInput)
	amount = forms.DecimalField(label='Fee Amount', min_value=0, decimal_places=2)


class UtilityFeeForm(FeeForm):
	identifier = forms.CharField(max_length=30, label="Unique Identifier")
	lat = forms.FloatField(required=False, min_value=-90, max_value=90)
	lon = forms.FloatField(required=False, min_value=-180, max_value=180)

	def save(self, user=None, account=None, *args, **kwargs):
		upi = self.cleaned_data.get('identifier')
		lat = self.cleaned_data.get('lat')
		lon = self.cleaned_data.get('lon')
		location = None
		if lat and lon:
			location = Point(lat, lon)
		else:
			location = Point()

		utility, updated = Utility.objects.update_or_create(location=location, defaults=dict(utility_type=self.cleaned_data.get('fee_type'), identifier=upi))
		fee = super(UtilityFeeForm, self).save(*args, **kwargs)
		fee.account = account
		fee.user = user
		fee.utility = utility
		fee.save()
		return fee


class CleaningFeeForm(FeeForm):
	def save(self, user=None, account=None, *args, **kwargs):
		upi = self.cleaned_data.get('identifier')
		fee = super(CleaningFeeForm, self).save(*args, **kwargs)
		fee.account = account
		fee.user = user
		fee.save()
		return fee


class LandLeaseFeeForm(FeeForm):
	identifier = forms.CharField(max_length=30, label="Property UPI")
	lat = forms.FloatField(required=False, min_value=-90, max_value=90)
	lon = forms.FloatField(required=False, min_value=-180, max_value=180)

	def save(self, user=None, account=None, *args, **kwargs):
		upi = self.cleaned_data.get('identifier')
		prop = Property.find_by_upi(upi)
		if not prop:
			prop = Property(upi=upi).save()
		fee = super(LandLeaseFeeForm, self).save(*args, **kwargs)
		fee.account = account
		fee.user = user
		fee.utility = prop
		fee.save()
		return fee


class BusinessForm(forms.ModelForm, FormExtra):
	class Meta:
		model = Business
		fields = ('name', 'tin', 'date_started', 'phone1', 'phone2', 'email', 'address')

	date_started = forms.DateField(widget=html5_widgets.DateInput)
	lat = forms.FloatField(required=False, min_value=-90, max_value=90, label='Latitude')
	lon = forms.FloatField(required=False, min_value=-180, max_value=180, label='Longitude')

	def clean(self):
		cleaned_data = super(BusinessForm, self).clean()
		identifier = cleaned_data.get("tin")
		name = cleaned_data.get("name")
		phone1 = cleaned_data.get('phone1')
		phone2 = cleaned_data.get('phone2')
		email = cleaned_data.get('email')

		q_objects = Q(pk__isnull=True)
		if identifier:
			q_objects.add(Q(tin__iexact=identifier), Q.OR)
		if name:
			q_objects.add(Q(name__icontains=name), Q.OR)
		if phone1:
			q_objects.add(Q(phone1__icontains=phone1), Q.OR)
		if phone2:
			q_objects.add(Q(phone1__icontains=phone2), Q.OR)
		if email:
			q_objects.add(Q(phone1__icontains=email), Q.OR)

		duplicates = Business.objects.filter(q_objects)
		if duplicates:
			fields = self.fields
			self.fields = OrderedDict({'duplicate': forms.ModelChoiceField(label='Select duplicate to merge with', required=False, queryset=duplicates)})
			self.fields.update(fields)
			self.field_clean('duplicate')
			if 'duplicate' not in self.cleaned_data:
				raise forms.ValidationError("There were possible duplicate records found. Please select one to merge with.")

		return cleaned_data


class CitizenForm(forms.ModelForm, FormExtra):
	class Meta:
		model = Citizen
		fields = ('first_name', 'last_name', 'middle_name', 'citizen_id', 'date_of_birth', 'year_of_birth',
			'email', 'phone_1', 'phone_2', 'address')


	start_date = forms.DateField(widget=html5_widgets.DateInput)
	date_of_birth = forms.DateField(widget=html5_widgets.DateInput, required=False)
	year_of_birth = forms.IntegerField(required=False, min_value=1900, max_value=2016)

	def clean(self):
		cleaned_data = super(CitizenForm, self).clean()
		first_name = cleaned_data.get("first_name")
		last_name = cleaned_data.get("last_name")
		date_of_birth = cleaned_data.get("date_of_birth")
		year_of_birth = cleaned_data.get("year_of_birth")
		phone_1 = cleaned_data.get("phone_1")
		phone_2 = cleaned_data.get("phone_2")
		citizen_id = cleaned_data.get("citizen_id")
		email = cleaned_data.get("email")

		q_objects = Q(pk__isnull=True)
		if first_name and last_name and date_of_birth:
			q_objects.add(Q(date_of_birth=date_of_birth, first_name__icontains=first_name, last_name__icontains=last_name), Q.OR)

		if phone_1:
			q_objects.add(Q(phone_1__iexact=phone_1), Q.OR)
		if phone_2:
			q_objects.add(Q(phone_2__iexact=phone_1), Q.OR)
		if citizen_id:
			q_objects.add(Q(citizen_id=citizen_id), Q.OR)

		if email:
			q_objects.add(Q(email__iexact=email), Q.OR)

		duplicates = Citizen.objects.filter(q_objects)
		if duplicates:
			fields = self.fields
			self.fields = OrderedDict({'duplicate': forms.ModelChoiceField(label='Select duplicate to merge with', required=False, queryset=duplicates)})
			self.fields.update(fields)
			self.field_clean('duplicate')
			if 'duplicate' not in self.cleaned_data:
				raise forms.ValidationError("There were possible duplicate records found. Please select one to merge with.")

		return cleaned_data


class NewPaymentForm(forms.ModelForm):
	class Meta:
		model = AccountPayment
		fields =  ['payment_date', 'amount', 'receipt_no', 'user']

	#payment_date = forms.DateField(widget=html5_widgets.DateInput, initial=date.today())



def camelcase(word):
   wordarray = word.split('_')
   return ''.join(word.capitalize() for word in wordarray)


def form_for_model(fee_type):
	fee_type = fee_type.lower()
	if fee_type.find('fee') == -1:
		fee_type += '_fee'
	try:
		return eval(camelcase(fee_type)+'Form')
	except:
		return UtilityFeeForm


class AddAccountDates(forms.Form):
	date_from = forms.DateField(widget=html5_widgets.DateInput, initial=date.today(), help_text="inclusive")
	date_to = forms.DateField(widget=html5_widgets.DateInput, initial=date.today(), help_text='inclusive')
	days = forms.TypedMultipleChoiceField(coerce=int, choices=[('-1','Every day'), ('1','Monday'),('2','Tuesday'),('3','Wednesday'),('4','Thursday'),('5','Friday'),('6','Saturday'), ('0','Sunday'),], widget=forms.CheckboxSelectMultiple)
	cycle = forms.TypedChoiceField(coerce=int, choices=[('-1','Every day'), ('1','Everyweek'),])
	dates = forms.CharField(widget=forms.HiddenInput())
	collector = forms.ModelChoiceField( help_text='allocated collector can be assigned later', required=False, queryset=User.objects.filter(is_active=True, groups__name='Collector'))
	fee_type = forms.ModelChoiceField(queryset=CategoryChoice.objects.filter(category__code='fee_type'))
	utility = forms.ModelChoiceField(queryset=Utility.objects.none())

	def clean_dates(self, *args, **kwargs):
		dates = self.cleaned_data.get('dates')
		try:
			self.cleaned_dates = [ parser.parse(d) for d in dates.split(',')]
		except:
			raise forms.ValidationError("There was an invalid date submitted.")
		else:
			return self.cleaned_dates

	def __init__(self, *args, **kwargs):
		account = kwargs.pop('account')
		super(AddAccountDates, self).__init__(*args, **kwargs)
		if account:
			self.fields['utility'].queryset=account.utilities.all()
			self.fields['utility'].empty_label = None
			self.fields['fee_type'].empty_label = None
			utilities = account.utilities.all()
			#set the default fee type
			if utilities:
				default_fee_code = fee_defaults.get(utilities[0].utility_type.code)
				if default_fee_code:
					self.fields['fee_type'].initial = CategoryChoice.objects.get(code=default_fee_code, category__code='fee_type')
		else:
			self.fields['utility'].queryset=Utility.objects.none()

class UserForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ('first_name', 'last_name', 'email', 'is_active', 'groups')

	email = forms.EmailField(max_length=30, required=False)
	phone = forms.CharField(max_length=40, required=False)
	registration_no = forms.CharField(max_length=40, required=False)
	groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), widget=forms.CheckboxSelectMultiple)
	reset_password = forms.BooleanField(required=False)
	photo = forms.FileField(required=False)

	def clean(self, *args, **kwargs):
		cd = self.cleaned_data
		if cd.get('reset_password'):
			self.cleaned_data['raw_password'] = User.objects.make_random_password()
		return cd

class NewUserForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ('first_name', 'last_name', 'email', 'is_active', 'groups')

	first_name = forms.CharField(max_length=30)
	last_name = forms.CharField(max_length=30)
	email = forms.EmailField(max_length=30, required=False)
	phone = forms.CharField(max_length=40, required=False)
	registration_no = forms.CharField(max_length=40, required=False)
	is_active = forms.BooleanField(initial=True)
	groups = forms.ModelMultipleChoiceField(queryset=Group.objects.all(), widget=forms.CheckboxSelectMultiple)
	photo = forms.FileField(required=False)

	def clean(self, *args, **kwargs):
		self.cleaned_data['password'] = User.objects.make_random_password()
		email = self.cleaned_data.get('email')
		first_name = self.cleaned_data.get('first_name')
		last_name = self.cleaned_data.get('last_name')
		if email and User.objects.filter(email=email).count() ==0:
			self.cleaned_data['username'] = email
		elif first_name and last_name:
			self.cleaned_data['username'] = (first_name[0] + last_name)[:30]

		return self.cleaned_data


class BankDepositForm(forms.ModelForm):
	class Meta:
		model = BankDeposit
		fields = ['bank', 'branch', 'bank_receipt_no', 'rra_receipt', 'depositor_name', 'date_banked']

	date_banked = forms.DateField(widget=html5_widgets.DateInput)

	def __init__(self, *args, **kwargs):
		super(BankDepositForm, self).__init__(*args, **kwargs)
		if not self.instance.pk:
			for k, v in self.fields.items():
				v.required = False

	@property
	def not_empty(self):
		return True in [ bool(i) for i in self.cleaned_data.values()]

	def clean(self, *args, **kwargs):
		cd = super(BankDepositForm, self).clean(*args, **kwargs)
		if not self.instance.pk:
			not_empty = self.not_empty
			errors = {}
			if not_empty and not cd.get('bank'):
				errors['bank'] = 'Bank Name is required'
			if not_empty and not cd.get('bank_receipt_no'):
				errors['bank_receipt_no'] = 'Bank Receipt is required'
			if not_empty and not cd.get('date_banked'):
				errors['date_banked'] = 'Date banked is required'
			if errors:
				raise forms.ValidationError(errors)

		return cd

	def save(self, *args, **kwargs):
		bank_receipt_no = self.cleaned_data.get('bank_receipt_no')
		if not self.instance.pk and bank_receipt_no:
			try:
				self.instance = BankDeposit.objects.get(bank_receipt_no__iexact=bank_receipt_no)
			except BankDeposit.DoesNotExist:
				pass

		deposit = super(BankDepositForm, self).save(*args, **kwargs)
		return deposit


class NewAccountHolderForm(forms.Form):
	account_holder_type = forms.ModelChoiceField(queryset=ContentType.objects.filter(app_label='taxplus', model__in=['business','citizen']))
	last_name = forms.CharField(max_length=30, label="Last Name or Business Name")
	first_name = forms.CharField(max_length=30, required=False)
	phone = forms.CharField(max_length=30, required=False)
	phone_2 = forms.CharField(max_length=30, required=False)
	email = forms.EmailField(max_length=30, required=False)
	address = forms.CharField(max_length=30, widget=forms.Textarea(), required=False)


class DistrictForm(forms.ModelForm):
	class Meta:
		model = District
		fields = ('name', )


class SectorForm(forms.ModelForm):
	class Meta:
		model = Sector
		fields = ('name', 'district')


class CellForm(forms.ModelForm):
	class Meta:
		model = Cell
		fields = ('name', 'sector')

	def __init__(self, *args, **kwargs):
		super(CellForm,self).__init__(*args, **kwargs)
		district = self.instance.sector.district
		self.fields['sector'].queryset = Sector.objects.filter(district=district)


class VillageForm(forms.ModelForm):
	class Meta:
		model = Village
		fields = ('name', 'cell')


	def __init__(self, *args, **kwargs):
		super(VillageForm,self).__init__(*args, **kwargs)
		sector = self.instance.cell.sector
		self.fields['cell'].queryset = Cell.objects.filter(sector=sector)








