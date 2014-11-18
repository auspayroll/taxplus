from django.db import models
from django.contrib.gis.db import models as gis_models
from django.db.models import Q
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date, datetime
from decimal import Decimal
from django.db.models import Sum

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



class Setting(models.Model):
	tax_fee_name = models.CharField(max_length = 50, help_text="Tax / Fee Name")
	setting_name = models.CharField(max_length = 50, help_text="Tax / Fee Setting Name")
	sub_type = models.CharField(max_length = 250, blank = True, help_text="Tax / Fee Setting Sub Catergories that differentiate the rate / fee")
	value = models.CharField(max_length = 50, default='',help_text="Setting Value, can be fee/tax rate/date/etc")
	description = models.TextField(null=True, blank = True, help_text="Description about this payment.")
	valid_from = models.DateField(help_text='Date this setting to be valid from.')
	valid_to = models.DateField(help_text='Date this setting get deprecated.', null=True, blank = True)
	district = models.ForeignKey(District, null=True, blank=True, help_text="")
	sector = models.ForeignKey(Sector, null=True, blank=True, help_text="")
	cell = models.ForeignKey(Cell, null=True, blank=True, help_text="")
	village = models.ForeignKey(Village, null=True, blank=True, help_text="")
	i_status = models.CharField(max_length = 10, default='active', blank = True)
	date_time = models.DateTimeField(help_text="The date when this setting is entered into the system.",auto_now_add=True,auto_now=True)

	class Meta:
		app_label = 'taxplus'
		db_table = 'jtax_setting'
		managed = False

	def __unicode__(self):
		return "ID:" + str(self.id) + " - " + str(self.tax_fee_name) + " " + str(self.setting_name) + " - " + str(self.sub_type) + "[ " + str(self.value) + " ] (" + self.i_status + ")"



	@classmethod
	def calculateLandLeaseFee(cls, date_from, date_to, land_use_type, size, sector=None, cell=None, village=None, *args, **kwargs):
		if type(date_from) is datetime:
			date_from = date_from.astimezone(timezone.get_default_timezone()).date()

		if type(date_to) is datetime:
			date_to = date_to.astimezone(timezone.get_default_timezone()).date()

		size = Decimal(size).quantize(Decimal('.0001'))
		land_use_types = None
		if land_use_type in ('Agricultural', 'agricultural', 'agriculture'):
			land_use_type = 'Agricultural'
			units = 'hectares'
			hectares = (size * Decimal('0.0001')).quantize(Decimal('.0001'))
			if hectares > 35:
				land_use_types = 'Agricultural(>35 ha)'

			elif hectares >= 2 and hectares <= 35:
			   land_use_types = 'Agricultural(2-35 ha)'

			elif hectares > 2:
				land_use_types = ('Agricultural(>2 ha)', 'Agriculture (>2 hectares)')

		elif land_use_type in ('Residential', 'residential'):
			land_use_types = ('Residential', 'Urban Area')

		elif land_use_type in ('Commericial','Commercial', 'commercial'):
			land_use_types = ('Commercial', 'Trading Centre', 'Industries')

		elif land_use_type in ('Industrial', 'industrial'):
			land_use_types = 'Industries'

		elif land_use_type == 'Quarry Purpose':
			land_use_types = 'Quarries Exploitation'

		settings = Setting.objects.filter(valid_from__lte=date_to).filter(Q(valid_to__gte=date_from) | Q(valid_to__isnull=True)).filter(tax_fee_name='land_lease_fee', sub_type__in=land_use_types).\
			filter(Q(district=sector.district) | Q(sector=sector) | Q(cell=cell) | Q(sector=sector) | Q(village=village)).\
			order_by('-village').order_by('-cell').order_by('-sector').order_by('-district').order_by('-valid_from')

		if settings:
			return float(settings[0].value)

		else:
			print("NOT FOUND: date from: %s, date to: %s, land_use_types: %s, village: %s, cell: %s, sector: %s" % (date_from, date_to, land_use_types, village, cell, sector))
			import pdb
			pdb.set_trace()



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
			district = District.objects.get(pk=district)

		if sector and type(sector) is int:
			sector = Sector.objects.get(pk=sector)

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
			district = District.objects.get(pk=district)

		if sector and type(sector) is int:
			sector = Sector.objects.get(pk=sector)

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
	entity_id = models.IntegerField(null=True)

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
	entity_id = models.IntegerField(null=True)

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
	identifier = models.CharField(max_length=100, null=True)

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

		elif self.entity_type.code == 'individual':
			title = self.citizen
			return "%s %s" % (self.citizen.first_name, self.citizen.last_name)

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
	date_created = models.DateTimeField(auto_now_add=True, blank=True)
	date_modified = models.DateTimeField(auto_now=True, blank=True)

	class Meta:
		db_table = 'property_property'


	@property
	def outstanding_fees(self):
		return self.property_fees.filter(remaining_amount__gt=0)



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
			return self.boundary.shape_area

		else:
			return 0


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

	def __unicode__(self):
		name = "%s %s - " % (self.prop, self.date_from.strftime('%d/%m/%Y'))
		if self.date_to:
			name += self.date_to.strftime('%d/%m/%Y')
		if self.land_lease_issue_date:
			name += " land lease issue date: %s" % self.land_lease_issue_date.strftime('%d/%m/%Y')
		return name

	@property
	def owners(self):
		for ownership in self.title_ownership.all():
			yield ownership.owner.name


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
		if self.prop.is_land_lease:
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

				try:
					fee = Fee.objects.get(category__code='land_lease', date_from__lte=date_to, date_to__gte=date_from, prop=self.prop, prop_title=self)

				except Fee.DoesNotExist:
					land_lease = CategoryChoice.objects.get(category__code='fee_type', code='land_lease')
					fee = Fee.objects.create(prop_title=self, category=land_lease, date_from=date_from, date_to=date_to, \
						prop=self.prop, fee_type='land_lease', status=active, is_paid=False, submit_date=date.today(), amount=0, remaining_amount=0, due_date=date_to)
					print 'created Fee %s' % fee

				except Fee.MultipleObjectsReturned:
					import pdb
					pdb.set_trace()

				else:
					fee.date_from = date_from
					fee.date_to = date_to
					fee.prop_title = prop_title
					fee.calc_amount(save=True)

					if fee.remaining_amount > 0:
						fee.is_paid = False
					else:
						fee.is_paid = True

					if prop_title.date_to:
						fee.remaining_amount = 0

					fee.save()
				date_from = date(date_from.year+1, 1, 1)

			if self.date_to:
				Fee.objects.filter(prop_title=self, date_to__gt=self.date_to).update(prop_title=None)
			Fee.objects.filter(prop_title=self, date_from__lt=self.date_from).update(prop_title=None)


