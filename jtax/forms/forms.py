from django import forms
from dev1.variables import *
from property.models import Sector, Cell, District
from django.forms.widgets import RadioSelect, CheckboxSelectMultiple
from dev1 import settings
from dev1 import variables
from asset.models import *
from admin.Common import Common
from jtax.models import *
from jtax.mappers.TaxMapper import TaxMapper
from jtax.mappers.DeclaredValueMapper import DeclaredValueMapper
from dev1 import ThreadLocal
from common.fields import CurrencyField

deferred_choices=[[i,"%s months" % i] for i in range(7)]
deferred_choices[0][1] = "No deferment"
deferred_choices[1][1] = "1 month"

class MiscFeeForm(forms.Form):
	quantity = forms.IntegerField(min_value=0)
	submit_details = forms.CharField(widget=forms.Textarea)


class PayFeesForm(forms.Form):
	receipt_no = forms.CharField(max_length = 50, required=False)
	bank =  forms.ChoiceField(choices=variables.banks)
	paid_on = forms.DateField(required=False, input_formats=settings.DATE_INPUT_FORMATS, initial=date.today().strftime('%d/%m/%Y'), widget=forms.TextInput(attrs={'class':'date_picker'}))
	manual_receipt = forms.CharField(max_length = 50, required=False)
	note = forms.CharField(required=False, help_text="note about this payment.", widget=forms.Textarea)

	def clean(self):
		cleaned_data = super(PayFeesForm, self).clean()
		if cleaned_data.get('bank') != 'N/A' and not cleaned_data.get('receipt_no'):
			self._errors["receipt_no"] = self.error_class(["Please enter a receipt number"])
		return cleaned_data

class LandLeaseForm(forms.Form):
	land_lease_choices = [('','----------')]
	land_lease_choices += variables.land_lease_types
	land_lease_type = forms.ModelChoiceField(queryset=LandUse.objects.all(), empty_label=None)
	exempt = forms.BooleanField(required=False)

class TradingLicenseForm(forms.Form):
	small_rural = forms.BooleanField(required=False)
	small_town = forms.BooleanField(required=False)
	small_kigali = forms.BooleanField(required=False)

	motorcycle_rural = forms.IntegerField(min_value=1, required=False, help_text=" each motorcycle")
	motorcycle_town = forms.IntegerField(min_value=1, required=False, help_text=" each motorcycle")
	motorcycle_kigali = forms.IntegerField(min_value=1, required=False, help_text=" each motorcycle")

	machine_rural = forms.BooleanField(required=False)
	machine_town = forms.BooleanField(required=False)
	machine_kigali = forms.BooleanField(required=False)

	car_rural = forms.IntegerField(min_value=1, required=False, help_text=" each vehicle")
	car_town = forms.IntegerField(min_value=1, required=False, help_text=" each vehicle")
	car_kigali = forms.IntegerField(min_value=1, required=False, help_text=" each vehicle")

	boat_rural = forms.IntegerField(min_value=1, required=False, help_text=" each motorboat")
	boat_town = forms.IntegerField(min_value=1, required=False, help_text=" each motorboat")
	boat_kigali = forms.IntegerField(min_value=1, required=False, help_text=" each motorboat")

	other_rural = forms.BooleanField(required=False)
	other_town = forms.BooleanField(required=False)
	other_kigali = forms.BooleanField(required=False)

	months_exempted = forms.TypedChoiceField(required = False, choices=[(i,i) for i in range(7)], coerce=lambda x: int(x), empty_value=0 )
	deferred = forms.TypedChoiceField(required = False, choices=deferred_choices, coerce=lambda x: int(x), empty_value=0 )
	exempt = forms.BooleanField(required=False)
	vat_registered = forms.TypedChoiceField(choices = [('Yes', 'Yes'),('No', 'No')], coerce=lambda x: True if x in ('Yes',1,True,'True') else False)

	turnover_choices = [(40000000, 'Yearly turnover up to 40,000,000 Rwf => 60,000 Rwf'), (60000000, 'From 40,000,001 to 60,000,000 Rwf => 90,000 Rwf'), \
		(150000000,'From 60,000,001 to 150,000,000 Rwf => 150,000 Rwf'), (150000001,'Above 150 Million Rwf => 250,000 Rwf')]
	turnover = forms.TypedChoiceField( widget=forms.RadioSelect, choices = turnover_choices, coerce=lambda x: Decimal(x), required=False)
	tin = forms.CharField(help_text='', required=False)

	def clean(self):
		cleaned_data = super(TradingLicenseForm, self).clean()
		for k, v in cleaned_data.iteritems(): # transform boolean values to int
			if v is True:
				cleaned_data[k] = 1

		if cleaned_data.get('vat_registered') and not cleaned_data.get('turnover'):
			self._errors['turnover'] = self.error_class([u"Turnover is required"])

		if cleaned_data.get('vat_registered') and not cleaned_data.get('tin'):
			pass #this may be needed in future
			#self._errors['tin'] = self.error_class([u"TIN is required for VAT Registered business"])
		
		return cleaned_data



class FixedAssetForm(forms.Form):
	land_use_choices = [('','----------')]
	land_use_choices += variables.land_use_types
	#declared_value = CurrencyField(required=True)
	land_use_type = forms.ModelMultipleChoiceField(queryset=LandUse.objects.filter(code__in=variables.fixed_asset_land_uses), widget=CheckboxSelectMultiple)
	declared_by = forms.CharField(widget=forms.HiddenInput())
	declared_on = forms.DateField(required=True, input_formats=settings.DATE_INPUT_FORMATS, widget=forms.TextInput(attrs={'class':'date_picker'}))
	declared_by_search = forms.CharField(help_text='begin typing citizen name or CID to search')
	exempt = forms.BooleanField(required=False)
	deferred = forms.TypedChoiceField(required = False, choices=deferred_choices, coerce=lambda x: int(x), empty_value=0 )
	declared_commercial_amount = CurrencyField()
	declared_residential_amount = CurrencyField()
	declared_agriculture_amount = CurrencyField()
	floor_count = forms.IntegerField(required=False)
	floor_total_square_meters = forms.FloatField(required=False)
	year_built = forms.IntegerField(required=False)

	def __init__(self, *args, **kwargs):
		property = kwargs.pop('property')
		super(FixedAssetForm, self).__init__(*args, **kwargs)
		#self.fields['declared_by'].queryset = property.currentOwners


class RentalIncomeForm(forms.Form):
		rental_income = CurrencyField(required=True)
		interest_paid = CurrencyField(required=True)
		exempt = forms.BooleanField(required=False)
		deferred = forms.TypedChoiceField(required = False, choices=deferred_choices, coerce=lambda x: int(x), empty_value=0 )

