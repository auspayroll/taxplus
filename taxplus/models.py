from datetime import date, datetime, timedelta
from dateutil import parser
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db import models as gis_models
from django.db import models
from django.db.models import Q
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core import serializers
import ast
import binascii
import json
import os
from dev1.ThreadLocal import get_current_request_log

class LoggedModel(models.Model):
	class Meta:
		abstract = True

	def save(self, *args, **kwargs):
		log = get_current_request_log()
		if not log:
			log = Log.objects.create()
		content_type = ContentType.objects.get_for_model(self)
		if type(self) is Property:
			log.prop = self

		elif type(self) is Business:
			log.business = self

		elif type(self) is Citizen:
			log.citizen = self

		if self.pk: #update operation
			log_relation = LogRelation(content_type=content_type, object_id=self.pk, log=log, crud=3)
			try:
				db_object = self.__class__.objects.get(pk=self.pk)
			except self.__class__.DoesNotExist:
				pass
			else:
				updated_fields = []
				excluded_fields = ['updated', 'date_updated', 'created', 'date_created', 'update', 'submit_date']
				db_dict = dict([(field.name, getattr(db_object,field.name)) for field in db_object._meta.fields if field.name not in excluded_fields])
				updated_dict = dict([(field.name, getattr(self,field.name)) for field in self._meta.fields if field.name not in excluded_fields])
				for k,v in updated_dict.items():
					if db_dict.get(k) != updated_dict.get(k):
						updated_fields.append(k)

				if updated_fields: #serialize old and new objects (using natural keys) if there are updated fields
					log_relation.old_object = json.dumps(json.loads(serializers.serialize("json", [db_object], fields=updated_fields, use_natural_keys=True))[0]['fields'])
					log_relation.new_object = json.dumps(json.loads(serializers.serialize("json", [self], fields=updated_fields, use_natural_keys=True))[0]['fields'])
					log_relation.save()
					log.message = ((log.message or '') + ("; %s updated" % self)).strip(';')

					if hasattr(self,'tags'):
						for tag in self.tags:
							if type(tag) is Property and not log.prop:
								log.prop = tag

							elif type(tag) is Business and not log.business:
								log.business = tag

							elif type(tag) is Citizen and not log.citizen:
								log.citizen = tag
					log.modified_objects = True
					log.save()

		else:
			saved = super(LoggedModel, self).save(*args, **kwargs)
			log_relation = LogRelation(content_type=content_type, object_id=self.pk, log=log, crud=1)
			log.message = ((log.message or '') + ("; %s created" % self)).strip(';')

			if hasattr(self,'tags'):
				for tag in self.tags:
					if type(tag) is Property:
						log.prop = tag

					elif type(tag) is Business and not log.business_id:
						log.business = tag

					elif type(tag) is Citizen and not log.citizen_id:
						log.citizen = tag

			log.modified_objects = True
			log.save()
			return saved

		return super(LoggedModel, self).save(*args, **kwargs)

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

class PlotBoundary(models.Model):
	gid = models.IntegerField(primary_key=True)
	cell_code = models.CharField(max_length=8)
	polygon = gis_models.MultiPolygonField(srid=3857, db_column='the_geom')
	parcel_id = models.IntegerField()

	class Meta:
		db_table = 'converted'

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
		return self.name

	def natural_key(self):
		return self.name

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

	def natural_key(self):
		return self.name

class Council(models.Model):
	name = models.CharField(max_length=100, help_text="Council name.")
	address = models.CharField(max_length = 200, help_text="Address of council.")
	boundary = models.OneToOneField(Boundary, null=True, blank=True, help_text="The boundary of council.")

	class Meta:
		db_table = 'property_council'

	def __unicode__(self):
		return self.name

	def natural_key(self):
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
		return "%s / %s" % (self.name, self.district.name.upper())

	def natural_key(self):
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

	def natural_key(self):
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

	def natural_key(self):
		return self.name

class CleaningCategory(models.Model):
	name = models.CharField(max_length=50)
	#amount = models.DecimalField(max_digits=8, decimal_places=0)

	class Meta:
		db_table = 'asset_businesscategory'

	def __unicode__(self):
		return self.name

	def natural_key(self):
		return self.name

class BusinessCategory(models.Model):
	name = models.CharField(max_length=100)
	cleaning_category = models.ForeignKey(CleaningCategory, db_column='business_category_id')

	class Meta:
		db_table = 'asset_businesssubcategory'

	def __unicode__(self):
		return self.name

	def natural_key(self):
		return self.name

