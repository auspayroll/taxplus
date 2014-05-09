from django import forms
from property.models import Sector,District, Cell

class select_property_form(forms.Form):
	plot_id = forms.CharField(max_length = 50, required = False)
	parcel_id = forms.IntegerField(required = False)
	village = forms.CharField(max_length = 50, required = False)
	cell = forms.CharField(max_length= 50, required = False)
	sector = forms.ChoiceField(required = False, choices = [('',''),])

	def __init__(self, *args, **kw):
		super(select_property_form, self).__init__(*args, **kw)
		sectors = [(o.id, o.district.name + '--' + o.name) for o in Sector.objects.select_related('district').all().order_by('district','name')]
		self.fields['sector'].choices += sectors

		
class select_property_upi_form(forms.Form):
	upi = forms.CharField(max_length = 100, required = False)
	district = forms.ChoiceField(required = False)
	
	sector_choices = [('','----------')]
	sector = forms.ChoiceField(required = False, choices = sector_choices)
	
	cell_choices = [('','----------')]
	cell = forms.ChoiceField(required = False, choices = cell_choices)
	
	parcel_id = forms.IntegerField(required = False)

	def __init__(self, *args, **kw):
		super(select_property_upi_form, self).__init__(*args, **kw)
		initial = kw.get('initial', {})

		district_choices = [('','----------')]
		district_choices.extend((o.id, o.name) for o in District.objects.all().order_by('name'))
		self.fields['district'] = forms.ChoiceField(required = False, choices = district_choices)

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
		if 'upi' in initial and initial['upi']:
			kw['initial']['upi'] = initial['upi']
	def clean(self):
		super(select_property_upi_form,self).clean()
		if 'sector' in self._errors:
			del self.errors['sector']
			self.cleaned_data['sector'] = self.data['sector']
		if 'cell' in self._errors:
			del self.errors['cell']
			self.cleaned_data['cell'] = self.data['cell']
		return self.cleaned_data
		

class select_district_form(forms.Form):
	name = forms.CharField(required = True)
	superuser = forms.BooleanField(required = False)
	

class select_council_form(forms.Form):
	name = forms.CharField(required = True)
	superuser = forms.BooleanField(required = False)


class select_sector_form(forms.Form):
	id = forms.IntegerField(required = True)
	name = forms.CharField(required = False)
	