class finalize_land_lease_fee_form(forms.Form):
	incomplete_payment_id = forms.CharField(max_length = 100)
	peroperty = None

	district_choices = [('','----------')]
	district = forms.ChoiceField(choices = district_choices)

	sector_choices = [('','----------')]
	sector = forms.ChoiceField( choices = sector_choices)
	
	cell_choices = [('','----------')]
	cell = forms.ChoiceField(choices = cell_choices)
	
	village_choices = [('','----------')]
	village = forms.ChoiceField(choices = village_choices, required = False)
	
	parcel_id = forms.CharField(max_length = 100)
	
	land_lease_type = forms.ChoiceField(required = True, choices = land_lease_types)
	size_in_square_meter = forms.FloatField(required = False)
	
	period_from = forms.DateField()
	period_to = forms.DateField()
	paid_date = forms.DateField()
	paid_amount = forms.FloatField()
	bank_choices = [('','-----------')]
	bank_choices.extend(variables.banks)
	bank = forms.ChoiceField(choices = bank_choices)
	bank_receipt = forms.CharField(max_length=50)

	def __init__(self, *args, **kw):
		incomplete_payment = None
		if 'instance' in kw:
			incomplete_payment = kw['instance']
			del kw['instance']
		super(finalize_land_lease_fee_form, self).__init__(*args, **kw)
		district_list = District.objects.all().order_by('name')
		district_choices = [('','----------')]
		district_choices.extend((o.id, o.name) for o in district_list)
		self.fields['district'].choices = district_choices

		if incomplete_payment:
			self.fields['incomplete_payment_id'].initial = incomplete_payment.id
			self.fields['incomplete_payment_id'].widget =self.fields['incomplete_payment_id'].hidden_widget() 

			if incomplete_payment.district:
				sector_list = Sector.objects.filter(district = incomplete_payment.district)
				sector_choices = [('','----------')]
				if sector_list:
					for tt in sector_list:
						sector_choices.append((tt.id, tt.name)) 
				self.fields['sector'].choices = sector_choices
				self.fields['district'].initial = incomplete_payment.district.id
							
			if incomplete_payment.sector:
				cell_list = Cell.objects.filter(sector = incomplete_payment.sector)
				cell_choices = [('','----------')]
				if cell_list:
					for tt in cell_list:
						cell_choices.append((tt.id, tt.name))
				self.fields['cell'].choices = cell_choices
				self.fields['sector'].initial = incomplete_payment.sector.id
				
			if incomplete_payment.cell:
				village_list = Village.objects.filter(cell = incomplete_payment.cell)
				village_choices = [('','----------')]
				if village_list:
					for tt in village_list:
						village_choices.append((tt.id, tt.name))
				self.fields['village'].choices = village_choices
				self.fields['cell'].initial = incomplete_payment.cell.id
			
			if incomplete_payment.village:
				self.fields['village'].initial = incomplete_payment.village.id
				
				
			self.fields['parcel_id'].initial = incomplete_payment.parcel_id
			self.fields['period_from'].initial = incomplete_payment.period_from
			self.fields['period_to'].initial = incomplete_payment.period_to
			self.fields['paid_date'].initial = incomplete_payment.paid_date
			self.fields['paid_amount'].initial = incomplete_payment.paid_amount
			self.fields['bank'].initial = incomplete_payment.bank
			self.fields['land_lease_type'].initial = ''
			self.fields['size_in_square_meter'].initial = ''
		elif args and args[0]:
			
			if args[0].has_key('district') and args[0]['district']:
				sector_list = Sector.objects.filter(district = args[0]['district'])
				sector_choices = [('','----------')]
				if sector_list:
					for tt in sector_list:
						sector_choices.append((tt.id, tt.name)) 
				self.fields['sector'].choices = sector_choices
				self.fields['district'].initial = args[0]['district']
							
			if args[0].has_key('sector') and args[0]['sector']:
				cell_list = Cell.objects.filter(sector = args[0]['sector'])
				cell_choices = [('','----------')]
				if cell_list:
					for tt in cell_list:
						cell_choices.append((tt.id, tt.name))
				self.fields['cell'].choices = cell_choices
				self.fields['sector'].initial = args[0]['sector']
				
			if args[0].has_key('cell') and args[0]['cell']:
				village_list = Village.objects.filter(cell = args[0]['cell'])
				village_choices = [('','----------')]
				if village_list:
					for tt in village_list:
						village_choices.append((tt.id, tt.name))
				self.fields['village'].choices = village_choices
				self.fields['cell'].initial = args[0]['cell']
			
			if args[0].has_key('village') and args[0]['village']:
				self.fields['village'].initial = args[0]['village']
			
			if args[0].has_key('land_lease_type') and args[0]['land_lease_type']:
				self.fields['land_lease_type'].initial = args[0]['land_lease_type']
			
			if args[0].has_key('size_in_square_meter') and args[0]['size_in_square_meter']:
				self.fields['size_in_square_meter'].initial = args[0]['size_in_square_meter']
		
		self.fields['period_from'].widget.attrs['class'] = 'date_picker'
		self.fields['period_from'].widget.format = settings.DATE_INPUT_FORMAT
		self.fields['period_from'].input_formats=['%d/%m/%Y']
		self.fields['period_to'].widget.attrs['class'] = 'date_picker'
		self.fields['period_to'].widget.format = settings.DATE_INPUT_FORMAT
		self.fields['period_to'].input_formats=['%d/%m/%Y']
		self.fields['paid_date'].widget.attrs['class'] = 'date_picker'
		self.fields['paid_date'].widget.format = settings.DATE_INPUT_FORMAT
		self.fields['paid_date'].input_formats=['%d/%m/%Y']
		
		
		if self.fields['sector'].initial and self.fields['cell'].initial and self.fields['parcel_id'].initial:
			try:
				int(self.fields['parcel_id'].initial)
				property = Property.objects.filter(sector__id = self.fields['sector'].initial, cell__id = self.fields['cell'].initial, parcel_id = self.fields['parcel_id'].initial)
				if self.fields['village'].initial:
					property = property.filter(village__id = self.fields['village'].initial)
				if property and len(property) == 1:
					if property.land_lease_type:
						self.fields['land_lease_type'].initial = int(property.land_lease_type)
					if property.size_sqm:
						self.fields['size_in_square_meter'].initial = int(property.size_sqm)
					elif property.size_hectare:
						self.fields['size_in_square_meter'].initial = int(property.size_hectare * 10000)
			except:
				pass
		
	def clean(self):
		data = self.cleaned_data
		incomplete_payment_id = data.get('incomplete_payment_id','')
		paid_amount = data.get('paid_amount',0)
		period_from = data.get('period_from','')
		period_to = data.get('period_to','')
		paid_date = data.get("paid_date",'')
		bank = data.get('bank','')
		bank_receipt = data.get('bank_receipt','')
		district = data.get('district','')
		sector = data.get('sector','')
		cell = data.get('cell','')
		village = data.get('village','')
		parcel_id = data.get('parcel_id','')
		land_lease_type = data.get('land_lease_type','')
		size_in_square_meter = data.get('size_in_square_meter','')
		
		self.fields['incomplete_payment_id'].widget =self.fields['incomplete_payment_id'].hidden_widget()
		incomplete_payment = IncompletePayment.objects.get(pk = incomplete_payment_id)
		
		if not land_lease_type:
			self.errors['land_lease_type'] = ['Please select land lease type']
		if not size_in_square_meter:
			self.errors['size_in_square_meter'] = ['Please enter size in square meter']
		district_choices = [('','----------')]
		district_list = District.objects.all().order_by('name')
		if district_list:
			for tt in district_list:
				district_choices.append((tt.id, tt.name))
		self.fields['district'].widget.choices = district_choices
		
		if district:
			sector_list = Sector.objects.filter(district__id = district)
			sector_choices = [('','----------')]
			if sector_list:
				for tt in sector_list:
					sector_choices.append((tt.id, tt.name)) 
			self.fields['sector'].choices = sector_choices
			self.fields['district'].initial = district
			incomplete_payment.district = District.objects.get(pk = district)
						
		if sector:
			cell_list = Cell.objects.filter(sector__id = sector)
			cell_choices = [('','----------')]
			if cell_list:
				for tt in cell_list:
					cell_choices.append((tt.id, tt.name))
			self.fields['cell'].choices = cell_choices
			self.fields['sector'].initial = sector
			incomplete_payment.sector = Sector.objects.get(pk = sector)
			
		if cell:
			village_list = Village.objects.filter(cell__id = cell)
			village_choices = [('','----------')]
			if village_list:
				for tt in village_list:
					village_choices.append((tt.id, tt.name))
			self.fields['village'].choices = village_choices
			self.fields['cell'].initial = cell
			incomplete_payment.cell = Cell.objects.get(pk = cell)
		
		if village:
			self.fields['village'].initial = village
			incomplete_payment.village = Village.objects.get(pk = village)
			
		if parcel_id:
			self.fields['parcel_id'].initial = parcel_id
		
		incomplete_payment.paid_amount = paid_amount
		if period_from:
			incomplete_payment.period_from = period_from
		if period_to:
			incomplete_payment.period_to = period_to
		if paid_amount:
			incomplete_payment.paid_amount = paid_amount
		else:
			self.errors['paid_amount'] = ['Paid amount is invalid!']
		if paid_date:
			incomplete_payment.paid_date = paid_date
		if period_from and period_to:
			if period_to < period_from:
				self.errors['period_to'] = ['Period to should be after period from!']
			elif period_from.year!=period_to.year:
				self.errors['period_to'] = ['Period from and period to should be within the same year!']
		
		incomplete_payment.bank = bank
		incomplete_payment.bank_receipt = bank_receipt
		incomplete_payment.parcel_id = parcel_id
		incomplete_payment.save()
		if sector and cell and parcel_id:
			try:
				int(parcel_id)
				property = None
				if village:
					property = Property.objects.filter(sector__id = sector, cell__id = cell, village = village, parcel_id = parcel_id)
				else:
					property = Property.objects.filter(sector__id = sector, cell__id = cell, parcel_id = parcel_id)
				if not property:
					self.errors['parcel_id'] = ['This property does not exist!']
				elif len(property) > 1:
					self.errors['parcel_id'] = ['Multiple properties found. Please select a village!']
			except:
				self.errors['parcel_id'] = ['Please enter a valid plot ID!']

		if self.fields['sector'].initial and self.fields['cell'].initial and self.fields['parcel_id'].initial:
			try:
				int(parcel_id)
				property = Property.objects.filter(sector__id = self.fields['sector'].initial, cell__id = self.fields['cell'].initial, parcel_id = self.fields['parcel_id'].initial)
				if self.fields['village'].initial:
					property = property.filter(village__id = self.fields['village'].initial)
				if property and len(property) == 1:
					property = property[0]
					if land_lease_type:
						property.land_lease_type = land_lease_type
						self.fields['land_lease_type'].initial = land_lease_type
					if size_in_square_meter:
						property.size_sqm = int(size_in_square_meter)
						self.fields['size_in_square_meter'].initial = size_in_square_meter
					property.save()
			except:
				self.errors['parcel_id'] = ['Please enter a valid plot ID!']
		return self.cleaned_data


