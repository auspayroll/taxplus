from __future__ import unicode_literals
from datetime import date
from django.contrib.auth.models import User
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.gdal import SpatialReference, CoordTransform
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.db import models
from django.db.models import Sum
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from taxplus.models import Boundary, Media, Citizen, Fee, District, CategoryChoice, District, Sector, Cell, Village, Property
import copy
import os
import re
import json

def validate_upi(upi):
	if not re.match(r'(0?\d+/){4}0?\d*$',upi):
		raise ValidationError('Invalid UPI Format')
	province, district, sector, cell, parcel = upi.split('/')
	cell_code = "%02d" % int(province) + "%02d" % int(district) + "%02d" % int(sector) + "%02d" % int(cell)
	try:
		Cell.objects.get(code=cell_code)
	except Cell.DoesNotExist:
		raise ValidationError('Cell code %s not found' % cell_code)

	return upi

def get_fee_objects():
	return [ct.model_class() for ct in ContentType.objects.all() if ct.model_class() and issubclass(ct.model_class(),AccountFee)]


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


class Utility(models.Model):
	identifier = models.CharField(null=True, max_length=90)
	upi = models.CharField(null=True, max_length=30, validators=[validate_upi],help_text="eg. 1/03/10/01/655", verbose_name="UPI", blank=True)
	location = gis_models.PointField(srid=4326, blank=True, null= True)
	utility_type = models.ForeignKey(CategoryChoice)
	district = models.ForeignKey(District, null=True)
	sector = models.ForeignKey(Sector, null=True, blank=True)
	cell = models.ForeignKey(Cell, null=True, blank=True)
	village = models.ForeignKey(Village, null=True, blank=True)
	objects = gis_models.GeoManager()

	class Meta:
		unique_together = ('identifier', 'utility_type')
		unique_together = ('identifier', 'upi')

	def __unicode__(self):
		s = "<Location: %s:%s>" % (self.utility_type.name.capitalize(), self.identifier or self.pk)
		if self.upi:
			s = "%s %s" % (s, self.upi)

		if self.village:
			s = "%s, %s village" % (s, self.village)

		elif self.sector:
			s = "%s, %s sector" % (s, self.sector)

		return s




class LandPlot(models.Model):
	class Meta:
		db_table = 'property_property'
		managed = False

	identifier = models.TextField(null=True, max_length=30, db_column='upi')
	boundary = models.ForeignKey(Boundary, null=True)


class Account(models.Model):
	name = models.CharField(max_length=90, null=True)
	start_date = models.DateField(null=True)
	end_date = models.DateField(null=True)
	comments = models.TextField(null=True)
	principle_total = models.DecimalField(max_digits=16, decimal_places=2, default=0)
	principle_paid = models.DecimalField(max_digits=16, decimal_places=2,default=0)
	interest_total = models.DecimalField(max_digits=16, decimal_places=2,default=0)
	interest_paid = models.DecimalField(max_digits=16, decimal_places=2,default=0)
	penalty_total = models.DecimalField(max_digits=16, decimal_places=2,default=0)
	penalty_paid = models.DecimalField(max_digits=16, decimal_places=2,default=0)
	account_no = models.CharField(max_length=30, null=True)
	utilities = models.ManyToManyField(Utility)
	district = models.ForeignKey(District, null=True)
	sector = models.ForeignKey(Sector, null=True, blank=True)
	cell = models.ForeignKey(Cell, null=True, blank=True)
	village = models.ForeignKey(Village, null=True, blank=True)

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

	def __unicode__(self):
		return self.name or self.account_no or self.pk


	def utility_list(self):
		"""
		returns utilities as html string
		"""
		utilities  = []
		for u in self.utilities.all():
			s = ''
			if u.village:
				s += ' <a href="'+ reverse('village', args=[u.village.pk]) +'">%s village</a> ' % u.village
			elif u.cell:
				s += ' <a href="'+ reverse('cell', args=[u.cell.pk]) +'">%s cell</a> ' % u.cell
			elif u.sector:
				s += ' <a href="'+ reverse('sector', args=[u.sector.pk]) +'">%s sector</a> ' % u.sector
			elif u.district:
				s += ' <a href="'+ reverse('district', args=[u.district.pk]) +'">%s sector</a> ' % u.district

			s += '| <a href="' + reverse('edit_location', args=[u.pk]) +'">%s</a> ' % u.__unicode__()
			utilities.append(s)

		return '<BR/>'.join(utilities)



class AccountHolder(models.Model):
	account = models.ForeignKey(Account, related_name='holders')
	holder_type = models.ForeignKey(ContentType)
	holder_id = models.PositiveIntegerField()
	holder = GenericForeignKey('holder_type', 'holder_id')