@receiver(post_save, sender=PropertyTitle)
def after_prop_title_save(sender, instance, created, **kwargs):
	instance.title_ownership.update(date_from=instance.date_from, date_to=instance.date_to)
	instance.calc_taxes()

class FeeManager(models.Manager):
	def get_query_set(self):
		return super(FeeManager,self).get_query_set().filter(status__code='active')

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
	business = models.ForeignKey(Business, null=True, related_name='business_fees')
	citizen = models.ForeignKey(Citizen, null=True, related_name='citizen_fees')
	subbusiness = models.ForeignKey(SubBusiness, null=True)
	prop_title = models.ForeignKey(PropertyTitle, null=True, related_name='title_fees')
	addressee_name = models.CharField(null=True, max_length=100)
	#business = models.ForeignKey(Business, null=True, blank=True)
	#subbusiness = models.ForeignKey(SubBusiness,null=True, blank=True)
	prop = models.ForeignKey(Property, null=True, blank=True, related_name='property_fees', db_column='property_id')
	#citizen = models.ForeignKey(Citizen,null=True,blank=True)
	qty = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	rate = models.DecimalField(max_digits=6, decimal_places=2, default=0)
	objects = FeeManager()
	all_objects = models.Manager()

	class Meta:
		db_table = 'jtax_fee'

	def __unicode__(self):
		if self.category.code == 'land_lease':
			return "Land Lease %s - %s" % (self.date_from.strftime('%d/%m/%Y'), self.date_to.strftime('%d/%m/%Y'))

		if self.category.code == 'cleaning':
			return "Cleaning Fee %s - %s" % (self.date_from.strftime('%d/%m/%Y'), self.date_to.strftime('%d/%m/%Y'))


	def get_paid_amount(self):
		paid = self.fee_payments.filter(amount__gt=0, i_status='active').aggregate(amount=Sum('amount'), fines=Sum('fine_amount'))
		total = paid['amount'] or 0
		fines = paid['fines'] or 0
		capital_amount = total - fines
		return float(capital_amount), float(fines)


	def get_remaining_amount(self):
		return (float(self.amount) - self.get_paid_amount()[0])


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

		if self.category.code == 'land_lease':
			penalty_limit = 10000
			due_date = date(self.date_to.year, 12, 31) # end of year due date
			months_late = (pay_date.year - due_date.year ) * 12 + (pay_date.month - due_date.month)
			interest = round(0.015 * float(remaining_amount) * months_late)

			if self.date_to <= date(2012,12,31):
				interest = round((pay_date.year - due_date.year) * 0.08 * float(remaining_amount))
				penalty = 0

			else:
				penalty = round(0.1 * float(remaining_amount))
			penalty = int(penalty)
			interest = int(interest)
			if penalty > penalty_limit:
				return (penalty_limit, interest)
			else:
				return (penalty, interest)

		else:
			raise NotImplentedError

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


	def calc_amount(self, save=True):
		"""
		calculate the full amount of the fee owing based on fields
		"""
		if self.category.code == 'land_lease':
			rate = 0
			if self.prop.land_zone.code == 'agricultural':
				if self.prop.area >= 20000:
					return 4000
				else:
					return 0

			if self.date_from >= date(2014,1,1) and self.date_to <= date(2014,12,31):
				rate = Setting.calculateLandLeaseFee(self.date_from, self.date_to, self.prop.land_zone.code, self.prop.area, district=self.prop.sector.district, sector=self.prop.sector, cell=self.prop.cell, village=self.prop.village)


			elif self.date_from >= date(1998,2,1) and self.date_to <= date(2001,12,31):
				if self.prop.land_zone.code == 'residential':
					rate = 80

				elif self.prop.land_zone.code == 'commercial':
					rate = 100

			elif self.date_from >= date(2002,1,1) and self.date_to <= date(2002,12,31):
				if self.prop.land_zone.code == 'residential':
					rate = 150

				elif self.prop.land_zone.code == 'commercial':
					rate = 200

			elif self.date_from >= date(2003,1,1) and self.date_to <= date(2011,12,31):
				if self.prop.land_zone.code == 'residential' and self.prop.village:
					if self.prop.village.cell.sector.district.name.lower() == 'kicukiro' and self.prop.village.cell.sector.name.lower() in ('gahanga', 'masaka'):
						rate = 30
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

			self.qty = self.prop.area or 0
			self.rate = rate or 0
			self.amount = self.qty * self.rate
			if self.remaining_amount <= 0 and amount > 0:
				self.is_paid = True
			else:
				self.is_paid = False

			#calculate part year payment
			if self.date_from.month != 1 and self.date_from.day != 1 or self.date_to.month != 12 and self.date_to.day != 31:
				self.amount = self.amount * ((self.date_to - self.date_from ).days + 1.0) / float( 1 + (date(self.date_to.year,12,31) - date(self.date_from.year,1,1)).days )

			self.amount = round(self.amount)
			capital_paid_amount = self.get_paid_amount()[0]
			self.remaining_amount = self.amount - capital_paid_amount

			if save:
				self.save(update_fields=('qty', 'rate', 'amount', 'remaining_amount'))

			return self.amount


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
	prop_title = models.ForeignKey(PropertyTitle, null=True, related_name='title_ownership')
	date_from = models.DateField(null=True, blank=True)
	date_to = models.DateField(null=True, blank=True)
	status = models.ForeignKey(CategoryChoice, related_name='property_ownership_status', )
	stake = models.FloatField(null=True, blank=True)
	primary = models.NullBooleanField(blank=True)
	legacy = models.ForeignKey(Ownership, null=True)
	created = models.DateTimeField(auto_now_add=True, auto_now=True, null=True)
	modified = models.DateTimeField(auto_now=True, null=True)


