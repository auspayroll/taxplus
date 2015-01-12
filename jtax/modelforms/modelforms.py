
from django import forms
from django.forms import ModelForm

from jtax.models import *
from asset.models import *
from datetime import date, datetime, time

from dev1 import variables
from dev1 import settings
from jtax.shared_functions import sendEmailDebug
from common.fields import CurrencyField, CurrencyInput


class FeeForm(ModelForm):
	class Meta:
		model = Fee
		fields = ('quantity',)

class InstallmentForm(ModelForm):
	class Meta:
		model = Installment
		fields = ('amount', 'due')

	due = forms.DateField(required=True, input_formats=('%d/%m/%Y',), widget=forms.DateInput(format='%d/%m/%Y', attrs={'width':12}))

class IncompletePaymentModelForm(ModelForm):
	business_select = forms.CharField(max_length = 100, label='Business', required=False)
	business = forms.CharField(widget=forms.HiddenInput(), max_length = 100, label='Business ID', initial=None,required=False)
	subbusiness_choices = [('','-----------')]
	subbusiness = forms.ChoiceField(choices = subbusiness_choices, initial=None,required=False)
	district_choices = [('','----------')]
	district = forms.ChoiceField(district_choices,required=False, widget=forms.Select())
	sector_choices = [('','----------')]
	sector = forms.ChoiceField(sector_choices,required=False, widget=forms.Select())

	class Meta:
		model = IncompletePayment
		exclude = ('user','date_time','i_status')

	def __init__(self, *args, **kw):
		filter = False
		if 'filter' in kw:
			filter = kw['filter']
			del kw['filter']
		super(IncompletePaymentModelForm, self).__init__(*args, **kw)
		self.fields.keyOrder = ['tax_type', 'tin', 'business_select', 'business','subbusiness', 'paid_amount', 'paid_date', 'period_from', \
			'period_to', 'bank', 'bank_receipt', 'sector_receipt', 'district', 'sector', 'cell', 'village', \
			'parcel_id', 'tax_payer', 'citizen_id', 'date_of_birth', 'phone', 'email', 'note']

		self.fields['date_of_birth'].widget.attrs['class'] = 'date_picker'
		self.fields['period_from'].widget.attrs['class'] = 'date_picker'
		self.fields['period_from'].widget.format = settings.DATE_INPUT_FORMAT
		self.fields['period_from'].input_formats=['%d/%m/%Y']
		self.fields['period_to'].widget.attrs['class'] = 'date_picker'
		self.fields['period_to'].widget.format = settings.DATE_INPUT_FORMAT
		self.fields['period_to'].input_formats=['%d/%m/%Y']
		self.fields['tax_payer'].widget.attrs['autocomplete'] = 'off'
		self.fields['citizen_id'].widget.attrs['autocomplete'] = 'off'
		self.fields['email'].widget.attrs['autocomplete'] = 'off'
		self.fields['bank_receipt'].widget.attrs['autocomplete'] = 'off'
		self.fields['sector_receipt'].widget.attrs['autocomplete'] = 'off'
		self.fields['parcel_id'].widget.attrs['autocomplete'] = 'off'
		self.fields['phone'].widget.attrs['autocomplete'] = 'off'
		self.fields['tin'].widget.attrs['autocomplete'] = 'off'
		self.fields['business'].widget.attrs['autocomplete'] = 'off'
		self.fields['paid_date'].widget.format = settings.DATE_INPUT_FORMAT
		self.fields['paid_date'].input_formats=['%d/%m/%Y']
		self.fields['paid_date'].widget.attrs['class'] = 'date_picker'

		district_choices = [('','----------')]
		district_choices.extend((o.id, o.name) for o in District.objects.all().order_by('name'))
		self.fields['district'].choices = district_choices

		self.fields['sector'].choices = [('','----------')]
		self.fields['cell'].choices = [('','----------')]
		self.fields['village'].choices = [('','----------')]
		if self.instance:
			if self.instance.business:
				subbusiness_choices = [('','-----------')]
				subbusiness_choices.extend((o.id, o.branch) for o in self.instance.business.subbusiness_set.all().order_by('branch'))
				self.fields['subbusiness'].choices = subbusiness_choices
				self.fields['business_select'].initial = self.instance.business.name

			if self.instance.subbusiness:
				self.fields['subbusiness'].value = self.instance.subbusiness.id

			if self.instance.village:
				cell = self.instance.village.cell
				sector = cell.sector
				district = sector.district

				village_list = Village.objects.filter(cell = cell)
				village_choices = [('','----------')]
				if village_list:
					for tt in village_list:
						village_choices.append((tt.id, tt.name))
				self.fields['village'].choices = village_choices
				self.fields['village'].value = self.instance.village.id

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
				self.fields['sector'].value = sector.id

				self.fields['district'].value = district
			elif self.instance.cell:

				village_list = Village.objects.filter(cell = self.instance.cell)
				village_choices = [('','----------')]
				if village_list:
					for tt in village_list:
						village_choices.append((tt.id, tt.name))
				self.fields['village'].choices = village_choices

				sector = self.instance.cell.sector
				district = sector.district

				cell_list = Cell.objects.filter(sector = sector)
				cell_choices = [('','----------')]
				if cell_list:
					for tt in cell_list:
						cell_choices.append((tt.id, tt.name))
				self.fields['cell'].choices = cell_choices
				self.fields['cell'].value = self.instance.cell.id

				sector_list = Sector.objects.filter(district = district)
				sector_choices = [('','----------')]
				if sector_list:
					for tt in sector_list:
						sector_choices.append((tt.id, tt.name))
				self.fields['sector'].choices = sector_choices
				self.fields['sector'].value = sector.id
				self.fields['district'].value = district
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
				self.fields['sector'].value = sector.id

				self.fields['district'].value = district.id
			elif self.instance.district:
				district = self.instance.district
				self.fields['district'].value = district.id
				sector_list = Sector.objects.filter(district = district)
				sector_choices = [('','----------')]
				if sector_list:
					for tt in sector_list:
						sector_choices.append((tt.id, tt.name))
				self.fields['sector'].choices = sector_choices

			if args and len(args) > 0:
				if args[0].has_key('business') and args[0]['business']:
					business = Business.objects.get(pk = args[0]['business'])
					subbusiness_choices = [('','-----------')]
					subbusiness_choices.extend((o.id, o.branch) for o in business.subbusiness_set.all().order_by('branch'))
					self.fields['subbusiness'].choices = subbusiness_choices
					self.fields['business_select'].value = business.name


				if args[0].has_key('subbusiness') and args[0]['subbusiness']:
					self.fields['subbusiness'].value =  args[0]['subbusiness']

				if args[0].has_key('village') and args[0]['village']:
					village = Village.objects.get(pk = int(args[0]['village']))
					cell = village.cell
					sector = cell.sector
					district = sector.district

					village_list = Village.objects.filter(cell = cell)
					village_choices = [('','----------')]
					if village_list:
						for tt in village_list:
							village_choices.append((tt.id, tt.name))
					self.fields['village'].choices = village_choices
					self.fields['village'].value = village.id

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
					self.fields['sector'].value = sector.id
					self.fields['district'].value = district.id


				elif args[0].has_key('cell') and args[0]['cell']:
					cell = Cell.objects.get(pk=int(args[0]['cell']))
					village_list = Village.objects.filter(cell = cell)
					village_choices = [('','----------')]
					if village_list:
						for tt in village_list:
							village_choices.append((tt.id, tt.name))
					self.fields['village'].choices = village_choices

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
					self.fields['sector'].value = sector.id
					self.fields['district'].value = district.id

				elif args[0].has_key('sector') and args[0]['sector']:
					sector = Sector.objects.get(pk=int(args[0]['sector']))
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
					self.fields['sector'].value = sector.id
					self.fields['district'].value = district.id

				elif args[0].has_key('district') and args[0]['district']:
					district = District.objects.get(pk=int(args[0]['district']))
					self.fields['district'].value = district.id
					sector_list = Sector.objects.filter(district = district)
					sector_choices = [('','----------')]
					if sector_list:
						for tt in sector_list:
							sector_choices.append((tt.id, tt.name))
					self.fields['sector'].choices = sector_choices


	def clean_sector(self):
		sector_id = self.cleaned_data['sector']
		valid = False
		if self.fields['sector'].choices:
			for i in self.fields['sector'].choices:
				if str(sector_id) == str(i[0]):
					valid = True
		if not valid:
			#send email comprise of full info out to admin staffs for debugging
			sendEmailDebug("Incomplete Permission Debug", self)
			raise forms.ValidationError("Please select a valid sector from our suggestion list!")

		try:
			sector = Sector.objects.get(pk=sector_id, i_status='active')
			return sector
		except:
			raise forms.ValidationError("Please select a valid sector from our list!")
		return None


	def clean_district(self):
		district_id = self.cleaned_data['district']

		valid = False
		if self.fields['district'].choices:
			for i in self.fields['district'].choices:
				if str(district_id) == str(i[0]):
					valid = True

		if not valid:
			#send email comprise of full info out to admin staffs for debugging
			sendEmailDebug("Incomplete Permission Debug", self)
			raise forms.ValidationError("Please select a valid district from our suggestion list!")

		try:
			district = District.objects.get(pk=district_id, i_status='active')

			return district
		except:
			raise forms.ValidationError("Please select a valid district from our list!")

		return None


	def clean_business(self):
		business_id = self.cleaned_data['business']
		if business_id:
			try:
				business = Business.objects.get(pk=business_id, i_status='active')
				return business
			except:
				raise forms.ValidationError("Please select a valid business from our suggestion list!")
		return None

	def clean_subbusiness(self):
		subbusiness_id = self.cleaned_data['subbusiness']
		if subbusiness_id:
			try:
				subbusiness = SubBusiness.objects.get(pk=subbusiness_id, i_status='active')
				return subbusiness
			except:
				raise forms.ValidationError("Please select a valid subbusiness!")
		return None

	def _validate_period(self):
		tax_type = self.cleaned_data.get('tax_type')
		period_from = self.cleaned_data.get('period_from')
		period_to = self.cleaned_data.get('period_to')
		if period_from and period_to:
			if period_from.year!=period_to.year:
				raise forms.ValidationError("Period from and period to should be within the same year!")
		if tax_type == 'cleaning_fee':
			if period_from and period_from.day!=1:
				raise forms.ValidationError("Period from can only be the first day of a month!")
			if period_to:
				import calendar
				month_range = calendar.monthrange(period_to.year, period_to.month)
				if month_range[1] != period_to.day:
					raise forms.ValidationError("Period to should be the last day of a month!")
			if period_from and period_to and period_from.month!=period_to.month:
				raise forms.ValidationError("Period from and period to should be within the same month!")
		return True

	def clean_parcel_id(self):
		parcel_id = self.cleaned_data['parcel_id']
		if parcel_id:
			try:
				int(parcel_id)
				return int(parcel_id)
			except:
				raise forms.ValidationError("Please enter a valid parcel ID!")
		return parcel_id

	def clean_period_from(self):
		self._validate_period()
		return self.cleaned_data.get("period_from")

	def clean_period_to(self):
		self._validate_period()
		return self.cleaned_data.get("period_to")

	def clean_paid_amount(self):
		amount = self.cleaned_data['paid_amount']
		if amount < 0:
			raise forms.ValidationError("Please enter a valid paid amount!")
		return amount

	def clean_tax_type(self):
		tax_type = self.cleaned_data.get('tax_type')
		if not tax_type:
			raise forms.ValidationError("Please select tax type!")
		return tax_type


