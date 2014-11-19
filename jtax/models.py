from django.db import models
from django.db.models import Q, F
from property.models import Property, Council, LandUse, Cell, Village, Sector, District
from citizen.models import Citizen
from citizen.mappers.CitizenMapper import CitizenMapper
from datetime import datetime, timedelta, date
from django.utils.dateformat import DateFormat
from django.utils.formats import get_format
from dev1 import variables
from asset.models import *
from pmauth.models import *
from decimal import Decimal
from dev1 import ThreadLocal
from jtax.shared_functions import calc_interest
from dateutil.relativedelta import relativedelta
property_decorator = property
import json
import cPickle as pickle
from django.utils import timezone


# This is the new IncompletePayment model #

class IncompletePaymentManager(models.Manager):
	def get_query_set(self):
		user = ThreadLocal.get_current_user()
		if user:
			if user.superuser:
				return super(IncompletePaymentManager,self).get_query_set().all()
			else:
				return super(IncompletePaymentManager,self).get_query_set().filter(district__in = District.objects.all(), sector__in = Sector.objects.all()).distinct()
		else:
			return super(IncompletePaymentManager,self).get_query_set().none()


class IncompletePayment(models.Model):
	tax_type = models.CharField(choices=variables.tax_and_fee_types, max_length = 100, null = True, blank = True, verbose_name = 'Type of Tax')
	tin = models.CharField(max_length = 100, null = True, blank = True, verbose_name = 'TIN')
	business = models.ForeignKey(Business, null=True, blank = True)
	subbusiness = models.ForeignKey(SubBusiness, null=True, blank = True)
	paid_amount = models.FloatField(null = True, blank  = True, default = 0, verbose_name = "Paid amount")
	paid_date = models.DateField(null=True, blank=True, verbose_name = "Paid date")
	period_from = models.DateField(null=True, blank=True)
	period_to = models.DateField(null=True, blank=True)
	bank = models.CharField(choices=variables.banks,max_length = 100, null = True, blank = True, verbose_name = 'Bank')
	bank_receipt = models.CharField(max_length = 100, null = True, blank = True, verbose_name = 'Bank Receipt')
	sector_receipt = models.CharField(max_length = 100, null = True, blank = True, verbose_name = 'Sector Receipt/manual receipt')
	district = models.ForeignKey(District, null=True, blank=True, verbose_name = 'District')
	sector = models.ForeignKey(Sector, null = True, blank = True, verbose_name = 'Sector')
	cell = models.ForeignKey(Cell, null = True, blank = True, verbose_name = 'Cell')
	village = models.ForeignKey(Village, null = True, blank = True, verbose_name = 'Village')
	parcel_id = models.CharField(max_length = 100, null = True, blank=True, verbose_name = 'Plot/Parcel ID')
	tax_payer = models.CharField(max_length = 100, null = True, blank = True, verbose_name = 'Tax Payer')
	citizen_id = models.CharField(max_length = 50, null = True, blank=True, verbose_name = 'Citizen ID')
	date_of_birth = models.CharField(max_length = 50, null = True, blank=True, verbose_name = 'Date of Birth')
	phone = models.CharField(max_length = 100, null = True, blank=True, verbose_name = 'Phone')
	email = models.EmailField(max_length = 100, null = True, blank=True, verbose_name = 'Email')
	note = models.TextField(null = True, blank=True, verbose_name = 'Reasons for incomplete payment')
	user = models.ForeignKey(PMUser, null=True, blank = True)
	date_time = models.DateTimeField(help_text='This is the Date and Time the Entry has been entered into the database.',auto_now_add=True,auto_now=True)
	i_status = models.CharField(max_length = 10, choices = variables.status_choices, default='active', blank = True)
	objects = IncompletePaymentManager()
	objectsIgnorePermission = models.Manager()

	def save(self, *args, **kwargs):
		"""
		1. set user to be the staff
		"""
		user = ThreadLocal.get_current_user()
		self.user = user
		models.Model.save(self)

	def __unicode__(self):
		return "Incomplete Payment " + str(self.id)

	def getLogMessage(self,old_data=None,new_data=None, action=None):
		return getLogMessage(self,old_data,new_data, action)


class Historical(models.Model):
	citizen = models.ForeignKey(Citizen, null=True, blank=True)
	business = models.ForeignKey(Business, null=True, blank=True)
	fee_id = models.IntegerField(null=True, blank=True)
	fee_type = models.CharField(max_length=50)
	period_from = models.DateTimeField(null=True, blank=True)
	period_to = models.DateTimeField(null=True, blank=True)
	due_date = models.DateTimeField(null=True, blank=True)
	amount_due = models.FloatField(null=True, blank=True)
	late_paymemt_penalty = models.FloatField(default=0)
	late_payment_interest = models.FloatField(default=0)
	is_paid = models.BooleanField(default = False)
	invoince_no = models.CharField(max_length = 50, null=True, blank = True)

"""
The DeclaredValue Models are based around Declared Values Supplied by Property Owners
These need to be checked against the Valuration system and checked if the supplied value is in line
If it is not it needs to be flaged and manually checked.
The Goverment / Council only has 6 months to Challange this value before it is automatticly accepted.
"""
class DeclaredValue(models.Model):
	"""
	This is the base class for the Delcated Values of a Plot of Land in Rwandap
	"""
	#plot_id = models.CharField(max_length = 50, help_text='This is the ID of the Plot that the Declared Value is for.')
	#citizen_id = models.CharField(max_length = 50, help_text='This is the Nation Id of the Cirizen Making the Delcared Value.')
	citizen = models.ForeignKey(Citizen, null=True, blank=True)
	commercial_amount = models.BigIntegerField(help_text='Commecial declared value', null=True, blank=True, default=0)
	residential_amount = models.BigIntegerField(help_text='Residential Declared Value', null=True, blank=True, default=0)
	agriculture_amount = models.BigIntegerField(help_text='Agricultural declared value', null=True, blank=True, default=0)
	amount = models.BigIntegerField(help_text='This is the amount The Declared Value is been Made for.')
	currency = models.CharField(max_length=4,choices=variables.currency_types,help_text='This is the Currencey the Amount has been specified in.')
	date_time = models.DateTimeField(help_text='This is the Date and Time the Entry has been entered into the database.',auto_now_add=True,auto_now=True)
	#staff_id = models.IntegerField(help_text='This is the Id of the Staff Member that Added the Declared Value for the Property.')
	user = models.ForeignKey(PMUser, null=True, blank = True)
	accepted = models.CharField(max_length=20,choices=variables.declare_value_statuses,help_text='This is whether the declare Value has been Accepted, rejected, or needs review.')
	property = models.ForeignKey(Property, null=True, blank=True)
	declared_on = models.DateField(null=True)

	def getLogMessage(self,old_data=None,new_data=None,action=None):
		"""
		return tailored log message for different actions taken on this group
		"""
		if action == "add":
			citizen = self.citizen
			citizen_fullname = CitizenMapper.getDisplayName(citizen)
			property = self.property
			property_info = property.getDisplayName()
			message = "approves Citizen ["+citizen_fullname+ "] to declare a value of "+ self.currency + " " + str(self.amount) + " on Property ["+ property_info + "]"
			return message


class DeclaredValueNotes(models.Model):
	"""
	This is a table of notes Related to the Declared Values model
	"""
	declared_value = models.ForeignKey(DeclaredValue)
	citizen = models.ForeignKey(Citizen, null=True, blank=True, help_text='The citizen who adds this note')
	user = models.ForeignKey(PMUser, null=True, blank = True, help_text='The staff who adds this note.')
	note = models.TextField(help_text='This is the Note that is been left for the Declared Value')
	date_time = models.DateTimeField(help_text='This is the Date and Time the Note was added to the Declared Value in the system.',auto_now_add=True,auto_now=True)

class DeclaredValueMedia(models.Model):
	"""
	This is a list of media files that have been attached to the Declared Value Application / Item directly.
	"""
	declared_value = models.ForeignKey(DeclaredValue)
	description = models.TextField(null=True, blank = True, help_text = 'Notes/Reminder')
	file_name = models.CharField(max_length = 150)
	path = models.CharField(max_length = 255)
	file_type = models.CharField(max_length = 50)
	file_size = models.CharField(max_length = 50)
	user = models.ForeignKey(PMUser, null=True, blank = True, help_text='The staff who adds this note.')
	date_time = models.DateTimeField(help_text='This is the date and time the file was uploaded',auto_now_add=True,auto_now=True)

	def __unicode__(self):
		return str(self.file_name)

"""
The Assigned Value models are for the assigned Values to a property, this would be the official price of the land/property accepted by the Goverment. All Tax Items based off Property Value should use this table.
These values are apparently accepted for 4 years from timme of acceptance.
"""
class AssignedValue(models.Model):
	"""
	This model is for the offically assigned Values of a plot for the purpose of taxation
	"""
	plot_id = models.IntegerField()
	amount = models.BigIntegerField(help_text='This is the Offical Property Price')
	date_time = models.DateTimeField(help_text='This is the Date and time that the record for this assigned value was created',auto_now=True,auto_now_add=True)
	currency = models.CharField(max_length=4,choices=variables.currency_types,help_text='this is the Currencey that the assigned Value Amount is in')
	staff_id = models.IntegerField(help_text='This is the System Staff id of the staff member that entered the assigned value into the system.')
	citizen_id = models.CharField(max_length=50,help_text='This is the ID of the Citizen That Provided the Delcared Value that was accepted')
	valid_until = models.DateTimeField('This is when the Assigned Value Record Runs Out.')
	on_hold = models.CharField(max_length=4,choices=variables.on_hold,help_text='this will put the record on hold if needed.')
	property = models.ForeignKey(Property, null=True, blank=True)

class TaxType(models.Model):
	code = models.CharField(max_length=50, null=True, blank=True)
	name = models.CharField(max_length=50)

