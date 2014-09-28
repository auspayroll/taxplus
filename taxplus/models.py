from django.db import models
from django.contrib.gis.db import models as gis_models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date
from decimal import Decimal


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
	amount = models.DecimalField(max_digits=8, decimal_places=0)

	class Meta:
		db_table = 'asset_businesscategory'


class BusinessCategory(models.Model):
	name = models.CharField(max_length=100)
	cleaning_category = models.ForeignKey(CleaningCategory)

	class Meta:
		db_table = 'asset_businesssubcategory'


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

	class Meta:
		db_table = 'citizen_citizen'



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
	credit = models.FloatField(default = 0, help_text = 'Credit accumulated for this business.')
	accountant_name = models.CharField(max_length = 150, blank = True, null = True)
	accountant_phone = models.CharField(max_length = 50, blank = True, null = True)
	accountant_email = models.CharField(max_length = 50, blank = True, null = True)
	cp_password = models.CharField(max_length=128, help_text='Enter password.', blank = True, null = True)
	market_fee_applicable = models.BooleanField(help_text="Whether business is VAT registered.")
	i_status = models.CharField(max_length = 10, default='active', blank = True, verbose_name='Status')
	date_created = models.DateTimeField(help_text='Date this record is saved',auto_now_add=True)
	closed_date = models.DateField(blank=True, null=True)
	business_category_id = models.IntegerField(null=True) #models.ForeignKey(BusinessCategory, null=True, blank=True)
	business_subcategory_id = models.IntegerField(null=True) #models.ForeignKey(BusinessSubCategory, null=True, blank=True)

	class Meta:
		db_table = 'asset_business'

	@property
	def primary_owner(self):
		owners = self.owners.order_by('-stake')
		if owners:
			return owners[0]
		else:
			return None


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

	class Meta:
		db_table = 'asset_subbusiness'


class Entity(models.Model):
	entity_type = models.ForeignKey(CategoryChoice, related_name="entity_type", limit_choices_to={'category__code':'entity_type'})
	parent = models.ForeignKey('self', related_name='branches', null=True)
	owners = models.ManyToManyField('self', through='BusinessOwnership', symmetrical=False)
	sector = models.ForeignKey(Sector, null=True, blank=True)
	cell = models.ForeignKey(Cell, null=True, blank=True)
	village = models.ForeignKey(Village, null=True, blank=True)
	status = models.ForeignKey(CategoryChoice, limit_choices_to={'category__code':'status'})
	business = models.OneToOneField(Business, null=True)
	citizen = models.OneToOneField(Citizen, null=True)
	subbusiness = models.OneToOneField(SubBusiness, null=True)

	@property
	def primary_owner(self):
		owners = self.owners.order_by('-stake')
		if owners:
			return owners[0]
		else:
			return None


	@property
	def name(self):
		if self.entity_type.code == 'business':
			return self.business.name

		elif self.entity_type.code == 'citizen':
			return "%s  %s" % (self.citizen.first_name, self.citizen.last_name)

		elif self.entity_type.code == 'subsiduary':
			return self.subbusiness.branch


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
	owners = models.ManyToManyField(Entity, through='PropertyOwnership', related_name='properties')

	class Meta:
		db_table = 'property_property'


	def get_owners_on(self, date):
		return self.owners.filter(ownership__date_from__lte=date).filter( Q(ownership__date_to__gte=date) | Q(ownership__date_to__isnull=True)).order_by('-ownership__stake')


	def get_owners_between(self, date_from, date_to):
		return self.owners.filter(Q(ownership__date_from__lte=date_to) | Q(ownership__date_from__isnull=True)).filter(Q(ownership__date_to__gte=date_from) | Q(ownership__date_to__isnull=True)).order_by('-ownership__stake')

	@property
	def current_owners(self):
		return self.get_owners_on(date.today())


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
			return self.boundary.area

		else:
			return None


class PropertyTitle(models.Model):
	prop = models.ForeignKey(Property)
	date_from = models.DateField(null=True, blank=True)
	date_to = models.DateField(null=True, blank=True)
	status = models.ForeignKey(CategoryChoice, related_name='property_title_status', )


