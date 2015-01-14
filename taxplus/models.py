from django.db import models
from django.contrib.gis.db import models as gis_models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date, datetime, timedelta
from decimal import Decimal
from django.db.models import Sum
from django.utils import timezone
import binascii
from dateutil import parser
import os
from dateutil.relativedelta import relativedelta
from taxplus.functions import adjust_payments as adjustpayments


class PMUser(models.Model):
	username = models.CharField(max_length=30, help_text='Required. Maximum 30 characters.')
	firstname = models.CharField(max_length=30, help_text='Enter first name.')
	lastname = models.CharField(max_length=30, help_text='Enter last name.')
	contactnumber = models.CharField(max_length=30, blank=True, help_text='Telephone number or mobile number.')
	email = models.EmailField(unique=True,help_text='Enter email address.')
	superuser = models.BooleanField(default=False,help_text='Designates that this user has all permissions without explicitly assigning them.')
	lastlogin = models.DateTimeField(help_text='last login')
	datejoined = models.DateTimeField(help_text='date joined')
	active = models.BooleanField(default="active", blank = True)
	i_status = models.CharField(max_length= 10, default="active", blank = True, help_text='Designates whether this user should be treated as active.')

	class Meta:
		db_table = 'auth_pmuser'

	def __unicode__(self):
		if self.lastname and self.firstname:
			return '%s %s' % (self.firstname, self.lastname)
		else:
			return self.username


class Boundary(models.Model):
	shape_area = models.FloatField(blank=True, null=True)
	polygon_imported = gis_models.PolygonField(srid=3857, blank=True, null= True)
	polygon= gis_models.PolygonField(srid=4326, blank=True, null= True)
	central_point = gis_models.PointField(blank =True, null=True)
	#source = models.CharField(max_length=1, null=True)
	objects = gis_models.GeoManager()

	class Meta:
		db_table = 'property_boundary'

class Category(models.Model):
	code = models.CharField(max_length=50, primary_key=True)
	name = models.CharField(max_length=50)

	def __unicode__(self):
		return self.name;


class CategoryChoice(models.Model):
	code = models.CharField(max_length=50)
	name = models.CharField(max_length=55)
	category = models.ForeignKey(Category)

	def __unicode__(self):
		return self.name;


class Master(models.Model):
	class Meta:
		abstract = True

	created = models.DateTimeField(auto_now_add=True, blank=True)
	modified = models.DateTimeField(auto_now_add=True, auto_now=True, blank=True)
	status = models.ForeignKey(CategoryChoice, null=True, limit_choices_to={'category__code':'status'})


class Province(models.Model):
	name = models.CharField(max_length=100, help_text="Province name.")
	code = models.CharField(max_length=2, null=True, blank=True, help_text="Province code.")
	boundary = models.OneToOneField(Boundary, related_name='province_boundary', null=True, blank=True, help_text="The boundary of province.")

	class Meta:
		db_table = 'property_province'

	def __unicode__(self):
		return self.name;


class District(models.Model):
	name = models.CharField(max_length=100, help_text="District name.")
	code = models.CharField(max_length=4, null=True, blank=True, help_text="District code.")
	boundary = models.OneToOneField(Boundary, related_name='district_boundary', null=True, blank=True, help_text="The boundary of district.")
	province = models.ForeignKey(Province, null=True, blank=True, help_text="The province this district belongs to.")
	alias = models.TextField(null=True)

	class Meta:
		db_table = 'property_district'

	def __unicode__(self):
		return self.name


class Council(models.Model):
	name = models.CharField(max_length=100, help_text="Council name.")
	address = models.CharField(max_length = 200, help_text="Address of council.")
	boundary = models.OneToOneField(Boundary, null=True, blank=True, help_text="The boundary of council.")

	class Meta:
		db_table = 'property_council'

	def __unicode__(self):
		return self.name


class Sector(models.Model):
	name = models.CharField(max_length=100, help_text="Sector name.")
	code = models.CharField(max_length=6,help_text="sector code.", null=True, blank=True)
	district = models.ForeignKey(District, help_text="District the sector belongs to.")
	council = models.ForeignKey(Council, null=True, blank=True, help_text="Council the sector belongs to.")
	boundary = models.OneToOneField(Boundary, related_name='sector_boundary', null=True, blank=True, help_text="The boundary of sector.")
	alias = models.TextField(null=True)


	class Meta:
		ordering = ['name', 'district__name']
		db_table = 'property_sector'

	def __unicode__(self):
		return self.name


class SectorStats(Master):
	sector = models.ForeignKey(Sector)
	period_start = models.DateField()
	period_type = models.IntegerField() # 12 = monthly, 4 quarterly, 1 yearly
	market_change = models.FloatField() # percentage
	median_market_to_sold_days = models.FloatField()
	median_value = models.FloatField()
	no_sold = models.IntegerField()
	no_leased = models.IntegerField()
	no_liquidated = models.IntegerField()


class DistrictStats(Master):
	district = models.ForeignKey(District)
	period_start = models.DateField()
	period_type = models.IntegerField() # 12 = monthly, 4 quarterly, 1 yearly
	market_change = models.FloatField() # percentage
	median_market_to_sold_days = models.FloatField()
	median_value = models.FloatField()
	no_sold = models.IntegerField()
	no_leased = models.IntegerField()
	no_liquidated = models.IntegerField()



class Zone(Master):
	code = models.CharField(max_length=5)
	name = models.CharField(max_length=50, help_text="Zone name")


class Cell(models.Model):
	name = models.CharField(max_length=100, help_text="Cell name.")
	code = models.CharField(max_length=8,help_text="Cell code.", null=True)
	sector = models.ForeignKey(Sector, null=True, blank=True, help_text="Sector the cell belongs to.")
	boundary = models.OneToOneField(Boundary, null=True, blank=True, help_text="The boundary of Cell.", related_name='+')
	alias = models.TextField(null=True)
	#zone = models.ForeignKey(Zone, null=True, blank=True)

	class Meta:
		ordering = ['name']
		db_table = 'property_cell'

	def __unicode__(self):
		return self.name


class Village(models.Model):
	name = models.CharField(max_length=100, help_text="Village name.")
	code = models.CharField(max_length=10,help_text="Village code.", null=True)
	cell = models.ForeignKey(Cell, null=True, blank=True,help_text="Cell the village belongs to.")
	boundary = models.OneToOneField(Boundary, null=True, blank=True, help_text="The boundary of Village.", related_name='+')
	alias = models.TextField(null=True)

	class Meta:
		ordering = ['name']
		db_table = 'property_village'

	def __unicode__(self):
		return self.name