class finalize_trading_license_tax_form(forms.Form):
	incomplete_payment_id = forms.CharField(max_length = 100)
	tin = forms.CharField(max_length = 100, required=False)
	business_select = forms.CharField(max_length = 100, label='Business', required=False)
	business = forms.CharField(widget=forms.HiddenInput(), max_length = 100, label='Business ID', initial=None,required=False)
	subbusiness_choices = [('','-----------')]
	subbusiness = forms.ChoiceField(choices = subbusiness_choices, initial=None,required=False)
	turnover = forms.FloatField(required=False)

	# fields needed for jtax_fee table
	period_from = forms.DateField()
	period_to = forms.DateField()
	paid_date = forms.DateField()
	
	# fields needed for jtax_payfee table
	paid_amount = forms.FloatField()
	
	bank_choices = [('','-----------')]
	bank_choices.extend(variables.banks)
	bank = forms.ChoiceField(choices = bank_choices)
	
	bank_receipt = forms.CharField(max_length=50)
	
	def __init__(self, *args, **kw):
		business = None
		subbusiness = None
		incomplete_payment = None
		period_from = None
		period_to = None
		paid_date = None
		
		if 'instance' in kw:
			incomplete_payment = kw['instance']
			del kw['instance']
		initial = kw.get('initial', {})
		initial['business'] = None

		if incomplete_payment:
			initial['incomplete_payment_id'] = incomplete_payment.id
			initial['tin'] = incomplete_payment.tin
			initial['paid_amount'] = incomplete_payment.paid_amount
			initial['period_from'] = incomplete_payment.period_from
			initial['period_to'] = incomplete_payment.period_to
			initial['paid_date'] = incomplete_payment.paid_date
			initial['bank'] = incomplete_payment.bank
			initial['bank_receipt'] = incomplete_payment.bank_receipt
			initial['turnover'] = 0
			
			business = incomplete_payment.business
			subbusiness = incomplete_payment.subbusiness

		if args and args[0]:
			initial['incomplete_payment_id'] = args[0]['incomplete_payment_id']
			initial['tin'] = args[0]['tin']
			initial['paid_amount'] = args[0]['paid_amount']
			initial['period_from'] = Common.to_standard_date(args[0]['period_from'])
			initial['period_to'] = Common.to_standard_date(args[0]['period_to'])
			initial['paid_date'] = Common.to_standard_date(args[0]['paid_date'])
			initial['bank'] = args[0]['bank']
			initial['bank_receipt'] = args[0]['bank_receipt']
			initial['turnover'] = args[0]['turnover']
			
			if args[0].has_key('business') and args[0]['business'] != '':
				try:
					business = Business.objects.get(pk = args[0]['business'])
				except Exception:
					business = None
			if args[0].has_key('subbusiness')and args[0]['subbusiness'] != '':
				subbusiness = args[0]['subbusiness']

		kw['initial'] = initial
		super(finalize_trading_license_tax_form, self).__init__(*args, **kw)
			
		self.fields['period_from'].widget.attrs['class'] = 'date_picker'
		self.fields['period_from'].widget.format = settings.DATE_INPUT_FORMAT
		self.fields['period_from'].input_formats=['%d/%m/%Y']
		self.fields['period_to'].widget.attrs['class'] = 'date_picker'
		self.fields['period_to'].widget.format = settings.DATE_INPUT_FORMAT
		self.fields['period_to'].input_formats=['%d/%m/%Y']
		self.fields['paid_date'].widget.attrs['class'] = 'date_picker'
		self.fields['paid_date'].widget.format = settings.DATE_INPUT_FORMAT
		self.fields['paid_date'].input_formats=['%d/%m/%Y']

		if business:
			initial['business_select'] = business.name
			initial['business'] = business.id  
			subbusiness_choices = [('','-----------')]
			subbusiness_choices.extend((o.id, o.branch) for o in business.subbusiness_set.all().order_by('branch'))
			self.fields['subbusiness'].choices = subbusiness_choices
		if subbusiness:
			if type(subbusiness) is SubBusiness:
				self.fields['subbusiness'].initial = subbusiness.id
			else:
				self.fields['subbusiness'].value = subbusiness


		# hide incomplete payment id field
		self.fields['incomplete_payment_id'].widget = self.fields['incomplete_payment_id'].hidden_widget()
		
		
		# validate bank and bank receipt
		if not initial['bank']:
			self.errors['bank'] = ['bank is not selected!']
		if not initial['bank_receipt']:
			self.errors['bank_receipt'] = ['bank receipt is not entered!']
		if not initial['paid_amount']:
			self.errors['paid_amount'] = ['please enter a valid paid amount!']

		if not initial['paid_date']:
			self.errors['paid_date'] = ['paid date is not entered!']
		
		if not business:
			self.errors['business'] = ['Please input a valid business (select from suggestion list)!']
		
		if not initial['period_from']:
			self.errors['period_from'] = ['period from can not be empty!']
		else:
			import calendar
			period_from = Common.to_standard_date(str(initial['period_from']))
			period_from = datetime.strptime(period_from,'%Y-%m-%d')
	
		if not initial['period_to']:
			self.errors['period_to'] = ['period to can not be empty!']
		else:
			import calendar
			period_to = Common.to_standard_date(str(initial['period_to']))
			period_to = datetime.strptime(period_to,'%Y-%m-%d')
	
		if period_from and period_to:
			if period_from.year != period_to.year:
				self.errors['period_to'] = ['"Period from and period to should be within the same year!"']
		
	def clean(self):
		data = self.cleaned_data
		incomplete_payment_id = data.get('incomplete_payment_id','')
		tin = data.get('tin','')
		business = None
		subbusiness = None
		if data.has_key('business') and data['business'] != '':
			business = Business.objects.get(pk=data.get('business',''),i_status='active')
		if data.has_key('subbusiness') and data['subbusiness'] != '':
			subbusiness = SubBusiness.objects.get(pk=data.get('subbusiness',''),i_status='active')
		paid_amount = data.get('paid_amount',0)
		period_from = data.get('period_from','')
		period_to = data.get('period_to','')
		paid_date = data.get("paid_date",'')
		bank = data.get('bank','')
		bank_receipt = data.get('bank_receipt','')
		turnover = data.get('turnover',0)
				
		incomplete_payment = None
		
		if incomplete_payment_id:
			incomplete_payment = IncompletePayment.objects.get(pk = int(incomplete_payment_id))
		if incomplete_payment:
			if tin:
				incomplete_payment.tin = tin
			else:
				if incomplete_payment.tin:
					tin = incomplete_payment.tin
					self.cleaned_data['tin'] = tin
			if business:
				incomplete_payment.business = business
				self.cleaned_data['business'] = business
			else:
				if incomplete_payment.business:
					business = incomplete_payment.business
					self.cleaned_data['business'] = business
			if subbusiness:
				incomplete_payment.subbusiness = subbusiness
				self.cleaned_data['subbusiness'] = subbusiness
			else:
				if incomplete_payment.subbusiness:
					subbusiness = incomplete_payment.subbusiness
					self.cleaned_data['subbusiness'] = subbusiness
			if paid_amount:
				incomplete_payment.paid_amount = paid_amount
			else:
				if incomplete_payment.paid_amount:
					paid_amount = incomplete_payment.paid_amount
					self.cleaned_data['paid_amount'] = paid_amount
			if period_from:
				incomplete_payment.period_from = period_from
			else:
				if incomplete_payment.period_from:
					period_from = incomplete_payment.period_from
					self.cleaned_data['period_from'] = period_from
			if period_to:
				incomplete_payment.period_to = period_to
			else:
				if incomplete_payment.period_to:
					period_to = incomplete_payment.period_to
					self.cleaned_data['period_to'] = period_to
			if bank:
				incomplete_payment.bank = bank
			else:
				if incomplete_payment.bank:
					bank = incomplete_payment.bank
					self.cleaned_data['bank'] = bank
			if bank_receipt:
				incomplete_payment.bank_receipt = bank_receipt
			else:
				if incomplete_payment.bank_receipt:
					bank_receipt = incomplete_payment.bank_receipt
					self.cleaned_data['bank_receipt'] = bank_receipt
			if paid_date:
				incomplete_payment.paid_date = paid_date
			else:
				if incomplete_payment.paid_date:
					paid_date = incomplete_payment.paid_date
					self.cleaned_data['paid_date'] = Common.to_standard_date(paid_date)
			incomplete_payment.save()
		
		if not bank:
			self.errors['bank'] = ['bank is not selected!']
		if not bank_receipt:
			self.errors['bank_receipt'] = ['bank receipt is not entered!']
		
		period_valid = True
		if not paid_date:
			self.errors['paid_date'] = ['paid date is not entered!']
		if not paid_amount:			
			self.errors['paid_amount'] = ['Paid amount can not be empty!']
		if not period_from:
			period_valid = False
			self.errors['period_from'] = ['Period from can not be empty!']
		if not period_to:
			period_valid = False
			self.errors['period_to'] = ['Period to can not be empty!']
		
		if period_valid:
			if period_from.year!=period_to.year:
				period_valid = False
				self.errors['period_to'] = ['Period from and period to should be within the same year!']
				
			if period_valid:
				date_boundary = datetime.strptime('01/04/2013','%d/%m/%Y').date()
				if period_to < date_boundary or period_from <date_boundary:
					if paid_amount:
						self.cleaned_data['paid_amount']= int(paid_amount)
		if paid_date:
			if self.errors.has_key('paid_date'):
				del self.errors['paid_date']
		
		return self.cleaned_data	


