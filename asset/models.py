from django.db import models
from django.contrib.gis.db import models
from datetime import datetime, timedelta
from dev1 import variables
from property.models import *
from dateutil.relativedelta import relativedelta
from django.db.models.signals import post_save
from django.dispatch import receiver


class Business(models.Model):
	pm_tin = models.CharField(max_length=50,help_text='Propertymode TIN', blank = True)
	name = models.CharField(max_length=100,help_text='Business Name')
	tin = models.CharField(max_length=50, help_text='TIN RRA',null=True,  blank = True)
	date_started = models.DateField(blank = True, null=True, help_text='Date Business Started')
	foreign_record_id = models.IntegerField(blank = True, null = True, help_text="Record ID from remote source database")
	address = models.CharField(max_length = 255, null = True, blank = True, help_text="Contact address")
	phone1 = models.CharField(max_length=50,help_text='')
	phone2 = models.CharField(max_length=50, blank = True,help_text='')
	email = models.CharField(max_length=50,help_text='', blank = True)
	po_box = models.TextField(help_text='Business PO Box', blank = True)
	vat_register = models.BooleanField(help_text="Whether business is VAT registered.")
	area_type = models.CharField(max_length = 50, choices = variables.area_types, blank = True, null = True)
	business_type = models.CharField(max_length = 50, choices = variables.business_types, blank = True, null = True)
	sector = models.ForeignKey(Sector, null=True, blank=True)
	cell = models.ForeignKey(Cell, null=True, blank=True,help_text="<b>Sector, Area Type and Business Type will determine the Cleaning fee.</b><hr/>")
	credit = models.FloatField(default = 0, help_text = 'Credit accumulated for this business.')
	accountant_name = models.CharField(max_length = 150, blank = True, null = True)
	accountant_phone = models.CharField(max_length = 50, blank = True, null = True)
	accountant_email = models.CharField(max_length = 50, blank = True, null = True)
	cp_password = models.CharField(max_length=128, help_text='Enter password.', blank = True, null = True)
	market_fee_applicable = models.BooleanField(help_text="Whether business is VAT registered.")
	i_status = models.CharField(max_length = 10, choices = variables.status_choices, default='active', blank = True, verbose_name='Status')
	date_created = models.DateTimeField(help_text='Date this record is saved',auto_now_add=True)
	closed_date = models.DateField(blank=True, null=True)

	def close(self, close_date):
		from jtax.models import TradingLicenseTax, Fee
		self.closed_date = close_date
		self.status = 'inactive'
		self.save()
		trading_license_taxes = TradingLicenseTax.objects.filter(business=self, date_to__gt=close_date, i_status='active', is_paid=False)
		for trading_license_tax in trading_license_taxes:
			trading_license_tax.date_to = close_date
			trading_license_tax.period_to = datetime(*close_date.timetuple()[:6])
			trading_license_tax.calc_tax()
			if trading_license_tax.amount <= 0 or not trading_license_tax.amount:
				trading_license_tax.i_status = 'inactive'
				trading_license_tax.is_paid = True
				trading_license_tax.amount = 0
				trading_license_tax.remaining_amount = 0
				trading_license_tax.save()

		cleaning_fees = Fee.objects.filter(business=self, date_from__gte=close_date, fee_type__in=('cleaning','cleaning_fee'), is_paid=False)
		cleaning_fees.update(i_status='inactive', amount=0, remaining_amount=0, is_paid=True)

		fees = Fee.objects.filter(business=self, date_to__gt=close_date, i_status='active', is_paid=False)
		for fee in fees:
			fee.date_to = close_date
			fee.period_to = datetime(*close_date.timetuple()[:6])
			fee.calc_tax()
			if fee.amount <= 0 or not fee.amount:
				fee.i_status = 'inactive'
				fee.remaining_amount = 0
				fee.amount = 0
				fee.is_paid = True
				fee.save()


	def __unicode__(self):
		return self.name

	def getDisplayName(self):
		if self.tin:
			return self.name + ' (' + self.name + ')'
		else:
			return self.name

	def getLogMessage(self,old_data=None,new_data=None, action=None):
		return getLogMessage(self,old_data,new_data, action)

	##### get a new PM tin 
	##### TIN + 10 digit 
	def getNewPMTIN(self):
		business = Business.objects.filter(tin__isnull = False).order_by('-pm_tin')
		if len(business) == 0:
			return 'TIN0000000001'
		else:
			tin_number = business[0].pm_tin
			if not tin_number:
				return 'TIN0000000001'
			tin_digit_part = int(tin_number[3:]) + 1
			tin_digit_part = str(tin_digit_part)
			zeros = ''
			for i in range(10-len(tin_digit_part)):
				zeros = zeros + '0'
			return 'TIN' + zeros + tin_digit_part

	def save(self, *args, **kwargs):
		"""
		Generate a local TIN number
		"""
		if not self.pm_tin:
			self.pm_tin = self.getNewPMTIN()

		#strip any white space out of name
		self.name = self.name.strip()
		if self.tin:
			self.tin = self.tin.strip()
		models.Model.save(self)


	def calc_taxes(self, now=None, include_only=False):
		from jtax.models import TradingLicenseTax, Fee
		"""
		generate business taxes & fees(Trading Licence, Cleaning Fee)
		"""
		if self.i_status != 'active':
			return None
		
		if not now:
			now = timezone.make_aware(datetime.now(), timezone.get_default_timezone())
		else:
			if type(now) is datetime and not now.tzinfo:
				now = timezone.make_aware(now, timezone.get_default_timezone())
			elif type(now) is date:
				now = timezone.make_aware(datetime.combine(now, datetime.min.time()), timezone.get_default_timezone())
		current_year = str(now.year)
		year_start = period_from = timezone.make_aware(parser.parse("%s-01-01 00:00:00" % current_year), timezone.get_default_timezone())
		year_end = timezone.make_aware(parser.parse("%s-12-31 23:59:59" % current_year), timezone.get_default_timezone())
		year_start_date = date_from = date(now.year, 1,1)
		year_end_date = date(now.year, 12, 31)

		subbusinesses = SubBusiness.objects.filter(business = self, i_status='active')

		if not include_only or 'trading_license' in include_only:
			#no trading license tax, create one
			try:
				trading_license_tax, created = TradingLicenseTax.objects.get_or_create(business=self, date_to = year_end_date, i_status='active', defaults=dict(date_from=date_from, period_from=year_start, period_to=year_end, is_paid=False, currency='RWF', date_time=now))
				if not trading_license_tax.is_paid:
					trading_license_tax.calc_tax()
			except:
				pass
			
			for subbusiness in subbusinesses:
				try:
					trading_license_tax, created = TradingLicenseTax.objects.get_or_create(subbusiness=subbusiness, date_to = year_end_date, i_status='active', defaults=dict(date_from=date_from, period_from=period_from, period_to=year_end, is_paid=False, currency='RWF', date_time=now))
					if not trading_license_tax.is_paid:
						trading_license_tax.calc_tax()
				except:
					pass

		if not include_only or 'cleaning' in include_only:
			#if there is no Cleaning fee for this business in the current year, add monthly Cleaning fee, also exclude the business with no cleaning_fee_amount (No premise)
			if not self.business_type or 'No premises' not in self.business_type:
				if self.date_started and self.date_started > year_start_date:
					cleaning_month = date(self.date_started.year, self.date_started.month, 1)
				else:
					cleaning_month = year_start_date
				
				while cleaning_month <= year_end_date:
					next_month = cleaning_month + relativedelta(months=1)
					end_month = next_month - timedelta(days=1)
					month_from = timezone.make_aware(datetime.combine(cleaning_month, datetime.min.time()), timezone.get_default_timezone())
					month_to = timezone.make_aware(datetime.combine(end_month, datetime.min.time()), timezone.get_default_timezone())
					try:
						fee, created = Fee.objects.get_or_create(fee_type='cleaning', business=self, date_from=cleaning_month, i_status='active', defaults=dict(is_paid=False, date_time=now, currency='RWF', date_to=end_month, period_from=month_from, period_to=month_to))
						if not fee.is_paid:
							fee.calc_cleaningFee()
					except:
						pass
					for subbusiness in subbusinesses:
						try:
							fee, created = Fee.objects.get_or_create(fee_type='cleaning', subbusiness=subbusiness, date_from=cleaning_month, i_status='active', defaults=dict(is_paid=False, date_time=now, currency='RWF', date_to=end_month, period_from=month_from, period_to=month_to))
							if not fee.is_paid:
								fee.calc_cleaningFee()
						except:
							pass
					cleaning_month = next_month

	def get_properties(self):
		return Property.objectsIgnorePermission.filter(owners__owner_business=self)

