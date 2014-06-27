from django.db.models.loading import get_model
from django.forms import ModelForm
from django import forms
from asset.models import *
from citizen.models import Citizen
#from django.contrib.gis.geos import Point, GEOSGeometry, Polygon
from django.forms import model_to_dict
from log.models import Log
from log.mappers.LogMapper import LogMapper
import simplejson 
import datetime
from django.forms.util import ErrorList
from dev1 import settings
from annoying.functions import get_object_or_None
from property.mappers.PropertyMapper import PropertyMapper

class AssetModelForm(ModelForm):
	owner_ids = forms.CharField(widget=forms.HiddenInput(),  initial='', required = False)
	total_share = forms.FloatField(widget=forms.HiddenInput(), initial=0, required = False)
	owners = forms.CharField(widget=forms.HiddenInput(),  initial='', required = False)
	owner_select_options = forms.CharField(widget=forms.HiddenInput(),  initial='', required = False)
	class Meta:
		abstract = True
		exclude = ('i_status','date_created','owner_ids','total_share','owners','owner_select_options','foreign_record_id')

	def __init__(self, *args, **kwargs):
		#overwrite init to set up ownership for assets form
		
		initial = kwargs.get('initial', {})
		if 'id' in initial:
			asset_type = self.Meta.model.__name__.lower();
			asset_column = 'asset_' + asset_type
			#asset = {asset_type}.objects.filter()
			query = {asset_column : initial['id'],'i_status':'active'}
			ownerships = Ownership.objects.filter(**query)
			owner_ids = '';
			total_share = 0
			owners = ''
			owner_select_options = ''
			for i in ownerships:
				owner_type = ''
				if i.owner_citizen:
					owner = i.owner_citizen
					owner_label = owner.getDisplayName() + ' (CID: ' + owner.citizen_id + ') [ ' + str(i.share) + '% Share ]'
					owner_type = 'citizen'
				elif i.owner_business:
					owner = i.owner_business
					owner_label = owner.name + ' (TIN: ' + owner.tin + ') [ ' + str(i.share) + '% Share ]'
					owner_type = 'business'
				if owner:
					#set up ownership info for display purpose
					owner_ids += ',%d' % owner.id
					total_share += i.share
					owners += '{"id": "' + str(owner.id) + '", "share": "' + str(i.share) + '", "type": "' + owner_type + '"},'
					owner_select_options += '<option value="' + str(owner.id) + '" opt_share="' + str(i.share) + '" opt_type="' + owner_type + '" >' + owner_label  + '</option>'

			initial['owner_ids'] = owner_ids
			initial['owners'] = owners
			initial['owner_select_options'] = owner_select_options
			initial['total_share'] = total_share
		kwargs['initial'] = initial
		super(AssetModelForm, self).__init__(*args, **kwargs)

	def clean(self):
		#if self.cleaned_data['owners'] == '':
		#	asset_type = self.Meta.model.__name__.lower();
			#self._errors['owners'] =  ErrorList([u"Please specify the ownership for this new " + asset_type])
		#	raise forms.ValidationError("Please specify the ownership for this new " + asset_type)

		return super(AssetModelForm,self).clean()

	def save(self, request, commit=True):
		asset = super(AssetModelForm, self).save(commit=commit)
		if(commit):
			owners = simplejson.loads('[%s]' % self.cleaned_data['owners'][:-1])
			ownerIds = []
			actions = []
			for i in owners:
				ownerIds.append(i['id'])

			asset_type = self.Meta.model.__name__.lower();
			asset_column = 'asset_' + asset_type
			query = {asset_column : asset,'i_status':'active'}
			old_ownerships = Ownership.objects.filter(**query)

			#get list of ownerships to keep / delete / add
			deleteIds = []
			keepOwnerIds = []
			for i in old_ownerships:
				if i.owner_citizen and str(i.owner_citizen.id) not in ownerIds:
					deleteIds.append(i.id)
					actions.append(' deactivated Ownership of ' + i.owner_citizen.getDisplayName() + ' (CID: ' + i.owner_citizen.citizen_id + ')')
				elif i.owner_citizen and str(i.owner_citizen.id) in ownerIds:
					keepOwnerIds.append(i.owner_citizen.id)
				elif i.owner_business and str(i.owner_business.id) not in ownerIds:
					deleteIds.append(i.id)
					actions.append(' deactivated Ownership of ' + i.owner_business.name + ' (TIN: ' + i.owner_business.tin + ')')
				elif i.owner_business and str(i.owner_business.id) in ownerIds:
					keepOwnerIds.append(i.owner_business.id)

			#deactive any existing ownerships of this asset that has been removed
			if deleteIds:
				old_ownerships.filter(id__in=deleteIds).update(date_ended=datetime.date.today(),i_status='inactive')
				

			#add in new ownerships, ignore the one in the keepIds list
			for i in owners:
				if int(i['id']) not in keepOwnerIds:
					ownership = Ownership()
					ownership.share = i['share']
					ownership.date_started = datetime.date.today()
					if i['type']=='citizen':
						ownership.owner_citizen = get_object_or_None(Citizen,id=i['id'])
						actions.append(' added Ownership of ' + ownership.owner_citizen.getDisplayName() + ' (CID: ' + ownership.owner_citizen.citizen_id + ')')
					if i['type']=='business':
						ownership.owner_business = get_object_or_None(Business,id=i['id'])
						actions.append(' added Ownership of ' + ownership.owner_business.name + ' (TIN: ' + ownership.owner_business.tin + ')')

					if asset_type == 'business':
						ownership.asset_business = asset
					if asset_type == 'subbusiness':
						ownership.asset_subbusiness = asset
					if asset_type == 'property':
						ownership.asset_property = asset
					if asset_type == 'billboard':
						ownership.asset_billboard = asset
					if asset_type == 'vehicle':
						ownership.asset_vehicle = asset

					ownership.save()
					
			if actions:
				LogMapper.createLog(request,action="change", message= ','.join(actions) + " for " + asset_type.title() + " " + str(asset) )	   
		return asset