class finalize_fixed_asset_tax_form(forms.Form):
	incomplete_payment_id = forms.CharField(max_length = 100)
	
	peroperty = None

	district_choices = [('','----------')]
	district = forms.ChoiceField(choices = district_choices)

	sector_choices = [('','----------')]
	sector = forms.ChoiceField( choices = sector_choices)
	
	cell_choices = [('','----------')]
	cell = forms.ChoiceField(choices = cell_choices)
	
	village_choices = [('','----------')]
	village = forms.ChoiceField(choices = village_choices, required = False)
	
	parcel_id = forms.CharField(max_length = 100)
	
	declared_value = forms.FloatField(required = False)
	period_from = forms.DateField()
	period_to = forms.DateField()
	paid_date = forms.DateField()
	paid_amount = forms.FloatField()
	bank_choices = [('','-----------')]
	bank_choices.extend(variables.banks)
	bank = forms.ChoiceField(choices = bank_choices)
	bank_receipt = forms.CharField(max_length=50)

	def __init__(self, *args, **kw):
		incomplete_payment = None
		if 'instance' in kw:
			incomplete_payment = kw['instance']
			del kw['instance']
		super(finalize_fixed_asset_tax_form, self).__init__(*args, **kw)

		district_choices = [('','----------')]
		district_list = District.objects.all().order_by('name')
		district_choices.extend((o.id, o.name) for o in district_list)
		self.fields['district'] = forms.ChoiceField(choices = district_choices)

		if incomplete_payment:
			self.fields['incomplete_payment_id'].initial = incomplete_payment.id
			self.fields['incomplete_payment_id'].widget =self.fields['incomplete_payment_id'].hidden_widget() 
			
			district_choices = [('','----------')]
			if district_list:
				for tt in district_list:
					district_choices.append((tt.id, tt.name))
			self.fields['district'].widget.choices = district_choices
			
			if incomplete_payment.district:
				sector_list = Sector.objects.filter(district = incomplete_payment.district)
				sector_choices = [('','----------')]
				if sector_list:
					for tt in sector_list:
						sector_choices.append((tt.id, tt.name)) 
				self.fields['sector'].choices = sector_choices
				self.fields['district'].initial = incomplete_payment.district.id
							
			if incomplete_payment.sector:
				cell_list = Cell.objects.filter(sector = incomplete_payment.sector)
				cell_choices = [('','----------')]
				if cell_list:
					for tt in cell_list:
						cell_choices.append((tt.id, tt.name))
				self.fields['cell'].choices = cell_choices
				self.fields['sector'].initial = incomplete_payment.sector.id
				
			if incomplete_payment.cell:
				village_list = Village.objects.filter(cell = incomplete_payment.cell)
				village_choices = [('','----------')]
				if village_list:
					for tt in village_list:
						village_choices.append((tt.id, tt.name))
				self.fields['village'].choices = village_choices
				self.fields['cell'].initial = incomplete_payment.cell.id
			
			if incomplete_payment.village:
				self.fields['village'].initial = incomplete_payment.village.id
				
				
			self.fields['parcel_id'].initial = incomplete_payment.parcel_id
			self.fields['period_from'].initial = incomplete_payment.period_from
			self.fields['period_to'].initial = incomplete_payment.period_to
			self.fields['paid_date'].initial = incomplete_payment.paid_date
			self.fields['paid_amount'].initial = incomplete_payment.paid_amount
			self.fields['bank'].initial = incomplete_payment.bank
			self.fields['bank_receipt'].initial = incomplete_payment.bank_receipt
			
		elif args and args[0]:
			district_choices = [('','----------')]
			if district_list:
				for tt in district_list:
					district_choices.append((tt.id, tt.name))
			self.fields['district'].widget.choices = district_choices
			
			if args[0].has_key('district') and args[0]['district']:
				sector_list = Sector.objects.filter(district = args[0]['district'])
				sector_choices = [('','----------')]
				if sector_list:
					for tt in sector_list:
						sector_choices.append((tt.id, tt.name)) 
				self.fields['sector'].choices = sector_choices
				self.fields['district'].initial = args[0]['district']
							
			if args[0].has_key('sector') and args[0]['sector']:
				cell_list = Cell.objects.filter(sector = args[0]['sector'])
				cell_choices = [('','----------')]
				if cell_list:
					for tt in cell_list:
						cell_choices.append((tt.id, tt.name))
				self.fields['cell'].choices = cell_choices
				self.fields['sector'].initial = args[0]['sector']
				
			if args[0].has_key('cell') and args[0]['cell']:
				village_list = Village.objects.filter(cell = args[0]['cell'])
				village_choices = [('','----------')]
				if village_list:
					for tt in village_list:
						village_choices.append((tt.id, tt.name))
				self.fields['village'].choices = village_choices
				self.fields['cell'].initial = args[0]['cell']
			
			if args[0].has_key('village') and args[0]['village']:
				self.fields['village'].initial = args[0]['village']
		
		self.fields['period_from'].widget.attrs['class'] = 'date_picker'
		self.fields['period_from'].widget.format = settings.DATE_INPUT_FORMAT
		self.fields['period_from'].input_formats=['%d/%m/%Y']
		self.fields['period_to'].widget.attrs['class'] = 'date_picker'
		self.fields['period_to'].widget.format = settings.DATE_INPUT_FORMAT
		self.fields['period_to'].input_formats=['%d/%m/%Y']
		self.fields['paid_date'].widget.attrs['class'] = 'date_picker'
		self.fields['paid_date'].widget.format = settings.DATE_INPUT_FORMAT
		self.fields['paid_date'].input_formats=['%d/%m/%Y']
		
		
		if self.fields['sector'].initial and self.fields['cell'].initial and self.fields['parcel_id'].initial:
			try:
				property = Property.objects.filter(sector__id = self.fields['sector'].initial, cell__id = self.fields['cell'].initial, parcel_id = self.fields['parcel_id'].initial)
				if self.fields['village'].initial:
					property = property.filter(village__id = self.fields['village'].initial)
				if property and len(property) == 1:
					declared_value = DeclaredValueMapper.getDeclaredValueByProperty(property[0])
					if declared_value:
						self.fields['declared_value'].initial = declared_value.amount
			except:
				print ''


		
	def clean(self):
		data = self.cleaned_data
		incomplete_payment_id = data.get('incomplete_payment_id','')
		paid_amount = data.get('paid_amount',0)
		period_from = data.get('period_from','')
		period_to = data.get('period_to','')
		paid_date = data.get("paid_date",'')
		bank = data.get('bank','')
		bank_receipt = data.get('bank_receipt','')
		district = data.get('district','')
		sector = data.get('sector','')
		cell = data.get('cell','')
		village = data.get('village','')
		parcel_id = data.get('parcel_id','')
		declared_value = data.get('declared_value','')
		
		self.fields['incomplete_payment_id'].widget =self.fields['incomplete_payment_id'].hidden_widget()
		incomplete_payment = IncompletePayment.objects.get(pk = incomplete_payment_id)
		
		district_choices = [('','----------')]
		district_list = District.objects.all().order_by('name')
		if district_list:
			for tt in district_list:
				district_choices.append((tt.id, tt.name))
		self.fields['district'].widget.choices = district_choices
		
		if district:
			sector_list = Sector.objects.filter(district__id = district)
			sector_choices = [('','----------')]
			if sector_list:
				for tt in sector_list:
					sector_choices.append((tt.id, tt.name)) 
			self.fields['sector'].choices = sector_choices
			self.fields['district'].initial = district
			incomplete_payment.district = District.objects.get(pk = district)
						
		if sector:
			cell_list = Cell.objects.filter(sector__id = sector)
			cell_choices = [('','----------')]
			if cell_list:
				for tt in cell_list:
					cell_choices.append((tt.id, tt.name))
			self.fields['cell'].choices = cell_choices
			self.fields['sector'].initial = sector
			incomplete_payment.sector = Sector.objects.get(pk = sector)
			
		if cell:
			village_list = Village.objects.filter(cell__id = cell)
			village_choices = [('','----------')]
			if village_list:
				for tt in village_list:
					village_choices.append((tt.id, tt.name))
			self.fields['village'].choices = village_choices
			self.fields['cell'].initial = cell
			incomplete_payment.cell = Cell.objects.get(pk = cell)
		
		if village:
			self.fields['village'].initial = village
			incomplete_payment.village = Village.objects.get(pk = village)
			
		if parcel_id:
			self.fields['parcel_id'].initial = parcel_id
			try:
				int(parcel_id)
			except:
				self.errors['parcel_id'] = ['Please enter a valid parcel ID!']
		
		incomplete_payment.paid_amount = paid_amount
		if period_from:
			incomplete_payment.period_from = period_from
		if period_to:
			incomplete_payment.period_to = period_to
		if paid_amount:
			incomplete_payment.paid_amount = paid_amount
		else:
			self.errors['paid_amount'] = ['Paid amount is invalid!']
		if paid_date:
			incomplete_payment.paid_date = paid_date
		if period_from and period_to:
			if period_to < period_from:
				self.errors['period_to'] = ['Period to should be after period from!']
			elif period_from.year!=period_to.year:
				self.errors['period_to'] = ['Period from and period to should be within the same year!']
		
		incomplete_payment.bank = bank
		incomplete_payment.bank_receipt = bank_receipt
		incomplete_payment.parcel_id = parcel_id
		incomplete_payment.save()
		if sector and cell and parcel_id:
			try:
				int(parcel_id)
				property = None
				if village:
					property = Property.objects.filter(sector__id = sector, cell__id = cell, village = village, parcel_id = parcel_id)
				else:
					property = Property.objects.filter(sector__id = sector, cell__id = cell, parcel_id = parcel_id)
				if not property:
					self.errors['parcel_id'] = ['This property does not exist!']
				elif len(property) > 1:
					self.errors['parcel_id'] = ['Multiple properties found. Please select a village!']
			except:
				self.errors['parcel_id'] = ['Please enter a valid parcel ID!']
		if self.fields['sector'].initial and self.fields['cell'].initial and self.fields['parcel_id'].initial:
			try:
				int(self.fields['parcel_id'].initial)
				property = Property.objects.filter(sector__id = self.fields['sector'].initial, cell__id = self.fields['cell'].initial, parcel_id = self.fields['parcel_id'].initial)
				if self.fields['village'].initial:
					property = property.filter(village__id = self.fields['village'].initial)
				if property and len(property) == 1:
					property = property[0]
					latest_declared_value = DeclaredValueMapper.getDeclaredValueByProperty(property)

					if declared_value:
						if not latest_declared_value or (latest_declared_value and latest_declared_value.amount!=declared_value):
							new_declared_value = DeclaredValue()
							new_declared_value.amount = declared_value
							new_declared_value.currency = 'RWF'
							new_declared_value.date_time = datetime.now()
							new_declared_value.accepted = 'YE'
							new_declared_value.property = property
							user = ThreadLocal.get_current_user()
							new_declared_value.user = user
							new_declared_value.save()
						self.fields['declared_value'].initial = declared_value
					else:
						self.errors['parcel_id'] = ['This property is not declared yet!']
			except:
				self.errors['parcel_id'] = ['Please enter a valid parcel ID!']
		return self.cleaned_data
	