class PayTaxModelForm(ModelForm):
	citizen_id = forms.IntegerField(widget=forms.HiddenInput(), initial=None,required=False)
	business_id = forms.IntegerField(widget=forms.HiddenInput(), initial=None,required=False)
	#amount = forms.CharField(label="Total Tax Amount",  widget = forms.TextInput(attrs={'readonly':'readonly'}))

	final_tax_due = forms.CharField(widget=forms.HiddenInput(), initial=None,required=False)
	paid_date = forms.DateField(widget=forms.DateInput(format = '%d/%m/%Y',attrs={'class' : 'date_picker'}), input_formats=('%d/%m/%Y',),initial=datetime.now,)

	manual_receipt = forms.CharField(widget=forms.TextInput(), label="Manual Receipt Number", required=False)
	submit_pending = forms.CharField(widget=forms.HiddenInput(), required=False)
	pending_reason = forms.CharField(widget=forms.HiddenInput(), required=False)
	pending_note = forms.CharField(widget=forms.HiddenInput(), required=False)
	i_status = forms.CharField(widget=forms.HiddenInput(),  initial='active')

	amount = forms.DecimalField( widget=forms.TextInput(attrs={'class':'disabled, numeric', 'readonly':'readonly'}))
	fine = forms.DecimalField(label="Additional Fine", initial='0', widget=forms.TextInput(attrs={'class':'numeric'}))
	fine_description = forms.CharField(widget=forms.TextInput(attrs={'class':'disabled', 'readonly':'readonly'}), required=False)

	class Meta:
		abstract = True
		exclude = ('staff',)