class Citizen(LoggedModel):
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

	def natural_key(self):
		return "%s %s DOB:%s CID:%s" % (self.first_name, self.last_name, self.date_of_birth, self.citizen_id)

	@property
	def name(self):
		if self.middle_name and self.middle_name!='' and self.middle_name !='null':
			return self.first_name +' '+ self.middle_name +' '+ self.last_name
		else:
			return self.first_name + ' ' + self.last_name

	def __unicode__(self):
		return self.name

	@property
	def current_assets(self):
		ownerships = Ownership.objects.filter(owner_citizen=self, date_ended__isnull=True)
		for ownership in ownerships:
			if ownership.asset_property:
				yield ownership.asset_property
			if ownership.asset_business:
				yield ownership.asset_business

	@property
	def link(self):
		return 'citizen'

class Business(LoggedModel):
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
	over_due_lt_month = models.IntegerField(default=0)
	over_due_lt_month_interest = models.IntegerField(default=0)
	over_due_lt_month_penalty = models.IntegerField(default=0)
	over_due_gt_month = models.IntegerField(default=0)
	over_due_gt_month_interest = models.IntegerField(default=0)
	over_due_gt_month_penalty = models.IntegerField(default=0)
	over_due_gt_3month = models.IntegerField(default=0)
	over_due_gt_3month_interest = models.IntegerField(default=0)
	over_due_gt_3month_penalty = models.IntegerField(default=0)
	over_due_gt_6month = models.IntegerField(default=0)
	over_due_gt_6month_interest = models.IntegerField(default=0)
	over_due_gt_6month_penalty = models.IntegerField(default=0)
	over_due_gt_year = models.IntegerField(default=0)
	over_due_gt_year_interest = models.IntegerField(default=0)
	over_due_gt_year_penalty = models.IntegerField(default=0)
	over_due_interest = models.IntegerField(default=0)
	over_due_penalty = models.IntegerField(default=0)
	over_due = models.IntegerField(default=0)
	total_over_due = models.IntegerField(default=0)
	as_at = models.DateField(null=True)

	class Meta:
		db_table = 'asset_business'

	def natural_key(self):
		return "%s (ph:%s, District:%s, Sector:%s, Cell:%s, Village:%s)" % (self.name, self.phone1, self.cell.sector.district, self.cell.sector, self.cell, self.village)

	def __unicode__(self):
		return self.name

	@property
	def owners(self):
		for ownership in Ownership.objects.filter(asset_business=self, date_ended__isnull=True):
			if ownership.owner_business:
				yield ownership.owner_busines
			elif owernship.owner_citizen:
				yield ownership.owner_citizen

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
		self.adjust_payments()
		BusinessOwnership.objects.filter(business__in=businesses).exclude(citizen__in=self.owners).update(business=self)

	def reset_fees(self):
		active_receipts = PaymentReceipt.objects.filter(receipt_payments__fee__business=self, status__code='active')
		fees = Fee.objects.filter(business=self).exclude(fee_payments__receipt__in=active_receipts)
		for fee in fees:
			fee.reset()

	def adjust_payments(self, adjust_from=None):
		balance = 0
		receipts = PaymentReceipt.objects.filter(receipt_payments__fee__business_id=self.pk, status__code='active').distinct().order_by('date_time')
		for receipt in receipts:
			receipt.bf = bf = balance
			balance = receipt.amount
			for pay_fee in receipt.receipt_payments.all().order_by('fee__due_date'):
				balance = pay_fee.fee.pay(receipt=receipt, pay_fee=pay_fee, payment_amount=balance, bf=bf)
				bf = 0

			receipt.credit = balance
			receipt.save()

		self.credit = balance
		self.save(update_fields=['credit'])
		return balance

	def pay_balance(self):
		if self.credit > 0:
			outstanding_fees = self.business_fees.filter(is_paid=False).order_by('due_date')
			if outstanding_fees:
				balance = process_payment(self.credit, payment_date=date.today(), citizen_id=None, business_id=self.pk, \
					    sector_receipt='CREDIT', payer_name='SYSTEM', bank_receipt='CREDIT', bank='CREDIT', staff_id=1, fees=outstanding_fees)
				return balance

		return 0

	@property
	def link(self):
		return 'business'

	def calc_taxes(self, from_date=None, include_only=False):
		"""
		generate cleaning fees: if now is specified, calculate from the current year
		all fees that are not paid will be re-calculated
		"""
		cleaning = CategoryChoice.objects.get(category__code='fee_type', code='cleaning')
		active = CategoryChoice.objects.get(category__code='status', code='active')
		inactive = CategoryChoice.objects.get(category__code='status', code='inactive')
		if self.i_status != 'active':
			Fee.objects.filter(category=cleaning, business=self, is_paid=False).update(status=inactive)
			return None

		if from_date:
			year_start_date = from_date
			if self.date_started and self.date_started > year_start_date:
				year_start_date = self.date_started
		else:
			year_start_date = self.date_started or from_date

		if date.today().month >=10:
			year_end_date = date(date.today().year + 1, 12, 31)
		else:
			year_end_date = date(date.today().year, 12, 31)

		if self.closed_date and self.closed_date < year_end_date:
			year_end_date  = self.closed_date

		if not include_only or 'cleaning' in include_only:
			if self.cleaning_category:
				cleaning_month = year_start_date

				while cleaning_month <= year_end_date:
					next_month = cleaning_month + relativedelta(months=1)
					next_month = date(next_month.year, next_month.month, 1) # 1st of next month
					end_month = next_month - timedelta(days=1)

					fees = Fee.all_objects.filter(category=cleaning, business=self, date_to__gte=cleaning_month, date_from__lte=end_month)
					if fees:
						fee = fees[0]
						fee.status = active
						fee.date_from = cleaning_month
						fee.date_to = end_month
						fee.save()
						fees.exclude(id=fee.pk).update(status=inactive)

					else:
						fee = Fee(category=cleaning, business=self, date_from=cleaning_month, date_to=end_month, amount=0, is_paid=False, date_time=datetime.now())

					if not fee.is_paid:
						fee.calc_amount()
					cleaning_month = next_month

				#inactive all outside of the range
				Fee.objects.filter(business=self, category=cleaning).filter(Q(date_from__gt=year_end_date) | Q(date_from__lt=(self.date_started or year_start_date))).update(status=inactive)

			else:
				Fee.objects.filter(category=cleaning, business=self, is_paid=False).update(status=inactive)

	@property
	def cleaningFee(self):
		if self.cleaning_category:
			if self.cleaning_category_id in range(1,7):
				return 10000
			elif self.cleaning_category_id ==7:
				return 5000
			elif self.cleaning_category_id ==8:
				return 3000
		return 0