@receiver(post_save, sender=PropertyOwnership)
def after_prop_ownership_save(sender, instance, created, **kwargs):
	try:
		if instance.owner.citizen_id:
			citizen = Citizen.objects.get(pk=instance.owner.citizen_id)
			o, created = Ownership.objects.get_or_create(asset_property=instance.prop, owner_citizen=citizen, i_status=instance.status.code, defaults=dict(share=instance.stake or 0, date_started=instance.date_from, date_ended=instance.date_to))
			if not created:
				#o.share = instance.stake or 0
				o.date_started = instance.date_from
				o.date_ended = instance.date_to
				o.save()
			else:
				print 'created'

		elif instance.owner.business_id:
			business = Business.objects.get(pk=instance.owner.business_id)
			o, created = Ownership.objects.get_or_create(asset_property=instance.prop, owner_business=business, i_status=instance.status.code, defaults=dict(share=instance.stake or 0, date_started=instance.date_from, date_ended=instance.date_to))
			if not created:
				#o.share = instance.stake or 0
				o.date_started = instance.date_from
				o.date_ended = instance.date_to
				o.save()
			else:
				print 'created'

		elif instance.owner.subbusiness_id:
			business = SubBusiness.objects.get(pk=instance.owner.business_id)
			o, created = Ownership.objects.get_or_create(asset_property=instance.prop, owner_subbusiness=business, i_status=instance.status.code, defaults=dict(share=instance.stake or 0, date_started=instance.date_from, date_ended=instance.date_to))
			if not created:
				#o.share = instance.stake or 0
				o.date_started = instance.date_from
				o.date_ended = instance.date_to
				o.save()
			else:
				print 'created'

	except Ownership.MultipleObjectsReturned:
		if instance.owner.citizen_id:
			ownerships = Ownership.objects.filter(asset_property=instance.prop, owner_citizen=citizen, i_status=instance.status.code)

		elif instance.owner.business_id:
			ownerships = Ownership.objects.get_or_create(asset_property=instance.prop, owner_business=business, i_status=instance.status.code)

		elif instance.owner.subbusiness_id:
			ownerships = Ownership.objects.get_or_create(asset_property=instance.prop, owner_subbusiness=business, i_status=instance.status.code)

		o = ownerships[0]
		ownerships.exclude(pk=o.pk).update(i_status='inactive')
		#o.share = instance.stake or 0
		o.date_started = instance.date_from
		o.date_ended = instance.date_to
		o.save()