class PayFixedAssetTaxForm(PayTaxModelForm):
	class Meta(PayTaxModelForm.Meta):
		model = PayFixedAssetTax
		fields = [ 'bank', 'receipt_no','paid_date', 'manual_receipt', 'note', 'fine', 'fine_description', 'amount' ]


class PayRentalIncomeTaxForm(PayTaxModelForm):
	last_year_income = forms.CharField(label='Rental Income for the tax year ' + str(datetime.today().year - 1),initial='',required=False,  widget=forms.TextInput(attrs={'autocomplete':'off'}))
	bank_interest_paid = forms.CharField(label='Bank Interest Paid',initial='0')

	class Meta(PayTaxModelForm.Meta):
		model = PayRentalIncomeTax
		widgets = {'rental_income_tax': forms.HiddenInput}


class PayTradingLicenseTaxForm(PayTaxModelForm):

	def __init__(self, *args, **kw):
		super(PayTaxModelForm, self).__init__(*args, **kw)
		#self.fields.keyOrder = ['final_tax_due','amount','receipt_no','bank','paid_date','manual_receipt','note','citizen_id','business_id','staff_id','trading_license_tax','fine_amount','fine_description','submit_pending']

	class Meta(PayTaxModelForm.Meta):
		model = PayTradingLicenseTax
		fields = [ 'bank', 'receipt_no','paid_date', 'manual_receipt', 'note', 'fine', 'fine_description', 'amount' ]