@receiver(post_save, sender=Business)
def after_business_save(sender, instance, created, **kwargs):
	if created:
		instance.calc_taxes()


class SubBusiness(models.Model):
	branch = models.CharField(max_length=100,help_text='Branch Name')
	sector = models.ForeignKey(Sector, null=True, blank=True, help_text="The sector where this branch is located.")
	cell = models.ForeignKey(Cell, null=True, blank=True, help_text="The cell where this branch is located.")
	village = models.ForeignKey(Village, null=True, blank=True, help_text="The village where this branch is located.")
	parcel_id = models.IntegerField(null=True, blank = True, help_text="The parcl ID of branch location.")
	date_created = models.DateTimeField(help_text='Date this branch is created in our system.',auto_now_add=True)
	credit = models.FloatField(default = 0, help_text = 'Credit accumulated for this business.')
	i_status = models.CharField(max_length = 10, choices = variables.status_choices, default='active', blank = True)
	business = models.ForeignKey(Business)

	def getDisplayName(self):
		return self.business.getDisplayName() + ', branch: '+ self.branch

	def get_properties(self):
		return Property.objectsIgnorePermission.filter(owners__owner_subbusiness=self)

@receiver(post_save, sender=SubBusiness)
def after_sub_business_save(sender, instance, **kwargs):
	instance.business.calc_taxes()


