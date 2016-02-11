from django import forms
from django.contrib.contenttypes.models import ContentType
from taxplus.models import Business, Citizen, District, Sector, Property, CategoryChoice, Cell
from crud.models import AccountPayment, CleaningFee, TowerFee, QuarryFee, Contact, AccountPayment, Media, AccountFee, Utility, AccountNote
from django.contrib.gis.geos import Point
from collections import OrderedDict

import html5.forms.widgets as html5_widgets
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.core.validators import RegexValidator
import re

from django.core.exceptions import ValidationError

def validate_upi(upi):
	if not re.match(r'(0?\d+/){4}0?\d*$',upi):
		raise ValidationError('Invalid UPI Format')
	province, district, sector, cell, parcel = upi.split('/')
	cell_code = "%02d" % int(province) + "%02d" % int(district) + "%02d" % int(sector) + "%02d" % int(cell)
	try:
		Cell.objects.get(code=cell_code)
	except Cell.DoesNotExist:
		raise ValidationError('Cell code %s not found' % cell_code)

	return upi


fee_auto_choices = [(0,'Add as one-off fee'),(12,'Auto generate fees every month'),(4,'Auto generate fees every quarter'),
(52,'Auto generate fees every week'),(1,'Auto generate fees every year')]
fee_auto_choices = [('','I will specify the amount'),(1,'Automatically calculate the amount')]


class ContactForm(forms.ModelForm):
	class Meta:
		model = Contact
		fields = ('first_name','last_name','phone','email')

class PaymentForm(forms.ModelForm):
	class Meta:
		model = AccountPayment
		fields = ('payment_date','receipt_no','amount')

	payment_date = forms.DateField(widget=html5_widgets.DateInput)


class AccountUtilityForm(forms.Form):
	utility_type = forms.ModelChoiceField(queryset=CategoryChoice.objects.filter(category__code='utility_type'), label='Utility/Site type')
	identifier = forms.CharField(max_length=30, label="Unique Identifer", help_text="Market ID, UPI etc.")

	def clean_identifier(self):
		identifier = self.cleaned_data.get('identifier')
		if self.cleaned_data.get('utility_type').code == 'property':
			validate_upi(identifier)
		return identifier


class UtilityForm(forms.ModelForm):
	class Meta:
		model = Utility
		fields = ('utility_type', 'identifier', 'name',)
	utility_type = forms.ModelChoiceField(queryset=CategoryChoice.objects.filter(category__code='utility_type').exclude(code='property'), label='Utility/Site type')
	identifier = forms.CharField(max_length=30, label="Unique Identifer", help_text="Market ID, Quarry etc.")
	lat = forms.FloatField(required=False, min_value=-90, max_value=90, label='Latitude')
	lon = forms.FloatField(required=False, min_value=-180, max_value=180, label='Longitude')
	name = forms.CharField(required=False)

	def save(self, *args, **kwargs):
		utility = super(UtilityForm, self).save(commit=False, *args, **kwargs)
		lat = self.cleaned_data.get('lat')
		lon = self.cleaned_data.get('lon')
		if lat and lon:
			utility.location = Point(lat, lon)
		utility.save()
		return utility



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


class FormExtra:
	def field_clean(self, field_name):
		try:
			field = self.fields.get(field_name)
			value = field.widget.value_from_datadict(self.data, self.files, self.add_prefix(field_name))
			if value is None:
				return
			value = field.clean(value)
			self.cleaned_data[field_name] = value
		except ValidationError as e:
			self.add_error(field_name, e)


class FeeForm(forms.ModelForm):
	class Meta:
		model = AccountFee
		fields = ['fee_type',  'period', 'from_date', 'auto', 'amount', 'due_date']

	auto = forms.BooleanField(label="Auto-calculate fee" , help_text="Uncheck to specify amount", required=False)
	from_date = forms.DateField(widget=html5_widgets.DateInput, label="Start fee on")
	due_date = forms.DateField(widget=html5_widgets.DateInput)
	amount = forms.DecimalField(label='Fee Amount', min_value=0, decimal_places=2)




class FeeFormOld(forms.ModelForm, FormExtra):
	"""
	Base Form for all Fee Types
	"""
	class Meta:
		model = AccountFee
		fields = ['fee_type','auto','from_date', 'period']

	fee_type = forms.ModelChoiceField(queryset=CategoryChoice.objects.filter(category__code='fee_type'),widget=forms.HiddenInput())
	auto = forms.BooleanField(label="Auto-calculate fee" , help_text="Uncheck to specify amount", required=False,widget=forms.HiddenInput())
	district = forms.ModelChoiceField(queryset=District.objects.all().order_by('name'),widget=forms.HiddenInput())
	from_date = forms.DateField(widget=html5_widgets.DateInput)

	def __init__(self, *args, **kwargs):
		auto = district = account_start = None
		if 'auto' in kwargs:
			auto = kwargs.pop('auto')
		if 'district' in kwargs:
			district = kwargs.pop('district')
		super(FeeForm, self).__init__(*args, **kwargs)

		if not auto:
			self.fields['amount'] = forms.DecimalField(label='Fee Amount', min_value=0, decimal_places=2)
			self.Meta.fields.append('amount')
			self.fields['due_date'] = forms.DateField(label='Due Date', widget=html5_widgets.DateInput)
			self.Meta.fields.append('due_date')

		if district and 'sector' in self.fields:
			self.fields['sector'].queryset = Sector.objects.filter(district=district).order_by('name')
			self.Meta.fields.append('sector')



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
		fields =  ['payment_date', 'amount', 'receipt_no']

	payment_date = forms.DateField(widget=html5_widgets.DateInput)



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
