from django import forms
from dev1 import settings
from property.models import District, Sector,Cell
from dev1.variables import *
from django.forms import model_to_dict
import datetime
from dev1 import ThreadLocal

class ReportSearchFormBasic(forms.Form):
	"""
	Enter searching criteria to generate report
	"""
	
	district_choices = [('','----------')]
	district = forms.ChoiceField(required = False, choices = district_choices)

	sector_choices = [('','----------')]
	sector = forms.ChoiceField(required = False, choices = sector_choices)
	
	cell_choices = [('','----------')]
	cell = forms.ChoiceField(required = False, choices = cell_choices)
	
	def __init__(self, request, *args, **kw):
		super(ReportSearchFormBasic, self).__init__(*args, **kw)

		district_choices = [('','----------')]
		district_list = District.objects.all().order_by('name')
		if district_list:
			for tt in district_list:
				district_choices.append((tt.id, tt.name))
		self.fields['district'].choices = district_choices
	
		
		if request.method == 'POST':
			district = request.POST.get('district')
			sector = request.POST.get('sector')

		elif request.method == 'GET':
			district = request.GET.get('district')
			sector = request.GET.get('sector')

		# populate sector list
		sector_choices = [('','-----------')]
		if district:
			sector_list = Sector.objects.filter(district__id = district)	
			if sector_list:
				for tt in sector_list:
					sector_choices.append((tt.id, tt.name)) 
				self.fields['sector'].choices = sector_choices
						
		# populate cell list
		cell_choices = [('','-----------')]
		if sector:
			cell_list = Cell.objects.filter(sector__id = sector)
			
			if cell_list:
				for tt in cell_list:
					cell_choices.append((tt.id, tt.name))
				self.fields['cell'].choices = cell_choices
			
	
	def clean(self):
		super(ReportSearchFormBasic,self).clean()
		if 'sector' in self._errors:
			del self.errors['sector']
			self.cleaned_data['sector'] = self.data['sector']

		if 'cell' in self._errors:
			del self.errors['cell']
			self.cleaned_data['cell'] = self.data['cell']

		return self.cleaned_data


class ReportSearchForm(forms.Form):
	"""
	Enter searching criteria to generate report
	"""
	tax_types_choices = [('All','All')]
	tax_types = forms.ChoiceField(widget=forms.CheckboxSelectMultiple, choices=tax_types_choices, required = False)
	
	district_choices = [('','----------')]
	district = forms.ChoiceField(required = False, choices = district_choices)

	sector_choices = [('','----------')]
	sector = forms.ChoiceField(required = False, choices = sector_choices)
	
	cell_choices = [('','----------')]
	cell = forms.ChoiceField(required = False, choices = cell_choices)
	
	citizen_id = forms.CharField(max_length = 50, required = False)
	upi = forms.CharField(max_length = 50, required = False)
	calendar_year = forms.ChoiceField(required = False)
	period_from = forms.DateTimeField(required = False,initial='', input_formats=settings.DATE_INPUT_FORMATS)
	period_to = forms.DateTimeField(required = False,initial='', input_formats=settings.DATE_INPUT_FORMATS)
	
	today = datetime.datetime.now()
	year = int(today.year)
	year_range = reversed(range(1950,year+1))
	year_options = ((o,o) for o in year_range)
	years = forms.MultipleChoiceField(choices = year_options, required = False, widget = forms.SelectMultiple(attrs={'size':'5',}))
	
	
	def __init__(self, request, *args, **kw):
		super(ReportSearchForm, self).__init__(*args, **kw)
		initial = kw.get('initial', {})
		
		
		tax_types_choices = [('All','All')]
		user = request.session['user']
		if user and user.getTaxTypes():
			for c in user.getTaxTypes():
				tax_types_choices.append((c.codename,c.displayname))
		self.fields['tax_types'].choices = tax_types_choices
	
		district_choices = [('','----------')]
		district_list = District.objects.all().order_by('name')
		if district_list:
			for tt in district_list:
				district_choices.append((tt.id, tt.name))
		self.fields['district'].choices = district_choices
	
		if 'district' in initial and initial['district']:
			sector_list = Sector.objects.filter(district = initial['district'])
			sector_choices = [('','----------')]
			if sector_list:
				for tt in sector_list:
					sector_choices.append((tt.id, tt.name)) 
			self.fields['sector'].choices = sector_choices
			kw['initial']['district'] = initial['district'].id
						
		if 'sector' in initial and initial['sector']:
			cell_list = Cell.objects.filter(sector = initial['sector'])
			cell_choices = [('','----------')]
			if cell_list:
				for tt in cell_list:
					cell_choices.append((tt.id, tt.name))
			self.fields['cell'].choices = cell_choices
			kw['initial']['sector'] = initial['sector'].id
			
		if 'cell' in initial and initial['cell']:
			kw['initial']['cell'] = initial['cell'].id
			
		if 'tax_types' in initial and initial['tax_types']:
			kw['initial']['tax_types'] = initial['tax_types']
	
		
		today = datetime.datetime.now()
		year = int(today.year)
		year_range = reversed(range(1950,year+1))
		year_options = ((o,o) for o in year_range)	
		self.fields['calendar_year'].choices = year_options
		
		if 'calendar_year' in initial and initial['calendar_year']:
			kw['initial']['calendar_year'] = initial['calendar_year']
			
		self.fields['period_from'].widget.attrs['class'] = 'date_picker'
		self.fields['period_to'].widget.attrs['class'] = 'date_picker'
		
		
	
	def clean(self):
		super(ReportSearchForm,self).clean()
		if 'sector' in self._errors:
			del self.errors['sector']
			self.cleaned_data['sector'] = self.data['sector']
		if 'cell' in self._errors:
			del self.errors['cell']
			self.cleaned_data['cell'] = self.data['cell']
		if 'years' in self.errors:
			del self.errors['years']
			self.cleaned_data['years'] = self.data['years']
		return self.cleaned_data