class finalize_rental_income_tax_form(forms.Form):
	incomplete_payment_id = forms.CharField(max_length = 100)
	
	peroperty = None

	district_choices = [('','----------')]
	
	district = forms.ChoiceField(choices = district_choices)

	sector_choices = [('','----------')]
	sector = forms.ChoiceField( choices = sector_choices)
	
	cell_choices = [('','----------')]
	cell = forms.ChoiceField(choices = cell_choices)
	
	village_choices = [('','----------')]
	village = forms.ChoiceField(choices = village_choices, required = False)
	
	parcel_id = forms.CharField(max_length = 100)
	
	
	rental_income = forms.FloatField(error_messages={'required': 'Please enter rental income'})
	bank_interest_paid = forms.FloatField(initial=0)
	period_from = forms.DateField()
	period_to = forms.DateField()
	paid_date = forms.DateField()
	paid_amount = forms.FloatField()
	bank_choices = [('','-----------')]
	bank_choices.extend(variables.banks)
	bank = forms.ChoiceField(choices = bank_choices)
	bank_receipt = forms.CharField(max_length=50)

	def __init__(self, *args, **kw):
		incomplete_payment = None
		if 'instance' in kw:
			incomplete_payment = kw['instance']
			del kw['instance']
		super(finalize_rental_income_tax_form, self).__init__(*args, **kw)

		district_choices = [('','----------')]
		district_list = District.objects.all().order_by('name')
		district_choices.extend((o.id, o.name) for o in district_list)
		self.fields['district'].choices = district_choices

		if incomplete_payment:
			self.fields['incomplete_payment_id'].initial = incomplete_payment.id
			self.fields['incomplete_payment_id'].widget =self.fields['incomplete_payment_id'].hidden_widget() 
			
			district_choices = [('','----------')]
			district_list = District.objects.all().order_by('name')
			if district_list:
				for tt in district_list:
					district_choices.append((tt.id, tt.name))
			self.fields['district'].widget.choices = district_choices
			
			if incomplete_payment.district:
				sector_list = Sector.objects.filter(district = incomplete_payment.district)
				sector_choices = [('','----------')]
				if sector_list:
					for tt in sector_list:
						sector_choices.append((tt.id, tt.name)) 
				self.fields['sector'].choices = sector_choices
				self.fields['district'].initial = incomplete_payment.district.id
							
			if incomplete_payment.sector:
				cell_list = Cell.objects.filter(sector = incomplete_payment.sector)
				cell_choices = [('','----------')]
				if cell_list:
					for tt in cell_list:
						cell_choices.append((tt.id, tt.name))
				self.fields['cell'].choices = cell_choices
				self.fields['sector'].initial = incomplete_payment.sector.id
				
			if incomplete_payment.cell:
				village_list = Village.objects.filter(cell = incomplete_payment.cell)
				village_choices = [('','----------')]
				if village_list:
					for tt in village_list:
						village_choices.append((tt.id, tt.name))
				self.fields['village'].choices = village_choices
				self.fields['cell'].initial = incomplete_payment.cell.id
			
			if incomplete_payment.village:
				self.fields['village'].initial = incomplete_payment.village.id
				
				
			self.fields['parcel_id'].initial = incomplete_payment.parcel_id
			self.fields['period_from'].initial = incomplete_payment.period_from
			self.fields['period_to'].initial = incomplete_payment.period_to
			self.fields['paid_date'].initial = incomplete_payment.paid_date
			self.fields['paid_amount'].initial = incomplete_payment.paid_amount
			self.fields['bank'].initial = incomplete_payment.bank
			self.fields['bank_receipt'].initial = incomplete_payment.bank_receipt
			
		elif args and args[0]:
			district_choices = [('','----------')]
			district_list = District.objects.all().order_by('name')
			if district_list:
				for tt in district_list:
					district_choices.append((tt.id, tt.name))
			self.fields['district'].widget.choices = district_choices
			
			if args[0].has_key('district') and args[0]['district']:
				sector_list = Sector.objects.filter(district = args[0]['district'])
				sector_choices = [('','----------')]
				if sector_list:
					for tt in sector_list:
						sector_choices.append((tt.id, tt.name)) 
				self.fields['sector'].choices = sector_choices
				self.fields['district'].initial = args[0]['district']
							
			if args[0].has_key('sector') and args[0]['sector']:
				cell_list = Cell.objects.filter(sector = args[0]['sector'])
				cell_choices = [('','----------')]
				if cell_list:
					for tt in cell_list:
						cell_choices.append((tt.id, tt.name))
				self.fields['cell'].choices = cell_choices
				self.fields['sector'].initial = args[0]['sector']
				
			if args[0].has_key('cell') and args[0]['cell']:
				village_list = Village.objects.filter(cell = args[0]['cell'])
				village_choices = [('','----------')]
				if village_list:
					for tt in village_list:
						village_choices.append((tt.id, tt.name))
				self.fields['village'].choices = village_choices
				self.fields['cell'].initial = args[0]['cell']
			
			if args[0].has_key('village') and args[0]['village']:
				self.fields['village'].initial = args[0]['village']
		
		self.fields['period_from'].widget.attrs['class'] = 'date_picker'
		self.fields['period_from'].widget.format = settings.DATE_INPUT_FORMAT
		self.fields['period_from'].input_formats=['%d/%m/%Y']
		self.fields['period_to'].widget.attrs['class'] = 'date_picker'
		self.fields['period_to'].widget.format = settings.DATE_INPUT_FORMAT
		self.fields['period_to'].input_formats=['%d/%m/%Y']
		self.fields['paid_date'].widget.attrs['class'] = 'date_picker'
		self.fields['paid_date'].widget.format = settings.DATE_INPUT_FORMAT
		self.fields['paid_date'].input_formats=['%d/%m/%Y']
		
		
	def clean(self):
		data = self.cleaned_data
		incomplete_payment_id = data.get('incomplete_payment_id','')
		paid_amount = data.get('paid_amount',0)
		period_from = data.get('period_from','')
		period_to = data.get('period_to','')
		paid_date = data.get("paid_date",'')
		bank = data.get('bank','')
		bank_receipt = data.get('bank_receipt','')
		district = data.get('district','')
		sector = data.get('sector','')
		cell = data.get('cell','')
		village = data.get('village','')
		parcel_id = data.get('parcel_id','')
		
		
		self.fields['incomplete_payment_id'].widget =self.fields['incomplete_payment_id'].hidden_widget()
		incomplete_payment = IncompletePayment.objects.get(pk = incomplete_payment_id)
		
		district_choices = [('','----------')]
		district_list = District.objects.all().order_by('name')
		if district_list:
			for tt in district_list:
				district_choices.append((tt.id, tt.name))
		self.fields['district'].widget.choices = district_choices
		
		if district:
			sector_list = Sector.objects.filter(district__id = district)
			sector_choices = [('','----------')]
			if sector_list:
				for tt in sector_list:
					sector_choices.append((tt.id, tt.name)) 
			self.fields['sector'].choices = sector_choices
			self.fields['district'].initial = district
			incomplete_payment.district = District.objects.get(pk = district)
						
		if sector:
			cell_list = Cell.objects.filter(sector__id = sector)
			cell_choices = [('','----------')]
			if cell_list:
				for tt in cell_list:
					cell_choices.append((tt.id, tt.name))
			self.fields['cell'].choices = cell_choices
			self.fields['sector'].initial = sector
			incomplete_payment.sector = Sector.objects.get(pk = sector)
			
		if cell:
			village_list = Village.objects.filter(cell__id = cell)
			village_choices = [('','----------')]
			if village_list:
				for tt in village_list:
					village_choices.append((tt.id, tt.name))
			self.fields['village'].choices = village_choices
			self.fields['cell'].initial = cell
			incomplete_payment.cell = Cell.objects.get(pk = cell)
		
		if village:
			self.fields['village'].initial = village
			incomplete_payment.village = Village.objects.get(pk = village)
		
		incomplete_payment.paid_amount = paid_amount
		if period_from:
			incomplete_payment.period_from = period_from
		if period_to:
			incomplete_payment.period_to = period_to
		if paid_date:
			incomplete_payment.paid_date = paid_date
		if period_from and period_to:
			if period_to < period_from:
				self.errors['period_to'] = ['Period to should be after period from!']
			elif period_from.year!=period_to.year:
				self.errors['period_to'] = ['Period from and period to should be within the same year!']
		
		incomplete_payment.bank = bank
		incomplete_payment.bank_receipt = bank_receipt
		incomplete_payment.parcel_id = parcel_id
		incomplete_payment.save()
		if sector and cell and parcel_id:
			try:
				int(parcel_id)
				property = None
				if village:
					property = Property.objects.filter(sector__id = sector, cell__id = cell, village = village, parcel_id = parcel_id)
				else:
					property = Property.objects.filter(sector__id = sector, cell__id = cell, parcel_id = parcel_id)
				if not property:
					self.errors['parcel_id'] = ['This property does not exist!']
				elif len(property) > 1:
					self.errors['parcel_id'] = ['Multiple properties found. Please select a village!']
			except:
				self.errors['parcel_id'] = ['Please enter a valid plot ID!']
		return self.cleaned_data
	