class Bank(models.Model):
	code = models.CharField(max_length=10, null=True, blank=True)
	name = models.CharField(max_length=50)

class Currency(models.Model):
	code = models.CharField(max_length=10, null=True, blank=True)
	name = models.CharField(max_length=50)


class Tax(models.Model):
	"""
	plot_id = models.IntegerField(help_text='This is the ID of the Plot.')
	tax_type = models.ForeignKey(TaxType)
	amount = models.DecimalField(max_digits = 20, decimal_places = 2, help_text="The amount of tax item.")
	remaining_amount = models.DecimalField(max_digits = 20, decimal_places = 2, help_text="The remaining amount (subtracted past payments).", null=True, blank = True)
	currency = models.CharField(max_length=4, choices=variables.currency_types)
	period_from = models.DateTimeField(help_text="The start date of a period that this tax item is for.")
	period_to = models.DateTimeField(help_text="The end date of a period that this tax item is for.")
	due_date = models.DateField(help_text="The date this tax item is due.")
	is_paid = models.BooleanField(help_text="Whether tax is payed.")
	created = models.DateTimeField(help_text="The date this tax item is generated.")
	property = models.ForeignKey(Property, null=True, blank=True)
	citizen = models.ForeignKey(Citizen,null=True,blank=True)
	business = models.ForeignKey(Business, null=True, blank=True, help_text="Business that have trading license to be taxed.")
	subbusiness = models.ForeignKey(SubBusiness,  null=True, blank=True, help_text="SubBusiness that have trading license to be taxed.")
	is_challenged = models.BooleanField(help_text="whether this tax item is challenged.")
	submit_date = models.DateTimeField(help_text="The date this fee item is submited.", null=True, blank=True)
	submit_details = models.CharField(max_length=500, null=True, blank=True)
	is_reviewed = models.BooleanField(help_text ="whether this tax item is reviewed.")
	is_accepted = models.BooleanField(help_text="whether this tax item is accepted.")
	staff_id = models.IntegerField(help_text="The staff who generates this property tax item.", null=True, blank=True)
	i_status = models.CharField(max_length = 10, choices = variables.status_choices, default='active', blank = True)
	"""
	class Meta:
		abstract = True

	def calculatePaymentOld(self, pay_date=None, payment_amount=None):
		if not pay_date:
			pay_date = date.today()

		payment = self.calculateTotalPayment(pay_date=pay_date, payment_amount=payment_amount)
		due_date = payment['due_date']
		amount_due = payment['amount_due']
		interest = payment['interest']
		surcharge = payment['surcharge']
		late_fees = payment['late_fees']
		interest_rate = payment['interest_rate']
		months_late = payment['months_late']
		surcharge_rate = payment['surcharge_rate']
		surcharge_max = payment['surcharge_max']
		total = payment['total']

		default_installments = []
		installments = self.installments.all().order_by('due')
		late_installments = [ installment for installment in installments if installment.due < pay_date and installment.paid < installment.amount ]
		if installments and not late_installments: # set the next installment date as due date
			try:
				next_installment = [ installment for installment in installments if installment.due > pay_date and installment.owed > 0 ][0]
				due_date = next_installment.due
				amount_due = next_installment.owed
			except IndexError:
				pass

		total_due = amount_due + Decimal(late_fees)
		return { 'due_date':due_date, 'amount_due':amount_due, 'interest':interest, 'total':total,
		  'surcharge':surcharge, 'late_fees':late_fees, 'interest_rate':float(interest_rate * 100), 'total_due':total_due, 'months_late':months_late,
		  'surcharge_rate':surcharge_rate, 'surcharge_max':surcharge_max, 'installments':installments }


	def calculatePayment(self, pay_date=None, payment_amount=None):
		"""
		returns the next payment amount, due date and interest payment information
		"""
		if not pay_date:
			pay_date = date.today()

		property_or_business = None
		try:
			property_or_business = self.property
		except AttributeError:
			pass

		try:
			property_or_business = self.business
		except AttributeError:
			pass

		if property_or_business:
			sector = property_or_business.sector
		else:
			sector = None

		due_date = self.due_date
		tax_amount = self.amount or 0
		amount_paid = tax_amount - ( self.remaining_amount or 0)
		amount_due = tax_amount - amount_paid
		if amount_due < 0:
			amount_due = 0

		formula_data = []
		late_fees = Decimal(0)
		months_late = Decimal(0)
		total_due = Decimal(0)
		interest = Decimal(0)
		surcharge = Decimal(0)
		principle = Decimal(0)

		# get the settings to calculate late fee
		tax_periods = Setting.getTaxPeriods(self.fee_setting, self.period_from, self.period_to, sector=sector)
		tax_setting = tax_periods[0][2]

		interest_rate = Decimal(tax_setting['late_fee_interest_rate'])
		surcharge_rate = Decimal(tax_setting['late_fee_surcharge_rate'])
		surcharge_max = Decimal(tax_setting['late_fee_surcharge_max'])

		installments = self.installments.all().order_by('due')
		late_installments = False
		paid_amount = amount_paid
		unpaid_installments = []

		for i in installments:
			if paid_amount < i.amount:
				paid_amount = 0
				unpaid_installments.append(i)
			else: # already paid
				paid_amount -= i.amount

		late_installments = [ i for i in unpaid_installments if pay_date > i.due ]

		if not late_installments and unpaid_installments: # set the next installment date as due date
			due_date = unpaid_installments[0].due
			amount_due = unpaid_installments[0].remaining

		if due_date and pay_date > due_date:
			late_fees, months_late, interest, surcharge, principle = calc_interest(due_date, amount_due, surcharge_rate, surcharge_max, interest_rate, payment_amount, pay_date)

		return { 'due_date':due_date, 'amount_due':amount_due, 'interest':interest,
		  'surcharge':surcharge, 'late_fees':late_fees, 'interest_rate':float(interest_rate * 100),
		  'months_late':months_late, 'principle':principle, 'amount_paid':amount_paid,
		  'surcharge_rate':float(surcharge_rate * 100), 'surcharge_max':surcharge_max }


	def amount_owing(self, as_at=None):
		if not as_at:
			as_at = date.today()
		sector = None
		if hasattr(self, 'business'):
			sector = self.business.sector
		elif hasattr(self, 'property'):
			sector = self.property.sector

		tax_periods = Setting.getTaxPeriods(self.fee_setting, self.period_from, self.period_to, sector=sector)
		tax_setting = tax_periods[0][2]

		interest_rate = Decimal(tax_setting['late_fee_interest_rate'])
		surcharge_rate = Decimal(tax_setting['late_fee_surcharge_rate'])
		surcharge_max = Decimal(tax_setting['late_fee_surcharge_max'])

		late_fees, months_late, interest, surcharge, principle = calc_interest(self.due_date, self.remaining_amount, surcharge_rate, surcharge_max, interest_rate, self.remaining_amount, as_at)

		return self.remaining_amount, (late_fees or 0)


	def get_installments(self):
		paid = (self.amount or 0) - (self.remaining_amount or 0)
		installments = self.installments.all().order_by('due')
		for i in installments:
			if paid < i.amount:
				i.paid = paid
				paid = 0
			else: # already paid
				paid = paid - i.amount
				i.paid = i.amount
			i.owed = i.amount - i.paid
		return installments


	def calculateRemainingAmount(self, amount):
		from django.db.models import Sum
		"""given a new amount, calculate the amount remaining"""
		if amount is None:
			return None
		paid_amount = self.payments.filter(amount__gt=0).aggregate(sum=Sum('amount'))['sum'] or 0
		remaining_amount = amount - paid_amount
		return remaining_amount

	def get_paid_amount(self):
		from django.db.models import Sum
		paid = self.payments.filter(amount__gt=0).aggregate(amount=Sum('amount'), fines=Sum('fine_amount'))
		total = paid['amount'] or 0
		fines = paid['fines'] or 0
		capital_amount = total - fines
		return capital_amount, fines


	def get_remaining_amount(self):
		return (self.amount - self.get_paid_amount()[0])


	def reset_tax(self):
		self.submit_date = None
		self.amount = self.remaining_amount = 0
		self.is_paid = False
		self.save()
		try:
			self.formuladata.delete()
		except:
			pass


	@property
	def tax_type(self):
		if type(self) is PropertyTaxItem:
			return 'fixed_asset_tax'
		elif type(self) is RentalIncomeTax:
			return 'rental_income_tax'
		elif type(self) is TradingLicenseTax:
			return 'trading_license_tax'
		elif type(self) is Fee and 'land_lease' in self.fee_type:
			return 'land_lease_fee'
		elif type(self) is Fee:
			return 'fee'


	@property
	def fee_setting(self):
		if type(self) is PropertyTaxItem:
			return 'fixed_asset_tax'
		else:
			return 'general_fee'

	def generateInstallments(self):
		amount = self.remaining_amount
		months = 3
		no_installments = 12/months
		if type(self.period_from) is datetime:
			date_from = self.period_from.astimezone(timezone.get_default_timezone()).date()
		due_date = date_from
		for i in range(no_installments):
			due_date = due_date + relativedelta(months=months-1) + relativedelta(day=31)
			amount = round(self.remaining_amount / no_installments)
			Installment.objects.create(fee=self, amount=amount, paid=0, due=due_date)
		return self.installments.all()

	def pay_installment(self, amount, paid_on=None):
		installments = self.installments.filter(paid__lt=F('amount')).order_by('due')
		paid_on = paid_on or date.today()
		for installment in installments:
			unpaid = installment.amount - installment.paid
			if amount <= unpaid:
				installment.paid += amount
				installment.paid_on = paid_on
				installment.save()
				break
			else:
				installment.paid = installment.amount
				installment.paid_on = paid_on
				installment.save()
				amount -= unpaid

	def next_outstanding_installment(self):
		installments = self.installments.filter(paid__lt=F('amount')).order_by('due')
		if installments:
			return installments[0]
		else:
			return None

	def calc_tax_period(self):
		if type(self) is not Fee or type(self) is Fee and self.fee_type == 'land_lease':
			date_from = date(self.date_from.year, 1, 1)
			date_to = date(self.date_from.year, 12, 31)
		else:
			date_from = self.date_from
			date_to = self.date_to

		owners = None
		date_started = None
		if hasattr(self, 'subbusiness') and self.subbusiness:
			owners = self.subbusiness.business.owners.filter(i_status='active').order_by('date_started')
			date_started = self.subbusiness.business.date_started
		if hasattr(self, 'business') and self.business:
			owners = self.business.owners.filter(i_status='active').order_by('date_started')
			date_started = self.business.date_started
			if self.business.closed_date and self.business.closed_date < date_to:
				date_to = self.business.closed_date
		elif hasattr(self, 'property') and self.property:
			owners = self.property.owners.filter(i_status='active').order_by('date_started')
		if date_started:
			if date_started > date_from and date_started <= date_to:
				date_from = date_started
		if owners:
			date_started = owners[0].date_started
			if date_started > date_from and date_started <= date_to:
				date_from = date_started

		"""
		if self.months_exempted:
			date_from = date_from + relativedelta(months=self.months_exempted)
			if date_from > date_to:
				date_from = date_to
		"""

		return date_from, date_to