class CleaningCategory(models.Model):
	name = models.CharField(max_length=50)
	#amount = models.DecimalField(max_digits=8, decimal_places=0)

	class Meta:
		db_table = 'asset_businesscategory'

	def __unicode__(self):
		return self.name


class BusinessCategory(models.Model):
	name = models.CharField(max_length=100)
	cleaning_category = models.ForeignKey(CleaningCategory, db_column='business_category_id')

	class Meta:
		db_table = 'asset_businesssubcategory'

	def __unicode__(self):
		return self.name




class Citizen(models.Model):
	first_name = models.CharField(max_length = 50, help_text = 'First name')
	last_name = models.CharField(max_length = 50, help_text = 'Last name')
	middle_name = models.CharField(max_length = 50, blank = True, null = True, help_text = 'Middle name')
	date_of_birth = models.DateField(blank = True, null = True, help_text="Date of birth")
	year_of_birth = models.CharField(max_length = 4,blank = True, null = True, help_text="Year of birth")
	citizen_id = models.CharField(max_length=50, blank=False,  unique=True, help_text = 'unique ID for citizen')
	phone_1 = models.CharField(max_length = 30, blank = True, null = True, help_text = 'Primary Phone Number')
	phone_2 = models.CharField(max_length = 50, blank = True, null = True, help_text = 'Secondary Phone Number')
	email = models.EmailField(max_length = 50, blank = True, null = True, help_text = 'Email')
	address = models.CharField(max_length = 255, null = True, blank = True, help_text ='Address')
	po_box = models.CharField(max_length = 50, blank = True, null = True, help_text = 'PO Box')
	gender = models.CharField(max_length = 50, help_text = 'Gender')
	foreign_identity_type = models.CharField(max_length = 50, blank = True, null = True, help_text = 'Foreign identity type. For example: passport.')
	foreign_identity_number = models.CharField(max_length = 50, blank = True, null = True, help_text = 'Foreign identity ID.')
	status_id = models.IntegerField(null=True)
	deactivate_reason = models.CharField(max_length = 50, blank=False, default=1, null = True)
	note = models.TextField(null=True, blank=True)
	photo = models.ImageField(upload_to='citizenphotos', blank = True, null = True, help_text='Photo of The Citizen')
	foreign_record_id = models.CharField(max_length = 50, blank = True, null = True, help_text = 'Foreign id from the old DB.')
	cp_password = models.CharField(max_length=128, help_text='Enter password.', blank = True, null = True)
	contact_details_confirmed = models.DateField(null=True, blank=True, help_text="dd/mm/yyyy")
	created = models.DateTimeField(auto_now_add=True, null=True)
	status_new = models.ForeignKey(CategoryChoice, null=True)
	entity_id = models.IntegerField(null=True)


	class Meta:
		db_table = 'citizen_citizen'

	@property
	def name(self):
		if self.middle_name and self.middle_name!='' and self.middle_name !='null':
			return self.first_name +' '+ self.middle_name +' '+ self.last_name
		else:
			return self.first_name + ' ' + self.last_name

	def __unicode__(self):
		return self.name



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
	area_type = models.CharField(max_length = 50, blank = True, null = True)
	business_type = models.CharField(max_length = 50, blank = True, null = True)
	sector = models.ForeignKey(Sector, null=True, blank=True)
	cell = models.ForeignKey(Cell, null=True, blank=True,help_text="")
	village = models.ForeignKey(Village, null=True, blank=True)
	credit = models.IntegerField(default = 0, help_text = 'Credit accumulated for this business.')
	accountant_name = models.CharField(max_length = 150, blank = True, null = True)
	accountant_phone = models.CharField(max_length = 50, blank = True, null = True)
	accountant_email = models.CharField(max_length = 50, blank = True, null = True)
	cp_password = models.CharField(max_length=128, help_text='Enter password.', blank = True, null = True)
	market_fee_applicable = models.BooleanField(help_text="Whether business is VAT registered.")
	i_status = models.CharField(max_length = 10, default='active', blank = True, verbose_name='Status')
	date_created = models.DateTimeField(help_text='Date this record is saved',auto_now_add=True)
	closed_date = models.DateField(blank=True, null=True)
	business_category = models.ForeignKey(BusinessCategory, null=True, blank=True, db_column='business_subcategory_id')
	cleaning_category = models.ForeignKey(CleaningCategory, null=True, blank=True, db_column='business_category_id')
	#business_category_id = models.IntegerField(null=True) #models.ForeignKey(BusinessCategory, null=True, blank=True)
	#business_subcategory_id = models.IntegerField(null=True) #models.ForeignKey(BusinessSubCategory, null=True, blank=True)
	entity_id = models.IntegerField(null=True)

	class Meta:
		db_table = 'asset_business'


	def __unicode__(self):
		return self.name

	@property
	def owners(self):
		return Citizen.objects.filter(citizen_businessowners__date_to__isnull=True, citizen_businessowners__business=self)

	def merge(self, businesses):
		for fee in Fee.objects.filter(business__in=businesses, fee_payments__isnull=False).distinct():
			matched_fees = self.business_fees.filter(date_to__gte=fee.date_from, date_from__lte=fee.date_to, category=fee.category)
			if matched_fees:
				matched_fee = matched_fees[0]
				fee.fee_payments.update(fee=matched_fee)
			else:
				fee.business = self
				fee.save()

		businesses.update(i_status='inactive')
		Media.objects.filter(business__in=businesses).update(business=self)
		Log.objects.filter(business__in=businesses).update(business=self)
		self.adjust_payments()
		BusinessOwnership.objects.filter(business__in=businesses).exclude(citizen__in=self.owners).update(business=self)

	def adjust_payments(self):
		payments = PayFee.objects.filter(fee__business=self, fee__due_date__isnull=False, paid_date__isnull=False)
		balance = adjustpayments(payments)


	def pay_balance(self, balance=None):
		if not balance:
			balance = self.credit
		outstanding_fees = self.business_fees.filter(is_paid=False)
		if balance > 0 and outstanding_fees:
			fee_ids=[fee.pk for fee in outstanding_fees]
			receipt = process_payments(balance, payment_date=date.today(), citizen_id=None, business_id=self.pk,\
				sector_receipt='CREDIT', payer_name='SYSTEM-CREDIT', bank_receipt='CREDIT', bank='CREDIT', staff_id=1, fees=outstanding_fees)
			receipt.amount = 0
			receipt.save()
			payments = PayFee.objects.filter(fee__business=self).order_by('paid_date')
			balance = adjustpayments(payments, date_from=date.today())
			print '--------CREDITED---%s--------' % balance
		return balance



	def calc_taxes(self, now=None, include_only=False):
		"""
		generate business taxes & fees(Cleaning Fee)
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

		if now.month >=10:
			year_end_date = date(now.year + 1, 12, 31)
		else:
			year_end_date =  yed = date(now.year, 12, 31)

		cleaning = CategoryChoice.objects.get(category__code='fee_type', code='cleaning')
		active = CategoryChoice.objects.get(category__code='status', code='active')
		inactive = CategoryChoice.objects.get(category__code='status', code='inactive')
		if not include_only or 'cleaning' in include_only:
			#if there is no Cleaning fee for this business in the current year, add monthly Cleaning fee, also exclude the business with no cleaning_fee_amount (No premise)
			if self.cleaning_category is not None:
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
						fee = Fee.all_objects.get(category=cleaning, business=self, date_from=cleaning_month, date_to=end_month)

					except Fee.DoesNotExist:
						fee = Fee(category=cleaning, business=self, date_from=cleaning_month, date_to=end_month, amount=0, is_paid=False, date_time=now, period_from=month_from, period_to=month_to)

					except Fee.MultipleObjectsReturned:
						fees = Fee.all_objects.filter(category=cleaning, business=self, date_from=cleaning_month, date_to=end_month).order_by('date_from')
						fee = fees[0]
						fees.exclude(id=fee.pk).update(status=inactive)

					if not fee.is_paid:
						fee.calc_amount()
					cleaning_month = next_month



@receiver(post_save, sender=Business)
def after_business_save(sender, instance, created, **kwargs):
	business = instance
	#instance.calc_taxes()


class SubBusiness(models.Model):
	branch = models.CharField(max_length=100,help_text='Branch Name')
	sector = models.ForeignKey(Sector, null=True, blank=True, help_text="The sector where this branch is located.")
	cell = models.ForeignKey(Cell, null=True, blank=True, help_text="The cell where this branch is located.")
	village = models.ForeignKey(Village, null=True, blank=True, help_text="The village where this branch is located.")
	parcel_id = models.IntegerField(null=True, blank = True, help_text="The parcl ID of branch location.")
	date_created = models.DateTimeField(help_text='Date this branch is created in our system.',auto_now_add=True)
	credit = models.FloatField(default = 0, help_text = 'Credit accumulated for this business.')
	i_status = models.CharField(max_length = 10, default='active', blank = True)
	business = models.ForeignKey(Business)
	entity_id = models.IntegerField(null=True)

	class Meta:
		db_table = 'asset_subbusiness'


class Entity(models.Model):
	business = models.OneToOneField(Business, null=True, db_column='owner_business_id')
	citizen = models.OneToOneField(Citizen, null=True, db_column='owner_citizen_id')
	subbusiness = models.OneToOneField(SubBusiness, null=True, db_column='owner_subbusiness_id')

	class Meta:
		db_table = 'asset_ownership'

	@property
	def entity_type(self):
		if self.citizen:
			return 'citizen'

		elif self.business:
			return 'business'

	@property
	def identifier(self):
		if self.citizen:
			return self.citizen.citizen_id

		elif self.business:
			return self.business.tin

	@property
	def name(self):
		if self.citizen:
			return self.citizen.name

		elif self.business:
			return self.business.name


class IdentityDocument(models.Model):
	entity = models.ForeignKey(Entity)
	foreign_identity_type = models.CharField(max_length = 50, blank = True, null = True, help_text = 'Foreign identity type. For example: passport.')
	foreign_identity_number = models.CharField(max_length = 50, blank = True, null = True, help_text = 'Foreign identity ID.')



class Property(models.Model):
	#plot_id = models.CharField(max_length = 50, unique = True, null=True, blank = True, help_text="Each Plot ID identifies a property.")
	is_leasing = models.BooleanField(default=False, help_text='check whether the property is leased out')
	is_land_lease = models.BooleanField(default=False, help_text='check whether the property is land lease applicable')
	foreign_plot_id = models.CharField(max_length = 50, blank = True, null=True, help_text="Government official Plot ID.")
	parcel_id = models.IntegerField(help_text="Unique ID for this property.", null=True, blank=True)
	cell = models.ForeignKey(Cell, null=True, blank = True, help_text="The cell that this property resides in.")
	village = models.ForeignKey(Village, null=True, blank = True,help_text = "The village that this property resides in.")
	sector = models.ForeignKey(Sector, null=True, blank=True, help_text="The sector that this property belongs to.")
	boundary = models.OneToOneField(Boundary, null=True, help_text="The boundary of property")
	upi = models.CharField(max_length=20, null=True, blank=True)

	size_sqm = models.FloatField(blank = True, null = True)
	floor_count = models.IntegerField(blank = True, null = True)
	floor_total_square_meters = models.FloatField(blank = True, null = True)

	bedrooms = models.IntegerField(blank = True, null = True)
	bathrooms = models.IntegerField(blank = True, null = True)
	ensuites = models.IntegerField(blank=True, null=True)
	garages = models.IntegerField(blank = True, null = True)
	car_ports = models.IntegerField(blank = True, null = True)
	car_spaces = models.IntegerField(blank=True, null=True)

	year_built = models.IntegerField(blank = True, null = True)
	landuse_types = models.ManyToManyField(CategoryChoice, related_name='landuse_types', limit_choices_to={'category__code':'land_use'})
	building_type = models.ForeignKey(CategoryChoice, related_name='building_types', null=True, blank=True,  limit_choices_to={'category__code':'property_type'})
	#description = models.TextField(null=True, blank=True)
	#street_type = models.ForeignKey(StreetType, null=True, blank=True)
	lot_number = models.CharField(max_length=5, null=True, blank=True)
	street_number = models.IntegerField(null=True, blank=True)
	street = models.CharField(max_length=50, blank=True, null=True)

	is_tax_exempt = models.BooleanField(default=False, help_text='')
	taxexempt_reason = models.ForeignKey(CategoryChoice, blank = True, null = True, limit_choices_to={'category__code':'tax_exempt_reason'})
	tax_exempt_note = models.CharField(max_length = 100, blank = True, null = True)
	landlease_type = models.ForeignKey(CategoryChoice, related_name='landlease_types', limit_choices_to={'category__code':'land_lease'}, null=True, blank=True, default=None)
	land_zone = models.ForeignKey(CategoryChoice, related_name='landzone_types', limit_choices_to={'category__code':'land_use'}, null=True, blank=True, default=None)

	#features = models.ManyToManyField(CategoryChoice, related_name='property_features',  limit_choices_to={'category__code':'property_feature'})
	#ideal_for = models.ManyToManyField(CategoryChoice, related_name='property_ideal_for', limit_choices_to={'category__code':'property_ideal'})
	#days_on_market = models.IntegerField(null=True)
	#assets = models.ManyToManyField(Asset, related_name="property_assets")
	date_created = models.DateTimeField(auto_now_add=True, blank=True)
	date_modified = models.DateTimeField(auto_now=True, blank=True)
	credit = models.IntegerField(default = 0, help_text = 'Credit accumulated for this property')

	class Meta:
		db_table = 'property_property'


	def reset_fees(self):
		fees = self.property_fees.filter(fee_payments__isnull=True).distinct()
		for fee in fees:
			fee.reset()

	@property
	def outstanding_fees(self):
		return self.property_fees.filter(date_from__gte=date(2012,1,1), remaining_amount__gt=0)

	@property
	def owners(self):
		for ownership in PropertyOwnership.objects.filter(prop=self, date_to__isnull=True):
			yield ownership.owner

	def adjust_payments(self):
		self.reset_fees()
		payments = PayFee.objects.filter(fee__prop=self, fee__due_date__isnull=False, paid_date__isnull=False).order_by('paid_date')
		if payments:
			payment = payments[0]
			payment.bf = 0
			payment.save()
			balance = adjustpayments(payments)
			self.credit = balance
		else:
			self.credit = 0

		self.save(update_fields=['credit'])
		return self.credit

	def pay_balance(self, balance=None):
		if not balance:
			balance = self.credit

		outstanding_fees = self.property_fees.filter(is_paid=False).order_by('due_date')
		if balance > 0 and outstanding_fees:
			receipt = process_payments(balance, payment_date=date.today(), citizen_id=None, business_id=None,\
				sector_receipt='CREDIT', payer_name='SYSTEM-CREDIT', bank_receipt='CREDIT', bank='CREDIT', staff_id=1, fees=outstanding_fees)
			receipt.amount = 0
			receipt.save()
			payments = PayFee.objects.filter(fee__prop=self).order_by('paid_date')
			balance = adjustpayments(payments, date_from=date.today())
			self.credit = balance
			self.save(update_fields=('credit',))
			print '--------CREDITED---%s--------' % balance
		return balance

	def __unicode__(self):
		if self.street_number and self.street and self.street_type:
			name = "%s %s" % (self.street, self.street_type)
			if self.street_number:
				name = "%s %s" % (self.street_number, name)

		elif self.parcel_id:
			name = "parcel id: %s" % self.parcel_id

		if self.village:
			name += ", %s village" % self.village

		elif self.cell:
			name += ", %s cell" % self.cell

		elif self.sector:
			name += ", %s sector, %s district" % (self.sector, self.sector.district)

		return name


	def get_upi(self):
		if self.cell:
			cell_code = self.cell.code
			return cell_code[1:2]+'/'+cell_code[2:4]+'/'+cell_code[4:6]+'/'+cell_code[6:8]+'/'+str(self.parcel_id)
		else:
			return ''


	@property
	def area(self):
		if self.size_sqm:
			return self.size_sqm

		elif self.boundary:
			return self.boundary.shape_area

		else:
			return 0


@receiver(post_save, sender=Property)
def after_prop_save(sender, instance, created, **kwargs):
	fees = Fee.objects.filter(prop=instance, is_paid=False)
	for fee in fees:
		 fee.calc_amount(save=True)


class PropertyTitle(models.Model):
	prop = models.ForeignKey(Property, related_name='property_title')
	date_from = models.DateField(null=True, blank=True)
	date_to = models.DateField(null=True, blank=True)
	land_lease_issue_date = models.DateField(null=True, blank=True)
	status = models.ForeignKey(CategoryChoice, related_name='property_title_status', )
	first_name = models.CharField(max_length = 50, help_text = 'First name', null=True, blank=True)
	last_name = models.CharField(max_length = 50, help_text = 'Last name', null=True, blank=True)
	middle_name = models.CharField(max_length = 50, help_text = 'Last name', null=True, blank=True)
	created = models.DateTimeField(auto_now_add=True, auto_now=True, null=True)
	modified = models.DateTimeField(auto_now=True, null=True)
	imported = models.DateTimeField(null=True)
	hash_key = models.CharField(max_length=50)

	def __unicode__(self):
		name = "%s %s - " % (self.prop, self.date_from.strftime('%d/%m/%Y'))
		if self.date_to:
			name += self.date_to.strftime('%d/%m/%Y')
		if self.land_lease_issue_date:
			name += " land lease issue date: %s" % self.land_lease_issue_date.strftime('%d/%m/%Y')
		return name

	def set_hash_key(self):
		if not self.hash_key:
			hash_key = binascii.hexlify(os.urandom(3))
			PropertyTitle.objects.filter(pk=self.pk).update(hash_key=hash_key)

	@property
	def owners(self):
		for ownership in self.title_ownership.all():
			owner = ownership.citizen or ownership.business
			yield owner

	@property
	def citizens(self):
		for ownership in self.title_ownership.all():
			citizen = ownership.citizen
			if not citizen:
				business = ownership.business

			if citizen:
				yield citizen

			elif business:
				for business_owner in BusinessOwnership.objects.filter(business=business):
					if business_owner.owner_citizen:
						yield business_owner.owner_citizen

	def close(self, close_date):
		for ownership in self.title_ownership.filter(date_to__isnull=False):
			ownership.date_to = close_date
			ownership.save()
		self.date_to = close_date
		self.save()

	@property
	def epay(self):
		if self.prop.cell.sector.district.name == 'Kicukiro':
			district_code = 'KK'
		else:
			district_code = self.prop.cell.sector.district.name.upper()[0:2]

		sector_code = self.prop.cell.sector.name.upper()[0:2]

		return '%s%s%s' % (district_code, sector_code, self.pk)

	@property
	def outstanding_fees(self, overdue_only=False):
		fees = self.title_fees.filter(is_paid=False, status__code='active').order_by('due_date')
		total = 0
		overdue = 0
		for fee in fees:
			fee.total = fee.total_due
			total += fee.total
			if fee.due_date < date.today():
				overdue += fee.total

		return {'fees':fees, 'total':total, 'overdue':overdue }

	@property
	def land_lease_periods(self):
			date_from = date(2011,1,1)
			date_to = date(date.today().year,12,31)
			if self.land_lease_issue_date:
				date_from = self.land_lease_issue_date

			elif self.date_from:
				date_from = self.date_from

			if self.date_to and self.date_to < date_to:
				date_to = self.date_to

			periods = []
			tax_year = date_from.year
			while tax_year <= date_to.year:
				period = [date(tax_year, 1,1),date(tax_year,12,31)]
				if period[0] < date_from:
					period[0] = date_from
				if period[1] > date_to:
					period[1] = date_to
				periods.append(period)
				tax_year = tax_year + 1

			return periods

	def calc_taxes(self):
		prop_title = self
		active = CategoryChoice.objects.get(category__code='status', code='active')
		inactive = CategoryChoice.objects.get(category__code='status', code='inactive')
		if self.prop.is_tax_exempt:
			Fee.objects.filter(prop_title=self).update(status=inactive)

		elif self.prop.is_land_lease:
			land_lease_issue_date = self.land_lease_issue_date or date(2011,4,5)
			if prop_title.date_from < land_lease_issue_date:
				start_date = land_lease_issue_date
			else:
				start_date = prop_title.date_from

			date_from = start_date
			end_date = prop_title.date_to or date(date.today().year,12,31)
			while date_from <= end_date:
				date_to = date(date_from.year,12,31)
				if end_date < date_to:
					date_to = end_date

				fees = Fee.all_objects.filter(category__code='land_lease', date_from__lte=date_to, date_to__gte=date_from, prop_title=self)

				if not fees:
					land_lease = CategoryChoice.objects.get(category__code='fee_type', code='land_lease')
					fee = Fee.objects.create(prop_title=self, category=land_lease, date_from=date_from, date_to=date_to, prop=self.prop, status=active, is_paid=False, submit_date=date.today(), amount=0, due_date=date_to)
					fee.calc_amount()

				else:
					fee = fees[0]
					fee.date_from = date_from
					fee.date_to = date_to
					fee.status = active
					fee.prop_title = self
					fee.save(update_fields=['date_from', 'date_to', 'status', 'prop_title'])
					fee.calc_amount(save=True)
					dup_fees = fees.exclude(pk=fee.pk)
					dup_fees.update(status=inactive)

				date_from = date(date_from.year+1, 1, 1)

			if self.date_to:
				Fee.objects.filter(prop_title=self, date_to__gt=self.date_to).update(status=inactive)
			Fee.objects.filter(prop_title=self, date_from__lt=self.date_from).update(status=inactive)

		else:
			Fee.objects.filter(prop_title=self, category__code='land_lease').update(status=inactive)


@receiver(post_save, sender=PropertyTitle)
def after_prop_title_save(sender, instance, created, **kwargs):
	#instance.calc_taxes()
	Ownership.objects.filter(prop_title=instance).update(date_started=instance.date_from, date_ended=instance.date_to)


class FeeManager(models.Manager):
	def get_query_set(self):
		return super(FeeManager,self).get_query_set().filter(status__code='active')

class Fee(models.Model):
	# new  field
	category = models.ForeignKey(CategoryChoice, limit_choices_to={'category__code':'fee_type'}, related_name='fee_type', null=True)
	status = models.ForeignKey(CategoryChoice, limit_choices_to={'category__code':'status'}, related_name='fee_status', null=True)
	amount = models.IntegerField(help_text="The amount of fee item.")
	interest = models.IntegerField(default=0) # interest remaining; includes residual interest
	remaining_amount = models.IntegerField(default=0)
	penalty = models.IntegerField(default=0) # penalty remaining
	penalty_paid = models.IntegerField(default=0) # full amount of penalty
	interest_paid = models.IntegerField(default=0) # full amount of penalty
	residual_interest = models.IntegerField(default=0)
	date_from = models.DateField(null=True)
	date_to = models.DateField(null=True)
	due_date = models.DateField(help_text="The date this fee item is due.", null=True, blank=True)
	is_paid = models.BooleanField(help_text="Whether fee is payed.")
	submit_date = models.DateTimeField(help_text="The date this fee item is submited.", null=True, blank=True)
	date_time = models.DateTimeField(help_text="The date this fee item is generated.",auto_now_add=True, auto_now=True)
	business = models.ForeignKey(Business, null=True, related_name='business_fees')
	citizen = models.ForeignKey(Citizen, null=True, related_name='citizen_fees')
	subbusiness = models.ForeignKey(SubBusiness, null=True)
	prop_title = models.ForeignKey(PropertyTitle, null=True, related_name='title_fees')
	prop = models.ForeignKey(Property, null=True, blank=True, related_name='property_fees', db_column='property_id')
	qty = models.FloatField(default=0)
	rate = models.FloatField(default=0)
	period_from = models.DateTimeField(help_text="The start date of a period that this fee item is for.")
	period_to = models.DateTimeField(help_text="The end date of a period that this fee item is for.")
	objects = FeeManager()
	all_objects = models.Manager()
	principle_paid = models.IntegerField(default=0)

	class Meta:
		db_table = 'jtax_fee'
		ordering = ['-due_date', 'pk']


	def reset(self):
		"""
		reset as if no payments
		"""
		self.penalty_paid = 0
		self.interest_paid = 0
		self.principle_paid = 0
		self.residual_interest = 0
		self.is_paid = False
		self.remaining_amount = self.amount
		self.save()

	@property
	def total_due(self, pay_date=date.today()):
		total_due = self.remaining_amount + self.penalty + self.interest
		if total_due < 0:
			return 0
		else:
			return total_due

	def process_payment(self, payment_date, sector_receipt, bank_receipt, payment_amount, staff_id, bank, payer_name, citizen_id=None, business_id=None, notes=None):

		active = CategoryChoice.objects.get(category__code='status', code='active')
		inactive = CategoryChoice.objects.get(category__code='status', code='inactive')

		payment_amount = int(payment_amount)

		if citizen_id:
			payer_name = Citizen.objects.get(pk=citizen_id).name

		elif business_id:
			payer_name = Business.objects.get(pk=business_id).name

		pr = PaymentReceipt(amount= payment_amount, paid_date=payment_date, citizen_id=citizen_id, business_id=business_id,
			sector_receipt=sector_receipt, bank_receipt=bank_receipt, status=active, i_status='active', user_id=staff_id, bank=bank, payer_name=payer_name, note=notes)
		pr.save()

		pf = PayFee(citizen_id=citizen_id, business_id=business_id, fee=self, amount=payment_amount, receipt_no=bank_receipt,
			manual_receipt=sector_receipt, bank=bank, paid_date=payment_date, fine_amount = 0, receipt=pr, status=active, i_status='active', staff_id=staff_id, note=notes)

		pf.receipt = pr

		pf.save()
		balance = adjustpayments(pr.receipt_payments.all(), payment_date)
		if balance and self.business_id:
			balance = self.business.pay_balance(balance)
		elif balance and self.prop:
			balance = self.prop.pay_balance(balance)

		return balance

	def __unicode__(self):
		if self.category.code == 'land_lease':
			return "Land Lease %s - %s" % (self.date_from.strftime('%d/%m/%Y'), self.date_to.strftime('%d/%m/%Y'))

		if self.category.code == 'cleaning':
			return "Cleaning Fee for %s" % (self.date_from.strftime('%B %Y'))

	def get_paid_amount(self):
		return self.principle_paid

	def get_remaining_amount(self):
		return self.remaining_amount


	@property
	def addressee(self):
		if self.entity_id:
			return self.entity
		else:
			return self.addressee_name or None

	def calc_penalty(self, pay_date=None, remaining_amount=None):
		remaining_amount = remaining_amount or self.remaining_amount
		if not pay_date:
			pay_date = date.today()

		if pay_date <= self.due_date:
			return (0,0)

		if self.category.code in ('land_lease', 'cleaning'):
			penalty_limit = 10000
			due_date = self.due_date # end of year due date
			months_late = (pay_date.year - due_date.year ) * 12 + (pay_date.month - due_date.month)
			interest = round(0.015 * float(remaining_amount) * months_late)

			if self.date_to <= date(2012,12,31) and self.category.code == 'land_lease':
				interest = round((pay_date.year - due_date.year) * 0.08 * float(remaining_amount))
				penalty = 0

			elif pay_date > self.due_date and remaining_amount > 0:
				penalty = round(0.1 * float(self.amount))
			else:
				penalty = 0

			penalty = int(penalty)
			if remaining_amount <= 0:
				interest = 0
			else:
				interest = int(interest)

			if penalty > penalty_limit:
				return (penalty_limit, interest)
			else:
				return (penalty, interest)

	def calc_cleaningFee(self):
		if self.category.code == 'cleaning' and self.business and self.business.cleaning_category:
			if not self.is_paid:
				if self.business.cleaning_category_id in range(1,7):
					self.amount = 10000
				elif self.business.cleaning_category_id == 7:
					self.amount = 5000
				elif self.business.cleaning_category_id == 8:
					self.amount = 3000
				else:
					self.amount = 0

			self.submit_date = datetime.now()

		else:
			self.amount = 0
			self.qty = 0
			self.rate = 0

		due_date = self.date_from + relativedelta(months=1)
		self.due_date = date(due_date.year, due_date.month, 5)



	def get_late(self,  pay_date=None):
		if not pay_date:
			pay_date = date.today()
		penalty, interest = self.calc_penalty(pay_date)
		return penalty + interest

	@property
	def property_owners(self):
		if self.prop_id:
			return self.prop.get_owners_between(self.date_from, self.date_to)
		else:
			return None


	def calc_landlease(self):
			rate = 0
			if self.prop.land_zone.code == 'agricultural':
				if self.prop.area >= 20000:
					rate = 0.4

			else:

				if self.date_from >= date(1998,2,1) and self.date_to <= date(2001,12,31):
					if self.prop.land_zone.code == 'residential':
						rate = 80

					elif self.prop.land_zone.code == 'commercial':
						rate = 100

				elif self.date_from >= date(2002,1,1) and self.date_to <= date(2002,12,31):
					if self.prop.land_zone.code == 'residential':
						rate = 150

					elif self.prop.land_zone.code == 'commercial':
						rate = 200

				elif self.date_from >= date(2003,1,1) and self.date_to <= date(2012,12,31): #2003 to 2012
					if self.prop.land_zone.code == 'residential' and self.prop.village:
						if self.prop.village.cell.sector.district.name.lower() == 'kicukiro' and self.prop.village.cell.sector.name.lower() in ('gahanga', 'masaka'):
							rate = 30
						elif self.prop.village.cell.sector.district.name.lower() == 'kicukiro' and  self.prop.village.cell.name.lower() in ('muyange') and \
							self.prop.village.cell.village.name.lower() in ('kamuna','mugeyo'):
							rate = 70
						else:
							rate = 80

					elif self.prop.land_zone.code == 'commercial':
						rate = 150

				else:
					try:
						rate = Rate.objects.get(date_from__lte=self.date_to, date_to__gte=self.date_from, category__code='land_lease', sub_category=self.prop.land_zone, village=self.prop.village)
						rate = float(rate.amount)
					except Rate.MultipleObjectsReturned:
						rate = Rate.objects.filter(date_from__lte=self.date_to, date_to__gte=self.date_from, category__code='land_lease', sub_category=self.prop.land_zone, village=self.prop.village)[0]
						rate = float(rate.amount)
					except Rate.DoesNotExist:
						rate = 0

			if not self.is_paid:
				self.qty = self.prop.area or 0
				self.rate = rate or 0
				self.due_date = date(self.date_from.year, 12, 31)
				self.amount = self.qty * self.rate
				#calculate part year payment
				if self.date_from.month != 1 and self.date_from.day != 1 or self.date_to.month != 12 and self.date_to.day != 31:
					self.amount = self.amount * ((self.date_to - self.date_from ).days + 1.0) / float( 1 + (date(self.date_to.year,12,31) - date(self.date_from.year,1,1)).days )
				self.amount = round(self.amount)


	def calc_amount(self, save=True):
		"""
		calculate the Fee Amount and also the remaining amount based
		on payments made. If the Fee is marked as 'is_paid', then the amount
		wont be recalculated.
		"""
		if self.is_paid:
			return

		elif self.category.code == 'land_lease':
			self.calc_landlease()

		elif self.category.code == 'cleaning':
			self.calc_cleaningFee()

		else:
			raise NotImplentedError('invalid fee type')

		if save:
			if self.pk and not self.amount: # inactivate current records with zero amounts
				self.status = CategoryChoice.objects.get(category__code='status', code='inactive')
				self.save()

			elif self.amount and self.pk:
				self.status = CategoryChoice.objects.get(category__code='status', code='active')
				self.save()


# Model for Receipt of Multiple Tax/Fee payment
class PaymentReceipt(models.Model):
	amount = models.DecimalField(max_digits = 20, decimal_places = 2)
	#user = models.ForeignKey(PMUser, null=True, blank = True)
	date_time = models.DateTimeField(help_text='This is the Date and Time the Entry has been entered into the database.',auto_now_add=True,auto_now=True)
	fees = models.ManyToManyField(Fee, related_name='fee_receipts', through='PayFee')
	sector_receipt = models.CharField(max_length = 50, null=True, blank=True)
	bank_receipt = models.CharField(max_length = 50, null=True, blank=True)
	bank = models.CharField(max_length=100, null=True, blank=True)
	note = models.TextField(null=True, blank=True)
	paid_date = models.DateField()
	citizen = models.ForeignKey(Citizen, blank = True, null=True)
	business = models.ForeignKey(Business, help_text="The business who pay this tax item.", blank = True, null=True)
	#subbusiness_id = models.IntegerField(null=True)
	user = models.ForeignKey(PMUser, help_text="",blank = True, null=True)
	i_status = models.CharField(max_length = 10, default='active', blank = True)
	payer_name = models.CharField(max_length=100, blank = True, null=True)
	status = models.ForeignKey(CategoryChoice, related_name="paymentreceipt_status", null=True)
	payer = models.ForeignKey(Entity, related_name="payments", null=True)

	class Meta:
		db_table = 'jtax_multipayreceipt'

class PayFeeManager(models.Manager):
	def get_query_set(self):
		return super(PayFeeManager,self).get_query_set().filter(status__code='active')

class PayFee(models.Model):
	citizen_id = models.IntegerField(blank = True, null=True)
	business_id = models.IntegerField(help_text="The business who pay this tax item.", blank = True, null=True)
	staff = models.ForeignKey(PMUser, help_text="",blank = True, null=True)
	fee = models.ForeignKey(Fee, help_text="", related_name="fee_payments")
	amount = models.IntegerField()
	receipt_no = models.CharField(max_length = 50)
	#receipts = models.ManyToManyField(PaymentReceipt, through='MultipayReceiptPaymentRelation', related_name='line_items')
	bank =  models.CharField(max_length = 100, null=True, blank=True)
	paid_date = models.DateField()
	fine_amount = models.DecimalField(max_digits = 20, decimal_places = 2, default=0,null=True, blank = True)
	penalty =  models.IntegerField(default=0)
	interest = models.IntegerField(default=0)
	principle = models.IntegerField(default=0)
	penalty_due =  models.IntegerField(default=0)
	interest_due = models.IntegerField(default=0)
	principle_due = models.IntegerField(default=0)
	fine_description = models.TextField(null=True, blank = True)
	manual_receipt = models.CharField(max_length = 50)
	date_time = models.DateTimeField(help_text="The date when this payment is entered into the system.",auto_now_add=True,auto_now=True)
	note = models.TextField(null=True, blank = True, help_text="note about this payment.")
	receipt = models.ForeignKey(PaymentReceipt, related_name="receipt_payments", null=True)
	status = models.ForeignKey(CategoryChoice, related_name="paymentfee_status", null=True)
	i_status = models.CharField(max_length = 10, blank = True)
	bf = models.IntegerField(help_text="The amount of fee item.", default=0)
	credit = models.IntegerField(help_text="The amount of fee item.", default=0)
	objects = PayFeeManager()
	all_objects = models.Manager()

	class Meta:
		db_table = 'jtax_payfee'
		ordering = ['paid_date', 'pk']

	@property
	def total_due(self):
		return self.interest_due + self.penalty_due + self.principle_due

	@property
	def total_paid(self):
		return self.interest + self.penalty + self.principle


# Model for Receipt of Multiple Tax/Fee payment
"""
class MultipayReceiptPaymentRelation(models.Model):
	payfee = models.ForeignKey(PayFee, related_name="receipt_relations")
	receipt = models.ForeignKey(PaymentReceipt, related_name="payment_relations")

	class Meta:
		db_table ="jtax_multipayreceiptpaymentrelation"