class BusinessForm(AssetModelForm):
	phone1 = forms.CharField(label='Phone')
	phone2 = forms.CharField(label='Phone Alt',required=False)
	business_category = forms.ModelChoiceField(label='Cleaning Fee Category', queryset=BusinessCategory.objects.all(), required=False)
	business_subcategory = forms.ModelChoiceField(label="Business Category", queryset=BusinessSubCategory.objects.all(), required=False)
	date_started = forms.DateField(widget=forms.DateInput(format = settings.DATE_INPUT_FORMAT), input_formats=settings.DATE_INPUT_FORMATS, help_text="e.g. '28/05/1975'")
	sector = forms.ModelChoiceField(queryset=Sector.objects.none(), required=True, error_messages={'required':'Sector is required'})

	district_choices = [('','----------')]
	district = forms.ChoiceField(required = False, choices = district_choices)
	
	class Meta(AssetModelForm.Meta):
		model = Business
		fields = ['name', 'tin', 'date_started', 'address', 'phone1', 'phone2', 'email', 'po_box', 'vat_register',
				  'business_category', 'business_subcategory', 'district', 'sector', 'cell', 'village', 'accountant_name', 'accountant_phone',
				  'accountant_email', 'market_fee_applicable', 'i_status']
		#exclude = ('pm_tin', 'foreign_record_id', 'credit','cp_password')


	def __init__(self, *args, **kwargs):
		super(BusinessForm, self).__init__(*args, **kwargs)

		district_choices = [('','----------')]
		district_choices.extend((o.id, o.name) for o in District.objects.all().order_by('name'))
		self.fields['district'].choices = district_choices
		self.fields['sector'].choices = [('','----------')]
		self.fields['cell'].choices = [('','----------')]
		self.fields['village'].choices = [('','----------')]
		#self.fields['business_subcategory'].choices = [('','----------')]

		if self.instance:
			if self.instance.village:
				village_list = Village.objects.filter(cell=self.instance.village.cell)
				village_choices = [('','----------')]
				if village_list:
					for village in village_list:
						village_choices.append([village.pk, village.name])
				self.fields['village'].choices = village_choices
				self.fields['village'].initial = self.instance.village.pk

			if self.instance.cell:
				sector = self.instance.cell.sector
				district = sector.district
				cell_list = Cell.objects.filter(sector = sector)
				cell_choices = [('','----------')]
				if cell_list:
					for tt in cell_list:
						cell_choices.append((tt.id, tt.name))
				self.fields['cell'].choices = cell_choices
				self.fields['cell'].initial = self.instance.cell.id

				sector_list = Sector.objects.filter(district = district)
				sector_choices = [('','----------')]
				if sector_list:
					for tt in sector_list:
						sector_choices.append((tt.id, tt.name))
				self.fields['sector'].choices = sector_choices
				self.fields['sector'].initial = sector.id
				self.fields['district'].initial = district.id
			elif self.instance.sector:
				sector = self.instance.sector
				district = sector.district
				cell_list = Cell.objects.filter(sector = sector)
				cell_choices = [('','----------')]
				if cell_list:
					for tt in cell_list:
						cell_choices.append((tt.id, tt.name))
				self.fields['cell'].choices = cell_choices
				#self.fields['cell'].value = self.instance.cell.id

				sector_list = Sector.objects.filter(district = district)
				sector_choices = [('','----------')]
				if sector_list:
					for tt in sector_list:
						sector_choices.append((tt.id, tt.name))
				self.fields['sector'].choices = sector_choices
				self.fields['sector'].initial = sector.id
				self.fields['district'].initial = district.id

		if args and len(args) > 0:
			if args[0].has_key('cell') and args[0]['cell']:
				cell = Cell.objects.get(pk=int(args[0]['cell']))
				sector = cell.sector
				district = sector.district

				cell_list = Cell.objects.filter(sector = sector)
				cell_choices = [('','----------')]
				if cell_list:
					for tt in cell_list:
						cell_choices.append((tt.id, tt.name))
				self.fields['cell'].choices = cell_choices
				self.fields['cell'].value = cell.id

				sector_list = Sector.objects.filter(district = district)
				sector_choices = [('','----------')]
				if sector_list:
					for tt in sector_list:
						sector_choices.append((tt.id, tt.name))
				self.fields['sector'].choices = sector_choices
				self.fields['sector'].value = cell.sector.id

			elif args[0].has_key('sector') and args[0]['sector']:
				sector = Sector.objects.get(pk=int(args[0]['sector']))
				district = sector.district
				cell_list = Cell.objects.filter(sector = sector)
				cell_choices = [('','----------')]
				if cell_list:
					for tt in cell_list:
						cell_choices.append((tt.id, tt.name))
				self.fields['cell'].choices = cell_choices

				sector_list = Sector.objects.filter(district = district)
				sector_choices = [('','----------')]
				if sector_list:
					for tt in sector_list:
						sector_choices.append((tt.id, tt.name))
				self.fields['sector'].choices = sector_choices
				self.fields['sector'].value = sector.id

				self.fields['district'].value = district.id
			elif args[0].has_key('district') and args[0]['district']:
				district = District.objects.get(pk=int(args[0]['district']))
				self.fields['district'].value = district.id

		self.fields['district'].widget.attrs['class'] = 'column_clear'
		self.fields['sector'].widget.attrs['class'] = 'column'
		self.fields['cell'].widget.attrs['class'] = 'column_clear'
		self.fields['village'].widget.attrs['class'] = 'column'
		self.fields['phone1'].widget.attrs['class'] = 'column'
		self.fields['village'].widget.attrs['class'] = 'column'
		self.fields['business_category'].widget.attrs['class'] = 'column'
		self.fields['business_subcategory'].widget.attrs['class'] = 'column'
		self.fields['accountant_name'].widget.attrs['class'] = 'column_clear'
		self.fields['accountant_phone'].widget.attrs['class'] = 'column'
		self.fields['accountant_email'].widget.attrs['class'] = 'column'
		self.fields['market_fee_applicable'].widget.attrs['class'] = 'clear'

	def clean(self):
		super(BusinessForm,self).clean()
		if 'cell' in self._errors:
			if self.data.get('cell'):
				del self.errors['cell']
				self.cleaned_data['cell']=Cell.objects.get(pk=self.data['cell'])
		if 'sector' in self._errors:
			if self.data.get('sector'):
				del self.errors['sector']
				self.cleaned_data['sector']=Sector.objects.get(pk=self.data['sector'])
		if 'district' in self._errors:
			if self.data.get('district'):
				del self.errors['district']
				self.cleaned_data['district']=Sector.objects.get(pk=self.data['district'])

			#del self.errors['cell']
			#self.cleaned_data['cell'] = self.data['cell']
		return self.cleaned_data


