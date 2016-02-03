from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from original_models import Boundary, Media
from django.contrib.gis.gdal import SpatialReference, CoordTransform
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
	category = models.CharField(max_length=30, null=True)
	behaviour = models.PositiveSmallIntegerField(default=1, choices=[(1,'Generate Fees Manually'),(2,'Automatically generate fees each period')])
	period = models.PositiveSmallIntegerField(null=True, choices=[(12,'Monthly'),(1,'Annually'),(4,'Quarterly'),(52,'Weekly')])


class ZoneBase(models.Model):
	level = models.PositiveIntegerField(null=True)
	name = models.TextField(null=True)
	boundary = models.OneToOneField(Boundary, null=True, blank=True, help_text="The boundary of district.")


class Utility:
	class Meta:
		abstract = True

	zone = models.ForeignKey(ZoneBase)
	identifier = models.TextField(null=True, max_length=30)
	#gps


class Market(Utility):
	pass


class Cemetery(Utility):
	pass


class BillBoard(Utility):
	pass


class Quarry(Utility):
	pass

class Contact(models.Model):
	first_name = models.CharField(max_length = 100, help_text="Contact name.", null=True)
	last_name = models.CharField(max_length = 100, help_text="Contact name.", null=True)
	email = models.EmailField(max_length = 100, help_text="Contact email.", null=True)
	phone = models.CharField(max_length = 100, help_text="Contact phone.", null=True)

class Account(models.Model):
	name = models.CharField(max_length=30, null=True)
	start_date = models.DateField(null=True)
	end_date = models.DateField(null=True)
	fee = models.ForeignKey(FeeRegister, null=True)
	holder_type = models.ForeignKey(ContentType, null=True)
	holder_id = models.PositiveIntegerField(null=True)
	holder = GenericForeignKey('holder_type', 'holder_id')
	utility_type = models.ForeignKey(ContentType, null=True, related_name='utility_accounts')
	utility_id = models.PositiveIntegerField(null=True)
	utility = GenericForeignKey('utility_type', 'utility_id')
	comments = models.TextField(null=True)
	contacts = models.ManyToManyField(Contact)
	media = models.ManyToManyField(Media)