class PayFeeForm(PayTaxModelForm):
	class Meta(PayTaxModelForm.Meta):
		model = PayFee
		amount = CurrencyField()
		fields = [ 'bank', 'receipt_no', 'paid_date', 'manual_receipt', 'note', 'fine', 'fine_description', 'amount' ]

	def clean(self):
		cleaned_data = super(PayFeeForm, self).clean()
		fine = cleaned_data.get('fine')
		fine_description = cleaned_data.get('fine_description')
		if fine and not fine_description:
			self._errors["fine_description"] = self.error_class(["Please enter a fine description"])
		return cleaned_data


class PayMiscellaneousFeeForm(PayTaxModelForm):
	class Meta(PayTaxModelForm.Meta):
		model = PayMiscellaneousFee
		exclude = ('fee','business','citizen','staff')


def paymentModel(tax_object_or_model):
	"""
	returns a payment model object for a given tax object or model
	"""
	tax = tax_object_or_model

	if tax is Fee or isinstance(tax, Fee):
		return PayFee

	elif tax is PropertyTaxItem or isinstance(tax, PropertyTaxItem):
		return PayFixedAssetTax

	elif tax is TradingLicenseTax or isinstance(tax, TradingLicenseTax):
		return PayTradingLicenseTax

	elif tax is RentalIncomeTax or isinstance(tax, RentalIncomeTax):
		return PayRentalIncomeTax