"""
class Payment(models.Model):
	# models.ForeignKey(Tax)
	business_id = models.IntegerField(help_text="The business who pay this tax item.", blank = True, null=True)
	citizen_id = models.IntegerField(blank = True, null=True)
	staff  = models.ForeignKey(PMUser, help_text="",blank = True, null=True)
	amount = models.DecimalField(max_digits = 20, decimal_places = 2)
	receipt_no = models.CharField(max_length = 50)
	bank =  models.CharField(max_length = 100, choices=variables.banks)
	paid_date = models.DateField(help_text="",default=datetime.now)
	fine_amount = models.DecimalField(max_digits = 20, decimal_places = 2, default=0)
	fine_description = models.TextField(null=True, blank = True)
	manual_receipt = models.CharField(max_length = 50)
	date_time = models.DateTimeField(help_text="The date when this payment is entered into the system.",auto_now_add=True,auto_now=True)
	note = models.TextField(null=True, blank = True,  help_text="note about this payment.")
	i_status = models.CharField(max_length = 10, choices = variables.status_choices, default='active', blank = True)
"""
"""
Land Rental Tax Models
"""
class LandRentalTax(models.Model):
	plot_id = models.IntegerField(help_text='This is the ID of the Plot.')
	amount = models.DecimalField(max_digits = 20, decimal_places = 2, help_text="The amount of tax item.")
	currency = models.CharField(max_length=4, choices=variables.currency_types)
	period_from = models.DateTimeField(help_text="The start date of a period that this tax item is for.")
	period_to = models.DateTimeField(help_text="The end date of a period that this tax item is for.")
	due_date = models.DateField(help_text="The date this tax item is due.")
	is_paid = models.BooleanField(help_text="Whether tax is payed.")
	date_time = models.DateTimeField(help_text="The date this tax item is generated.")
	property = models.ForeignKey(Property, null=True, blank=True)


class LandRentalTaxNotes(models.Model):
	land_rental_tax = models.ForeignKey('LandRentalTax')
	staff_id = models.IntegerField(help_text='This is the Id of the Staff Member that created the note.')
	note = models.TextField(help_text='This is the Note for the LandRental Tax Record Itself.')
	date_time = models.DateTimeField(help_text='This is the Date and Time the Note Was Created',auto_now_add=True,auto_now=True)

class LandRentalTaxMedia(models.Model):
	land_rental_tax = models.ForeignKey('LandRentalTax')

"""
The following Models are Related to the P = IncompletePayment.objects.all()
			search_iroperty Asset Tax Collection and Evalutional
"""

class PropertyTaxItem(Tax):
	plot_id = models.CharField(max_length = 50, help_text = 'This is the ID of the Plot that the Declared Value is for.')
	amount = models.DecimalField(max_digits = 20, decimal_places = 2, help_text="The amount oIntegerFieldf property tax item.", null=True, blank = True)
	remaining_amount = models.DecimalField(max_digits = 20, decimal_places = 2, help_text="The remaining amount (subtracted past payments).", null=True, blank = True)
	currency = models.CharField(max_length=4, choices=variables.currency_types)
	period_from = models.DateTimeField(help_text="The start date of a period that this property tax item is for.")
	period_to = models.DateTimeField(help_text="The end date of a period that this property tax item is for.")
	date_from = models.DateField(null=True)
	date_to = models.DateField(null=True)
	due_date = models.DateField(help_text="The date this property tax item is due.", null=True, blank=True, default=None)
	date_time = models.DateTimeField(help_text="The date this propert tax item is generated.", blank=True, default=None)
	is_paid = models.BooleanField(help_text="Whether tax is payed.")
	is_chanllenged = models.BooleanField(help_text="whether this tax item is challenged.")
	is_reviewed = models.BooleanField(help_text ="whether this tax item is reviewed.")
	is_accepted = models.BooleanField(help_text="whether this tax item is accepted.")
	submit_date = models.DateTimeField(help_text="The date this fee item is submited.", null=True, blank=True)
	submit_details = models.CharField(max_length=500, null=True, blank=True)
	staff_id = models.IntegerField(help_text="The staff who generates this property tax item.", null=True, blank=True)
	i_status = models.CharField(max_length = 10, choices = variables.status_choices, default='active', blank = True)
	property = models.ForeignKey(Property, null=True, blank=True, related_name='fixed_asset_taxes')
	exempt = models.BooleanField(default=False)
	months_deferred = models.IntegerField(default=0)
	land_use_types = models.ManyToManyField(LandUse)
	declared_value = models.ForeignKey(DeclaredValue, null=True, blank=True)
	#citizen_owners = models.ManyToManyField(Citizen)
	#business_owners = models.ManyToManyField(Business)


	def __unicode__(self):
		#return 'sd ' + str(self.id)
		name = "Property Tax Item (UPI: " + str(self.property.getUPI()) + ") "
		if self.date_from and self.date_to:
			name += "[" + DateFormat(self.date_from).format('d/m/Y') + " - " + DateFormat(self.date_to).format('d/m/Y') + "]"
		return name

	def calc_tax(self):
		property = self.property
		declared_value = property.declaredValue
		self.date_from, self.date_to = self.calc_tax_period()

		if declared_value and declared_value.declared_on and declared_value.amount is not None and property.land_use_types.count() > 0:
			expired_declared_value = declared_value.declared_on + relativedelta(years=4) < self.date_from
			if not expired_declared_value: # declared value has not expired, auto submit tax calc
				if declared_value.residential_amount + declared_value.agriculture_amount + declared_value.commercial_amount == declared_value.amount:
					tax_summary = Setting.calculateFixedAssetTax(self.date_from, self.date_to, residential=declared_value.residential_amount, commercial=declared_value.commercial_amount, agricultural=declared_value.agriculture_amount)
				else:
					land_use_codes = [land_use_type.code for land_use_type in property.land_use_types.all()]
					if 'RES' in land_use_codes:
						tax_summary = Setting.calculateFixedAssetTax(self.date_from, self.date_to, residential=declared_value.amount)
					elif 'AGR' in land_use_codes:
						tax_summary = Setting.calculateFixedAssetTax(self.date_from, self.date_to, agricultural=declared_value.amount)
					elif 'IND' in land_use_codes or 'QRY' in land_use_codes or 'COM' in land_use_codes: # industrial
						tax_summary = Setting.calculateFixedAssetTax(self.date_from, self.date_to, industrial=declared_value.amount)
					else:
						raise Exception("Property ID %s does not contain a valid land use" % property.pk)
				if tax_summary:
					if self.exempt:
						self.amount = 0
					else:
						self.amount = tax_summary['amount']
					self.remaining_amount = self.calculateRemainingAmount(self.amount)
					if self.remaining_amount <= 0:
						self.is_paid = True
					else:
						self.is_paid = False
					self.due_date = tax_summary['due_date']
					self.save()

					fd, created = FormulaData.objects.get_or_create(property_item=self)
					fd.formula_data = tax_summary
					fd.save()
					return tax_summary
		self.due_date = Setting.get_due_date('fixed_asset_tax', self.date_to)
		self.reset_tax()
		return None

	def getLogMessage(self,old_data=None,new_data=None, action=None):
		return getLogMessage(self,old_data,new_data, action)


class ChallengePropertyTaxItem(models.Model):
	property_tax_item = models.ForeignKey(PropertyTaxItem)
	citizen_id = models.IntegerField(help_text="The person who pay this tax item.")
	staff_id = models.IntegerField(help_text="The government staff who accepts the payment.")
	period_from = models.DateTimeField(help_text="The date from which this tax item is challenged.",auto_now_add=True,auto_now=True)
	period_to = models.DateTimeField(help_text="The date till which this tax item is challenged.")

class ChallengePropertyTaxItemNote(models.Model):
	challenge_property_tax_item = models.ForeignKey(ChallengePropertyTaxItem)
	staff_id = models.IntegerField(help_text="The government staff who records this challenge.")
	note = models.TextField(help_text="Note on why this property tax item is challenged.")

class ChallengePropertyTaxItemMedia(models.Model):
	challengepropertytaxitemid = models.ForeignKey(ChallengePropertyTaxItem)
	mediatype = models.CharField(max_length=4,choices=variables.media_types,help_text='This is the type of media the file is')
	mediafile = models.FileField(help_text='This is the location of the file on the file system.',upload_to='tmp')
	staffid = models.IntegerField(help_text='The ID of the Staff Member who uploaded the file')
	mediadatetime = models.DateTimeField(help_text='This is the date and time the file was uploaded',auto_now_add=True,auto_now=True)