#@receiver(post_save, sender=Business)
def after_business_save(sender, instance, created, **kwargs):
	business = instance
	#instance.calc_taxes()

# deprecated
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

class IdentityDocument(models.Model):
	foreign_identity_type = models.CharField(max_length = 50, blank = True, null = True, help_text = 'Foreign identity type. For example: passport.')
	foreign_identity_number = models.CharField(max_length = 50, blank = True, null = True, help_text = 'Foreign identity ID.')

class Property(LoggedModel):
	#plot_id = models.CharField(max_length = 50, unique = True, null=True, blank = True, help_text="Each Plot ID identifies a property.")
	is_leasing = models.BooleanField(default=False, help_text='check whether the property is leased out')
	is_land_lease = models.BooleanField(default=False, help_text='check whether the property is land lease applicable')
	foreign_plot_id = models.CharField(max_length = 50, blank = True, null=True, help_text="Government official Plot ID.")
	parcel_id = models.IntegerField(help_text="Unique ID for this property.", null=True, blank=True)
	cell = models.ForeignKey(Cell, null=True, blank = True, help_text="The cell that this property resides in.")
	village = models.ForeignKey(Village, null=True, blank = True,help_text = "The village that this property resides in.")
	sector = models.ForeignKey(Sector, null=True, blank=True, help_text="The sector that this property belongs to.")
	boundary = models.OneToOneField(Boundary, null=True, help_text="The boundary of property")
	plot_boundary = models.ForeignKey(PlotBoundary, null=True, help_text="The boundary of property")
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
	over_due = models.IntegerField(default=0)
	over_due_interest = models.IntegerField(default=0)
	over_due_penalty = models.IntegerField(default=0)
	total_over_due = models.IntegerField(default=0)
	as_at = models.DateTimeField(null=True)

	class Meta:
		db_table = 'property_property'

	def natural_key(self):
		return self.upi

	def reset_fees(self):
		active_receipts = PaymentReceipt.objects.filter(receipt_payments__fee__prop=self, status__code='active')
		fees = Fee.objects.filter(business=self).exclude(fee_payments__receipt__in=active_receipts)
		for fee in fees:
			fee.reset()

	def adjust_payments(self, adjust_from=None):
		balance = 0
		receipts = PaymentReceipt.objects.filter(receipt_payments__fee__prop__pk=self.pk, status__code='active').distinct().order_by('date_time')
		for receipt in receipts:
			receipt.bf = bf = balance
			balance = receipt.amount
			for pay_fee in receipt.receipt_payments.all().order_by('fee__due_date'):
				balance = pay_fee.fee.pay(receipt=receipt, pay_fee=pay_fee, payment_amount=balance, bf=bf)
				bf = 0

			receipt.credit = balance
			receipt.save()

		self.credit = balance
		self.save(update_fields=['credit'])
		return balance

	@property
	def outstanding_fees(self):
		return self.property_fees.filter(date_from__gte=date(2012,1,1), remaining_amount__gt=0)

	@property
	def owners(self):
		for ownership in Ownership.objects.filter(asset_property=self, date_ended__isnull=True):
			if ownership.owner_business:
				yield ownership.owner_busines
			elif ownership.owner_citizen:
				yield ownership.owner_citizen

	def pay_balance(self):
		if self.credit > 0:
			outstanding_fees = self.property_fees.filter(is_paid=False).order_by('due_date')
			if outstanding_fees:
				process_payment(self.credit, payment_date=date.today(), citizen_id=None, business_id=None, \
				    sector_receipt='CREDIT', payer_name='SYSTEM', bank_receipt='CREDIT', bank='CREDIT', staff_id=1, fees=outstanding_fees)
		return 0

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

	@property
	def link(self):
		"""returns url link name"""
		return 'property'

