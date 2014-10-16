from django.db import models
from django.contrib.gis.db import models
from citizen.models import Citizen
from datetime import datetime, date
from dev1 import variables
from common.models import Status
from property.functions import getNextPlotId
from dev1 import ThreadLocal
from admin.Common import Common
from django.conf import settings
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from dateutil import parser
#from taxplus.models import Entity

class upiBreakdown(models.Model):
	province_id = models.IntegerField()
	district_id = models.IntegerField()
	sector_id = models.IntegerField()
	cell_id = models.IntegerField()
	parcel_id = models.IntegerField(blank=True, null=True)
	province = models.CharField(max_length=100)
	district = models.CharField(max_length=100)
	sector = models.CharField(max_length=100)
	cell = models.CharField(max_length=100)
	upicode = models.CharField(max_length=100)

	class Meta:
		db_table = 'dataimport_upibreakdown'

	def __unicode__(self):
		#return self.upicode
		return str(self.province_id).zfill(2)  + "/" + str(self.district_id).zfill(2)  + "/" + str(self.sector_id).zfill(2)  + "/" + str(self.cell_id).zfill(2)  + "(" +  self.province.upper() + "," + self.district.upper() + "," + self.sector.upper() + "," + self.cell.upper() + ")" + " ( " + self.upicode + " ) "


class Boundary(models.Model):
	"""
	Boundary type is official by default.
	If the boundary of a property is mannually drawed from google map, then the boundary type is set to be "manual"
	"""
	location_type = models.CharField(max_length = 20, choices = variables.location_types, default='property')
	parcel_id = models.IntegerField(help_text="Unique ID for this property.",blank=True, null=True)
	province = models.CharField(max_length = 50 ,null = True, blank = True, help_text="The name of province that associate with this boundary.")
	district = models.CharField(max_length = 50 ,null = True, blank = True, help_text="The name of district that associate with this boundary.")
	sector = models.CharField(max_length = 50 ,null = True, blank = True, help_text="The name of sector that associate with this boundary.")
	cell = models.CharField(max_length = 50 ,null = True, blank = True, help_text="The name of cell that associate with this boundary.")
	village = models.CharField(max_length = 50 ,null = True, blank = True, help_text="The village that associate with this boundary.")
	cell_code = models.CharField(max_length = 50 ,null = True, blank = True, help_text="The code of cell that associate with this boundary.")
	shape_leng = models.DecimalField(max_digits=19,decimal_places = 11,blank=True, null=True)
	shape_area = models.DecimalField(max_digits=19,decimal_places = 11,blank=True, null=True)

	polygon = models.PolygonField(srid=4326, blank=True, null= True,help_text="Mannually added boundary.")
	polygon_imported = models.PolygonField(srid=3857, blank=True, null= True,help_text="Boundary imported.")
	central_point = models.PointField(blank =True, null=True)
	type = models.CharField(max_length = 10, choices = variables.boundary_types, blank=True, null=True, default='official')
	i_status = models.CharField(max_length = 10, choices = variables.status_choices, default='active')
	objects = models.GeoManager()

	@property
	def size(self):
		return round(self.shape_area, 2)

	@property
	def hectares(self):
		if self.shape_area:
			return round(self.shape_area * 0.0001, 4)
		else: return None



class ProvinceManager(models.Manager):
	def get_query_set(self):
		user = ThreadLocal.get_current_user()
		if user:
			if user.superuser:
				return super(ProvinceManager,self).get_query_set().all()
			else:
				return super(ProvinceManager,self).get_query_set().filter(permission__in = user.getPermissions()).distinct()
		else:
			super(ProvinceManager,self).get_query_set().none()