class finalize_cleaning_fee_form(forms.Form):
	
	incomplete_payment_id = forms.CharField(max_length = 100)
	tin = forms.CharField(max_length = 100, required=False)
	business_select = forms.CharField(max_length = 100, label='Business', required=False)
	business = forms.CharField(widget=forms.HiddenInput(), max_length = 100, label='Business ID', initial=None,required=False)
	subbusiness_choices = [('','-----------')]
	subbusiness = forms.ChoiceField(choices = subbusiness_choices, initial=None,required=False)
	
	area_type_choices = [('','-----------')]
	area_type_choices.extend(variables.area_types)
	area_type = forms.ChoiceField(choices = area_type_choices, required = False)
	
	business_type_choices = [('','-----------')]
	business_type_choices.extend(variables.business_types)
	business_type = forms.ChoiceField(choices = business_type_choices, required = False)
	
	# fields needed for jtax_fee table
	period_from = forms.DateField()
	period_to = forms.DateField()
	paid_date = forms.DateField()
	
	
	# fields needed for jtax_payfee table
	paid_amount = forms.FloatField()
	
	bank_choices = [('','-----------')]
	bank_choices.extend(variables.banks)
	bank = forms.ChoiceField(choices = bank_choices)
	
	bank_receipt = forms.CharField(max_length=50)
	
	def __init__(self, *args, **kw):
		business = None
		subbusiness = None
		incomplete_payment = None
		period_from = None
		period_to = None
		paid_date = None
		
		if 'instance' in kw:
			incomplete_payment = kw['instance']
			del kw['instance']
		initial = kw.get('initial', {})
		
		initial['business'] = None

		if incomplete_payment:
			initial['incomplete_payment_id'] = incomplete_payment.id
			initial['tin'] = incomplete_payment.tin
			initial['paid_amount'] = incomplete_payment.paid_amount
			initial['period_from'] = incomplete_payment.period_from
			initial['period_to'] = incomplete_payment.period_to
			initial['paid_date'] = incomplete_payment.paid_date
			initial['bank'] = incomplete_payment.bank
			initial['bank_receipt'] = incomplete_payment.bank_receipt

			business = incomplete_payment.business
			subbusiness = incomplete_payment.subbusiness

			if business:
				initial['area_type'] = business.area_type
				initial['business_type'] = business.business_type
				
		if args and args[0]:
			initial['incomplete_payment_id'] = args[0]['incomplete_payment_id']
			initial['tin'] = args[0]['tin']
			initial['paid_amount'] = args[0]['paid_amount']
			initial['period_from'] = Common.to_standard_date(args[0]['period_from'])
			initial['period_to'] = Common.to_standard_date(args[0]['period_to'])
			initial['paid_date'] = Common.to_standard_date(args[0]['paid_date'])
			initial['bank'] = args[0]['bank']
			initial['bank_receipt'] = args[0]['bank_receipt']
			initial['area_type'] = args[0]['area_type']
			initial['business_type'] = args[0]['business_type']

			if args[0].has_key('business') and args[0]['business'] != '':
				business = Business.objects.get(pk = args[0]['business'])
			if args[0].has_key('subbusiness') and args[0]['subbusiness'] != '':
				subbusiness = args[0]['subbusiness']
		
		kw['initial'] = initial
		super(finalize_cleaning_fee_form, self).__init__(*args, **kw)
			
		if business:
			initial['business_select'] = business.name
			initial['business'] = business.id  
			subbusiness_choices = [('','-----------')]
			subbusiness_choices.extend((o.id, o.branch) for o in business.subbusiness_set.all().order_by('branch'))
			self.fields['subbusiness'].choices = subbusiness_choices
		if subbusiness:
			if type(subbusiness) is SubBusiness:
				self.fields['subbusiness'].initial = subbusiness.id
			else:
				self.fields['subbusiness'].value = subbusiness

		self.fields['period_from'].widget.attrs['class'] = 'date_picker'
		self.fields['period_from'].widget.format = settings.DATE_INPUT_FORMAT
		self.fields['period_from'].input_formats=['%d/%m/%Y']
		self.fields['period_to'].widget.attrs['class'] = 'date_picker'
		self.fields['period_to'].widget.format = settings.DATE_INPUT_FORMAT
		self.fields['period_to'].input_formats=['%d/%m/%Y']
		self.fields['paid_date'].widget.attrs['class'] = 'date_picker'
		self.fields['paid_date'].widget.format = settings.DATE_INPUT_FORMAT
		self.fields['paid_date'].input_formats=['%d/%m/%Y']
		
		# hide incomplete payment id field
		self.fields['incomplete_payment_id'].widget = self.fields['incomplete_payment_id'].hidden_widget()
		
		
		# validate bank and bank receipt
		if not initial['bank']:
			self.errors['bank'] = ['bank is not selected!']
		if not initial['bank_receipt']:
			self.errors['bank_receipt'] = ['bank receipt is not entered!']
		if not initial['paid_amount']:
			self.errors['paid_amount'] = ['please enter a valid paid amount!']
	
		if not initial['paid_date']:
			self.errors['paid_date'] = ['paid date is not entered!']
		
		if not business:
			self.errors['business'] = ['Please input a valid business (select from suggestion list)!']
			self.fields['area_type'].widget = self.fields['area_type'].hidden_widget()
			self.fields['business_type'].widget = self.fields['business_type'].hidden_widget()

		else:
			if not initial['area_type']:
				self.errors['area_type'] = ['business area type needs to be selected!']
			else:
				kw['initial']['area_type'] = business.area_type
				initial['area_type'] = business.area_type
			if not initial['business_type']:
				self.errors['business_type'] = ['business type needs to be selected!']
			else:
				kw['initial']['business_type'] = business.business_type
				initial['business_type'] = business.business_type
		
		
		if not initial['period_from']:
			self.errors['period_from'] = ['period from can not be empty!']
		else:
			import calendar
			period_from = Common.to_standard_date(str(initial['period_from']))
			period_from = datetime.strptime(period_from,'%Y-%m-%d')
			month_range = calendar.monthrange(period_from.year, period_from.month)
			if period_from.day != 1:
				self.errors['period_from'] = ['Period from should be the first day of a month!']
	
		if not initial['period_to']:
			self.errors['period_to'] = ['period to can not be empty!']
		else:
			import calendar
			period_to = Common.to_standard_date(str(initial['period_to']))
			period_to = datetime.strptime(period_to,'%Y-%m-%d')
			month_range = calendar.monthrange(period_to.year, period_to.month)
			if month_range[1] != period_to.day:
				self.errors['period_to'] = ['Period to should be the last day of a month!']
	
		if period_from and period_to:
			if period_from.year != period_to.year:
				self.errors['period_to'] = ['"Period from and period to should be within the same year!"']
			elif period_from.month != period_to.month: 
				self.errors['period_to'] = ['"Period from and period to should be within the same month!"']
		
	def clean(self):
		data = self.cleaned_data
		incomplete_payment_id = data.get('incomplete_payment_id','')
		tin = data.get('tin','')
		business = None
		subbusiness = None
		if data.has_key('business') and data['business'] != '':
			business = Business.objects.get(pk=data.get('business',''),i_status='active')
		if data.has_key('subbusiness') and data['subbusiness'] != '':
			subbusiness = SubBusiness.objects.get(pk=data.get('subbusiness',''),i_status='active')

		paid_amount = data.get('paid_amount',0)
		period_from = data.get('period_from','')
		period_to = data.get('period_to','')
		paid_date = data.get("paid_date",'')
		bank = data.get('bank','')
		bank_receipt = data.get('bank_receipt','')
		area_type = data.get('area_type','')
		business_type = data.get('business_type','')
		
		incomplete_payment = None
		
		if incomplete_payment_id:
			incomplete_payment = IncompletePayment.objects.get(pk = int(incomplete_payment_id))
		if incomplete_payment:
			if tin:
				incomplete_payment.tin = tin
			else:
				if incomplete_payment.tin:
					tin = incomplete_payment.tin
					self.cleaned_data['tin'] = tin

			if business:
				incomplete_payment.business = business
				self.cleaned_data['business'] = business
			else:
				if incomplete_payment.business:
					business = incomplete_payment.business
					self.cleaned_data['business'] = business
			if subbusiness:
				incomplete_payment.subbusiness = subbusiness
				self.cleaned_data['subbusiness'] = subbusiness
			else:
				if incomplete_payment.subbusiness:
					subbusiness = incomplete_payment.subbusiness
					self.cleaned_data['subbusiness'] = subbusiness

			if paid_amount:
				incomplete_payment.paid_amount = paid_amount
			else:
				if incomplete_payment.paid_amount:
					paid_amount = incomplete_payment.paid_amount
					self.cleaned_data['paid_amount'] = paid_amount
			if period_from:
				incomplete_payment.period_from = period_from
			else:
				if incomplete_payment.period_from:
					period_from = incomplete_payment.period_from
					self.cleaned_data['period_from'] = period_from
			if period_to:
				incomplete_payment.period_to = period_to
			else:
				if incomplete_payment.period_to:
					period_to = incomplete_payment.period_to
					self.cleaned_data['period_to'] = period_to
			if bank:
				incomplete_payment.bank = bank
			else:
				if incomplete_payment.bank:
					bank = incomplete_payment.bank
					self.cleaned_data['bank'] = bank
			if bank_receipt:
				incomplete_payment.bank_receipt = bank_receipt
			else:
				if incomplete_payment.bank_receipt:
					bank_receipt = incomplete_payment.bank_receipt
					self.cleaned_data['bank_receipt'] = bank_receipt
			if paid_date:
				incomplete_payment.paid_date = paid_date
			else:
				if incomplete_payment.paid_date:
					paid_date = incomplete_payment.paid_date
					self.cleaned_data['paid_date'] = Common.to_standard_date(paid_date)
			incomplete_payment.save()
		
		if not bank:
			self.errors['bank'] = ['bank is not selected!']
		if not bank_receipt:
			self.errors['bank_receipt'] = ['bank receipt is not entered!']
		if tin:
			if not business:
				self.errors['tin'] = ['There is no business with this tin number']
		else:
			self.errors['tin'] = ['Tin number is needed!']
		
		period_valid = True
		if not paid_date:
			self.errors['paid_date'] = ['paid date is not entered!']
		if not paid_amount:			
			self.errors['paid_amount'] = ['Paid amount can not be empty!']
		if not period_from:
			period_valid = False
			self.errors['period_from'] = ['Period from can not be empty!']
		elif period_from.day!=1:
			period_valid = False
			self.errors['period_from'] = ['Period from should be the first day of a month!']
		if not period_to:
			period_valid = False
			self.errors['period_to'] = ['Period to can not be empty!']
		else:
			import calendar
			month_range = calendar.monthrange(period_to.year, period_to.month)
			if month_range[1] != period_to.day:
				period_valid = False
				self.errors['period_to'] = ['Period to should be the last day of a month!']
		if business:
			if area_type and not business.area_type:
				business.area_type = area_type
			if business_type and not business.business_type:
				business.business_type = business_type
			business.save()
		
		if period_valid:
			if period_from.year!=period_to.year:
				period_valid = False
				self.errors['period_to'] = ['Period from and period to should be within the same year!']
			elif period_from.month!=period_to.month:
				period_valid = False
				self.errors['period_to'] = ['Period from and period to should be within the same month!']
			if period_valid:
				date_boundary = datetime.strptime('01/04/2013','%d/%m/%Y').date()
				if period_to < date_boundary or period_from <date_boundary:
					if paid_amount:
						self.cleaned_data['paid_amount']= int(paid_amount)
		if paid_date:
			if self.errors.has_key('paid_date'):
				del self.errors['paid_date']
		
		return self.cleaned_data		