#@receiver(post_save, sender=Property)
def after_prop_save(sender, instance, created, **kwargs):
	return
	"""
	fees = Fee.objects.filter(prop=instance, is_paid=False)
	for fee in fees:
		 fee.calc_amount(save=True)
	"""

class PropertyTitle(LoggedModel):
	prop = models.ForeignKey(Property, related_name='property_title')
	date_from = models.DateField(null=True, blank=True)
	date_to = models.DateField(null=True, blank=True)
	land_lease_issue_date = models.DateField(null=True, blank=True)
	status = models.ForeignKey(CategoryChoice, related_name='property_title_status', blank=True)
	first_name = models.CharField(max_length = 50, help_text = 'First name', null=True, blank=True)
	last_name = models.CharField(max_length = 50, help_text = 'Last name', null=True, blank=True)
	middle_name = models.CharField(max_length = 50, help_text = 'Last name', null=True, blank=True)
	created = models.DateTimeField(auto_now_add=True, auto_now=True, null=True)
	modified = models.DateTimeField(auto_now=True, null=True)
	imported = models.DateTimeField(null=True)
	hash_key = models.CharField(max_length=50)

	def natural_key(self):
		return "Property %s: from %s to %s" % (self.prop.upi, self.date_from, self.date_to)

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
	def tags(self):
		tags = [prop]


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