class Fee(models.Model):
	# new  field
	category = models.ForeignKey(CategoryChoice, limit_choices_to={'category__code':'fee_type'}, related_name='fee_type', null=True)
	status = models.ForeignKey(CategoryChoice, limit_choices_to={'category__code':'status'}, related_name='fee_status', null=True)
	fee_type = models.CharField(max_length=50)
	amount = models.DecimalField(max_digits = 20, decimal_places = 2, help_text="The amount of fee item.")
	remaining_amount = models.DecimalField(max_digits = 20, decimal_places = 2, help_text="The remaining amount (subtracted past payments).", null=True, blank = True)
	date_from = models.DateField(null=True)
	date_to = models.DateField(null=True)
	due_date = models.DateField(help_text="The date this fee item is due.", null=True, blank=True)
	is_paid = models.BooleanField(help_text="Whether fee is payed.")
	submit_date = models.DateTimeField(help_text="The date this fee item is submited.", null=True, blank=True)
	submit_details = models.CharField(max_length=500, null=True, blank=True)
	date_time = models.DateTimeField(help_text="The date this fee item is generated.",auto_now_add=True, auto_now=True)
	business_id = models.IntegerField(null=True)
	citizen_id = models.IntegerField(null=True)
	subbusiness_id = models.IntegerField(null=True)
	prop_title = models.ForeignKey(PropertyTitle, null=True)
	addressee_name = models.CharField(null=True, max_length=100)
	#business = models.ForeignKey(Business, null=True, blank=True)
	#subbusiness = models.ForeignKey(SubBusiness,null=True, blank=True)
	prop = models.ForeignKey(Property, null=True, blank=True, related_name='property_fees', db_column='property_id')
	#citizen = models.ForeignKey(Citizen,null=True,blank=True)
	#qty = models.DecimalField(max_digits=10, decimal_places=2)
	#rate = models.DecimalField(max_digits=6, decimal_places=2)

	class Meta:
		db_table = 'jtax_fee'

	@property
	def addressee(self):
		if self.entity_id:
			return self.entity
		else:
			return self.addressee_name or None

	@property
	def property_owners(self):
		if self.prop_id:
			return self.prop.get_owners_between(self.date_from, self.date_to)
		else:
			return None

	def calc_amount(self):
		"""
		calculate the full amount of the fee owing based on fields
		"""
		if self.category.code == 'land_lease':
			if self.prop.land_zone.code == 'Agricultural':
				if self.prop.area >= 20000:
					return 4000
				else: 
					return 0

			elif self.date_from >= date(1998,2,1) and self.date_to <= date(2001,12,31):
				if self.prop.land_zone.code == 'residential':
					return Decimal('80')
				elif self.prop.land_zone.code == 'commercial':
					return Decimal('100')

			elif self.date_from >= date(2002,1,1) and self.date_to <= date(2002,12,31) and self.prop.land_zone.code == 'Residential':
				if self.prop.land_zone.code == 'residential':
					return Decimal('150')
				elif self.prop.land_zone.code == 'commercial':
					return Decimal('200')

			elif self.date_from >= date(2003,1,1) and self.date_to <= date(2011,12,31) and self.prop.land_zone.code == 'Residential':
				if self.prop.land_zone.code == 'residential':
					return Decimal('80')
				elif self.prop.land_zone.code == 'commercial':
					return Decimal('150')

			else:
				rate = Rate.objects.get(date_from__lte=self.date_from, date_to__gte=self.date_to, category__code='land_lease', sub_category=self.prop.land_zone, village=self.prop.village)
				return rate.amount

		raise NotImplentedError('rate for %s not found' % self)


		@property
		def amount_owed(self):
			"""
			-check period of ownership and adjust the amount if less than full period.
			-then subtract the remaining amount
			"""
			raise NotImplentedError



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
	paid_date = models.DateField(null=True)
	citizen_id = models.IntegerField(blank = True, null=True)
	business_id = models.IntegerField(help_text="The business who pay this tax item.", blank = True, null=True)
	#subbusiness_id = models.IntegerField(null=True)
	user_id = models.IntegerField(null=True)
	i_status = models.CharField(max_length = 10, default='active', blank = True)
	payer_name = models.CharField(max_length=100, blank = True, null=True)
	status = models.ForeignKey(CategoryChoice, related_name="paymentreceipt_status", null=True)
	payer = models.ForeignKey(Entity, related_name="payments", null=True)

	class Meta:
		db_table = 'jtax_multipayreceipt'