class Province(models.Model):
	name = models.CharField(max_length=100, help_text="Province name.")
	code = models.CharField(max_length=2,null=True, blank=True, help_text="Province code.")
	boundary = models.ForeignKey(Boundary, related_name='province_boundary', null=True, blank=True, help_text="The boundary of province.")
	i_status = models.CharField(max_length = 10, choices = variables.status_choices, default='active', blank = True)

	objects = ProvinceManager()
	objectsIgnorePermission = models.Manager()

	def __unicode__(self):
		return self.name
	def getLogMessage(self,old_data=None,new_data=None,action=None):
		"""
		return tailored log message for different actions taken on this province
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


class DistrictManager(models.Manager):
	def get_query_set(self):
		user = ThreadLocal.get_current_user()
		if not user:
			return super(DistrictManager,self).get_query_set().none()
		else:
			if user.superuser:
				return super(DistrictManager,self).get_query_set().all()
			else:
				district_ids = []
				permissions = user.getPermissions()

				for permission in permissions:
					if permission.district:
						if permission.district.id not in district_ids:
							district_ids.append(permission.district.id)
					elif permission.province:
						ids_in_province = super(DistrictManager, self).get_query_set().filter(province = permission.province).values('id')
						ids_in_province = Common.get_value_list(ids_in_province, 'id')
						district_ids = district_ids + list(set(ids_in_province)-set(district_ids))
				if len(district_ids) == 0:
					return super(DistrictManager,self).get_query_set().none()
				else:
					return super(DistrictManager,self).get_query_set().filter(id__in = district_ids)


class District(models.Model):
	name = models.CharField(max_length=100, help_text="District name.")
	code = models.CharField(max_length=4, null=True, blank=True, help_text="District code.")
	boundary = models.ForeignKey(Boundary, related_name='district_boundary', null=True, blank=True, help_text="The boundary of district.")
	province = models.ForeignKey(Province, null=True, blank=True, help_text="The province this district belongs to.")
	i_status = models.CharField(max_length = 10, choices = variables.status_choices, default='active', blank = True)

	objects = DistrictManager()
	objectsIgnorePermission = models.Manager()


	def __unicode__(self):
		return self.name
	def getLogMessage(self,old_data=None,new_data=None,action=None):
		"""
		return tailored log message for different actions taken on this district
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


class Council(models.Model):
	name = models.CharField(max_length=100, help_text="Council name.")
	address = models.CharField(max_length = 200, help_text="Address of council.")
	boundary = models.ForeignKey(Boundary, null=True, blank=True, help_text="The boundary of council.")
	i_status = models.CharField(max_length = 10, choices = variables.status_choices, default='active', blank = True)
	def __unicode__(self):
		return self.name
	def getLogMessage(self,old_data=None,new_data=None,action=None):
		"""
		return tailored log message for different actions taken on this district
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


class SectorManager(models.Manager):
	def get_query_set(self):
		user = ThreadLocal.get_current_user()
		if not user:
			return super(SectorManager, self).get_query_set().none()
		else:
			if user.superuser:
				return super(SectorManager,self).get_query_set().all()
			else:
				sector_ids = []
				permissions = user.getPermissions()

				for permission in permissions:
					if permission.sector:
						if permission.sector.id not in sector_ids:
							sector_ids.append(permission.sector.id)
					elif permission.district:
						ids_in_district = super(SectorManager, self).get_query_set().filter(district = permission.district).values('id')
						ids_in_district = Common.get_value_list(ids_in_district, 'id')
						sector_ids = sector_ids + list(set(ids_in_district)-set(sector_ids))
					elif permission.province:
						ids_in_province = super(SectorManager, self).get_query_set().filter(district__province = permission.province).values('id')
						ids_in_province = Common.get_value_list(ids_in_province, 'id')
						sector_ids = sector_ids + list(set(ids_in_province)-set(sector_ids))
				if len(sector_ids) == 0:
					return super(SectorManager,self).get_query_set().none()
				else:
					return super(SectorManager,self).get_query_set().filter(id__in = sector_ids)


class Sector(models.Model):
	name = models.CharField(max_length=100, help_text="Sector name.")
	code = models.CharField(max_length=6,help_text="sector code.")
	district = models.ForeignKey(District, help_text="District the sector belongs to.")
	council = models.ForeignKey(Council, null=True, blank=True, help_text="Council the sector belongs to.")
	province = models.ForeignKey(Province, help_text="Province the sector belongs to.")
	boundary = models.ForeignKey(Boundary, related_name='sector_boundary', null=True, blank=True, help_text="The boundary of sector.")
	i_status = models.CharField(max_length = 10, choices = variables.status_choices, default='active', blank = True)
	objects = SectorManager()
	objectsIgnorePermission = models.Manager()

	class Meta:
		ordering = ['name', 'district__name']

	def getDisplayName(self):
		return self.name + ' ('+ self.district.name+')'
	def __unicode__(self):
		#return self.name + ' ('+ self.district.name+')'
		return self.name
	def getLogMessage(self,old_data=None,new_data=None,action=None):
		"""
		return tailored log message for different actions taken on this district
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