class UnpaidTaxSearchForm(forms.Form):
	"""
	Enter searching criteria to generate report
	"""
	
	tax_types_choices=[]
	
	tax_types = forms.ChoiceField(widget=forms.CheckboxSelectMultiple, choices=tax_types_choices, required = False)
	
	district_choices = [('','----------')]
	district = forms.ChoiceField(required = False, choices = district_choices)

	sector_choices = [('','----------')]
	sector = forms.ChoiceField(required = False, choices = sector_choices)
	
	cell_choices = [('','----------')]
	cell = forms.ChoiceField(required = False, choices = cell_choices)
	
	
	def __init__(self, request, *args, **kw):
		super(UnpaidTaxSearchForm, self).__init__(*args, **kw)
		initial = kw.get('initial', {})
		
		tax_types_choices=[]
		user = request.session['user']
		if user and user.getTaxTypes():
			for c in user.getTaxTypes():
				tax_types_choices.append((c.codename,c.displayname))
		self.fields['tax_types'].choices = tax_types_choices
		
		district_choices = [('','----------')]
		district_choices.extend((o.id, o.name) for o in District.objects.all().order_by('name'))
		self.fields['district'].choices = district_choices
		
		
		if 'district' in initial and initial['district']:
			sector_list = Sector.objects.filter(district = initial['district'])
			sector_choices = [('','----------')]
			sector_choices.extend((o.id, o.name) for o in sector_list)
			self.fields['sector'].choices = sector_choices
			kw['initial']['district'] = initial['district'].id
		if 'sector' in initial and initial['sector']:
			cell_list = Cell.objects.filter(sector = initial['sector'])
			cell_choices = [('','----------')]
			cell_choices.extend((o.id, o.name) for o in cell_list)
			self.fields['cell'].choices = cell_choices
			kw['initial']['sector'] = initial['sector'].id
		if 'cell' in initial and initial['cell']:
			kw['initial']['cell'] = initial['cell'].id
		if 'tax_types' in initial and initial['tax_types']:
			kw['initial']['tax_types'] = initial['tax_types']
	
	def clean(self):
		super(UnpaidTaxSearchForm,self).clean()
		if 'sector' in self._errors:
			del self.errors['sector']
			self.cleaned_data['sector'] = self.data['sector']
		if 'cell' in self._errors:
			del self.errors['cell']
			self.cleaned_data['cell'] = self.data['cell']
		return self.cleaned_data
	