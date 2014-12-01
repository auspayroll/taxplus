from django import forms
from property.models import District, Sector, Cell, Village
from django.conf import settings
from datetime import date
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple
from dev1 import variables
from common.fields import CurrencyField, CurrencyInput
from datetime import date
import math


include_field_choices = [('Fines', 'Fines'),('Receipt','Sector Receipt'),
		('Bank','Bank'),('Bank Receipt','Bank Receipt'),('User','User'),('Timestamp','Timestamp'),('Total Fee Amount','Total Fee Amount'),
		('Remaining Fee Amount','Remaining Fee Amount'), ('Cell','Cell'), ('Village','Village')]


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

		cleaned_data = super(SearchForm, self).clean()
		sector = cleaned_data.get("sector")
		if sector:
			self.fields['cell'].queryset = Cell.objects.filter(sector=sector)

		cleaned_data = super(SearchForm, self).clean()
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
	payer_id = forms.ChoiceField(choices=[], required=False)
	amount = CurrencyField(label="Payment Amount") #  widget=forms.TextInput(attrs={'class':'disabled', 'readonly':'readonly'})
	sector_receipt = forms.CharField(label="Sector Receipt Number")
	payer_type = forms.ChoiceField(widget=forms.RadioSelect, label="Payer", required=False, choices=payer_type_choices)
	bank = forms.ChoiceField(choices=bank_choices)
	bank_receipt = forms.CharField()

	def __init__(self, *args, **kwargs):
		self.fee = kwargs.pop('fee')
		super(PaymentForm, self).__init__(*args, **kwargs)
		self.fields['payer_id'].choices = [(ownership.owner.pk, ownership.owner.name) for ownership in self.fee.prop_title.title_ownership.all() ]

	def clean(self):
		cleaned_data = super(PaymentForm, self).clean()
		amount = cleaned_data.get('amount')
		paid_date = cleaned_data.get('paid_date')
		if amount is not None and paid_date:
				if amount <=0:
					self._errors["amount"] = self.error_class(["Specify a fee amount to pay"])

				if paid_date > self.fee.due_date and amount < self.fee.remaining_amount:
					self._errors["amount"] = self.error_class(["Overdue payment amount must be atleast %s Rwf" % self.fee.remaining_amount])

				total_due = self.fee.total_due(paid_date)
				if amount > total_due:
					self._errors["amount"] = self.error_class(["Payment amount is more than what is owed: %s Rwf" % total_due])

		return cleaned_data


class PayFeesForm(forms.Form):
	paid_date = forms.DateField(label="Payment date", widget=forms.DateInput(format = '%d/%m/%Y',attrs={'class' : 'date_picker'}), \
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