class Cell(models.Model):
	name = models.CharField(max_length=100, help_text="Cell name.")
	code = models.CharField(max_length=8,help_text="Cell code.")
	sector = models.ForeignKey(Sector, null=True, blank=True, help_text="Sector the cell belongs to.")
	boundary = models.ForeignKey(Boundary, null=True, blank=True, help_text="The boundary of Cell.", related_name='+')
	i_status = models.CharField(max_length = 10, choices = variables.status_choices, default='active', blank = True)
	class Meta:
		ordering = ['name']
	def __unicode__(self):
		return self.name


class Village(models.Model):
	name = models.CharField(max_length=100, help_text="Village name.")
	code = models.CharField(max_length=10,help_text="Village code.")
	cell = models.ForeignKey(Cell, null=True, blank=True,help_text="Cell the village belongs to.")
	boundary = models.ForeignKey(Boundary, null=True, blank=True, help_text="The boundary of Village.", related_name='+')
	i_status = models.CharField(max_length = 10, choices = variables.status_choices, default='active', blank = True)
	class Meta:
		ordering = ['name']
	def __unicode__(self):
		return self.name


class PropertyManager(models.Manager):
	def get_query_set(self):
		sectors = Sector.objects.all()
		return super(PropertyManager,self).get_query_set().filter(sector__in = sectors)


class PropertyManager1(models.Manager):
	def get_query_set(self):
		return super(PropertyManager1,self).get_query_set()

class LandUse(models.Model):
	code = models.CharField(max_length=10, null=True, blank=True, default=None)
	name = models.CharField(max_length = 50)
	fixed_asset = models.BooleanField()

	def __unicode__(self):
		return self.name