class PayFee(models.Model):
	citizen_id = models.IntegerField(blank = True, null=True)
	business_id = models.IntegerField(help_text="The business who pay this tax item.", blank = True, null=True)
	staff_id  = models.IntegerField(help_text="",blank = True, null=True)
	fee = models.ForeignKey(Fee, help_text="", related_name="fee_payments")
	amount = models.DecimalField(max_digits = 20, decimal_places = 2)
	receipt_no = models.CharField(max_length = 50)
	receipts = models.ManyToManyField(PaymentReceipt, through='MultipayReceiptPaymentRelation', related_name='line_items')
	bank =  models.CharField(max_length = 100, null=True, blank=True)
	paid_date = models.DateField()
	fine_amount = models.DecimalField(max_digits = 20, decimal_places = 2, default=0,null=True, blank = True)
	fine_description = models.TextField(null=True, blank = True)
	manual_receipt = models.CharField(max_length = 50)
	date_time = models.DateTimeField(help_text="The date when this payment is entered into the system.",auto_now_add=True,auto_now=True)
	note = models.TextField(null=True, blank = True, help_text="note about this payment.")
	receipt = models.ForeignKey(PaymentReceipt, related_name="fee_receipts", null=True)
	status = models.ForeignKey(CategoryChoice, related_name="paymentfee_status", null=True)
	i_status = models.CharField(max_length = 10, blank = True)

	class Meta:
		db_table = 'jtax_payfee'


# Model for Receipt of Multiple Tax/Fee payment
class MultipayReceiptPaymentRelation(models.Model):
	payfee = models.ForeignKey(PayFee, related_name="receipt_relations")
	receipt = models.ForeignKey(PaymentReceipt, related_name="payment_relations")

	class Meta:
		db_table ="jtax_multipayreceiptpaymentrelation"



class Ownership(models.Model):
	#owner_type = models.CharField(max_length=20,choices = variables.owner_types, help_text='Owner Types')
	#owner_id = models.IntegerField(help_text='Owner ID')
	#asset_type = models.CharField(max_length=20,choices = variables.asset_types, help_text='Asset Types') 
	#asset_id =  models.IntegerField(help_text='Asset ID')
	
	owner_citizen = models.ForeignKey(Citizen,null=True,blank=True, related_name="assets")
	owner_business = models.ForeignKey(Business,null=True,blank=True, related_name="assets")
	owner_subbusiness = models.ForeignKey(SubBusiness,null=True,blank=True, related_name="assets")
	
	asset_business = models.ForeignKey(Business,null=True,blank=True, related_name="related_name1")
	asset_subbusiness = models.ForeignKey(SubBusiness,null=True,blank=True, related_name="related_name2")
	asset_property = models.ForeignKey(Property,null=True,blank=True, related_name="related_name3")

	share = models.FloatField(help_text="Owner's share of the asset")

	date_started = models.DateField(help_text='Date this ownership started')
	date_ended = models.DateField(help_text='Date this ownership ended', null=True, blank = True)
	
	i_status = models.CharField(max_length = 10, default='active', blank = True, null=True)
	date_created = models.DateTimeField(help_text='Date this record is saved',auto_now_add=True)


	class Meta:
		db_table = 'asset_ownership'


class PropertyOwnership(models.Model):
	owner = models.ForeignKey(Entity, related_name='ownership')
	prop = models.ForeignKey(Property, related_name='property_ownership')
	prop_title = models.ForeignKey(PropertyTitle, null=True)
	date_from = models.DateField(null=True, blank=True)
	date_to = models.DateField(null=True, blank=True)
	status = models.ForeignKey(CategoryChoice, related_name='property_ownership_status', )
	stake = models.FloatField(null=True, blank=True)
	primary = models.NullBooleanField(blank=True)
	legacy = models.ForeignKey(Ownership, null=True)


class BusinessOwnership(models.Model):
	owner = models.ForeignKey(Entity, related_name='entity_businessownership')
	business = models.ForeignKey(Entity, related_name='business_businessownership')
	date_from = models.DateField(null=True, blank=True)
	date_to = models.DateField(null=True, blank=True)
	status = models.ForeignKey(CategoryChoice, related_name='business_ownership_status', )
	stake = models.FloatField(null=True, blank=True)
	primary = models.NullBooleanField(blank=True)
	legacy = models.ForeignKey(Ownership, null=True)



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
	user_id = models.IntegerField(null=True, blank=True)
	citizen_id = models.IntegerField(null=True, blank=True)
	property = models.ForeignKey(Property, null=True, blank=True)
	business_id = models.IntegerField(null = True, blank = True)
	subbusiness = models.IntegerField(null=True, blank=True)
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
	pay_receipt = models.ForeignKey(PaymentReceipt, null=True, blank=True)

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