class ShopForm(AssetModelForm):
	phone1 = forms.CharField(label='Phone',help_text="Shop Phone")
	phone2 = forms.CharField(label='Phone Alt',required=False,help_text="Shop Alternative Phone")
	class Meta(AssetModelForm.Meta):
		model = Shop

class OfficeForm(AssetModelForm):
	phone1 = forms.CharField(label='Phone',help_text="Office Phone")
	phone2 = forms.CharField(label='Phone Alt',required=False,help_text="Office Alternative Phone")
	class Meta(AssetModelForm.Meta):
		model = Office

class StallForm(AssetModelForm):
	phone1 = forms.CharField(label='Phone',help_text="Stall Phone")
	phone2 = forms.CharField(label='Phone Alt',required=False,help_text="Stall Alternative Phone")
	class Meta(AssetModelForm.Meta):
		model = Stall

class BillboardForm(AssetModelForm):
	property = forms.CharField(label="UPI",help_text="The property that this hold this billboard.")
	class Meta(AssetModelForm.Meta):
		model = Billboard

	def clean_property(self):
		upi = self.cleaned_data['property']
		property = PropertyMapper.getPropertyByUPI(upi)
		if property:
			return property
		else:
			raise forms.ValidationError('Invalid UPI entered.')

class VehicleForm(AssetModelForm):

	class Meta(AssetModelForm.Meta):
		model = Vehicle