class BankDeposit(models.Model):
	bank = models.CharField(max_length=30)
	branch = models.CharField(max_length=30, null=True, blank=True)
	amount = models.PositiveIntegerField(default=0)
	bank_receipt_no = models.CharField(max_length=30, null=True, help_text='bank deposit record amounts will be adjusted<br/> according to the receipt number entered. <br/>Make sure  the receipt number is correct. ')
	depositor_name = models.CharField(max_length=50, null=True, blank=True)
	user = models.ForeignKey(User, null=True)
	date_banked = models.DateField()
	created = models.DateTimeField(auto_now_add=True, null=True)
	rra_receipt = models.CharField(max_length=40, null=True, blank=True, verbose_name='RRA Receipt')
	account = models.ForeignKey(Account, null=True)
	sector_receipt = models.CharField(max_length=40, null=True, blank=True, verbose_name='RRA Receipt')
	note = models.TextField(null=True, blank=True)


class Contact(models.Model):
	account = models.ForeignKey(Account, null=True)
	first_name = models.CharField(max_length = 100, help_text="Contact name.", null=True, blank=True)
	last_name = models.CharField(max_length = 100, help_text="Contact name.", null=True)
	email = models.EmailField(max_length = 100, help_text="Contact email.", null=True, blank=True)
	phone = models.CharField(max_length = 100, help_text="Contact phone.", null=True, blank=True)

	def __unicode__(self):
		return "%s %s" % (self.first_name, self.last_name)


class AccountFee(models.Model):
	"""
	Manual fee entries for accounts, used for if `Generate Fees Manually`
	selected in fee register
	"""
	account = models.ForeignKey(Account, related_name='account_fees')
	from_date = models.DateField(null=True)
	to_date = models.DateField(null=True)
	amount = models.DecimalField(max_digits=16, decimal_places=2, default=0) # total collection taken
	principle_paid = models.DecimalField(max_digits=16, decimal_places=2,default=0)
	rate = models.DecimalField(max_digits=14, decimal_places=4, null=True) # manual entry only
	quantity = models.DecimalField(max_digits=18, decimal_places=4, null=True) # or no. collections taken, manual entry only
	user = models.ForeignKey(User, null=True)
	interest_total = models.DecimalField(max_digits=16, decimal_places=2, default=0)
	interest_paid = models.DecimalField(max_digits=16, decimal_places=2,default=0)
	penalty_total = models.DecimalField(max_digits=16, decimal_places=2,default=0)
	penalty_paid = models.DecimalField(max_digits=16, decimal_places=2,default=0)
	due_date = models.DateField(null=True) #manual entry only
	auto = models.BooleanField(default=False)
	period = models.PositiveSmallIntegerField(null=True, default=0,
		choices=[(0,'Once only'), (12,'Monthly'),(1,'Annually'),(4,'Quarterly'),(52,'Weekly')]) # auto gen only
	fee_type = models.ForeignKey(CategoryChoice, null=True, limit_choices_to={'category__code':'fee_type'})
	is_paid = models.BooleanField(default=False)
	utility = models.ForeignKey(Utility, null=True, blank=False)
	prop = models.ForeignKey(Property, null=True, blank=False)

	@property
	def principle_due(self):
		return self.amount - self.principle_paid

	@property
	def interest_due(self):
		return self.interest_total - self.interest_paid

	@property
	def penalty_due(self):
		return self.penalty_total - self.penalty_paid

	@property
	def total_due(self):
		return self.principle_due + self.interest_due + self.penalty_due

	@property
	def fee_object(self):
		if self.category.code:
			return get_fee_objects()[[ft.lower for ft in get_fee_objects()].index(self.category.code.replace('_').lower())]
		else: return self



class MarketFee(AccountFee):
	class Meta:
		verbose_name = 'Market Fee'
		proxy = True

class LandLeaseFee(AccountFee):
	class Meta:
		verbose_name = 'Land Lease Fee'
		proxy = True

class QuarryFee(AccountFee):
	class Meta:
		verbose_name = 'Quarry Fee'
		proxy = True

class CleaningFee(AccountFee):
	class Meta:
		verbose_name = 'Cleaning Fee'
		proxy = True

class TowerFee(AccountFee):
	class Meta:
		verbose_name = 'Phone Tower Fee'
		proxy = True

class CemeteryFee(AccountFee):
	class Meta:
		verbose_name = 'Cemetery Fee'
		proxy = True