"""


class Ownership(models.Model):
	owner_citizen = models.ForeignKey(Citizen,null=True,blank=True, related_name="assets")
	owner_business = models.ForeignKey(Business,null=True,blank=True, related_name="assets")
	asset_business = models.ForeignKey(Business,null=True,blank=True, related_name="related_name1")
	asset_property = models.ForeignKey(Property,null=True,blank=True, related_name="related_name3")
	share = models.FloatField(help_text="Owner's share of the asset", default=100)
	date_started = models.DateField(help_text='Date this ownership started')
	date_ended = models.DateField(help_text='Date this ownership ended', null=True, blank = True)
	i_status = models.CharField(max_length = 10, default='active', blank = True, null=True)
	date_created = models.DateTimeField(help_text='Date this record is saved',auto_now_add=True)
	prop_title = models.ForeignKey(PropertyTitle, related_name='prop_title_ownerships')

	class Meta:
		db_table = 'asset_ownership'


class BusinessOwnership(models.Model):
	citizen = models.ForeignKey(Citizen,null=True,blank=True, db_column='owner_citizen_id', related_name="citizen_businessowners")
	business = models.ForeignKey(Business,null=True,blank=True, db_column='asset_business_id', related_name="business_ownership")
	date_from = models.DateField(null=True, blank=True, db_column='date_started')
	date_to = models.DateField(null=True, blank=True, db_column='date_ended')
	status = models.ForeignKey(CategoryChoice, related_name='business_ownership_status', )
	stake = models.FloatField(null=True, blank=True, db_column='share')
	created = models.DateTimeField(auto_now_add=True, auto_now=True, null=True, db_column='date_created')

	class Meta:
		db_table = 'asset_ownership'
		managed = False


class PropertyOwnership(models.Model):
	prop = models.ForeignKey(Property, related_name='property_ownership', db_column='asset_property_id')
	prop_title = models.ForeignKey(PropertyTitle, null=True, related_name='title_ownership')
	date_from = models.DateField(null=True, blank=True, db_column='date_started')
	date_to = models.DateField(null=True, blank=True, db_column='date_ended')
	status = models.ForeignKey(CategoryChoice, related_name='property_ownership_status', )
	stake = models.FloatField(null=True, blank=True, db_column='share')
	created = models.DateTimeField(auto_now_add=True, auto_now=True, null=True, db_column='date_created')
	business = models.OneToOneField(Business, null=True, db_column='owner_business_id')
	citizen = models.OneToOneField(Citizen, null=True, db_column='owner_citizen_id')

	@property
	def owner(self):
		owner = self.citizen or self.business
		return owner

	class Meta:
		db_table = 'asset_ownership'
		managed = False



class DebtorsReport(models.Model):
	as_at = models.DateField(auto_now_add=True)
	fee_type = models.CharField(max_length=30)


class DebtorsReportLine(models.Model):
	report = models.ForeignKey(DebtorsReport)
	business = models.ForeignKey(Business)
	subbusiness = models.ForeignKey(SubBusiness, null=True)
	rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	month = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	month_1 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	month_3 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	month_6 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	month_12 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	total = models.DecimalField(max_digits=10, decimal_places=2, default=0)


class Log(models.Model):
	"""
	keep log for each action taken by user.
	"""
	transaction_id = models.IntegerField(null = True, blank = True)
	#user_id = models.IntegerField(null=True, blank=True)
	user = models.ForeignKey(PMUser, help_text="",blank = True, null=True)
	citizen = models.ForeignKey(Citizen, null=True, blank=True)
	property = models.ForeignKey(Property, null=True, blank=True)
	business = models.ForeignKey(Business, null = True, blank = True)
	tids = models.CharField(max_length = 200, null=True, blank = True)
	tax_type = models.CharField(max_length = 50, null=True, blank = True)
	tax_id = models.CharField(max_length = 50, null=True, blank = True)
	payment_type = models.CharField(max_length = 50, null=True, blank = True)
	payment_id = models.CharField(max_length = 50, null=True, blank = True)
	media_id = models.CharField(max_length = 50, null=True, blank = True)
	username = models.CharField(max_length=100)
	table = models.CharField(blank=True, null=True, max_length=100)
	date_time = models.DateTimeField(auto_now_add=True)
	old_data = models.CharField(blank=True, null=True, max_length=1000)
	new_data = models.CharField(blank=True, null=True, max_length=1000)
	message = models.TextField(blank=True, null=True)
	fee = models.ForeignKey(Fee, null=True, blank=True)
	payfee = models.ForeignKey(PayFee, blank=True, null=True)

	class Meta:
		db_table = 'log_log'



class Rate(models.Model):
	category = models.ForeignKey(CategoryChoice, related_name='rate_category')
	sub_category = models.ForeignKey(CategoryChoice, related_name='rate_subcategory')
	amount = models.DecimalField(decimal_places=2, max_digits=8)
	date_from = models.DateField()
	date_to = models.DateField(null=True)
	village = models.ForeignKey(Village, null=True)
	cell = models.ForeignKey(Cell, null=True)
	sector = models.ForeignKey(Sector, null=True)

	def __unicode__(self):
		return "category:%s period:%s-%s village:%s cell:%s sector:%s rate:%s" % (self.category, self.date_from, self.date_to, self.village, self.cell, self.sector, self.amount)


	def get_landlease(self, land_use, dait, village):
		land_lease = CategoryChoice.objects.get(category__code='fee_type', code='land_lease')
		return self.objects.get(date_from__lte=date, date_to__gte=dait, village=village, land_use=land_use, category=land_use)


class RateNotFound(models.Model):
	fee = models.ForeignKey(Fee, null=True)
	category = models.ForeignKey(CategoryChoice, related_name='category_not_found')
	sub_category = models.ForeignKey(CategoryChoice, related_name='sub_cat_not_found')
	date_from = models.DateField()
	date_to = models.DateField(null=True)
	village = models.ForeignKey(Village, null=True)
	cell = models.ForeignKey(Cell, null=True)
	sector = models.ForeignKey(Sector, null=True)
	created = models.DateTimeField(auto_now_add=True)



class MediaManager(models.Manager):
	def get_query_set(self):
		return super(MediaManager,self).get_query_set().exclude(restored=False, missing=1)


class Media(models.Model):
	tags = models.CharField(max_length = 150, help_text = 'Tags for the Media', null=True, blank = True)
	title = models.CharField(max_length = 150, null=True, blank = True, help_text = 'Display name of the media')
	description = models.TextField(null=True, blank = True, help_text = 'Notes/Reminder')
	file_name = models.CharField(max_length = 150)
	path = models.CharField(max_length = 255)
	file_type = models.CharField(max_length = 50)
	file_size = models.CharField(max_length = 50)
	citizen = models.ForeignKey(Citizen,  null=True, blank=True)
	business = models.ForeignKey(Business,  null=True, blank=True)
	property = models.ForeignKey(Property,  null=True, blank=True)
	tax_type = models.CharField(max_length = 50,  help_text = 'Type of Tax/Fee Associated with this Media', null=True, blank = True)
	tax_id = models.IntegerField(max_length = 50, help_text="", null=True, blank = True)
	payment_type = models.CharField(max_length = 50, help_text = 'Type of Payment Associated with this Media', null=True, blank = True)
	payment_id = models.IntegerField(max_length = 50, help_text="", null=True, blank = True)
	user = models.ForeignKey(PMUser, null=True, blank=True, help_text="")
	#user_id = models.IntegerField(max_length = 10, help_text="")
	i_status = models.CharField(max_length = 10, default='active', blank = True)
	date_created = models.DateTimeField(help_text='Date this record is saved',auto_now_add=True)
	missing = models.IntegerField(null=True)
	restored = models.NullBooleanField()
	payfee = models.ForeignKey(PayFee, null=True, blank=True)
	fee = models.ForeignKey(Fee, null=True, blank=True)
	receipt = models.ForeignKey(PaymentReceipt, blank=True, null=True)

	objects = MediaManager()

	class Meta:
		db_table = 'media_media'
		managed = False

	def __unicode__(self):
		return str(self.file_name) + " " + str(self.title)


class Duplicate(models.Model):
	business1 = models.ForeignKey(Business, related_name='duplicates')
	business2 = models.ForeignKey(Business, related_name='duplicate2')
	#merged_business = models.ForeignKey(Business, related_name='merged_business', null=True)
	status = models.IntegerField(default=1)
	similarity = models.FloatField(null=True)
	modified = models.DateTimeField(help_text='Date this record is saved',auto_now_add=True, null=True)

	class Meta:
		db_table = 'asset_duplicate'
		managed = False


def process_payments(amount, payment_date, citizen_id, business_id, sector_receipt, payer_name, bank_receipt, bank, staff_id, fees):
	amount = int(amount)
	assert payment_date <= date.today(), 'Payment cannot be in the future'
	active = CategoryChoice.objects.get(category__code='status', code='active')
	inactive = CategoryChoice.objects.get(category__code='status', code='inactive')
	fees = fees.order_by('due_date')

	entity = None
	if citizen_id:
		payer_name = Citizen.objects.get(pk=citizen_id).name
	elif business_id:
		payer_name = Business.objects.get(pk=business_id).name

	pr = PaymentReceipt(amount= amount, paid_date=payment_date, citizen_id=citizen_id, business_id=business_id, payer_name=payer_name,
	sector_receipt=sector_receipt, bank_receipt=bank_receipt, status=active, i_status='active', user_id=staff_id, bank=bank)

	pr.save()
	total_payment = 0

	for fee in fees:
		total_due = int(fee.total_due)
		if amount > 0 and total_due > 0:
			if amount > total_due:
				pay_amount = total_due
				amount = amount - total_due
			else:
				pay_amount = amount
				amount = 0
			pf = PayFee(citizen_id=citizen_id, business_id=business_id, fee=fee, amount=pay_amount, receipt_no=bank_receipt, \
				manual_receipt=sector_receipt, bank=bank, paid_date=payment_date, fine_amount = 0, receipt=pr, status=active, i_status='active', staff_id=staff_id)
			pr = pf.receipt
			pf.save()

	return pr