class ReviewPropertyTaxItem(models.Model):
	challengepropertytaxitemid = models.ForeignKey(ChallengePropertyTaxItem)
	staffid = models.IntegerField(help_text="The government staff who review the challenge.")
	reviewdate = models.DateTimeField(help_text="The date when this tax item is reviewd.",auto_now_add=True,auto_now=True)
	note = models.CharField(max_length=255, help_text="review result.")

"""
The following Models are Related to the Rental Income Tax Collection and Evalutional
"""
class RentalIncomeTax(Tax):
	plot_id = models.CharField(max_length = 50, help_text='This is the ID of the Plot that the Declared Value is for.')
	amount = models.DecimalField(max_digits = 20, decimal_places = 2, help_text="The amount of tax item.", null=True, blank = True)
	remaining_amount = models.DecimalField(max_digits = 20, decimal_places = 2, help_text="The remaining amount (subtracted past payments).", null=True, blank = True)
	currency = models.CharField(max_length=4, choices=variables.currency_types)
	period_from = models.DateTimeField(help_text="The start date of a period that this tax item is for.")
	period_to = models.DateTimeField(help_text="The end date of a period that this tax item is for.")
	date_from = models.DateField(null=True)
	date_to = models.DateField(null=True)
	due_date = models.DateField(help_text="The date this tax item is due.", null=True, blank=True)
	is_paid = models.BooleanField(help_text="Whether tax is payed.")
	submit_date = models.DateTimeField(help_text="The date this fee item is submited.", null=True, blank=True)
	submit_details = models.CharField(max_length=500, null=True, blank=True)
	date_time = models.DateTimeField(help_text="The date this tax item is generated.")
	i_status = models.CharField(max_length = 10, choices = variables.status_choices, default='active', blank = True)
	property = models.ForeignKey(Property, null=True, blank=True, related_name='rental_income_taxes')
	staff_id = models.IntegerField(help_text="The staff who generates this property tax item.", null=True, blank=True)
	exempt = models.BooleanField(default=False)
	months_deferred = models.IntegerField(default=0)
	declared_rental_income = models.DecimalField(max_digits = 20, decimal_places = 2, help_text="Last year declared rental income.", null=True, blank = True)
	declared_bank_interest = models.DecimalField(max_digits = 20, decimal_places = 2, help_text="Last year bank interest paid", null=True, blank = True)
	#citizen_owners = models.ManyToManyField(Citizen)
	#business_owners = models.ManyToManyField(Business)

	def __unicode__(self):
		name = "Rental Income Tax (UPI: " + str(self.property.getUPI()) + ") "
		if self.date_from and self.date_to:
			name += "[" + DateFormat(self.date_from).format('d/m/Y') + " - " + DateFormat(self.date_to).format('d/m/Y') + "]"
		return name


	def getLogMessage(self,old_data=None,new_data=None, action=None):
		return getLogMessage(self,old_data,new_data, action)

	def calc_tax(self):
		self.date_from, self.date_to = self.calc_tax_period()
		if self.declared_bank_interest and self.declared_rental_income:
			tax_summary = Setting.calculateRentalIncome(self.date_from, self.date_to, self.declared_rental_income, self.declared_bank_interest)
			if tax_summary:
				if self.exempt:
					self.amount = 0
				else:
					self.amount = tax_summary['amount']
				self.remaining_amount = self.calculateRemainingAmount(self.amount)
				if self.remaining_amount <= 0 and not self.exempt:
					self.is_paid = True
				else:
					self.is_paid = False
				self.due_date = tax_summary['due_date']
				self.save()
				fd, created = FormulaData.objects.get_or_create(rental_income=self)
				fd.formula_data = tax_summary
				fd.save()
				return tax_summary

		self.due_date = Setting.get_due_date('rental_income_tax', self.date_to)
		self.reset_tax()
		return None


class RentalIncomeTaxNotes(Tax):
	rental_income_tax = models.ForeignKey('rentalIncomeTax')
	staff_id = models.IntegerField(help_text='This is the Id of the Staff Member that created the note.')
	note = models.TextField(help_text='This is the Note for the LandRental Tax Record Itself.')
	date_time = models.DateTimeField(help_text='This is the Date and Time the Note Was Created',auto_now_add=True,auto_now=True)
	def getLogMessage(self,old_data=None,new_data=None, action=None):
		return getLogMessage(self,old_data,new_data, action)

"""
The following Models are Related to the Trading License Tax Collection and Evalutional
"""
class TradingLicenseTax(Tax):
	business = models.ForeignKey(Business, null=True, blank=True, help_text="Business that have trading license to be taxed.")
	subbusiness = models.ForeignKey(SubBusiness,  null=True, blank=True, help_text="SubBusiness that have trading license to be taxed.")
	amount = models.DecimalField(max_digits = 20, decimal_places = 2, help_text="The amount of property tax item.", null=True, blank = True)
	remaining_amount = models.DecimalField(max_digits = 20, decimal_places = 2, help_text="The remaining amount (subtracted past payments).", null=True, blank = True)
	currency = models.CharField(max_length=4, choices=variables.currency_types)
	period_from = models.DateTimeField(help_text="The start date of a period that this property tax item is for.")
	period_to = models.DateTimeField(help_text="The end date of a period that this property tax item is for.")
	date_from = models.DateField(null=True)
	date_to = models.DateField(null=True)
	due_date = models.DateField(help_text="The date this property tax item is due.", null=True, blank = True)
	is_paid = models.BooleanField(help_text="Whether tax is payed.")
	submit_date = models.DateTimeField(help_text="The date this fee item is submited.", null=True, blank=True)
	submit_details = models.CharField(max_length=500, null=True, blank=True)
	staff_id = models.IntegerField(help_text="The staff who generates this property tax item.", null=True, blank = True)
	date_time = models.DateTimeField(help_text="The date this propert tax item is generated.")
	i_status = models.CharField(max_length = 10, choices = variables.status_choices, default='active', blank = True)
	exempt = models.BooleanField(default=False)
	turnover = models.DecimalField(max_digits=20, decimal_places=2, help_text="Declared Turnover", null=True)
	months_deferred = models.IntegerField(default=0)
	activity_data = models.TextField(blank=False, null=True)


	def __unicode__(self):
		if self.business:
			name = "Trading License Tax (TIN: " + str(self.business.tin) + ") "

		elif self.subbusiness:
			name = "Trading License Tax (TIN: " + str(self.subbusiness.business.tin) + ",branch:"+self.subbusiness.branch + ") [" + DateFormat(self.period_from).format('d/m/Y') + " - " + DateFormat(self.period_to).format('d/m/Y') + "]"
			if self.date_from and self.date_to:
				name += "[" + DateFormat(self.date_from).format('d/m/Y') + " - " + DateFormat(self.date_to).format('d/m/Y') + "]"
		return name

	def getLogMessage(self,old_data=None,new_data=None, action=None):
		return getLogMessage(self,old_data,new_data, action)


	def calculateActivityTax(self, *args, **kwargs):
		if not self.activity_data:
			self.reset_tax()
			return None
		else:
			activity_data = pickle.loads(self.activity_data.decode('base64'))
		tax_due = 0
		date_from = self.date_from
		date_to = self.date_to
		due_date = self.date_to
		formula_data = {}
		current_year = date_from.year
		total_days_in_period = Decimal((date(current_year, 12, 31) - date(current_year, 1, 1)).days + 1)
		period = (date_from, date_to)
		days_in_period = Decimal((date_to - date_from).days + 1)
		activities = variables.activities
		formula_data = {}
		activity_description = variables.activity_description
		for activity, settings in activities:
			for setting_name, rate in settings:
				units = activity_data.get("%s_%s" % (activity, setting_name), 0)
				if not units: continue
				amount= Decimal(units * rate).quantize(Decimal('0.01'))
				tax_due += amount
				formula_data["%s - %s" % (activity_description[activity], setting_name)] = {'units':units, 'rate': rate, 'amount':amount }

		tax_due = Decimal(int(tax_due * days_in_period / total_days_in_period))
		return { 'amount':tax_due, 'due_date': due_date, 'due': due_date, 'formula_data':formula_data, 'days':days_in_period, 'total_days':total_days_in_period, 'vat':False }


	def calc_tax(self):

		if self.subbusiness:
			business = self.subbusiness.business
		else:
			business = self.business

		self.date_from, self.date_to = self.calc_tax_period()

		if business.vat_register:
			if self.turnover:
				tax_summary = Setting.calculateTradingLicenseTax(self.date_from, self.date_to, self.turnover,
					sector=business.sector)
			else:
				tax_summary = None
		else:
			tax_summary = self.calculateActivityTax()

		if tax_summary:
			if self.exempt:
				self.amount = 0
			else:
				self.amount = tax_summary['amount']
			self.remaining_amount = self.calculateRemainingAmount(self.amount)
			if self.remaining_amount <= 0:
				self.is_paid = True
			else:
				self.is_paid = False
			self.due_date = tax_summary['due_date']
			self.save()
		else:
			self.due_date = Setting.get_due_date('trading_license_tax', self.date_to)
			self.reset_tax()
			return None

		fd, created = FormulaData.objects.get_or_create(trading_license=self)
		fd.formula_data = tax_summary
		fd.save()
		if self.exempt:
			self.amount = 0
		self.save()
		return tax_summary


class FeeManager(models.Manager):
	def get_query_set(self):
		return super(FeeManager,self).get_query_set().filter(status__code='active')