class finalize_market_fee_form(forms.Form):
	
	incomplete_payment_id = forms.CharField(max_length = 100)
	tin = forms.CharField(max_length = 100, required=False)
	business_select = forms.CharField(max_length = 100, label='Business', required=False)
	business = forms.CharField(widget=forms.HiddenInput(), max_length = 100, label='Business ID', initial=None,required=False)
	subbusiness_choices = [('','-----------')]
	subbusiness = forms.ChoiceField(choices = subbusiness_choices, initial=None,required=False)

	# fields needed for jtax_fee table
	period_from = forms.DateField()
	period_to = forms.DateField()
	paid_date = forms.DateField()
	
	
	# fields needed for jtax_payfee table
	paid_amount = forms.FloatField()
	
	bank_choices = [('','-----------')]
	bank_choices.extend(variables.banks)
	bank = forms.ChoiceField(choices = bank_choices)
	
	bank_receipt = forms.CharField(max_length=50)
	
	def __init__(self, *args, **kw):
		business = None
		subbusiness = None
		incomplete_payment = None
		period_from = None
		period_to = None
		paid_date = None
		
		if 'instance' in kw:
			incomplete_payment = kw['instance']
			del kw['instance']
		initial = kw.get('initial', {})
		
		initial['business'] = None

		if incomplete_payment:
			initial['incomplete_payment_id'] = incomplete_payment.id
			initial['tin'] = incomplete_payment.tin
			initial['paid_amount'] = incomplete_payment.paid_amount
			initial['period_from'] = incomplete_payment.period_from
			initial['period_to'] = incomplete_payment.period_to
			initial['paid_date'] = incomplete_payment.paid_date
			initial['bank'] = incomplete_payment.bank
			initial['bank_receipt'] = incomplete_payment.bank_receipt

			business = incomplete_payment.business
			subbusiness = incomplete_payment.subbusiness
				
		if args and args[0]:
			initial['incomplete_payment_id'] = args[0]['incomplete_payment_id']
			initial['tin'] = args[0]['tin']
			initial['paid_amount'] = args[0]['paid_amount']
			initial['period_from'] = Common.to_standard_date(args[0]['period_from'])
			initial['period_to'] = Common.to_standard_date(args[0]['period_to'])
			initial['paid_date'] = Common.to_standard_date(args[0]['paid_date'])
			initial['bank'] = args[0]['bank']
			initial['bank_receipt'] = args[0]['bank_receipt']

			if args[0].has_key('business') and args[0]['business'] != '':
				business = Business.objects.get(pk = args[0]['business'])
			if args[0].has_key('subbusiness') and args[0]['subbusiness'] != '':
				subbusiness = args[0]['subbusiness']		
		
		kw['initial'] = initial
		super(finalize_market_fee_form, self).__init__(*args, **kw)

		if business:
			initial['business_select'] = business.name
			initial['business'] = business.id  
			subbusiness_choices = [('','-----------')]
			subbusiness_choices.extend((o.id, o.branch) for o in business.subbusiness_set.all().order_by('branch'))
			self.fields['subbusiness'].choices = subbusiness_choices
		if subbusiness:
			if type(subbusiness) is SubBusiness:
				self.fields['subbusiness'].initial = subbusiness.id
			else:
				self.fields['subbusiness'].value = subbusiness
			
		self.fields['period_from'].widget.attrs['class'] = 'date_picker'
		self.fields['period_from'].widget.format = settings.DATE_INPUT_FORMAT
		self.fields['period_from'].input_formats=['%d/%m/%Y']
		self.fields['period_to'].widget.attrs['class'] = 'date_picker'
		self.fields['period_to'].widget.format = settings.DATE_INPUT_FORMAT
		self.fields['period_to'].input_formats=['%d/%m/%Y']
		self.fields['paid_date'].widget.attrs['class'] = 'date_picker'
		self.fields['paid_date'].widget.format = settings.DATE_INPUT_FORMAT
		self.fields['paid_date'].input_formats=['%d/%m/%Y']
		
		# hide incomplete payment id field
		self.fields['incomplete_payment_id'].widget = self.fields['incomplete_payment_id'].hidden_widget()
		
		
		# validate bank and bank receipt
		if not initial['bank']:
			self.errors['bank'] = ['bank is not selected!']
		if not initial['bank_receipt']:
			self.errors['bank_receipt'] = ['bank receipt is not entered!']
		if not initial['paid_amount']:
			self.errors['paid_amount'] = ['please enter a valid paid amount!']
	
		if not initial['paid_date']:
			self.errors['paid_date'] = ['paid date is not entered!']
		
		if not business:
			self.errors['business'] = ['Please input a valid business (select from our suggestion list)!']
		
		if not initial['period_from']:
			self.errors['period_from'] = ['period from can not be empty!']
		else:
			import calendar
			period_from = Common.to_standard_date(str(initial['period_from']))
			period_from = datetime.strptime(period_from,'%Y-%m-%d')
			month_range = calendar.monthrange(period_from.year, period_from.month)
			if period_from.day != 1:
				self.errors['period_from'] = ['Period from should be the first day of a month!']
	
		if not initial['period_to']:
			self.errors['period_to'] = ['period to can not be empty!']
		else:
			import calendar
			period_to = Common.to_standard_date(str(initial['period_to']))
			period_to = datetime.strptime(period_to,'%Y-%m-%d')
			month_range = calendar.monthrange(period_to.year, period_to.month)
			if month_range[1] != period_to.day:
				self.errors['period_to'] = ['Period to should be the last day of a month!']
	
		if period_from and period_to:
			if period_from.year != period_to.year:
				self.errors['period_to'] = ['"Period from and period to should be within the same year!"']
			elif period_from.month != period_to.month: 
				self.errors['period_to'] = ['"Period from and period to should be within the same month!"']
		
	def clean(self):
		data = self.cleaned_data
		incomplete_payment_id = data.get('incomplete_payment_id','')
		tin = data.get('tin','')

		business = None
		subbusiness = None
		if data.has_key('business') and data['business'] != '':
			business = Business.objects.get(pk=data.get('business',''),i_status='active')
		if data.has_key('subbusiness') and data['subbusiness'] != '':
			subbusiness = SubBusiness.objects.get(pk=data.get('subbusiness',''),i_status='active')

		paid_amount = data.get('paid_amount',0)
		period_from = data.get('period_from','')
		period_to = data.get('period_to','')
		paid_date = data.get("paid_date",'')
		bank = data.get('bank','')
		bank_receipt = data.get('bank_receipt','')
		
		incomplete_payment = None
		
		if incomplete_payment_id:
			incomplete_payment = IncompletePayment.objects.get(pk = int(incomplete_payment_id))
		if incomplete_payment:
			if tin:
				incomplete_payment.tin = tin
			else:
				if incomplete_payment.tin:
					tin = incomplete_payment.tin
					self.cleaned_data['tin'] = tin

			if business:
				incomplete_payment.business = business
				self.cleaned_data['business'] = business
			else:
				if incomplete_payment.business:
					business = incomplete_payment.business
					self.cleaned_data['business'] = business
			if subbusiness:
				incomplete_payment.subbusiness = subbusiness
				self.cleaned_data['subbusiness'] = subbusiness
			else:
				if incomplete_payment.subbusiness:
					subbusiness = incomplete_payment.subbusiness
					self.cleaned_data['subbusiness'] = subbusiness

			if paid_amount:
				incomplete_payment.paid_amount = paid_amount
			else:
				if incomplete_payment.paid_amount:
					paid_amount = incomplete_payment.paid_amount
					self.cleaned_data['paid_amount'] = paid_amount
			if period_from:
				incomplete_payment.period_from = period_from
			else:
				if incomplete_payment.period_from:
					period_from = incomplete_payment.period_from
					self.cleaned_data['period_from'] = period_from
			if period_to:
				incomplete_payment.period_to = period_to
			else:
				if incomplete_payment.period_to:
					period_to = incomplete_payment.period_to
					self.cleaned_data['period_to'] = period_to
			if bank:
				incomplete_payment.bank = bank
			else:
				if incomplete_payment.bank:
					bank = incomplete_payment.bank
					self.cleaned_data['bank'] = bank
			if bank_receipt:
				incomplete_payment.bank_receipt = bank_receipt
			else:
				if incomplete_payment.bank_receipt:
					bank_receipt = incomplete_payment.bank_receipt
					self.cleaned_data['bank_receipt'] = bank_receipt
			if paid_date:
				incomplete_payment.paid_date = paid_date
			else:
				if incomplete_payment.paid_date:
					paid_date = incomplete_payment.paid_date
					self.cleaned_data['paid_date'] = Common.to_standard_date(paid_date)
			incomplete_payment.save()

		if not bank:
			self.errors['bank'] = ['bank is not selected!']
		if not bank_receipt:
			self.errors['bank_receipt'] = ['bank receipt is not entered!']
		if tin:
			if not business:
				self.errors['tin'] = ['There is no business with this tin number']
		else:
			self.errors['tin'] = ['Tin number is needed!']
		
		period_valid = True
		if not paid_date:
			self.errors['paid_date'] = ['paid date is not entered!']
		if not paid_amount:			
			self.errors['paid_amount'] = ['Paid amount can not be empty!']
		if not period_from:
			period_valid = False
			self.errors['period_from'] = ['Period from can not be empty!']
		elif period_from.day!=1:
			period_valid = False
			self.errors['period_from'] = ['Period from should be the first day of a month!']
		if not period_to:
			period_valid = False
			self.errors['period_to'] = ['Period to can not be empty!']
		else:
			import calendar
			month_range = calendar.monthrange(period_to.year, period_to.month)
			if month_range[1] != period_to.day:
				period_valid = False
				self.errors['period_to'] = ['Period to should be the last day of a month!']


		if period_valid:
			if period_from.year!=period_to.year:
				period_valid = False
				self.errors['period_to'] = ['Period from and period to should be within the same year!']
			elif period_from.month!=period_to.month:
				period_valid = False
				self.errors['period_to'] = ['Period from and period to should be within the same month!']
			if period_valid:
				date_boundary = datetime.strptime('01/04/2013','%d/%m/%Y').date()
				if period_to < date_boundary or period_from <date_boundary:
					if paid_amount:
						self.cleaned_data['paid_amount']= int(paid_amount)
		if paid_date:
			if self.errors.has_key('paid_date'):
				del self.errors['paid_date']
		
		return self.cleaned_data		


class tax_setting_search_form(forms.Form):
	district = forms.ChoiceField(required = False)
	sector_choices = [('','----------')]
	sector = forms.ChoiceField(required = False, choices = sector_choices)

	def __init__(self, *args, **kw):
		super(tax_setting_search_form, self).__init__(*args, **kw)
		district_choices = [('','----------')]
		district_choices.extend((o.id, o.name) for o in District.objects.all().order_by('name'))
		self.fields['district'].choices = district_choices

		initial = kw.get('initial', {})
		if 'district' in initial and initial['district']:
			sector_list = Sector.objects.filter(district = initial['district'])
			sector_choices = [('','----------')]
			sector_choices.extend((o.id, o.name) for o in sector_list)
			self.fields['sector'].choices = sector_choices

			kw['initial']['district'] = initial['district'].id
			kw['initial']['sector'] = initial['sector'].id

	def clean(self):
		super(tax_setting_search_form,self).clean()
		if 'sector' in self._errors:
			del self.errors['sector']
			self.cleaned_data['sector'] = self.data['sector']

		return self.cleaned_data


class tax_search_property_form(forms.Form):
	citizen_id = forms.CharField(required = False)
	upi = forms.CharField(max_length = 50, required = False)
	parcel_id = forms.IntegerField(required = False)
	#village = forms.CharField(max_length = 100, required = False)
	
	ownership_choices = (('with','With ownership'),('without','Without ownership'),('all','All'),)
	has_ownership = forms.ChoiceField(required = False, widget=forms.RadioSelect, choices = ownership_choices)


	district = forms.ChoiceField(required = False)
	sector = forms.ChoiceField(required = False)
	
	cell_choices = [('','----------')]
	cell = forms.ChoiceField(required = False, choices = cell_choices)
	
	def __init__(self, *args, **kw):
		super(tax_search_property_form, self).__init__(*args, **kw)
		district_choices = [('','----------')]
		district_choices.extend((o.id, o.name) for o in District.objects.all().order_by('name'))
		self.fields['district'].choices = district_choices


		initial = kw.get('initial', {})
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
		if 'parcel_id' in initial and initial['parcel_id']:
			kw['initial']['parcel_id'] = initial['parcel_id']
		if 'citizen_id' in initial and initial['citizen_id']:
			kw['initial']['citizen_id'] = initial['citizen_id']
		if 'upi' in initial and initial['upi']:
			kw['initial']['upi'] = initial['upi']
		if 'has_ownership' in initial and initial['has_ownership']:
			kw['initial']['has_ownership'] = initial['has_ownership']
			
	def clean(self):
		super(tax_search_property_form,self).clean()
		if 'district' in self._errors:
			del self.errors['district']
			self.cleaned_data['district'] = self.data['district']
		if 'sector' in self._errors:
			del self.errors['sector']
			self.cleaned_data['sector'] = self.data['sector']
		if 'cell' in self._errors:
			del self.errors['cell']
			self.cleaned_data['cell'] = self.data['cell']
		return self.cleaned_data
	
	