class Fee(LoggedModel):
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
	interest_charged = models.IntegerField(default=0)
	penalty_charged = models.IntegerField(default=0)
	penalty = models.IntegerField(default=0)
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
		self.penalty, self.interest_charged = self.calc_penalty(date.today(), self.amount)
		self.interest = self.interest_charged
		self.save()


	@property
	def tags(self):
		tags = []
		if self.citizen_id:
			tags.append(self.citizen)
		if self.business_id:
			tags.append(self.business)
		if self.business:
			tags.append(self.business)
		if self.prop:
			tags.append(self.prop)
		return tags

	@property
	def total_due(self, pay_date=date.today()):
		total_due = self.remaining_amount + self.penalty + self.interest
		if total_due < 0:
			return 0
		else:
			return total_due

	def pay(self, receipt, pay_fee, payment_amount=0, bf=0):
		"""
		process a payment for a Fee
		all other payments will be re-adjusted according to the Fee paid date.
		"""
		payments = self.fee_payments.filter(status__code='active', receipt__date_time__lte=receipt.date_time, receipt__status__code='active').order_by('paid_date', 'id')
		self.penalty = self.interest = self.penalty_paid = self.interest_paid = 0
		self.principle_paid = self.residual_interest = penalty = self.penalty_charged = self.interest_charged = 0
		self.remaining_amount = self.amount
		active = CategoryChoice.objects.get(category__code='status', code='active')
		balance = payment_amount
		for payment in payments:
			if not payment.receipt or not payment.paid_date:
				continue

			#calculate amounts owed before payment
			calc_penalty, calc_interest = self.calc_penalty(payment.paid_date, self.remaining_amount)
			if not self.penalty_charged:
				self.penalty_charged = calc_penalty

			self.penalty = self.penalty_charged - self.penalty_paid
			if receipt and payment.pk == pay_fee.pk:
 				payment = pay_fee
				balance = payment_amount + bf
				payment.bf = bf
			else:
				balance = payment.amount + payment.bf

			payment.penalty_due = self.penalty
			payment.interest_due = calc_interest + self.residual_interest - self.interest_paid
			payment.principle_due = self.remaining_amount

			if balance <= self.remaining_amount:
				_, calc_interest_balance = self.calc_penalty(payment.paid_date, self.remaining_amount - balance)
				calc_interest = calc_interest - calc_interest_balance
				self.residual_interest += calc_interest
				self.remaining_amount = self.remaining_amount - balance
				payment.interest = 0
				payment.principle = balance
				balance = 0

			else: # balance > remaining amount
				balance = balance - self.remaining_amount
				payment.principle = self.remaining_amount
				self.residual_interest += calc_interest #add together interest

				# pay off interest
				if payment.interest_due > 0:
					if balance > payment.interest_due:
						balance = balance - payment.interest_due
						payment.interest = payment.interest_due
					else:
						payment.interest = balance
						balance = 0 # self.residual_intererest -= balance
				else:
					payment.interest = 0

				self.remaining_amount = 0

			#pay off penalty
			if self.penalty > 0 and balance > 0:
				if balance >= self.penalty:
					balance = balance - self.penalty
					payment.penalty = self.penalty
				else:
					payment.penalty = balance
					balance = 0
			else:
				payment.penalty = 0

			if receipt and payment.pk == pay_fee.pk:
				payment.amount = payment.principle + payment.interest + payment.penalty
				pay_fee.credit = balance
			else: #if pre-existing payment, subtract existing credit from current overpayment
				#previous overpayment credits cannot be altered as they count towards payment receipt credits
				pay_fee.credit += (balance - payment.credit)
				payment.save()

			self.penalty_paid += payment.penalty
			self.interest_paid += payment.interest
			self.principle_paid += payment.principle

		if self.total_due <= 0:
			self.is_paid = True
		else:
			self.is_paid = False
		self.save()
		pay_fee.save()
		return pay_fee.credit

	def update_interest_penalty(self):
		calc_penalty, calc_interest = self.calc_penalty(date.today(), self.remaining_amount)
		if not self.penalty_charged:
			self.penalty_charged = calc_penalty

		self.penalty = self.penalty_charged - self.penalty_paid
		self.interest_charged = calc_interest + self.residual_interest
		self.interest = self.interest_charged - self.interest_paid

		self.save()
		return self.interest, self.penalty


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

		if not self.due_date or pay_date <= self.due_date:
			return (0,0)

		if self.category.code in ('land_lease', 'cleaning', 'market'):
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

		return 0, 0

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
							self.prop.village.cell.name.lower() in ('kamuna','mugeyo'):
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

			elif self.amount:
				self.status = CategoryChoice.objects.get(category__code='status', code='active')
				self.save()

			else: # not self.amount and not self.pk, don't save
				pass

# Model for Receipt of Multiple Tax/Fee payment
class PaymentReceipt(LoggedModel):
	amount = models.IntegerField(default=0)
	#user = models.ForeignKey(PMUser, null=True, blank = True)
	date_time = models.DateTimeField(help_text='This is the Date and Time the Entry has been entered into the database.',auto_now_add=True)
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
	bf = models.IntegerField(help_text="The amount of fee item.", default=0)
	credit = models.IntegerField(help_text="The amount of fee item.", default=0)

	class Meta:
		db_table = 'jtax_multipayreceipt'

	def __unicode__(self):
		return "#%s - %s" % (self.bank_receipt, self.amount)

	@property
	def tags(self):
		t = []
		for payfee in self.receipt_payments.all():
			fee = payfee.fee
			if fee.business_id and fee.business not in t:
				t.append(payfee.fee.business)
			elif fee.prop and fee.prop not in t:
				t.append(fee.prop)
			if fee.citizen and fee.citizen not in t:
				t.append(fee.citizen)

			try:
				if self.citizen_id and self.citizen not in t:
					t.append(self.citizen)
			except:
				pass

			try:
				if self.business_id and self.business not in t:
					t.append(self.business)
			except:
				pass

		return t

	def reverse(self, user=None):
		inactive = CategoryChoice.objects.get(category__code='status', code='inactive')
		self.status = inactive
		self.save()
		fees = Fee.objects.filter(fee_payments__pk__in=self.receipt_payments.values_list('pk', flat=True)).distinct()
		for fee in fees:
			fee.reset()
		self.receipt_payments.all().update(status=inactive)
		Log.log(message='Payment reversed', target=self)

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
	fine_amount = models.IntegerField(default=0, null=True, blank = True)
	penalty =  models.IntegerField(default=0)
	interest = models.IntegerField(default=0)
	principle = models.IntegerField(default=0)
	penalty_due =  models.IntegerField(default=0)
	interest_due = models.IntegerField(default=0)
	principle_due = models.IntegerField(default=0)
	fine_description = models.TextField(null=True, blank = True)
	manual_receipt = models.CharField(max_length = 50)
	date_time = models.DateTimeField(help_text="The date when this payment is entered into the system.",auto_now_add=True)
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