class Fee(Tax):
	fee_type = models.CharField(max_length=25, choices=variables.fee_types)
	name = models.CharField(max_length=50, null=True, blank=True)
	quantity = models.IntegerField(default=1, null=True, blank=True)
	#target = models.CharField(max_length=25, null = True, blank=True, help_text="Payer type.")
	#target_id = models.IntegerField(null=True, blank=True, help_text="Who will pay.")
	#target_branch_id = models.IntegerField(help_text="Branch of target. i.e., branch of business", null=True, blank=True)
	amount = models.DecimalField(max_digits = 20, decimal_places = 2, help_text="The amount of fee item.")
	remaining_amount = models.DecimalField(max_digits = 20, decimal_places = 2, help_text="The remaining amount (subtracted past payments).", null=True, blank = True)
	currency = models.CharField(max_length=4, choices=variables.currency_types)
	period_from = models.DateTimeField(help_text="The start date of a period that this fee item is for.")
	period_to = models.DateTimeField(help_text="The end date of a period that this fee item is for.")
	date_from = models.DateField(null=True)
	date_to = models.DateField(null=True)
	due_date = models.DateField(help_text="The date this fee item is due.", null=True, blank=True)
	is_paid = models.BooleanField(help_text="Whether fee is payed.")
	submit_date = models.DateTimeField(help_text="The date this fee item is submited.", null=True, blank=True)
	submit_details = models.CharField(max_length=500, null=True, blank=True)
	staff_id = models.IntegerField(help_text="The staff who generates this fee item.", null=True, blank=True)
	date_time = models.DateTimeField(help_text="The date this fee item is generated.",auto_now_add=True, auto_now=True)
	i_status = models.CharField(max_length = 10, choices = variables.status_choices, default='active', blank = True)
	business = models.ForeignKey(Business, null=True, blank=True, related_name='business_fees')
	subbusiness = models.ForeignKey(SubBusiness,null=True, blank=True)
	property = models.ForeignKey(Property,null=True,blank=True, related_name='property_fees')
	citizen = models.ForeignKey(Citizen,null=True,blank=True)
	exempt = models.BooleanField(default=False)
	land_lease_type = models.ForeignKey(LandUse, null=True, blank=True, default=None)
	#citizen_owners = models.ManyToManyField(Citizen)
	#business_owners = models.ManyToManyField(Business)
	category = models.ForeignKey(CategoryChoice, related_name='fee_category')
	status = models.ForeignKey(CategoryChoice)
	objects = FeeManager()
	all_objects = models.Manager()

	def __unicode__(self):
		if 'cleaning' in self.fee_type:
			return 'Cleaning fee for %s' % self.date_from.strftime("%B %Y")

		name = self.fee_type.title() + " Fee "
		if self.date_from and self.date_to:
			name += "[" + DateFormat(self.date_from).format('d/m/Y') + " - " + DateFormat(self.date_to).format('d/m/Y') + "]"
		return name

	def getLogMessage(self,old_data=None,new_data=None, action=None):
		return getLogMessage(self,old_data,new_data, action)


	def calc_tax(self):
		if self.fee_type in ('cleaning_fee', 'cleaning'):
			return self.calc_cleaningFee()
		elif self.fee_type in ('land_lease', 'land_lease_fee'):
			raise Exception('not implemented')
		else:
			return None

	def calc_landlease(self):
		self.date_from, self.date_to = self.calc_tax_period()
		land_size = self.property.get_sq_m()
		if self.property.land_use_type and land_size:
			tax_summary = Setting.calculateLandLeaseFee(self.date_from, self.date_to, self.property.land_use_type, land_size, district=self.property.sector.district, sector=self.property.sector, cell=self.property.cell, village=self.property.village)
			if tax_summary:
				if self.exempt:
					self.amount = 0
				else:
					self.amount = tax_summary['amount']
				self.remaining_amount = self.calculateRemainingAmount(self.amount) or 0
				self.due_date = tax_summary['due_date']

				fd, created = FormulaData.objects.get_or_create(fee=self)
				fd.formula_data = tax_summary
				fd.save()
				self.save()
				return tax_summary

		self.due_date = Setting.get_due_date('land_lease_fee', self.date_to)
		self.reset_tax()
		return None


	def calc_cleaningFee(self):
		if self.category.code == 'cleaning' and not self.is_paid:
			business = self.business
			if business.business_category is not None:
				if business.business_category_id in range(1,7):
					self.amount = 10000
				elif business.business_category_id == 7:
					self.amount = 5000
				elif business.business_category_id == 8:
					self.amount = 3000
				else:
					self.amount = 0

				self.remaining_amount = self.calculateRemainingAmount(self.amount) or 0
				if self.remaining_amount <= 0 and self.amount > 0:
					self.is_paid = True
				else:
					self.is_paid = False

				self.submit_date = datetime.now()
				due_date = self.date_from + relativedelta(months=1)
				self.due_date = date(due_date.year, due_date.month, 5)

				if self.amount:
					self.i_status = 'active'
					self.status = CategoryChoice.objects.get(category__code='status', code='active')
				self.save()
				return self.amount, self.due_date

			if self.pk:
				self.submit_date = None
				self.i_status = 'inactive'
				self.status = CategoryChoice.objects.get(category__code='status', code='inactive')
				self.is_paid = False
				self.save()

		return (None, None)

	def medias(self):
		from media.models import Media
		return Media.objects.filter(tax_type__in=['cleaning_fee','cleaning','fee'], tax_id=self.pk)


class MiscellaneousFee(models.Model):
	fee_type = models.CharField(max_length=250)
	fee_sub_type = models.CharField(max_length=250)
	amount = models.DecimalField(max_digits = 20, decimal_places = 2, help_text="The amount of fee item.")
	remaining_amount = models.DecimalField(max_digits = 20, decimal_places = 2, help_text="The remaining amount (subtracted past payments).", null=True, blank = True)
	currency = models.CharField(max_length=4, choices=variables.currency_types)
	is_paid = models.BooleanField(help_text="Whether fee is paid.")
	submit_date = models.DateTimeField(help_text="The date this fee item is submited.", null=True, blank=True)
	submit_details = models.CharField(max_length=500, null=True, blank=True)
	staff_id = models.IntegerField(help_text="The staff who generates this fee item.", null=True, blank=True)
	date_time = models.DateTimeField(help_text="The date this fee item is generated.",auto_now_add=True,auto_now=True)
	i_status = models.CharField(max_length = 10, choices = variables.status_choices, default='active', blank = True)
	business = models.ForeignKey(Business, null=True, blank=True)
	subbusiness = models.ForeignKey(SubBusiness,null=True, blank=True)
	property = models.ForeignKey(Property,null=True,blank=True)
	citizen = models.ForeignKey(Citizen,null=True,blank=True)

	def __unicode__(self):
		return self.fee_type.title() + " - " + self.fee_sub_type.title() + " Miscellaneous Fee "

	def getLogMessage(self,old_data=None,new_data=None, action=None):
		return getLogMessage(self,old_data,new_data, action)

"""
The following Models is for saving payments for Tax Items
"""
class PayRentalIncomeTax(models.Model):
	rental_income_tax = models.ForeignKey(RentalIncomeTax, help_text="", related_name="payments")
	business_id = models.IntegerField(help_text="The business who pay this tax item.", blank = True, null=True)
	citizen_id = models.IntegerField(blank = True, null=True)
	staff  = models.ForeignKey(PMUser, help_text="",blank = True, null=True)
	amount = models.DecimalField(max_digits = 20, decimal_places = 2)
	receipt_no = models.CharField(max_length = 50)
	bank =  models.CharField(max_length = 100, choices=variables.banks)
	paid_date = models.DateField(help_text="",default=datetime.now)
	fine_amount = models.DecimalField(max_digits = 20, decimal_places = 2, default=0)
	fine_description = models.TextField(null=True, blank = True)
	manual_receipt = models.CharField(max_length = 50)
	date_time = models.DateTimeField(help_text="The date when this payment is entered into the system.",auto_now_add=True,auto_now=True)
	note = models.TextField(null=True, blank = True,  help_text="note about this payment.")
	i_status = models.CharField(max_length = 10, choices = variables.status_choices, default='active', blank = True)

	def __unicode__(self):
		return "Rental Income Tax Payment"

	def getLogMessage(self,old_data=None,new_data=None, action=None):
		return getLogMessage(self,old_data,new_data, action)


class PayTradingLicenseTax(models.Model):
	citizen_id = models.IntegerField(blank = True, null=True)
	business_id = models.IntegerField(help_text="The business who pay this tax item.", blank = True, null=True)
	#staff_id = models.IntegerField(help_text="The government staff who accepts the payment.")
	staff  = models.ForeignKey(PMUser, help_text="",blank = True, null=True)
	trading_license_tax = models.ForeignKey(TradingLicenseTax, help_text="", related_name="payments")
	amount = models.DecimalField(max_digits = 20, decimal_places = 2)
	receipt_no = models.CharField(max_length = 50)
	bank =  models.CharField(max_length = 100, choices=variables.banks)
	paid_date = models.DateField(help_text="",default=datetime.now)
	fine_amount = models.DecimalField(max_digits = 20, decimal_places = 2, default=0)
	fine_description = models.TextField(null=True, blank = True)
	manual_receipt = models.CharField(max_length = 50)
	date_time = models.DateTimeField(help_text="The date when this payment is entered into the system.",auto_now_add=True,auto_now=True)
	note = models.TextField(null=True, blank = True,  help_text="note about this payment.")
	i_status = models.CharField(max_length = 10, choices = variables.status_choices, default='active', blank = True)
	def __unicode__(self):
		return "Trading License Tax Payment"
	def getLogMessage(self,old_data=None,new_data=None, action=None):
		return getLogMessage(self,old_data,new_data, action)

class PayFeeManager(models.Manager):
	def get_query_set(self):
		return super(PayFeeManager,self).get_query_set().filter(status__code='active')