class tax_search_property_declarevalue_form(forms.Form):
	upi = forms.CharField(max_length = 50, required = False)
	parcel_id = forms.IntegerField(required = False)
	#village = forms.CharField(max_length = 50, required = False)
	cell = forms.CharField(max_length = 50, required = False)
	sector = forms.ChoiceField(required = False, choices = [('',''),])

	def __init__(self, *args, **kw):
		super(tax_search_property_declarevalue_form, self).__init__(*args, **kw)
		sectors = [(o.id, o.district.name + '--' + o.name) for o in Sector.objects.select_related('district').all().order_by('district','name')]
		self.fields['sector'].choices += sectors


class payment_search_form(forms.Form):
	
	bank_choices = [('','')]
	tax_types_choices = [('','')]
	for c in banks:
		bank_choices.append((c[0],c[1]))
	for c in tax_and_fee_types:
		tax_types_choices.append((c[0],c[1]))

	invoice_id = forms.CharField(max_length = 50, required = False)
	citizen_id = forms.CharField(max_length = 50, required = False)
	tin = forms.CharField(max_length = 100, required = False)
	upi = forms.CharField(max_length = 50, required = False)
	bank = forms.ChoiceField(widget=forms.Select, choices=bank_choices, required = False)
	receipt_no = forms.CharField(max_length = 50, required = False)
	manual_receipt = forms.CharField(max_length = 50, required = False)
	tax_type = forms.ChoiceField(widget=forms.Select, choices=tax_types_choices, required = False)
	period_from = forms.DateTimeField(required = False,initial='', input_formats=settings.DATE_INPUT_FORMATS)
	period_to = forms.DateTimeField(required = False,initial='', input_formats=settings.DATE_INPUT_FORMATS)


class verify_target_for_pay_form(forms.Form):
	pay_citizen_id = forms.CharField(max_length=50, required = False)
	pay_citizen_name = forms.CharField(max_length= 50, required = False)
	#pay_first_name = forms.CharField(max_length= 50, required = False)
	#pay_middle_name = forms.CharField(max_length = 50, required = False)
	#pay_last_name = forms.CharField(max_length=50, required = False)
	pay_tin = forms.CharField(max_length= 50, required = False)
	pay_business_name = forms.CharField(max_length = 50, required = False)
	pay_business_owner_name = forms.CharField(max_length = 50, required = False)
	pay_business_owner_ID = forms.CharField(max_length = 50, required = False)
	
	
	pay_upi = forms.CharField(max_length = 50, required = False)
	pay_parcel_id = forms.IntegerField(required = False)
	pay_village = forms.CharField(max_length = 50, required = False)

	pay_district = forms.ChoiceField(required = False)

	sector_choices = [('','----------')]
	pay_sector = forms.ChoiceField(required = False, choices = sector_choices)
	
	cell_choices = [('','----------')]
	pay_cell = forms.ChoiceField(required = False, choices = cell_choices)

	
	def __init__(self, *args, **kw):
		super(verify_target_for_pay_form, self).__init__(*args, **kw)
		district_choices = [('','----------')]
		district_choices.extend((o.id, o.name) for o in District.objects.all().order_by('name'))
		self.fields['pay_district'].choices = district_choices

		initial = kw.get('initial', {})
		if 'pay_district' in initial and initial['pay_district']:
			pay_sector_list = Sector.objects.filter(district = initial['pay_district'])
			pay_sector_choices = [('','----------')]
			pay_sector_choices.extend((o.id, o.name) for o in pay_sector_list)
			self.fields['pay_sector'].choices = pay_sector_choices
			kw['initial']['pay_district'] = initial['pay_district'].id
		if 'pay_sector' in initial and initial['pay_sector']:
			pay_cell_list = Cell.objects.filter(sector = initial['pay_sector'])
			pay_cell_choices = [('','----------')]
			pay_cell_choices.extend((o.id, o.name) for o in pay_cell_list)
			self.fields['pay_cell'].choices = pay_cell_choices
			kw['initial']['pay_sector'] = initial['pay_sector'].id
		if 'pay_cell' in initial and initial['pay_cell']:
			kw['initial']['pay_cell'] = initial['pay_cell'].id
		
	def clean(self):
		super(verify_target_for_pay_form,self).clean()
		if 'pay_district' in self._errors:
			del self.errors['pay_district']
			self.cleaned_data['pay_district'] = self.data['pay_district']
		if 'pay_sector' in self._errors:
			del self.errors['pay_sector']
			self.cleaned_data['pay_sector'] = self.data['pay_sector']
		if 'pay_cell' in self._errors:
			del self.errors['pay_cell']
			self.cleaned_data['pay_cell'] = self.data['pay_cell']
		return self.cleaned_data


class payment_reverse_form(forms.Form):
	reason = forms.CharField(widget=forms.Textarea,max_length=500)


class incomplete_payment_search_form(forms.Form):
	id = forms.CharField(max_length = 50, required = False)
	tax_types = [('','')]
	tax_types.extend(variables.tax_and_fee_types)
	tax_type = forms.ChoiceField(required = False, choices = tax_types)

	tin = forms.CharField(max_length = 100, required = False)

	bank_choices = [('','')]
	bank_choices.extend(variables.banks)
	bank = forms.ChoiceField(required = False, choices = bank_choices)
	
	bank_receipt = forms.CharField(max_length = 50, required = False)
	sector_receipt = forms.CharField(max_length = 100, required = False)

	sector = forms.ChoiceField(required = False)

	tax_payer = forms.CharField(max_length = 100, required = False)
	citizen_id = forms.CharField(max_length = 50, required = False)
	phone = forms.CharField(max_length = 100, required = False)
	parcel_id = forms.CharField(max_length = 100, required = False)
	
	filter_period_from = forms.DateTimeField(required = False,initial='', input_formats=settings.DATE_INPUT_FORMATS)
	filter_period_to = forms.DateTimeField(required = False,initial='', input_formats=settings.DATE_INPUT_FORMATS)
	
	user = forms.CharField(max_length="100", required=False)
	
	def __init__(self, *args, **kw):

		super(incomplete_payment_search_form, self).__init__(*args, **kw)
		sector_choices = [('','')]
		sector_choices.extend((o.id, o.district.name + '--' + o.name) for o in Sector.objects.all().select_related('district').order_by('district__name','name'))
		self.fields['sector'].choices = sector_choices

		self.fields['filter_period_from'].widget.attrs['class'] = 'date_picker'
		self.fields['filter_period_to'].widget.attrs['class'] = 'date_picker'

	
class pending_payment_search_form(forms.Form):
	
	tax_types = [('','')]
	tax_types.extend(variables.tax_and_fee_types)
	tax_type = forms.ChoiceField(required = False, choices = tax_types)

	tin = forms.CharField(max_length = 100, required = False)

	bank_choices = [('','')]
	bank_choices.extend(variables.banks)
	bank = forms.ChoiceField(required = False, choices = bank_choices)
	
	receipt_no = forms.CharField(max_length = 100, required = False)
	invoice_id = forms.CharField(max_length = 100, required = False)
	manual_receipt = forms.CharField(max_length = 100, required = False)
	upi = forms.CharField(max_length = 100, required = False)

	citizen_id = forms.CharField(max_length = 50, required = False)
	
	period_from = forms.DateTimeField(required = False,initial='', input_formats=settings.DATE_INPUT_FORMATS)
	period_to = forms.DateTimeField(required = False,initial='', input_formats=settings.DATE_INPUT_FORMATS)
	
	user = forms.CharField(max_length="100", required=False)
	
	def __init__(self, *args, **kw):

		super(pending_payment_search_form, self).__init__(*args, **kw)

		self.fields['period_from'].widget.attrs['class'] = 'date_picker'
		self.fields['period_to'].widget.attrs['class'] = 'date_picker'
		

class fee_view_search_form(forms.Form):
	"""
	Enter searching criteria to generate report
	"""
	tax_types_choices=[('All','All')]
	
	tax_types = forms.ChoiceField(widget=forms.CheckboxSelectMultiple, choices=tax_types_choices, required = False)
	
	district_choices = [('','----------')]
	district = forms.ChoiceField(required = False, choices = district_choices)

	sector_choices = [('','----------')]
	sector = forms.ChoiceField(required = False, choices = sector_choices)
	
	cell_choices = [('','----------')]
	cell = forms.ChoiceField(required = False, choices = cell_choices)

	village_choices=[('','----------')]
	village=forms.ChoiceField(required=False, choices=village_choices)
	
	def __init__(self, request, *args, **kw):
		super(fee_view_search_form, self).__init__(*args, **kw)
		initial = kw.get('initial', {})
		if not initial:
			kw['initial']={}
		if request.POST:
			initial['district']=request.POST['district']
			initial['sector']=request.POST['sector']
			initial['cell']=request.POST['cell']
			initial['village']=request.POST['village']
		tax_types_choices=[('All','All')]
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
# 			self.fields['district'].initial = initial['district']
			sector_choices = [('','----------')]
			sector_choices.extend((o.id, o.name) for o in sector_list)
			self.fields['sector'].choices = sector_choices
			kw['initial']['district'] = initial['district']
		if 'sector' in initial and initial['sector']:
			cell_list = Cell.objects.filter(sector = initial['sector'])
			cell_choices = [('','----------')]
			cell_choices.extend((o.id, o.name) for o in cell_list)
			self.fields['cell'].choices = cell_choices
			kw['initial']['sector'] = initial['sector']
		if 'cell' in initial and initial['cell']:
			village_list=Village.objects.filter(cell=initial['cell'])
			village_choices=[('','----------')]
			village_choices.extend((o.id, o.name) for o in village_list)
			self.fields['village'].choices = village_choices
			kw['initial']['cell'] = initial['cell']
		if 'village' in initial and initial['village']:
			kw['initial']['village'] = initial['village']
		print "----initial-------"
		print initial
		self.initial=kw['initial']
		
	
	def clean(self):
		super(fee_view_search_form,self).clean()
# 		if 'sector' in self._errors:
# 			del self.errors['sector']
# 			self.cleaned_data['sector'] = self.data['sector']
# 		if 'cell' in self._errors:
# 			del self.errors['cell']
# 			self.cleaned_data['cell'] = self.data['cell']
# 		if 'village' in self._errors:
# 			del self.errors['village']
		return self.cleaned_data
	



	