class Ownership(LoggedModel):
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

	@property
	def tags(self):
		tags = []
		if self.owner_citizen:
			tags.append(self.owner_citizen)
		if self.owner_business:
			tags.append(self.owner_business)
		if self.asset_business:
			tags.append(self.asset_business)
		if self.asset_property:
			tags.append(self.asset_property)
		return tags

# deprecated
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


# deprecated
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

class Media(LoggedModel):
	tags = models.CharField(max_length = 150, help_text = 'Tags for the Media', null=True, blank = True)
	title = models.CharField(max_length = 150, null=True, blank = True, help_text = 'Display name of the media')
	description = models.TextField(null=True, blank = True, help_text = 'Notes/Reminder')
	file_name = models.CharField(max_length = 150)
	path = models.CharField(max_length = 255)
	file_type = models.CharField(max_length = 50)
	file_size = models.CharField(max_length = 50)
	citizen = models.ForeignKey(Citizen,  null=True, blank=True)
	business = models.ForeignKey(Business,  null=True, blank=True)
	prop = models.ForeignKey(Property, null=True, blank=True, db_column='property_id')
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

	@property
	def tags(self):
		tags = []
		try:
			if self.business:
				tags.append(self.business)
		except:
			pass

		try:
			if self.prop:
				tags.append(self.prop)
		except:
			pass

		try:
			if self.citizen:
				tags.append(self.citizen)
		except:
			pass

		if self.payfee and not self.fee:
			self.fee = self.payfee.fee

		if self.receipt and not self.fee:
			receipt_payments = self.receipt.receipt_payments.all()
			if receipt_payments:
				self.fee = receipt_payments[0].fee

		if self.fee:
			if self.fee.business and self.fee.business not in tags:
				tags.append(self.fee.business)

			if self.fee.citizen and self.fee.citizen not in tags:
				tags.append(self.fee.citizen)

			if self.fee.prop and self.fee.prop not in tags:
				tags.append(self.fee.prop)

		return tags

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