class confirmPaymentForm(forms.Form):
		citizen_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
		business_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
		amount = CurrencyField(widget=forms.HiddenInput())
		late_fees = CurrencyField(widget=forms.HiddenInput())
		receipt_no = forms.CharField(required=False, widget=forms.HiddenInput())
		manual_receipt = forms.CharField(required=False, widget=forms.HiddenInput())
		fine_amount = CurrencyField(widget=forms.HiddenInput())
		fine_description = forms.CharField(widget=forms.HiddenInput(), required=False)
		note = forms.CharField(widget=forms.HiddenInput(), required=False)
		paid_date = forms.DateField(input_formats=('%d/%m/%Y',), widget=forms.HiddenInput())
		bank = forms.CharField(required=False, widget=forms.HiddenInput())
		fee_id = forms.CharField(widget=forms.HiddenInput())
		fee_type = forms.CharField(widget=forms.HiddenInput())


def paymentForm(tax_object, *args, **kwargs):
	class PaymentForm(forms.ModelForm):
		citizen_id = forms.IntegerField(widget=forms.HiddenInput(), initial=None, required=False)
		business_id = forms.IntegerField(widget=forms.HiddenInput(), initial=None, required=False)
		amount = CurrencyField(label="Payment Amount") #  widget=forms.TextInput(attrs={'class':'disabled', 'readonly':'readonly'})
		final_tax_due = forms.CharField(widget=forms.HiddenInput(), initial=None,required=False)
		paid_date = forms.DateField(widget=forms.DateInput(format = '%d/%m/%Y',attrs={'class' : 'date_picker'}), input_formats=('%d/%m/%Y',),initial=datetime.now,)
		manual_receipt = forms.CharField(widget=forms.TextInput(), label="Manual Receipt Number", required=False)
		submit_pending = forms.CharField(widget=forms.HiddenInput(), required=False)
		pending_reason = forms.CharField(widget=forms.HiddenInput(), required=False)
		pending_note = forms.CharField(widget=forms.HiddenInput(), required=False)
		payer_type = forms.ChoiceField(widget=forms.RadioSelect, label="Payer", required=False, choices=(('citizen','citizen'),('business','business')))
		# citizen_search = forms.CharField(required=False)
		if tax_object.exempt:
			bank_choices = [('N/A', 'N/A - Exempt')]
		else:
			bank_choices = [('','----------')] + [ (code, name) for code, name in variables.banks]
		bank = forms.ChoiceField(choices=bank_choices, required=False)
		receipt_no = forms.CharField(required=False)
		i_status = forms.CharField(widget=forms.HiddenInput(), initial='active')
		fine_amount = CurrencyField(label="Additional Fine", initial='0')
		fine_description = forms.CharField(widget=forms.TextInput(attrs={'class':'disabled', 'readonly':'readonly'}), required=False)

		class Meta:
			model = paymentModel(tax_object)
			tax = tax_object
			fields = [ 'payer_type', 'bank', 'receipt_no', 'paid_date', 'manual_receipt', 'note', 'amount', 'fine_amount', 'fine_description', 'business_id', 'citizen_id']

		def clean(self):
			cleaned_data = super(PaymentForm, self).clean()
			fine = cleaned_data.get('fine')
			fine_description = cleaned_data.get('fine_description')
			if fine and not fine_description:
				self._errors["fine_description"] = self.error_class(["Please enter a fine description"])
			if not tax_object.exempt and not cleaned_data.get('bank'):
				self._errors["bank"] = self.error_class(["Please enter a bank"])
			if not tax_object.exempt and not cleaned_data.get('receipt_no'):
				self._errors["receipt_no"] = self.error_class(["Please enter a receipt number"])
			if not cleaned_data.get('citizen_id') and not cleaned_data.get('business_id'):
				self._errors["payer_type"] = self.error_class(["You must specify a payer"])
			if cleaned_data.get('amount') > self.Meta.tax.remaining_amount:
				self._errors['amount'] = self.error_class(["Payment amount cannot be greater than %s" % self.Meta.tax.remaining_amount])
			return cleaned_data

	return PaymentForm