class BusinessOwnership(models.Model):
	owner = models.ForeignKey(Entity, related_name='entity_businessownership')
	business = models.ForeignKey(Entity, related_name='business_businessownership')
	date_from = models.DateField(null=True, blank=True)
	date_to = models.DateField(null=True, blank=True)
	status = models.ForeignKey(CategoryChoice, related_name='business_ownership_status', )
	stake = models.FloatField(null=True, blank=True)
	primary = models.NullBooleanField(blank=True)
	legacy = models.ForeignKey(Ownership, null=True)
	created = models.DateTimeField(auto_now_add=True, auto_now=True, null=True)
	modified = models.DateTimeField(auto_now=True, null=True)



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


class PropertyOwner(models.Model):
	owner_business = models.ForeignKey(Business,null=True,blank=True, related_name="business_propertyowners")
	owner_citizen = models.ForeignKey(Citizen,null=True,blank=True, related_name="citizen_propertyowners")
	asset_property = models.ForeignKey(Property,null=True,blank=True, related_name="property_assets")

	class Meta:
		db_table = 'asset_ownership'
		managed = False

class BusinessOwner(models.Model):
	owner_citizen = models.ForeignKey(Citizen,null=True,blank=True, related_name="citizen_businessowners")
	asset_business = models.ForeignKey(Business,null=True,blank=True, related_name="business_assets")

	class Meta:
		db_table = 'asset_ownership'
		managed = False



