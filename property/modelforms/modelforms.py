from django.forms import ModelForm
from django import forms
from property.models import *
from property.functions import *
from django.contrib.gis.geos import Point, GEOSGeometry, Polygon
from django.forms import model_to_dict
from log.models import Log
from property.mappers.DistrictMapper import DistrictMapper
from property.mappers.CouncilMapper import CouncilMapper
from log.mappers.LogMapper import LogMapper
from common.models import *

class PropertyCreationForm(forms.Form):
	"""
	Consider the boundary of a property as a polygon, then boundary textfield stores the coordinators of polygon vertices
	"""

	boundary = forms.CharField(widget=forms.Textarea)

	district_choices = [('','----------')]
	district = forms.ChoiceField(required = False, choices = district_choices)

	sector_choices = [('','----------')]
	sector = forms.ChoiceField(required = False, choices = sector_choices)

	cell_choices = [('','----------')]
	cell = forms.ChoiceField(required = False, choices = cell_choices)

	village_choices = [('','----------')]
	village = forms.ChoiceField(required = False, choices = village_choices)

	parcel_id = forms.IntegerField()
	is_leasing = forms.BooleanField(required = False)


	def __init__(self, *args, **kw):
		super(PropertyCreationForm, self).__init__(*args, **kw)
		initial = kw.get('initial', {})

		district_choices = [('','----------')]
		district_choices.extend((o.id, o.name) for o in District.objects.all().order_by('name'))
		self.fields['district']= forms.ChoiceField(required = False, choices = district_choices)

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

	def save(self,request):
		# create polygan
		plist=[]
		boundary=self.cleaned_data["boundary"]
		points = boundary.split('#')
		for point in points:
			parts = point.split(',')
			point_x=parts[0]
			point_y=parts[1]
			plist.append(GEOSGeometry('POINT(%s %s)' %(point_x, point_y)))
		plist.append(plist[0])
		polygon = Polygon(plist)
		boundary = Boundary.objects.create(polygon=polygon, type = "manual", i_status="active")
		property = forms.ModelForm.save(self, False)
		property.boundary = boundary
		property.status = Status.objects.get(name = 'Active')
		property.i_status="active"
		property.plot_id = getNextPlotId()
		property.save()
		new_data = model_to_dict(property)
		LogMapper.createLog(request,object=property,action="add")
		return property


class CouncilCreationForm(ModelForm):
	"""
	Consider the boundary of a district as a polygon, then boundary textfield stores the coordinators of polygon vertices
	"""

	boundary = forms.CharField(widget=forms.Textarea)
	class Meta:
		model = Council
		fields = ("name","address",)


class SectorCreationForm(ModelForm):
	"""
	Consider the boundary of a district as a polygon, then boundary textfield stores the coordinators of polygon vertices
	"""
	#councils = [(c.id, c.name) for c in CouncilMapper.getAllCouncils()]
	boundary = forms.CharField(widget=forms.Textarea)
	district = forms.ChoiceField(widget = forms.Select(),required = True, choices = ())
	#council = forms.ChoiceField(widget = forms.Select(),required = True, choices = councils)
	class Meta:
		model = Sector
		fields = ("name","council")
	def __init__(self, request, *args, **kwargs):
		super(SectorCreationForm, self).__init__(*args, **kwargs)
		districts = [(d.id, d.name) for d in DistrictMapper.getAllDistricts()]
		self.fields['districts'] = forms.ChoiceField(widget = forms.Select(),required = True, choices = districts)
		councils = None
		user = request.session.get('user')
		if user.is_superuser:
			councils = [(c.id, c.name) for c in CouncilMapper.getAllCouncils()]
		else:
			councils = [(user.council.id, user.council.name)]
		self.fields['council'] = forms.ChoiceField(widget = forms.Select(),required = True, choices = councils)


class DistrictCreationForm(ModelForm):
	"""
	Consider the boundary of a district as a polygon, then boundary textfield stores the coordinators of polygon vertices
	"""
	boundary = forms.CharField(widget=forms.Textarea)
	class Meta:
		model = District
		fields = ("name",)
	def save(self,request):
		## create polygan
		plist=[]
		boundary=self.cleaned_data["boundary"]
		points = boundary.split('#')
		for point in points:
			parts = point.split(',')
			point_x=parts[0]
			point_y=parts[1]
			plist.append(GEOSGeometry('POINT(%s %s)' %(point_x, point_y)))
		plist.append(plist[0])
		polygon = Polygon(plist)
		boundary = Boundary.objects.create(polygon=polygon, type = "manual", i_status="active")
		district = forms.ModelForm.save(self, False)
		district.boundary = boundary
		district.i_status="active"
		district.save()
		new_data = model_to_dict(district)
		LogMapper.createLog(request,object=district,action="add")
		return district


class PropertyUpdateTaxExemptForm(ModelForm):
	tax_exempt_reason = forms.ChoiceField(variables.tax_exempt_reasons,required=False,label="Reason")
	tax_exempt_note = forms.CharField(widget=forms.Textarea,required=False,label="Note")
	proof = forms.FileField(required=False,label="Document Proof")

	class Meta:
		model = Property
		fields = ['is_tax_exempt', 'tax_exempt_reason', 'tax_exempt_note','proof']

	def clean_proof(self):
		if self.cleaned_data['is_tax_exempt'] == False:
			return None
		else:
			if not self.cleaned_data['proof']:
				raise forms.ValidationError("Please upload proof of approval document for Tax Exempt!")

			return self.cleaned_data['proof']

	def clean_tax_exempt_note(self):
		if self.cleaned_data['is_tax_exempt'] == False:
			return None
		else:
			if self.cleaned_data['tax_exempt_reason'] == 'Other' and not self.cleaned_data['tax_exempt_note']:
				raise forms.ValidationError("Please describe Exempt Reason in the !")

			return self.cleaned_data['tax_exempt_note']

	def clean_tax_exempt_reason(self):
		if self.cleaned_data['is_tax_exempt'] == False:
			return None
		else:
			if not self.cleaned_data['tax_exempt_reason']:
				raise forms.ValidationError("Please select the Exempt Reason!")

			return self.cleaned_data['tax_exempt_reason']