class PayFee(models.Model):
	citizen_id = models.IntegerField(blank = True, null=True)
	business_id = models.IntegerField(help_text="The business who pay this tax item.", blank = True, null=True)
	staff  = models.ForeignKey(PMUser, help_text="",blank = True, null=True)
	fee = models.ForeignKey(Fee, help_text="", related_name="payments")
	amount = models.DecimalField(max_digits = 20, decimal_places = 2)
	receipt_no = models.CharField(max_length = 50)
	bank =  models.CharField(max_length = 100, choices=variables.banks)
	paid_date = models.DateField(help_text="",default=datetime.now)
	fine_amount = models.DecimalField(max_digits = 20, decimal_places = 2, default=0,null=True, blank = True)
	fine_description = models.TextField(null=True, blank = True)
	manual_receipt = models.CharField(max_length = 50)
	date_time = models.DateTimeField(help_text="The date when this payment is entered into the system.",auto_now_add=True,auto_now=True)
	note = models.TextField(null=True, blank = True,   help_text="note about this payment.")
	i_status = models.CharField(max_length = 10, choices = variables.status_choices, default='active', blank = True)
	receipt_id = models.IntegerField(null=True)
	status = models.ForeignKey(CategoryChoice)
	objects = PayFeeManager()
	all_objects = models.Manager()

	def __unicode__(self):
		return "Fee Payment"
	def getLogMessage(self,old_data=None,new_data=None, action=None):
		return getLogMessage(self,old_data,new_data, action)



class PayFixedAssetTax(models.Model):
	property_tax_item = models.ForeignKey(PropertyTaxItem, related_name="payments")
	business_id = models.IntegerField(help_text="The business who pay this tax item.", blank = True, null=True)
	citizen_id = models.IntegerField(help_text="The person who pay this tax item.", blank = True, null=True)
	#staff_id = models.IntegerField(help_text="The government staff who accepts the payment.")
	staff  = models.ForeignKey(PMUser, help_text="",blank = True, null=True)
	amount = models.DecimalField(max_digits = 20, decimal_places = 2)
	receipt_no = models.CharField(max_length = 50)
	bank =  models.CharField(max_length = 100, choices=variables.banks)
	paid_date = models.DateField(help_text="",default=datetime.now)
	fine_amount = models.DecimalField(max_digits = 20, decimal_places = 2, default=0)
	fine_description = models.TextField(null=True, blank = True)
	manual_receipt = models.CharField(max_length = 50)
	date_time = models.DateTimeField(help_text="The date when this payment is entered into the system.",auto_now_add=True,auto_now=True)
	note = models.TextField(null=True, blank = True, help_text="note about this payment.")
	i_status = models.CharField(max_length = 10, choices = variables.status_choices, default='active', blank = True)
	def __unicode__(self):
		return "Fixed Asset Tax Payment"
	def getLogMessage(self,old_data=None,new_data=None, action=None):
		return getLogMessage(self,old_data,new_data, action)


class PayMiscellaneousFee(models.Model):
	business = models.ForeignKey(Business, null=True, blank=True)
	citizen = models.ForeignKey(Citizen,null=True,blank=True)
	#staff_id = models.IntegerField(help_text="The government staff who accepts the payment.")
	staff  = models.ForeignKey(PMUser, help_text="",blank = True, null=True)
	fee = models.ForeignKey(MiscellaneousFee, help_text="", related_name="payments")
	amount = models.DecimalField(max_digits = 20, decimal_places = 2)
	receipt_no = models.CharField(max_length = 50)
	bank =  models.CharField(max_length = 100, choices=variables.banks)
	paid_date = models.DateField(help_text="",default=datetime.now)
	fine_amount = models.DecimalField(max_digits = 20, decimal_places = 2, default=0,null=True, blank = True)
	fine_description = models.TextField(null=True, blank = True)
	manual_receipt = models.CharField(max_length = 50)
	date_time = models.DateTimeField(help_text="The date when this payment is entered into the system.",auto_now_add=True,auto_now=True)
	note = models.TextField(null=True, blank = True,   help_text="note about this payment.")
	i_status = models.CharField(max_length = 10, choices = variables.status_choices, default='active', blank = True)

	def __unicode__(self):
		return "Fee Payment"
	def getLogMessage(self,old_data=None,new_data=None, action=None):
		return getLogMessage(self,old_data,new_data, action)


#Pending Payment
class PendingPayment(models.Model):
	payment_id = models.CharField(max_length = 50)
	tax_type = models.CharField(max_length = 50)
	tax_id = models.CharField(max_length = 50)
	reason = models.CharField(max_length = 250)
	note = models.TextField(null=True, blank = True,   help_text="note about this payment.")
	user = models.ForeignKey(PMUser, null=True, blank = True)
	date_time = models.DateTimeField(help_text="The date when this payment is entered into the system.",auto_now_add=True,auto_now=True)
	i_status = models.CharField(max_length = 10, choices = variables.status_choices, default='active', blank = True)

	def __unicode__(self):
		return "Pending Payment"
	def getLogMessage(self,old_data=None,new_data=None, action=None):
		return getLogMessage(self,old_data,new_data, action)

class FormulaData(models.Model):

	data = models.TextField()
	fee = models.OneToOneField(Fee, null=True)
	property_item = models.OneToOneField(PropertyTaxItem, null=True)
	trading_license = models.OneToOneField(TradingLicenseTax, null=True)
	rental_income = models.OneToOneField(RentalIncomeTax, null=True)

	def get_pickle(self):
		return pickle.loads(self.data.decode('base64'))

	def set_pickle(self, value):
		self.data = pickle.dumps(value).encode('base64')

	def del_pickle(self):
		self.data = None

	formula_data = property_decorator(get_pickle, set_pickle, del_pickle)


class CleaningSchedule(models.Model):
	valid_from = models.DateField(help_text='Date this setting to be valid from.')
	council = models.ForeignKey(Council, null=True, blank=True, help_text="The council that setting applied to.")
	district = models.ForeignKey(District, null=True, blank=True, help_text="")
	sector = models.ForeignKey(Sector, null=True, blank=True, help_text="")
	cell = models.ForeignKey(Cell, null=True, blank=True, help_text="")
	amount =  models.DecimalField(decimal_places=0, max_digits=9)
	due_date = models.DateField(null=True, blank=True)
	business_category = models.ForeignKey(BusinessCategory)
	modified = models.DateTimeField(help_text="The date when this setting is entered into the system.",auto_now_add=True,auto_now=True)