class Collection(models.Model):
	"""
	Represents a fee collection
	"""
	date_from = models.DateField(null=True)
	date_to = models.DateField()
	account = models.ForeignKey(Account, null=True)
	deposit = models.ForeignKey(BankDeposit, related_name='deposit_collections', null=True)
	amount = models.DecimalField(max_digits=16, decimal_places=2, default=0)
	fee_type = models.ForeignKey(CategoryChoice, null=True, limit_choices_to={'category__code':'fee_type'})
	no_collections = models.PositiveIntegerField(default=1)
	receipt_no = models.TextField(blank=True, null=True, help_text="seperate multiple receipts with commas") #auto generate receipt number if None, seperate by space if collection
	user = models.ForeignKey(User)
	collector = models.ForeignKey(User, related_name="user_collections", null=True, blank=True) # limit_choices_to={'groups__name':'Collector'}
	created = models.DateTimeField(auto_now_add=True, null=True)
	utility = models.ForeignKey(Utility, null=True, verbose_name='Location')

	def save(self, *args, **kwargs):
		if self.utility:
			self.district = self.utility.district
			self.sector =  self.utility.sector
			self.cell = self.utility.cell
			self.village = self.utility.village

		return super(Collection, self).save(*args, **kwargs)

	def __unicode__(self):
		s =  "<Collection:%s on %s>" % (self.fee_type, self.date_to)
		if self.utility:
			s = "%s for %s" % (s, self.utility)
		return s

@receiver(post_save, sender=Collection)
def update_bank_deposit(sender, instance, *args, **kwargs):
   	if instance.deposit:
		instance.deposit.amount = instance.deposit.deposit_collections.all().aggregate(total=Sum('amount'))['total'] or 0
		instance.deposit.save()


class AccountPayment(models.Model):
	"""
	Represents an individual account payment, as opposed to a collection
	"""
	payment_date = models.DateField()
	account = models.ForeignKey(Account)
	deposit = models.ForeignKey(BankDeposit, related_name='deposit_acccounts', null=True)
	amount = models.DecimalField(max_digits=16, decimal_places=2, default=0)
	receipt_no = models.TextField(max_length=30, blank=True, null=True, help_text="seperate multiple receipts with commas") #auto generate receipt number if None, seperate by space if collection
	user = models.ForeignKey(User)
	created = models.DateTimeField(null=True, auto_now_add=True)

class Media(models.Model):
	account = models.ForeignKey(Account, null=True)
	created_on = models.DateField(auto_now_add=True)
	title = models.TextField(max_length=30, null=True, blank=True)
	size = models.PositiveIntegerField(null=True, blank=True)
	user = models.ForeignKey(User, null=True, blank=True)
	file_type = models.TextField(max_length=4, null=True, blank=True)
	item = models.FileField(upload_to='uploads', null=True)
	record_type = models.ForeignKey(ContentType,null=True)
	record_id = models.PositiveIntegerField(null=True)
	record = GenericForeignKey('record_type', 'record_id')

	@property
	def extension(self):
		name, extension = os.path.splitext(self.item.name)
		return extension

	def save(self, *args, **kwargs):
		if not self.title:
			self.title = self.item.name
		return super(Media, self).save(*args, **kwargs)


class AccountNote(models.Model):
	account = models.ForeignKey(Account)
	text = models.TextField()
	user = models.ForeignKey(User, null=True, blank=True)
	created_on = models.DateField(auto_now_add=True)


def user_photo_path(instance, filename):
	_, extension = os.path.splitext(filename)
	return "users/user_%s%s" % (instance.user.username.replace('.','_'), extension)


class Profile(models.Model):
	user = models.OneToOneField(User, related_name='profile')
	registration_no = models.CharField(max_length=40)
	phone = models.CharField(max_length=40)
	photo = models.ImageField(upload_to=user_photo_path, null=True)

	def __unicode__(self):
		return '<Profile: %s>' % self.user.__unicode__()


class Log(models.Model):
	account = models.ForeignKey(Account, null=True)
	instance_type = models.ForeignKey(ContentType,null=True)
	instance_id = models.PositiveIntegerField(null=True)
	instance = GenericForeignKey('instance_type', 'instance_id')
	user = models.ForeignKey(User, null=True)
	created = models.DateTimeField(null=True, auto_now_add=True)
	changes = models.TextField(null=True)
	request_path = models.TextField(null=True)
	request_ip = models.CharField(max_length=40, null=True)

	@property
	def changes_as_html(self):
		if self.changes:
			try:
				change_dict = json.loads(self.changes)
			except:
				return self.changes
			else:
				html = ''
				for k,v in change_dict.items():
					html += '<div><strong>%s</strong>: %s &#8594; %s</div>' % (k, v[0], v[1])
				return html
		return '-'