class Billboard(models.Model):
	name = models.CharField(max_length=100,help_text='Billboard Name')
	property = models.ForeignKey(Property, null=True, blank = True, help_text="The property that this hold this billboard.")
	description = models.TextField(help_text='Billboard Description', blank = True)
	longitude = models.CharField(max_length=50,help_text='Billboard geo-location longitude', blank = True)
	latitude = models.CharField(max_length=50,help_text='Billboard geo-location latitude', blank = True)
	i_status = models.CharField(max_length = 10, choices = variables.status_choices, default='active', blank = True)
	date_created = models.DateTimeField(help_text='Date this record is saved',auto_now_add=True)
	def __unicode__(self):
		return self.name + " (UPI: " + str(self.property.getUPI()) + ")"
	def getLogMessage(self,old_data=None,new_data=None, action=None):
		return getLogMessage(self,old_data,new_data, action)


class Vehicle(models.Model):
	vehicle_type = models.CharField(max_length=25,choices=variables.vehicle_types,help_text='Types of vehicles.')
	plate_number = models.CharField(max_length=50,help_text='Vehicle Plate Number', unique=True)
	use_since = models.DateTimeField(help_text="Date the vehicle started to be used.")
	brand = models.CharField(max_length=50,help_text='Vehicle Brand')
	model = models.CharField(max_length=50,help_text='Vehicle Model')
	description = models.TextField(help_text='Detail description of the vehicle', blank = True)
	i_status = models.CharField(max_length = 10, choices = variables.status_choices, default='active', blank = True)
	date_created = models.DateTimeField(help_text='Date this record is saved',auto_now_add=True)
	def __unicode__(self):
		return self.brand + ' ' + self.model + ' ' + self.vehicle_type
	def getLogMessage(self,old_data=None,new_data=None, action=None):
		return getLogMessage(self,old_data,new_data, action)