class MessageBatch(models.Model):
	date_time = models.DateTimeField(auto_now_add=True)
	message = models.TextField()
	exported = models.DateTimeField(null=True)
	sent = models.DateTimeField(null=True)
	district = models.ForeignKey(District, null=True)
	sector = models.ForeignKey(Sector, null=True)
	cell = models.ForeignKey(Cell, null=True)
	village = models.ForeignKey(Village, null=True)
	count = models.IntegerField(default=0)
	message_type = models.IntegerField(default=1)
	staff = models.ForeignKey(User, null=True)

	class Meta:
		ordering = ['-date_time']

	def __unicode__(self):
		return 'Batch %s' % self.pk

	def generate_messages(self, limit=None):
		if self.message_type == 1:
			return self.generate_business_messages(limit=limit)
		elif self.message_type == 2:
			return self.generate_property_messages(limit=limit)

	def generate_property_messages(self, limit=None):
		if not self.message:
			message = "Citizen:{name}, EPAY:{epay}, Overdue:{overdue}, as at:{as_at}"
			self.message = message

		ownerships = Ownership.objects.filter(asset_property__isnull=False, asset_property__total_over_due__gt=0, owner_citizen__isnull=False, owner_citizen__citizen_id__regex=r'^\d{16}$').\
			select_related('asset_property', 'owner_citizen')
		if self.village:
			ownerships = ownerships.filter(asset_property__village=self.village)
		elif self.cell:
			ownerships = ownerships.filter(asset_property__village__cell=self.cell)
		elif self.sector:
			ownerships = ownerships.filter(asset_property__village__cell__sector=self.sector)
		elif self.district:
			ownerships = ownerships.filter(asset_property__village__cell__sector__district=self.district)

		if limit:
			ownerships = ownerships[:limit]

		ownerships = ownerships.order_by('asset_property__upi')
		count=ownerships.count()
		self.count = count
		self.save()

		for ownership in ownerships:
			sms = Message(message=self.message, prop=ownership.asset_property, prop_title=ownership.prop_title, citizen=ownership.owner_citizen, batch=self)
			sms.message = sms.message.replace('{name}', ownership.owner_citizen.name).\
			replace('{epay}', "B%s" % ownership.prop_title.epay).\
			replace('{overdue}', '{0:,}'.format(ownership.asset_property.over_due)).\
			replace('{upi}', '{0:,}'.format(ownership.asset_property.upi)).\
			replace('{interest}', '{0:,}'.format(ownership.asset_property.over_due_interest)).\
			replace('{penalty}', '{0:,}'.format(ownership.asset_property.over_due_penalty)).\
			replace('{total}', '{0:,}'.format(ownership.asset_property.total_over_due)).\
			replace('{as_at}', ownership.asset_property.as_at.strftime('%d %B %Y'))
			sms.phone = ownership.owner_citizen.phone_1
			sms.save()

		return count

	def generate_business_messages(self, limit=None):
		if not self.message:
			message = "Business:{name}, EPAY:{epay}, Overdue:{overdue}, as at:{as_at}"
			self.message = message

		businesses = Business.objects.filter(total_over_due__gt=0, phone1__regex=r'^07\d{8}$')
		if self.village:
			businesses = businesses.filter(village=self.village)
		elif self.cell:
			businesses = businesses.filter(village__cell=self.cell)
		elif self.sector:
			businesses = businesses.filter(village__cell__sector=self.sector)
		elif self.district:
			businesses = businesses.filter(village__cell__sector__district=self.district)

		if limit:
			businesses = businesses[:limit]

		businesses = businesses.order_by('name')

		count=businesses.count()
		self.count = count
		self.save()

		for b in businesses:
			sms = Message(message=self.message, business=b, batch=self)
			sms.message = sms.message.replace('{name}', b.name).\
			replace('{epay}', "B%s" % b.pk).\
			replace('{overdue}', '{0:,}'.format(b.over_due)).\
			replace('{interest}', '{0:,}'.format(b.over_due_interest)).\
			replace('{penalty}', '{0:,}'.format(b.over_due_penalty)).\
			replace('{total}', '{0:,}'.format(b.total_over_due)).\
			replace('{as_at}', b.as_at.strftime('%d %B %Y'))
			sms.phone = b.phone1
			sms.save()

		return count

class Message(models.Model):
	batch = models.ForeignKey(MessageBatch, related_name='batch_messages')
	business  = models.ForeignKey(Business, null=True)
	prop = models.ForeignKey(Property, null=True)
	prop_title = models.ForeignKey(PropertyTitle, null=True)
	citizen = models.ForeignKey(Citizen, null=True)
	message = models.TextField()
	sent = models.DateTimeField(null=True)
	phone = models.CharField(max_length=30, null=True, blank=True)

	class Meta:
		ordering = ['pk']

def process_payment(payment_amount, payment_date, citizen_id, business_id, sector_receipt, payer_name, bank_receipt, bank, staff_id, fees):
	fees = fees.order_by('due_date')
	fee = fees[0]
	prop_id = None
	if fee.prop:
		prop_id = fee.prop.pk
		credit = fee.prop.credit

	elif fee.business_id:
		business = get_object_or_404(Business, pk=fee.business_id)
		credit = business.credit

	if business_id:
		business = get_object_or_404(Business, pk=business_id)
		payer_name = business.name
	if citizen_id:
		citizen = get_object_or_404(Citizen, pk=citizen_id)
		payer_name = citizen.name

	active = CategoryChoice.objects.get(category__code='status', code='active')
	receipt = PaymentReceipt(amount=payment_amount, bf=credit, paid_date=payment_date, citizen_id=citizen_id, business_id=business_id, payer_name=payer_name,
		sector_receipt=sector_receipt, bank_receipt=bank_receipt, status=active, i_status='active', user_id=staff_id, bank=bank)

	receipt.save()

	bf = credit
	balance  = receipt.amount

	for fee in fees:
		pf = PayFee(citizen_id=receipt.citizen_id, business_id=receipt.business_id, fee=fee, amount=0,
		receipt_no=receipt.bank_receipt, manual_receipt=receipt.sector_receipt,
			bank=receipt.bank, paid_date=receipt.paid_date, fine_amount = 0, receipt=receipt,
			status=active, i_status='active', staff_id=receipt.user.pk)

		pf.save()
		balance = fee.pay(receipt=receipt, pay_fee=pf, payment_amount=balance, bf=bf)
		bf = 0

	receipt.credit = balance
	receipt.save()
	if prop_id:
		fee.prop.credit = balance
		fee.prop.save(update_fields=['credit'])

	elif fee.business_id:
		business.credit = balance
		business.save(update_fields=['credit'])

	return balance