class Property(models.Model):
	plot_id = models.CharField(max_length = 50, unique = True, blank = True, help_text="Each Plot ID identifies a property.")
	is_leasing = models.BooleanField(default=False, help_text='check whether the property is leased out')
	is_land_lease = models.BooleanField(default=False, help_text='check whether the property is land lease applicable')
	land_lease_type = models.CharField(max_length = 50, blank = True, null = True)
	land_lease_approval_date = models.DateField(blank = True, null = True, help_text="")
	foreign_plot_id = models.CharField(max_length = 50, blank = True, null=True, help_text="Government official Plot ID.")
	#street_no = models.IntegerField(null = True, blank = True, help_text="The street number of property. This could be empty.")
	#street_name = models.CharField(max_length = 30 ,null = True, blank = True, help_text="The street name of property. This could be empty.")
	parcel_id = models.IntegerField(help_text="Unique ID for this property.")

	#cell = models.CharField(max_length = 50 ,null = True, blank = True, help_text="The name of cell where this property is located. This could be empty.")
	cell = models.ForeignKey(Cell, null=True, blank = True, help_text="The cell that this property resides in.")
	#cell_code = models.CharField(max_length = 50 ,null = True, blank = True, help_text="The code of cell where this property is located. This could be empty.")
	#village = models.CharField(max_length = 50 ,null = True, blank = True, help_text="The village where this property is located. This could be empty.")
	village = models.ForeignKey(Village, null=True, blank = True,help_text = "The village that this property resides in.")

	shape_leng = models.DecimalField(max_digits=19,decimal_places = 11,blank=True, null=True)
	shape_area = models.DecimalField(max_digits=19,decimal_places = 11,blank=True, null=True)
	sector = models.ForeignKey(Sector, null=True, blank=True, help_text="The sector that this property belongs to.")
	boundary = models.ForeignKey(Boundary, null=True, help_text="The boundary of property")
	region_type = models.CharField(max_length = 20, choices = variables.region_types, blank = True, null = True)

	# land use type deprecated, use land_use_types instead
	land_use_type = models.CharField(max_length = 20, choices = variables.land_use_types, blank = True, null = True)
	size_sqm = models.FloatField(blank = True, null = True)
	size_hectare = models.FloatField(blank = True, null = True)
	floor_count = models.IntegerField(blank = True, null = True)
	floor_total_square_meters = models.FloatField(blank = True, null = True)
	year_built = models.IntegerField(blank = True, null = True)

	is_tax_exempt = models.BooleanField(default=False, help_text='')
	tax_exempt_reason = models.CharField(max_length = 40, choices = variables.tax_exempt_reasons, blank = True, null = True)
	tax_exempt_note = models.CharField(max_length = 100, blank = True, null = True)

	date_created = models.DateTimeField(auto_now_add=True, blank=True)
	date_modified = models.DateTimeField(auto_now_add=True, blank=True)
	#citizens = models.ManyToManyField(Citizen, null=True, through = 'Ownership',help_text="a property could belong to multiple citizens")
	status = models.ForeignKey(Status, blank = True, null = True, help_text = 'Status')
	land_use_types = models.ManyToManyField(LandUse)
	lease_type = models.ForeignKey(LandUse, related_name='leased_property', null=True, blank=True, default=None)


	def get_sq_m(self):
		if self.size_sqm:
			return self.size_sqm
		else:
			if not self.boundary:
				return 0
			else:
				if self.boundary.polygon_imported:
					sq_m = self.boundary.polygon_imported.area
					self.size_sqm = sq_m
					self.save()
					return sq_m

	objects = PropertyManager()
	objects1 = PropertyManager1()
	objectsIgnorePermission = models.Manager()

	def save(self, *args, **kwargs):
		if self.plot_id == None or self.plot_id == '':
			if Property.objects.count() == 0:
				self.plot_id = "PM0000000001"
			else:
				last_plot_id = Property.objects1.all().order_by("-id")[0].plot_id
				plot_id_digit_part = int(last_plot_id[2:]) + 1
				plot_id_digit_part = str(plot_id_digit_part)
				zeros = ''
				for i in range(10-len(plot_id_digit_part)):
					zeros = zeros + '0'
				self.plot_id = 'PM' + zeros + plot_id_digit_part
		super(Property,self).save(*args,**kwargs)

	def __unicode__(self):
		display_str = ""
		if self.village:
			display_str = str(self.parcel_id)  + " " + self.village.name + ", "
		else:
			display_str = str(self.parcel_id)  + ", "
		if self.cell:
			display_str = display_str + self.cell.name + ", "
		if self.sector:
			display_str = display_str + self.sector.name + ',' + self.sector.district.name

		return display_str

	def getDisplayName(self):
		display_str = ""
		if self.village:
			display_str = str(self.parcel_id)  + " " + self.village.name + ", "
		else:
			display_str = str(self.parcel_id)  + ", "
		if self.cell:
			display_str = display_str + self.cell.name + ", "
		if self.sector:
			display_str = display_str + self.sector.name + ',' + self.sector.district.name
		return display_str

	def getLogMessage(self,old_data=None,new_data=None,action=None):
		"""
		return tailored log message for different actions taken on this property
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

	def getUPI(self):
		if self.cell:
			cell_code = self.cell.code
			return cell_code[1:2]+'/'+cell_code[2:4]+'/'+cell_code[4:6]+'/'+cell_code[6:8]+'/'+str(self.parcel_id)
		else:
			return ''

	def getTaxExemptProofUrl(self):
		if self.is_tax_exempt:
			proof_media = self.media_set.filter(i_status='active',file_name__startswith='Tax_Exempt_Proof').order_by('-id')[0:1]
			if proof_media:
				return '/admin/media/media/preview/' + str(proof_media[0].id) + '/'
			#settings.MEDIA_URL + 'property/' + self.id + '/Tax_Exempt_Proof.jpg'
		else:
			return None

	@property
	def declaredValues(self):
		return self.declaredvalue_set.order_by('-date_time').all()

	@property
	def currentOwners(self):
		return Citizen.objects.filter(assets__asset_property=self, assets__i_status='active')

	@property
	def declaredValue(self):
		try: return self.declaredvalue_set.order_by('-date_time').all()[0]
		except IndexError: return None

	@property
	def outstanding_taxes(self):
		taxes = []
		for tax in self.fixed_asset_taxes.filter(is_paid=False):
			taxes.append(tax)

		for tax in self.rental_income_taxes.filter(is_paid=False):
			taxes.append(tax)

		for fee in self.property_fees.filter(is_paid=False):
			taxes.append(tax)

		return taxes
