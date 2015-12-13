from django import forms
from django.conf import settings
from datetime import date
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple, Textarea
from dev1 import variables
from common.fields import CurrencyField, CurrencyInput
from datetime import date, datetime
from taxplus.models import Business, Sector, Cell, Village, BusinessCategory, CleaningCategory, PropertyTitle, MessageBatch, District, Sector, Cell, Village, Citizen
import math
from django.core.exceptions import ValidationError
import re
from django.contrib.auth.models import User

class EpayForm(forms.Form):
	number = forms.IntegerField(min_value=1, max_value=1000, label="Number of Forms")
	collectors = forms.ModelMultipleChoiceField(required=False, widget=CheckboxSelectMultiple, queryset=User.objects.all())
	
"""
class PaymentSearchForm(forms.Form):
	search_string = forms.CharField(min_length=3, max_length=20, required=True, label="Sector or Bank receipt")
	date_from = forms.DateField(label="Date range (optional) between ", widget=forms.DateInput(format = '%d/%m/%Y',attrs={'class' : 'date_picker'}), \
		input_formats=('%d/%m/%Y',), required=False)
	date_to = forms.DateField(label="and..", widget=forms.DateInput(format = '%d/%m/%Y',attrs={'class' : 'date_picker'}), \
		input_formats=('%d/%m/%Y',), required=False)


class SearchRegion(forms.Form):
	district = forms.ModelChoiceField(queryset = District.objects.none(), error_messages={'required':'District is required'})
	sector = forms.ModelChoiceField(queryset = Sector.objects.none(), error_messages={'required':'Sector is required'})
	cell = forms.ModelChoiceField(required = False, queryset = Cell.objects.none())
	village = forms.ModelChoiceField(required = False, queryset = Village.objects.none())

	def __init__(self, *args, **kwargs):
		super(SearchRegion, self).__init__(*args, **kwargs)
		self.fields['district'].queryset = District.objects.all().order_by('name')
		if args:
			district = args[0].get('district')
			if district:
				try:
					district_id = int(district)
				except:
					pass
				else:
					self.fields['sector'].queryset = Sector.objects.filter(district__pk=district_id)

			sector = args[0].get('sector')
			if sector:
				try:
					sector_id = int(sector)
				except:
					pass
				else:
					self.fields['cell'].queryset = Cell.objects.filter(sector__pk=sector_id)

			cell = args[0].get('cell')
			if cell:
				try:
					cell_id = int(cell)
				except:
					pass
				else:
					self.fields['village'].queryset = Village.objects.filter(cell__pk=cell_id)


def validate_phone(value):
    if not re.match( r'^07\d{8}$', value, re.M|re.I):
        raise ValidationError(u'%s is not a valid phone number' % value)


include_field_choices = [('Fines', 'Fines'),('Receipt','Sector Receipt'),
		('Bank','Bank'),('Bank Receipt','Bank Receipt'),('User','User'),('Timestamp','Timestamp'),('Total Fee Amount','Total Fee Amount'),
		('Remaining Fee Amount','Remaining Fee Amount'), ('Cell','Cell'), ('Village','Village')]




class PhoneField(forms.CharField):
	def __init__(self, *args, **kwargs):
		kwargs['validators'] = [validate_phone]
		kwargs['help_text'] = "valid phone number format: 07 followed by eight digits"
		super(PhoneField, self).__init__(*args, **kwargs )


class TitleForm(forms.ModelForm):
	class Meta:
		model = PropertyTitle
		fields = ['date_from', 'date_to']

	date_from = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS, error_messages={'invalid':'date from is invalid', 'required':'date from is required'}, initial=date.today().strftime('%d/%m/%Y'), widget=forms.DateInput(format = '%d/%m/%Y',attrs={'class' : 'date_picker'}))
	date_to = forms.DateField(required=False, input_formats=settings.DATE_INPUT_FORMATS, error_messages={'invalid':'date to is invalid', }, widget=forms.DateInput(format = '%d/%m/%Y',attrs={'class' : 'date_picker'}))




class MergeBusinessForm(forms.ModelForm):
	class Meta:
		model = Business
		fields = ['name', 'tin', 'date_started', 'address', 'phone1', 'phone2', 'email', 'po_box', 'sector', 'cell', 'village', 'closed_date', 'i_status', 'credit',
		'accountant_name', 'accountant_phone', 'accountant_email', 'cleaning_category', 'business_category']

	name = forms.ChoiceField(choices=[], required=False )
	tin = forms.ChoiceField(choices=[], required=False )
	date_started = forms.TypedChoiceField(choices=[], coerce=lambda x: datetime.strptime(x,'%Y-%m-%d').date(), empty_value=None)
	address = forms.ChoiceField(choices=[], required=False )
	phone1 = forms.ChoiceField(choices=[], required=False )
	phone2 = forms.ChoiceField(choices=[], required=False )
	email = forms.ChoiceField(choices=[], required=False )
	po_box = forms.ChoiceField(choices=[], required=False )
	sector = forms.ModelChoiceField(queryset=None, required=False )
	cell = forms.ModelChoiceField(queryset=None, required=False )
	village = forms.ModelChoiceField(queryset=None, required=False )
	#credit =forms.TypedChoiceField(choices=[], required=False, coerce=lambda x: 7)
	closed_date = forms.TypedChoiceField(choices=[], required=False, coerce=lambda x: datetime.strptime(x,'%Y-%m-%d').date(), empty_value=None)
	i_status  = forms.ChoiceField(choices=[], label='status' )
	credit = forms.TypedChoiceField(choices=[], required=False, coerce=int, empty_value=0)
	accountant_name = forms.ChoiceField(choices=[], required=False )
	accountant_phone = forms.ChoiceField(choices=[], required=False )
	accountant_email = forms.ChoiceField(choices=[], required=False )
	cleaning_category = forms.ModelChoiceField(queryset=None, required=False, label='Cleaning Fee Category')
	business_category = forms.ModelChoiceField(queryset=None, required=False, label='Business Category')

	def __init__(self, *args, **kwargs):
		businesses = kwargs.pop('businesses')
		super(MergeBusinessForm, self).__init__(*args, **kwargs)

		for field_name, field in self.fields.items():
			if type(field) is forms.ModelChoiceField:
				continue

			field.choices = [(i or '', i or 'None') for i in [getattr(b1,field_name) for b1 in businesses]]

		self.fields['sector'].queryset = Sector.objects.filter(pk__in=[business.sector.pk for business in businesses if business.sector])
		self.fields['cell'].queryset = Cell.objects.filter(pk__in=[business.cell.pk for business in businesses if business.cell])
		self.fields['village'].queryset = Village.objects.filter(pk__in=[business.village.pk for business in businesses if business.village])

		self.fields['cleaning_category'].queryset = CleaningCategory.objects.filter(pk__in=[business.cleaning_category.pk for business in businesses if business.cleaning_category])
		self.fields['business_category'].queryset = BusinessCategory.objects.filter(pk__in=[business.business_category.pk for business in businesses if business.business_category])




class SearchForm(forms.Form):
	district = forms.ModelChoiceField(queryset = District.objects.all().order_by('name'), error_messages={'required':'District is required'})
	sector = forms.ModelChoiceField(queryset = Sector.objects.none(), error_messages={'required':'Sector is required'})
	cell = forms.ModelChoiceField(required = False, queryset = Cell.objects.none())
	village = forms.ModelChoiceField(required = False, queryset = Village.objects.none())
	date_from = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS, error_messages={'invalid':'date from is invalid', 'required':'date from is required'}, initial=date.today().strftime('%d/%m/%Y'), widget=forms.TextInput(attrs={'class':'date_picker'}))
	date_to = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS, initial=date.today().strftime('%d/%m/%Y'), error_messages={'invalid':'date to is invalid', 'required':'date to is required' }, widget=forms.TextInput(attrs={'class':'date_picker'}))
	fee_type = forms.ChoiceField(required = False, choices=(('cleaning','cleaning'), ('land_lease','land lease')))
	#include_fields = forms.MultipleChoiceField(required=False, widget=CheckboxSelectMultiple, choices=include_field_choices)

	def __init__(self, *args, **kw):
		super(SearchForm, self).__init__(*args, **kw)
		self.fields['district'].queryset = District.objects.all().order_by('name')
		self.fields['sector'].queryset = Sector.objects.all()
		self.fields['cell'].queryset = Cell.objects.all()
		self.fields['village'].queryset = Village.objects.all()
		self.initial = {'include_fields':[ i for (i,j) in include_field_choices ]}

	def clean(self):
		cleaned_data = super(SearchForm, self).clean()
		district = cleaned_data.get("district")
		if district:
			self.fields['sector'].queryset = Sector.objects.filter(district=district)

		sector = cleaned_data.get("sector")
		if sector:
			self.fields['cell'].queryset = Cell.objects.filter(sector=sector)

		cell = cleaned_data.get("cell")
		if cell:
			self.fields['village'].queryset = Village.objects.filter(cell=cell)

		return cleaned_data


# overdue_choices = [('1','less than 1 month'), ('30', 'greater than 1 month'),('90','greater than 3 months'),('180','greater than 6 months'),('365','greater than 1 year')]

class DebtorsForm(forms.Form):
	district = forms.ModelChoiceField(queryset = District.objects.all(), error_messages={'required':'District is required'})
	sector = forms.ModelChoiceField(queryset = Sector.objects.none(), error_messages={'required':'Sector is required'})
	cell = forms.ModelChoiceField(required = False, queryset = Cell.objects.none())
	village = forms.ModelChoiceField(required = False, queryset = Village.objects.none())
	# as_at = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS, error_messages={'invalid':"'as at' date is invalid", 'required':"'as at' date is required"}, initial=date.today().strftime('%d/%m/%Y'), widget=forms.TextInput(attrs={'class':'date_picker'}))
	#include_fields = forms.MultipleChoiceField(required=False, widget=CheckboxSelectMultiple, choices=overdue_choices)

	def __init__(self, *args, **kw):
		super(DebtorsForm, self).__init__(*args, **kw)
		self.fields['district'].queryset = District.objects.all()
		self.fields['sector'].queryset = Sector.objects.all()
		self.fields['cell'].queryset = Cell.objects.all()
		self.fields['village'].queryset = Village.objects.all()
		# self.initial = {'include_fields':[ i for (i,j) in overdue_choices ]}

	def clean(self):
		cleaned_data = super(DebtorsForm, self).clean()
		district = cleaned_data.get("district")
		if district:
			self.fields['sector'].queryset = Sector.objects.filter(district=district)

		cleaned_data = super(DebtorsForm, self).clean()
		sector = cleaned_data.get("sector")
		if sector:
			self.fields['cell'].queryset = Cell.objects.filter(sector=sector)

		cleaned_data = super(DebtorsForm, self).clean()
		return cleaned_data

bank_choices = [('','----------')] + [ (code, name) for code, name in variables.banks]
payer_type_choices = (('citizen','Citizen'),('business','Business'))


class PaymentForm(forms.Form):
	paid_date = forms.DateField(label="Payment date", widget=forms.DateInput(format = '%d/%m/%Y',attrs={'class' : 'date_picker'}), \
		input_formats=('%d/%m/%Y',),initial=date.today().strftime('%d/%m/%Y'),)
	citizen_id = forms.IntegerField(widget=forms.HiddenInput(), initial=None, required=False)
	business_id = forms.IntegerField(widget=forms.HiddenInput(), initial=None, required=False)
	payer_name = forms.CharField(max_length=200, required=True)
	payer_id = forms.CharField(required=False)
	amount = forms.IntegerField(label="Payment Amount") #  widget=forms.TextInput(attrs={'class':'disabled', 'readonly':'readonly'})
	sector_receipt = forms.CharField(label="Sector Receipt Number")
	payer_type = forms.ChoiceField(widget=forms.RadioSelect, label="Payer", required=False, choices=payer_type_choices)
	bank = forms.ChoiceField(choices=bank_choices)
	bank_receipt = forms.CharField()

	def __init__(self, *args, **kwargs):
		self.fee = kwargs.pop('fee')
		super(PaymentForm, self).__init__(*args, **kwargs)
		#self.fields['payer_id'].choices = [(ownership.owner.pk, ownership.owner.name) for ownership in self.fee.prop_title.title_ownership.all() ]

	def clean(self):
		cleaned_data = super(PaymentForm, self).clean()
		amount = cleaned_data.get('amount')
		paid_date = cleaned_data.get('paid_date')
		if amount is not None and paid_date:
				if paid_date > date.today():
					self._errors['paid_date'] = self.error_class(["Paid date cannot be in the future"])

		return cleaned_data


class PayFeesForm(forms.Form):
	amount = forms.IntegerField()
	paid_date = forms.DateField(label="Payment datex", widget=forms.DateInput(format = '%d/%m/%Y',attrs={'class' : 'date_picker'}), \
		input_formats=('%d/%m/%Y',),initial=date.today().strftime('%d/%m/%Y'),)
	citizen_id = forms.IntegerField(widget=forms.HiddenInput(), initial=None, required=False)
	business_id = forms.IntegerField(widget=forms.HiddenInput(), initial=None, required=False)
	payer_name = forms.CharField(max_length=200, required=True)
	sector_receipt = forms.CharField(label="Sector Receipt Number")
	payer_type = forms.ChoiceField(widget=forms.RadioSelect, label="Payer", required=False, choices=[(i,i) for i in ('citizen','business')])
	bank = forms.ChoiceField(choices=bank_choices)
	bank_receipt = forms.CharField()

	def __init__(self, *args, **kwargs):
		super(PayFeesForm, self).__init__(*args, **kwargs)


class BusinessForm(forms.ModelForm):
	class Meta:
		model = Business
		fields = ['name', 'tin', 'cleaning_category', 'vat_register', 'date_started', 'phone1', 'phone2', 'email', 'address', 'po_box', 'accountant_name', 'accountant_phone', 'accountant_email']

	date_started = forms.DateField(label="Date started", widget=forms.DateInput(format = '%d/%m/%Y',attrs={'class' : 'date_picker'}), \
		input_formats=('%d/%m/%Y',),initial=date.today().strftime('%d/%m/%Y'),)

	phone1 = PhoneField()
	phone2 = PhoneField(required=False)
	accountant_phone = PhoneField(required=False)


class BusinessFormRegion(forms.ModelForm):
	class Meta:
		model = Business
		fields = ['sector', 'cell', 'village']

	district = forms.ModelChoiceField(queryset = District.objects.all().order_by('name'), error_messages={'required':'District is required'})
	sector = forms.ModelChoiceField(queryset = Sector.objects.none(), error_messages={'required':'Sector is required'})
	cell = forms.ModelChoiceField(queryset = Cell.objects.none(), error_messages={'required':'Cell is required'})
	village = forms.ModelChoiceField(queryset = Village.objects.none(), error_messages={'required':'Village is required'})

	def __init__(self, *args, **kwargs):
		super(BusinessFormRegion, self).__init__(*args, **kwargs)
		self.fields.keyOrder = ['district', 'sector', 'cell', 'village']
		self.fields['district'].queryset = District.objects.all().order_by('name')
		if args:
			district = args[0].get('district')
			if district:
				try:
					district_id = int(district)
				except:
					pass
				else:
					self.fields['sector'].queryset = Sector.objects.filter(district__pk=district_id)

			sector = args[0].get('sector')
			if sector:
				try:
					sector_id = int(sector)
				except:
					pass
				else:
					self.fields['cell'].queryset = Cell.objects.filter(sector__pk=sector_id)

			cell = args[0].get('cell')
			if cell:
				try:
					cell_id = int(cell)
				except:
					pass
				else:
					self.fields['village'].queryset = Village.objects.filter(cell__pk=cell_id)

		elif self.instance.village:
			self.fields['village'].queryset = Village.objects.filter(cell=self.instance.village.cell)
			self.fields['cell'].queryset = Cell.objects.filter(sector=self.instance.village.cell.sector)
			self.fields['sector'].queryset = Sector.objects.filter(district=self.instance.village.cell.sector.district)
			self.initial['district'] = self.instance.village.cell.sector.district


class MessageBatchForm(SearchRegion):
	message = forms.CharField(widget=Textarea, help_text="You can use the following placeholders: {name}, {overdue}, {penalty}, {interest}, {total}, {epay}, {as_at}")
	message_type = forms.TypedChoiceField(choices=[(1,'For Business'),(2,'For Property')], coerce=int)
	district = forms.ModelChoiceField(queryset = District.objects.none(), required=False)
	sector = forms.ModelChoiceField(queryset = Sector.objects.none(), required=False)
	cell = forms.ModelChoiceField(required = False, queryset = Cell.objects.none())
	village = forms.ModelChoiceField(required = False, queryset = Village.objects.none())

class LogSearchForm(forms.Form):
	date_from = forms.DateField(label="Date range (optional) between ", widget=forms.DateInput(format = '%d/%m/%Y',attrs={'class' : 'date_picker'}), \
		input_formats=('%d/%m/%Y',), required=False)
	date_to = forms.DateField(label="and..", widget=forms.DateInput(format = '%d/%m/%Y',attrs={'class' : 'date_picker'}), \
		input_formats=('%d/%m/%Y',), required=False)
	user = forms.CharField(min_length=3, required=False, label="Staff User by name or email:")
	changes_only = forms.TypedChoiceField(required=False, choices=[("", "All Requests"), ("1","Record Changes Only")], coerce=bool, label="Display:")

class LogSearchFormExtended(LogSearchForm):
	search_for = forms.ChoiceField(required=False, choices=[(i,i) for i in ('All', 'Property', 'Business', 'Citizen')])
	search_string = forms.CharField(min_length=3, max_length=20, required=False, label="Search for Busines Name, UPI, TIN or CID:")

class CitizenUpdate(forms.ModelForm):
	class Meta:
		model = Citizen
		fields = ['citizen_id', 'foreign_identity_type', 'foreign_identity_number', 'first_name', 'last_name', 'gender', 'date_of_birth', 'year_of_birth']

	date_of_birth = forms.DateField(label="Date of birth", widget=forms.DateInput(format = '%d/%m/%Y',attrs={'class' : 'date_picker'}), \
		input_formats=('%d/%m/%Y',), required=False)

	gender = forms.ChoiceField(required=False, choices=[(i,i) for i in ("Male", "Female")], widget=RadioSelect)

class CitizenContact(forms.ModelForm):
	class Meta:
		model = Citizen
		fields = ['address', 'po_box', 'phone_1', 'phone_2', 'email', 'contact_details_confirmed',]

 	contact_details_confirmed = forms.DateField(label="Contact details confirmed on", widget=forms.DateInput(format = '%d/%m/%Y',attrs={'class' : 'date_picker'}), \
		input_formats=('%d/%m/%Y',), required=False)

 	phone_1 = PhoneField(required=False)
 	phone_2 = PhoneField(required=False)
"""