class Shop(models.Model):
	name = models.CharField(max_length=100,help_text='Shop Name')
	phone1 = models.CharField(max_length=50,help_text='Phone')
	phone2 = models.CharField(max_length=50,help_text='Alternative Phone', blank = True)
	email = models.CharField(max_length=50,help_text='Email', blank = True)
	i_status = models.CharField(max_length = 10, choices = variables.status_choices, default='active', blank = True)
	date_created = models.DateTimeField(help_text='Date this record is saved',auto_now_add=True)
	def __unicode__(self):
		return self.name
	def getLogMessage(self,old_data=None,new_data=None, action=None):
		return getLogMessage(self,old_data,new_data, action)


class Stall(models.Model):
	name = models.CharField(max_length=100,help_text='Stall Name')
	phone1 = models.CharField(max_length=50,help_text='Phone')
	phone2 = models.CharField(max_length=50,help_text='Alternative Phone', blank = True)
	email = models.CharField(max_length=50,help_text='Email', blank = True)
	i_status = models.CharField(max_length = 10, choices = variables.status_choices, default='active', blank = True)
	date_created = models.DateTimeField(help_text='Date this record is saved',auto_now_add=True)
	def __unicode__(self):
		return self.name
	def getLogMessage(self,old_data=None,new_data=None, action=None):
		return getLogMessage(self,old_data,new_data, action)


class Office(models.Model):
	name = models.CharField(max_length=100,help_text='Office Name')
	phone1 = models.CharField(max_length=50,help_text='Phone')
	phone2 = models.CharField(max_length=50,help_text='Alternative Phone', blank = True)
	email = models.CharField(max_length=50,help_text='Email', blank = True)
	i_status = models.CharField(max_length = 10, choices = variables.status_choices, default='active', blank = True)
	date_created = models.DateTimeField(help_text='Date this record is saved',auto_now_add=True)
	def __unicode__(self):
		return self.name
	def getLogMessage(self,old_data=None,new_data=None, action=None):
		return getLogMessage(self,old_data,new_data, action)


class Ownership(models.Model):
	#owner_type = models.CharField(max_length=20,choices = variables.owner_types, help_text='Owner Types')
	#owner_id = models.IntegerField(help_text='Owner ID')
	#asset_type = models.CharField(max_length=20,choices = variables.asset_types, help_text='Asset Types') 
	#asset_id =  models.IntegerField(help_text='Asset ID')
	
	owner_citizen = models.ForeignKey(Citizen,null=True,blank=True, related_name="assets")
	owner_business = models.ForeignKey(Business,null=True,blank=True, related_name="assets")
	owner_subbusiness = models.ForeignKey(SubBusiness,null=True,blank=True, related_name="assets")
	
	asset_business = models.ForeignKey(Business,null=True,blank=True, related_name="owners")
	asset_subbusiness = models.ForeignKey(SubBusiness,null=True,blank=True, related_name="owners")
	asset_property = models.ForeignKey(Property,null=True,blank=True, related_name="owners")
	asset_billboard = models.ForeignKey(Billboard,null=True,blank=True, related_name="owners")
	asset_vehicle = models.ForeignKey(Vehicle,null=True,blank=True, related_name="owners")

	share = models.FloatField(help_text="Owner's share of the asset")

	date_started = models.DateField(help_text='Date this ownership started')
	date_ended = models.DateField(help_text='Date this ownership ended', null=True, blank = True)
	
	i_status = models.CharField(max_length = 10, choices = variables.status_choices, default='active', blank = True)
	date_created = models.DateTimeField(help_text='Date this record is saved',auto_now_add=True)
	
	def getLogMessage(self,old_data=None,new_data=None, action=None):
		return getLogMessage(self,old_data,new_data, action)


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