class Log(models.Model):
	"""
	keep log for each action taken by user.
	"""
	transaction_id = models.IntegerField(null = True, blank = True)
	user = models.ForeignKey(PMUser, help_text="",blank = True, null=True)
	staff = models.ForeignKey(User, help_text="",blank = True, null=True, related_name="staff_logs")
	tids = models.CharField(max_length = 200, null=True, blank = True)
	tax_type = models.CharField(max_length = 50, null=True, blank = True)
	tax_id = models.CharField(max_length = 50, null=True, blank = True)
	payment_type = models.CharField(max_length = 50, null=True, blank = True)
	payment_id = models.CharField(max_length = 50, null=True, blank = True)
	media_id = models.CharField(max_length = 50, null=True, blank = True)
	username = models.CharField(max_length=10, null=True, blank=True)
	table = models.CharField(blank=True, null=True, max_length=100)
	date_time = models.DateTimeField(auto_now_add=True)
	old_data = models.CharField(blank=True, null=True, max_length=1000)
	new_data = models.CharField(blank=True, null=True, max_length=1000)
	message = models.TextField(blank=True, null=True)
	request_type = models.CharField(blank=True, null=True, max_length=1)
	fee = models.ForeignKey(Fee, null=True, blank=True)
	request_path = models.TextField(blank=True, null=True)
	request_remote	= models.TextField(blank=True, null=True)
	citizen = models.ForeignKey(Citizen, null=True, blank=True)
	business = models.ForeignKey(Business, null=True, blank=True)
	prop = models.ForeignKey(Property, db_column='property_id', null=True, blank=True)
	payfee = models.ForeignKey(PayFee, blank=True, null=True)
	receipt = models.ForeignKey(PaymentReceipt
		, blank=True, null=True)
	modified_objects = models.NullBooleanField()

	class Meta:
		db_table = 'log_log'
		app_label = 'taxplus'

	def __unicode__(self):
		return self.message or self.request_path

	@classmethod
	def log(cls, target=None, target2=None, targets=None, message=None):
		log = get_current_request_log()
		if not log:
			log = Log.objects.create()

		log.message  = message
		if target or target2:
			targets = [target, target2]
		if targets:
			for target in targets:
				if type(target) is Property:
						log.prop = target
				elif type(target) is Business:
					log.business = target
				elif type(target) is Citizen:
					log.citizen = target
		log.save()
		return log

class LogRelation(models.Model):
	content_type = models.ForeignKey(ContentType, null=True)
	object_id = models.PositiveIntegerField(null=True)
	content_object = generic.GenericForeignKey('content_type', 'object_id')
	log = models.ForeignKey(Log, related_name='log_updates')
	old_object = models.TextField(null=True)
	new_object = models.TextField(null=True)
	crud = models.PositiveIntegerField(null=True)

	class Meta:
		db_table = 'taxplus_logrelation'
		app_label = 'taxplus'

	@property
	def changes(self):
		return ", ".join([("%s: '%s' to '%s'" % (k, v[0], v[1])).replace('_',' ') for k,v in self.change_dict.items() ])

	@property
	def change_dict(self):
		"""
		return a dictionary of whats changed in the format
		{'field_name':(old_value, new_value), ...}
		"""
		try:
			old_data = json.loads(self.old_object)
		except ValueError:
			old_data = ast.literal_eval(self.old_object)

		try:
			new_data = json.loads(self.new_object)
		except ValueError:
			new_data = ast.literal_eval(self.new_object)

		changed = {}
		for k,v in new_data.items():
			changed[k] = (old_data.get(k), v)

		return changed
