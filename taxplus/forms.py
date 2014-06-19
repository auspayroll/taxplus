from django import forms
from property.models import District, Sector, Cell, Village
from django.conf import settings
from datetime import date
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple


include_field_choices = [('Business Name','Business Name'), ('Fines', 'Fines'),('Receipt','Sector Receipt'),
		('Bank','Bank'),('Bank Receipt','Bank Receipt'),('User','User'),('Timestamp','Timestamp'),('Total Fee Amount','Total Fee Amount'),
		('Remaining Fee Amount','Remaining Fee Amount'), ('Cell','Cell'), ('Village','Village')]


class SearchForm(forms.Form):
	district = forms.ModelChoiceField(queryset = District.objects.all(), error_messages={'required':'District is required'})
	sector = forms.ModelChoiceField(queryset = Sector.objects.none(), error_messages={'required':'Sector is required'})
	cell = forms.ModelChoiceField(required = False, queryset = Cell.objects.none())
	village = forms.ModelChoiceField(required = False, queryset = Village.objects.none())
	date_from = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS, error_messages={'invalid':'date from is invalid', 'required':'date from is required'}, initial=date.today().strftime('%d/%m/%Y'), widget=forms.TextInput(attrs={'class':'date_picker'}))
	date_to = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS, initial=date.today().strftime('%d/%m/%Y'), error_messages={'invalid':'date to is invalid', 'required':'date to is required' }, widget=forms.TextInput(attrs={'class':'date_picker'}))
	include_fields = forms.MultipleChoiceField(required=False, widget=CheckboxSelectMultiple, choices=include_field_choices)

	def __init__(self, *args, **kw):
		super(SearchForm, self).__init__(*args, **kw)
		self.fields['district'].queryset = District.objects.all()
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


overdue_choices = [('1','less than 1 month'), ('30', 'greater than 1 month'),('90','greater than 3 months'),('180','greater than 6 months'),('365','greater than 1 year')]

class DebtorsForm(forms.Form):
	district = forms.ModelChoiceField(queryset = District.objects.all(), error_messages={'required':'District is required'})
	sector = forms.ModelChoiceField(queryset = Sector.objects.none(), error_messages={'required':'Sector is required'})
	cell = forms.ModelChoiceField(required = False, queryset = Cell.objects.none())
	village = forms.ModelChoiceField(required = False, queryset = Village.objects.none())
	as_at = forms.DateField(input_formats=settings.DATE_INPUT_FORMATS, error_messages={'invalid':"'as at' date is invalid", 'required':"'as at' date is required"}, initial=date.today().strftime('%d/%m/%Y'), widget=forms.TextInput(attrs={'class':'date_picker'}))
	include_fields = forms.MultipleChoiceField(required=False, widget=CheckboxSelectMultiple, choices=overdue_choices)

	def __init__(self, *args, **kw):
		super(DebtorsForm, self).__init__(*args, **kw)
		self.fields['district'].queryset = District.objects.all()
		self.fields['sector'].queryset = Sector.objects.all()
		self.fields['cell'].queryset = Cell.objects.all()
		self.fields['village'].queryset = Village.objects.all()
		self.initial = {'include_fields':[ i for (i,j) in overdue_choices ]}

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