class Setting(models.Model):
	tax_fee_name = models.CharField(max_length = 50, help_text="Tax / Fee Name")
	setting_name = models.CharField(max_length = 50, help_text="Tax / Fee Setting Name")
	sub_type = models.CharField(max_length = 250, blank = True, help_text="Tax / Fee Setting Sub Catergories that differentiate the rate / fee")
	value = models.CharField(max_length = 50, default='',help_text="Setting Value, can be fee/tax rate/date/etc")
	description = models.TextField(null=True, blank = True, help_text="Description about this payment.")
	valid_from = models.DateField(help_text='Date this setting to be valid from.')
	valid_to = models.DateField(help_text='Date this setting get deprecated.', null=True, blank = True)
	council = models.ForeignKey(Council, null=True, blank=True, help_text="The council that setting applied to.")
	district = models.ForeignKey(District, null=True, blank=True, help_text="")
	sector = models.ForeignKey(Sector, null=True, blank=True, help_text="")
	cell = models.ForeignKey(Cell, null=True, blank=True, help_text="")
	village = models.ForeignKey(Village, null=True, blank=True, help_text="")
	i_status = models.CharField(max_length = 10, choices = variables.status_choices, default='active', blank = True)
	date_time = models.DateTimeField(help_text="The date when this setting is entered into the system.",auto_now_add=True,auto_now=True)

	def __unicode__(self):
		return "ID:" + str(self.id) + " - " + str(self.tax_fee_name) + " " + str(self.setting_name) + " - " + str(self.sub_type) + "[ " + str(self.value) + " ] (" + self.i_status + ")"

	def getLogMessage(self,old_data=None,new_data=None, action=None):
		return getLogMessage(self,old_data,new_data, action)


	@classmethod
	def calculateFixedAssetTax(cls, date_from, date_to, residential=0, commercial=0, agricultural=0, land_use_type=None, *args, **kwargs):

		if type(date_from) is datetime:
			date_from = date_from.astimezone(timezone.get_default_timezone()).date()

		if type(date_to) is datetime:
			date_to = date_to.astimezone(timezone.get_default_timezone()).date()

		tax = Decimal(0)

		current_year = date_from.year
		total_days_in_period = Decimal((date(current_year, 12, 31) - date(current_year, 1, 1)).days + 1)
		periods = cls.getTaxPeriods('fixed_asset_tax', date_from, date_to, *args, **kwargs)
		if not periods:
			raise Exception("No tax settings found for %s, %s" % (date_from, date_to))
		due_month, due_day = periods[0][2]['due_date'].split('-')
		due_date = date(date_from.year, int(due_month), int(due_day))

		formula_data = {}

		for date_from, date_to, period_setting in periods:
			period = (date_from, date_to)
			formula_data[period] = {}
			days_in_period = Decimal((date_to - date_from).days + 1)


			residential = residential - period_setting['residential_deduction']
			if residential < 0:
				residential = 0
			taxable = residential + commercial + agricultural
			taxable = (Decimal(taxable) / 1000).quantize(Decimal(0)) * 1000

			if taxable > 0:
				amount = (days_in_period / total_days_in_period  * period_setting['tax_rate'] * taxable).quantize(Decimal('.01'))
				tax += amount
				formula_data[period]['amount'] = amount
			else:
				formula_data[period]['amount'] = 0
			formula_data[period]['tax_rate'] = period_setting['tax_rate']
			formula_data[period]['days'] = days_in_period
			formula_data[period]['taxable'] = taxable

		tax = Decimal(int(tax))
		return {'amount':tax, 'due':due_date, 'days':total_days_in_period, 'due_date':due_date, 'formula_data':formula_data, 'vat':True}


	@classmethod
	def calculateRentalIncome(cls, date_from, date_to, last_year_rental_income, last_year_bank_interest, sector=None, cell=None, village=None, *args, **kwargs):
		last_year_rental_income = Decimal(last_year_rental_income).quantize(Decimal('.01'))
		last_year_bank_interest = Decimal(last_year_bank_interest).quantize(Decimal('.01'))
		if type(date_from) is datetime:
			date_from = date_from.astimezone(timezone.get_default_timezone()).date()

		if type(date_to) is datetime:
			date_to = date_to.astimezone(timezone.get_default_timezone()).date()

		current_year = date_from.year
		total_days_in_period = Decimal((date(current_year, 12, 31) - date(current_year, 1, 1)).days + 1)
		periods = cls.getTaxPeriods('rental_income_tax', date_from, date_to, sector=sector, cell=cell, village=village, *args, **kwargs)
		if not periods:
			raise Exception("No tax settings found for %s, %s, %s, %s" % (date_from, date_to, sector, cell, village))
		due_month, due_day = periods[0][2]['due_date'].split('-')
		due_date = date(date_from.year, int(due_month), int(due_day))
		tax = Decimal(0)

		formula_data = {}
		for date_from, date_to, period_setting in periods:
			period_total = Decimal(0)
			period = (date_from, date_to)
			formula_data[period] = {}
			days_in_period = Decimal((date_to - date_from).days + 1)
			formula_data[period]['days'] = days_in_period

			if last_year_bank_interest > 0:
				taxable = last_year_rental_income - ( last_year_rental_income * period_setting['rate_with_bank_interest']) - last_year_bank_interest
				formula_data[period]['taxable_rate'] = period_setting['rate_with_bank_interest']
			else:
				taxable = last_year_rental_income - ( last_year_rental_income * period_setting['rate']) - last_year_bank_interest
				formula_data[period]['taxable_rate'] = period_setting['rate']

			formula_data[period]['taxable'] = taxable
			tax_ranges = period_setting['tax_ranges']
			amounts = []
			amount = Decimal(0)
			if taxable > 1000000:
				taxable = taxable - 1000000
				amount = taxable * tax_ranges['>1000000']
				amounts.append({'taxable':taxable, 'rate':tax_ranges['>1000000'], 'amount':amount})
				taxable = 1000000
				period_total += amount
			if taxable > 180000:
				taxable = taxable - 180000
				amount = taxable * tax_ranges['180000-1000000']
				amounts.append({'taxable':taxable, 'rate':tax_ranges['180000-1000000'], 'amount':amount})
				taxable = 180000
				period_total += amount

			amount = taxable * tax_ranges['0-180000']
			period_total += amount
			period_total = (days_in_period / total_days_in_period * period_total).quantize(Decimal('0.01'))
			tax += period_total
			amounts.append({'taxable':taxable, 'rate':tax_ranges['0-180000'], 'amount':amount})

			formula_data[period]['amount'] = period_total
			formula_data[period]['amounts'] = amounts

		tax = Decimal(int(tax))
		return {'amount':tax, 'due':due_date, 'days':total_days_in_period, 'due_date':due_date, 'rental_income':last_year_rental_income, 'interest_paid':last_year_bank_interest, 'formula_data':formula_data}


	@classmethod
	def calculateLandLeaseFee(cls, date_from, date_to, land_use_type, size, sector=None, cell=None, village=None, *args, **kwargs):
		if type(date_from) is datetime:
			date_from = date_from.astimezone(timezone.get_default_timezone()).date()

		if type(date_to) is datetime:
			date_to = date_to.astimezone(timezone.get_default_timezone()).date()

		size = Decimal(size).quantize(Decimal('.0001'))
		land_use_types = None
		if land_use_type == 'Agricultural':
			units = 'hectares'
			hectares = Decimal(size * 0.0001).quantize(Decimal('.0001'))
			if hectares > 35:
				land_use_types = 'Agricultural(>35 ha)'
			elif hectares >= 2 and hectares <= 35:
			   land_use_types = 'Agricultural(2-35 ha)'
			elif hectares > 2:
				land_use_types = 'Agricultural(>2 ha)'
		elif land_use_type == 'Residential':
			land_use_types = 'Residential'
		elif land_use_type == 'Commericial':
			land_use_types = 'Commercial'
		elif land_use_type == 'Industrial':
			land_use_types = 'Industries'
		elif land_use_type == 'Quarry Purpose':
			land_use_types = 'Quarries Exploitation'
		formula_data = {}
		tax = Decimal(0)
		current_year = date_from.year
		total_days_in_period = Decimal((date(current_year, 12, 31) - date(current_year, 1, 1)).days + 1)
		if land_use_types:
			tax_periods = cls.getTaxPeriods(['land_lease','land_lease_fee'], date_from, date_to, setting_name='area_and_fee_matches', sub_type=land_use_types, sector=sector, cell=cell, village=village, *args, **kwargs)
		else:
			tax_periods = [(date_from, date_to, { 'value':Decimal(0), 'region':'No Fee applicable' })]
		if not tax_periods:
			tax_periods = [(date_from, date_to, { 'value':Decimal(0), 'region':'No Fee Found' })]
		formula_data = {}
		for date_from, date_to, values in tax_periods:
			period = (date_from, date_to)
			rate = values['value']
			days_in_period = (date_to - date_from).days + 1
			amount = (Decimal(days_in_period) / Decimal(total_days_in_period)  * rate * size).quantize(Decimal('0.1'))
			formula_data[period] = { 'days':days_in_period, 'tax_rate':rate, 'amount':amount, 'size':size, 'region':values['region'] }
			tax += amount

		due_date = date_to
		tax = Decimal(int(tax))
		return {'amount':tax, 'due':due_date, 'due_date':due_date, 'days':total_days_in_period, 'formula_data':formula_data }


	@classmethod
	def calculateCleaningFee(cls, period_date, business_type, area_type, sector=None, cell=None, village=None):
		#calculate due date
		tax_periods = cls.getTaxPeriods('general_fee', period_date, period_date, sector=sector, cell=cell, village=village)
		if not tax_periods:
			raise Exception("No tax settings found for %s, %s, %s, %s" % (period_date, sector, cell, village))
		for date_from, date_to, period_setting in tax_periods:
			due_date_day = period_setting.get('monthly_due_date')
		due_date = period_date + relativedelta(months=1)
		due_date = date(due_date.year, due_date.month, due_date_day)

		#calculate amount
		sub_type = "%s-%s" % (area_type, business_type)
		tax_periods = cls.getTaxPeriods('cleaning_fee', period_date, period_date, sector=sector, cell=cell, village=village)
		if not tax_periods:
			raise Exception("No tax settings found for %s, %s, %s, %s" % (period_date, sector, cell, village))
		if not tax_periods:
			return None, None
		for date_from, date_to, period_setting in tax_periods:
			try:
				rate = period_setting['fee_matches'][sub_type]
			except KeyError:
				rate = None
		return rate, due_date

	@classmethod
	def calculateTradingLicenseTax(cls, date_from, date_to, turnover, sector=None, *args, **kwargs):
		if type(date_from) is datetime:
			date_from = date_from.astimezone(timezone.get_default_timezone()).date()

		if type(date_to) is datetime:
			date_to = date_to.astimezone(timezone.get_default_timezone()).date()

		turnover = Decimal(turnover).quantize(Decimal('0.01'))
		current_year = date_from.year
		total_days_in_period = Decimal((date(current_year, 12, 31) - date(current_year, 1, 1)).days + 1)
		tax = Decimal(0)
		tax_periods = Setting.getTaxPeriods('trading_license_tax', date_from, date_to, sector=sector, *args, **kwargs)

		if not tax_periods:
			raise Exception("No tax settings found for %s, %s, %s" % (date_from, date_to, sector))
		formula_data = {}
		for date_from, date_to, period_setting in tax_periods:
			days_in_period = Decimal((date_to - date_from).days + 1)
			period = (date_from, date_to)
			formula_data[period] = { 'days':days_in_period }
			settings = period_setting['business_yearly_turnover_and_tax_matches']
			if turnover <= 40000000:
				rate = Decimal(settings.get('Up to 40,000000 Rwf'))
			elif turnover > 40000000 and turnover <= 60000000:
				rate = Decimal(settings.get('From 40,000,001 to 60,000,000'))
			elif turnover > 60000000 and turnover <= 150000000:
				rate = Decimal(settings.get('From 60,000,001 to 150,000,000'))
			else:
				rate = Decimal(settings.get('Above 150 Million Rwf'))
			formula_data[period]['rate'] = rate
			amount = (days_in_period / total_days_in_period  * rate).quantize(Decimal('0.01'))
			formula_data[period]['amount'] = amount
			tax += amount
		tax = Decimal(int(tax))
		return {'amount':tax, 'due':date_to, 'due_date':date_to, 'days':total_days_in_period, 'turnover':turnover, 'formula_data':formula_data, 'vat':True}

	@classmethod
	def get_due_date(cls, tax_fee_name, period_date, sector=None, district=None, *args, **kwargs):
		current_date = date.today()
		if tax_fee_name in ('trading_license_tax', 'land_lease_fee'):
			return date(period_date.year, 12, 31)
		due_date = cls.getTaxSetting(tax_fee_name, 'due_date', current_date, current_date, sector, district, *args, **kwargs)
		due_month, due_day = due_date.split('-')
		return date(period_date.year, int(due_month), int(due_day))


	@classmethod
	def getTaxSetting(cls, tax_fee_name, setting_name, date_from, date_to, sector=None, district=None, *args, **kwargs):
		"""gets the latest setting for a tax"""
		periods = cls.getTaxPeriods(tax_fee_name, date_from, date_to, sector, district, *args, **kwargs)
		if not periods:
			raise Exception("Could not find setting - %s from %s to %s" % (tax_fee_name, date_from, date_to))
		return periods[0][2][setting_name]


	@classmethod
	def getFees(cls, district=None, sector=None, cell=None, village=None, *args, **kwargs):
		"""
		returns the relevant tax period info as a dictionary
		in the format: {(date_from, date_to), { setting_name1: value, setting_name2: value2 }, ...}
		eg. {((2013,01,01), (2013,04,31)):{ 'tax_rate': 0.1, 'due_date': (2013,05,31), ...}, ... }
		( (date_from, date_to, {values}), (date_from, date_to, {values}) )
		The order of precedence s Sector tax values, District tax values then
		tax values with no associated Sector or District
		"""

		if district and type(district) is int:
			district = District.objectsIgnorePermission.get(pk=district)

		if sector and type(sector) is int:
			sector = Sector.objectsIgnorePermission.get(pk=sector)

		if cell and type(cell) is int:
			cell = Cell.objects.get(pk=cell)

		if village and type(village) is int:
			village = Village.objects.get(pk=village)

		settings = cls.objects.filter(tax_fee_name='misc_fee', i_status='active')

		if village:
			settings = settings.filter(Q(village__isnull=True) | Q(village=village))
			cell = village.cell
		else:
			settings = settings.filter(village__isnull=True)

		if cell:
			settings = settings.filter(Q(cell__isnull=True) | Q(cell=cell))
			sector = cell.sector
		else:
			settings = settings.filter(cell__isnull=True)

		if sector:
			settings = settings.filter(Q(sector__isnull=True) | Q(sector=sector))
			district = sector.district
		else:
			settings = settings.filter(sector__isnull=True)

		if district:
			settings = settings.filter(Q(district__isnull=True) | Q(district=district))
		else:
			settings = settings.filter(district__isnull=True)

		settings = settings.select_related('district','sector', 'cell', 'village').order_by('-valid_from', '-village', '-cell', '-sector', '-district', 'sub_type')

		fees = {}
		for setting in settings:
			setting_region = setting.village or setting.cell or setting.sector or setting.district
			category = fees.setdefault(setting.setting_name, {})
			sub_type = category.setdefault(setting.sub_type, { 'value': setting.value, 'description':setting.description, 'valid_from':setting.valid_from, 'region': setting_region })
			if setting_region == sub_type['region'] and setting.valid_from >= sub_type['valid_from'] and date.today() >= setting.valid_from or setting_region != sub_type['region']:
				sub_type['value'] = Decimal(setting.value)
				sub_type['description'] = setting.description
				sub_type['region'] = setting_region
				sub_type['pk'] = setting.pk

		return fees


	@classmethod
	def getTaxPeriods(cls, tax_fee_name, date_from, date_to, setting_name=None, sub_type=None, district=None, sector=None, cell=None, village=None, *args, **kwargs):
		"""
		returns the relevant tax period info as a dictionary
		in the format: {(date_from, date_to), { setting_name1: value, setting_name2: value2 }, ...}
		eg. {((2013,01,01), (2013,04,31)):{ 'tax_rate': 0.1, 'due_date': (2013,05,31), ...}, ... }
		( (date_from, date_to, {values}), (date_from, date_to, {values}) )
		The order of precedence s Sector tax values, District tax values then
		tax values with no associated Sector or District
		"""

		if district and type(district) is int:
			district = District.objectsIgnorePermission.get(pk=district)

		if sector and type(sector) is int:
			sector = Sector.objectsIgnorePermission.get(pk=sector)

		if cell and type(cell) is int:
			cell = Cell.objects.get(pk=cell)

		if village and type(village) is int:
			village = Village.objects.get(pk=village)

		if type(date_from) is datetime:
			date_from = date_from.astimezone(timezone.get_default_timezone()).date()

		if type(date_to) is datetime:
			date_to = date_to.astimezone(timezone.get_default_timezone()).date()

		if type(tax_fee_name) is not list:
			tax_fee_name = [tax_fee_name]

		settings = cls.objects.filter(tax_fee_name__in=tax_fee_name, valid_from__lte=date_to, i_status='active')

		if setting_name:
			settings = settings.filter(setting_name=setting_name)

		if sub_type:
			if not setting_name:
				raise Exception("You must specify a setting name")
			if hasattr(sub_type, "__iter__"):
				settings = settings.filter(sub_type__in=sub_type)
			else:
				settings = settings.filter(sub_type=sub_type)

		if village:
			settings = settings.filter(Q(village__isnull=True) | Q(village=village))
			cell = village.cell
		else:
			settings = settings.filter(village__isnull=True)

		if cell:
			settings = settings.filter(Q(cell__isnull=True) | Q(cell=cell))
			sector = cell.sector
		else:
			settings = settings.filter(cell__isnull=True)

		if sector:
			settings = settings.filter(Q(sector__isnull=True) | Q(sector=sector))
			district = sector.district
		else:
			settings = settings.filter(sector__isnull=True)

		if district:
			settings = settings.filter(Q(district__isnull=True) | Q(district=district))
		else:
			settings = settings.filter(district__isnull=True)

		settings = settings.order_by('-valid_from', '-village', '-cell', '-sector', '-district')

		settings = [setting for setting in settings]

		if not settings:
			return None
			# raise Exception("No Settings found for tax fee: %s, from %s to %s, setting name:%s, sub type: %s, district: %s, sector: %s, cell: %s, village: %s"  % (tax_fee_name, date_from, date_to, setting_name, sub_type, district, sector, cell, village))

		# set the most recent period
		#import pdb
		#pdb.set_trace()
		valid_from = settings[0].valid_from
		valid_to = date_to

		periods = {}
		for setting in settings:
			region = setting.village or setting.cell or setting.sector or setting.district or None
			if region:
				region_name = region.name
			else:
				region_name = None
			# get the next period setting
			if setting.valid_from < valid_from:
				valid_to = valid_from - timedelta(days=1)
				#stop if period is out of range
				if valid_to < date_from:
					break;

			# set the setting start range if less than date_from
			valid_from = setting.valid_from
			if valid_from < date_from:
				start_from = date_from
			else:
				start_from = valid_from

			period = periods.setdefault((start_from, valid_to), {})
			try:
				value = Decimal(setting.value)
			except:
				value = setting.value

			period['region'] = region_name
			if sub_type:
				if hasattr(sub_type,'__iter__'):
					period[setting.sub_type] = value
				else:
					period['value'] = value
			elif setting_name:
				if setting.sub_type:
					period[setting.sub_type] = value
				else: #setting_name provided,  no setting.sub_type
					period['value'] = value
			else: # no setting name
				if setting.sub_type:
					st = period.setdefault(setting.setting_name, {})
					st[setting.sub_type] = value
				else:
					period[setting.setting_name] = value

		periods = [ (dates[0], dates[1], values) for dates, values in periods.iteritems() ]
		periods.sort(key=lambda x:x[0], reverse=True)
		return periods


