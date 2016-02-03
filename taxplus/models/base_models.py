from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from original_models import Boundary, Media, Citizen, Fee
from django.contrib.gis.gdal import SpatialReference, CoordTransform
from django.contrib.gis.db import models as gis_models
from django.contrib.auth.models import User
import copy


def transform(geometry, from_srid=3857, to_srid=4326):
	g = copy.deepcopy(geometry)
	f = SpatialReference(from_srid)
	t = SpatialReference(to_srid)
	transformer = CoordTransform(f, t)
	g.transform(transformer)
	return g

def meters_to_degrees(geometry):
	return transform(geometry, 3857, 4326)

def degress_to_meters(geometry):
	return transform(geometry, 4326, 3857)


class FeeRegister(models.Model):
	name = models.CharField(max_length=30, null=True)


class ZoneBase(models.Model):
	level = models.PositiveIntegerField(null=True)
	name = models.TextField(null=True)
	boundary = models.OneToOneField(Boundary, null=True, blank=True, help_text="The boundary of district.")


class Utility:
	class Meta:
		abstract = True

	zone = models.ForeignKey(ZoneBase)
	identifier = models.TextField(null=True, max_length=30)
	location = gis_models.PointField(srid=4326, blank=True, null= True)
	boundary = models.ForeignKey(Boundary, null=True)
	objects = gis_models.GeoManager()


class LandPlot(models.Model):
	class Meta:
		db_table = 'property_property'
		managed = False

	identifier = models.TextField(null=True, max_length=30, db_column='upi')
	boundary = models.ForeignKey(Boundary, null=True)


class Market(Utility):
	pass


class Cemetery(Utility):
	pass


class BillBoard(Utility):
	pass


class Quarry(Utility):
	pass

class BankDeposit(models.Model):
	bank = models.CharField(max_length=30)
	branch = models.CharField(max_length=30)
	amount = models.PositiveIntegerField()
	user = models.ForeignKey(User)
	date_banked = models.DateField()

class Contact(models.Model):
	first_name = models.CharField(max_length = 100, help_text="Contact name.", null=True)
	last_name = models.CharField(max_length = 100, help_text="Contact name.", null=True)
	email = models.EmailField(max_length = 100, help_text="Contact email.", null=True)
	phone = models.CharField(max_length = 100, help_text="Contact phone.", null=True)


class Account(models.Model):
	name = models.CharField(max_length=30, null=True)
	start_date = models.DateField(null=True)
	end_date = models.DateField(null=True)
	holder_type = models.ForeignKey(ContentType, null=True)
	holder_id = models.PositiveIntegerField(null=True)
	holder = GenericForeignKey('holder_type', 'holder_id')
	utility_type = models.ForeignKey(ContentType, null=True, related_name='utility_accounts')
	utility_id = models.PositiveIntegerField(null=True)
	utility = GenericForeignKey('utility_type', 'utility_id')
	comments = models.TextField(null=True)
	contacts = models.ManyToManyField(Contact)
	media = models.ManyToManyField(Media)
	principle_total = models.FloatField(default=0)
	principle_paid = models.FloatField(default=0)
	interest_total = models.FloatField(default=0)
	interest_paid = models.FloatField(default=0)
	penalty_total = models.FloatField(default=0)
	penalty_paid = models.FloatField(default=0)
	account_no = models.CharField(max_length=30, null=True)

	@property
	def principle_due(self):
		return self.principle_total - self.principle_paid

	@property
	def interest_due(self):
		return self.interest_total - self.principle_paid

	@property
	def penalty_due(self):
		return self.penalty_total - self.penalty_paid

	@property
	def total_due(self):
		return self.principle_due + self.interest_due + self.penalty_due

class AccountFee(models.Model):
	"""
	Manual fee entries for accounts, used for if `Generate Fees Manually`
	selected in fee register
	"""
	account = models.ForeignKey(Account)
	fee_type = models.ForeignKey(FeeRegister, null=True) # used to auto gen fees
	from_date = models.DateField(null=True)
	to_date = models.DateField(null=True)
	amount = models.FloatField(default=0) # total collection taken
	rate = models.FloatField(null=True) # manual entry only
	quantity = models.FloatField(null=True) # or no. collections taken, manual entry only
	user = models.ForeignKey(User)
	interest_total = models.FloatField(default=0)
	interest_paid = models.FloatField(default=0)
	penalty_total = models.FloatField(default=0)
	penalty_paid = models.FloatField(default=0)
	due_date = models.DateField(null=True) #manual entry only
	behaviour = models.PositiveSmallIntegerField(default=1, choices=[(1,'Generate Fees Manually'),(2,'Automatically generate fees each period')])
	period = models.PositiveSmallIntegerField(null=True, choices=[(12,'Monthly'),(1,'Annually'),(4,'Quarterly'),(52,'Weekly')]) # auto gen only

	@property
	def principle_due(self):
		return self.principle_total - self.principle_paid

	@property
	def interest_due(self):
		return self.interest_total - self.principle_paid

	@property
	def penalty_due(self):
		return self.penalty_total - self.penalty_paid

	@property
	def total_due(self):
		return self.principle_due + self.interest_due + self.penalty_due


class AccountPayment(models.Model):
	"""
	Represents an individual account payment, as opposed to a collection
	"""
	payment_date = models.DateField()
	account = models.ForeignKey(Account)
	deposit = models.ForeignKey(BankDeposit, related_name='deposit_acccounts')
	amount = models.FloatField(default=0)
	receipt_no = models.TextField(max_length=30, blank=True, null=True) #auto generate receipt number if None, seperate by space if collection
	user = models.ForeignKey(User)