# Model for Receipt of Multiple Tax/Fee payment
class MultipayReceipt(models.Model):
	amount = models.DecimalField(max_digits = 20, decimal_places = 2)
	user = models.ForeignKey(PMUser, null=True, blank = True)
	date_time = models.DateTimeField(help_text='This is the Date and Time the Entry has been entered into the database.',auto_now_add=True,auto_now=True)
	i_status = models.CharField(max_length = 10, choices = variables.status_choices, default='active', blank = True)


# Model for Receipt of Multiple Tax/Fee payment
class MultipayReceiptPaymentRelation(models.Model):
	payfee = models.ForeignKey(PayFee, related_name="receipt_relations")
	receipt = models.ForeignKey(MultipayReceipt, related_name="payment_relations")
	i_status = models.CharField(max_length = 10, choices = variables.status_choices, default='active', blank = True)



#General functions used in many models
def getLogMessage(self,old_data=None,new_data=None, action=None):
	"""
	return tailored log message for different actions taken on this citizen
	"""
	if action == "view":
		return "view " + self.__class__.__name__ + " [" + self.__unicode__() + "]"
	if action == "delete":
		return "delete " + self.__class__.__name__ + " [" + self.__unicode__() + "]"
	if action == "add":
		return "add " + self.__class__.__name__ + " [" + self.__unicode__() + "]"
	if action == "change":
		message=""
		count = 0
		if old_data != None:
			for key, value in old_data.iteritems():
				if old_data[key] != new_data[key]:
					if count != 0:
						message = message + ","
					count = count + 1
					if type(value) is not list:
						message = message + " change "+key + " from '"+ str(value) + "' to '"+str(new_data[key])+"'"
		if message == "":
			message = "No change made"
		message = message + " on " + self.__class__.__name__ + " [" + self.__unicode__() + "]"
		return message



class Installment(models.Model):
	amount = models.DecimalField(max_digits=20, decimal_places=2)
	due = models.DateField()
	propertyTaxItem = models.ForeignKey(PropertyTaxItem, null=True, blank=True, related_name="installments")
	rentalIncomeTax = models.ForeignKey(RentalIncomeTax, null=True, blank=True, related_name="installments")
	tradingLicenseTax = models.ForeignKey(TradingLicenseTax, null=True, blank=True, related_name="installments")
	fee = models.ForeignKey(Fee, null=True, help_text="", related_name="installments")
	# tax = models.ForeignKey(Tax, null=True, help_text="", related_name="installments")

	def __unicode__(self):
		if hasattr(self, 'paid'):
			return "%s due on %s: %s paid" % (self.amount, self.due, self.paid)
		else:
			return "%s due on %s" % (self.amount, self.due)

	@staticmethod
	def previewInstallments(amount, date_from):
		months = 3
		no_installments = 4
		installments = {}
		due_date = date_from

		amount = (amount / no_installments).quantize(Decimal('.01'))
		for i in range(no_installments):
			due_date = due_date + relativedelta(months=months-1) + relativedelta(day=31)
			installments[due_date] = amount
		return installments

