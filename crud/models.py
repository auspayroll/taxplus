from __future__ import unicode_literals
from datetime import date, timedelta
from dateutil.relativedelta import relativedelta
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
from taxplus.models import Boundary, Media, Citizen, Fee, District,\
 CategoryChoice, District, Sector, Cell, Village, Property, Rate
import copy
import json
import os
import re
from decimal import Decimal
from django.db.models import Q

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


def get_next_period(period_ending, cycle):
	if cycle in (12,4,3):
		return (date(period_ending.year, period_ending.month, 1) + relativedelta(months=1),
			date(period_ending.year, period_ending.month, 1) + relativedelta(months=2) - timedelta(days=1))
	elif cycle == 1:
		return (date(period_ending.year+1, 1, 1),
			date(period_ending.year+1, 12, 31))
	elif cycle == 52:
		return (period_ending + timedelta(days+1), period_ending + timedelta(days+8))


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
		s = "%s %s, %s" % (self.utility_type.name.capitalize(), self.identifier or self.pk, self.village or self.cell or self.sector or self.district)
		if self.village:
			s += ' village'
		elif self.cell:
			s += ' cell'
		elif self.sector:
			s+= ' sector'
		elif self.district:
			s+= ' district'
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
	overdue = models.DecimalField(max_digits=16, decimal_places=2,default=0)
	account_no = models.CharField(max_length=30, null=True)
	utilities = models.ManyToManyField(Utility)
	district = models.ForeignKey(District, null=True)
	sector = models.ForeignKey(Sector, null=True, blank=True)
	cell = models.ForeignKey(Cell, null=True, blank=True)
	village = models.ForeignKey(Village, null=True, blank=True)
	prop_title_id = models.PositiveIntegerField(null=True)
	created = models.DateTimeField(null=True, auto_now_add=True)
	modified = models.DateTimeField(null=True, auto_now=True)
	period_ending = models.DateField(null=True)
	balance =  models.DecimalField(max_digits=16, decimal_places=2, null=True) # or no. collections taken, manual entry only

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
		return self.name or self.account_no or "%s" % self.pk


	def utility_list(self):
		"""
		returns utilities as html string
		"""
		utilities  = []
		for u in self.utilities.all():
			s = '<a href="' + reverse('edit_location', args=[u.pk]) +'">%s</a> ' % u.__unicode__()
			utilities.append(s)

		return '<BR/>'.join(utilities)

	def fee_transactions(self, update=False):
		fee_list = []
		fees = self.account_fees.all()
		self.period_ending =  date.today()
		self.principle_total = self.interest_total = self.penalty_total =  Decimal(0)
		self.principle_paid = self.interest_paid = self.penalty_paid =  Decimal(0)

		for fee in fees:
			fee.interest_total = Decimal(0)
			fee.interest_paid = Decimal(0)
			fee.penalty_total = Decimal(0)
			fee.penalty_paid = Decimal(0)
			fee.principle_paid = Decimal(0)
			fee.amount = Decimal(0)
			if fee.auto:
				if fee.period == 1:
					period_end = date(self.start_date.year-1, self.start_date.month, self.start_date.day)
				elif fee.period in (12,4,3):
					period_end = self.start_date - relativedelta(months=1)
				else:
					period_end = self.start_date - timedelta(days=1)

				while period_end <= self.period_ending:
					af = copy.copy(fee)
					af.from_date, period_end = get_next_period(period_end, fee.period)
					af.to_date = af.trans_date = period_end
					af.due_date =  af.to_date + timedelta(days=(af.due_days or 5))
					af.amount, calc_string = af.calc_rate(af.to_date)
					fee.amount += Decimal(af.amount)
					self.principle_total += Decimal(af.amount)
					af.description = "%s %s<br/><span class=\"calc_string\">%s</font>" % (af.fee_type, af.to_date, calc_string)
					fee_list.append(af)

		fee_list = sorted(fee_list, key=lambda x:x.trans_date)

		return fee_list, fees


	def payment_transactions(self):
		payments = [p for p in self.account_payments.all().order_by('date_banked')]
		for payment in payments:
			payment.trans_date = payment.date_banked
			payment.description = "<span style=\"color:green\">Payment %s %s</span>" % ((payment.bank_receipt_no or payment.sector_receipt or payment.rra_receipt), payment.note)

		return payments


	def transactions(self, update=True):
		fees, fee_records = self.fee_transactions()
		fee_record_dict = dict([(f.pk, f) for f in fee_records])
		trans_list = sorted(self.payment_transactions() + fees, key=lambda x:x.trans_date)
		penalty_list = []

		self.balance = kitty = Decimal(0)
		i = 1
		for t in trans_list:
			if kitty > 0:
				#first look for overdues and pay off first
				overdue =  [f for f in fees if  f.principle_due > 0 and f.due_date < t.trans_date]
				outstanding = [f for f in fees if f.total_due > 0 and f.trans_date <= t.trans_date and f.pk not in [o.pk for o in overdue]]
				all_outstanding = overdue + outstanding
				for o in all_outstanding:
					fee_record = fee_record_dict.get(o.pk)

					# pay off principle
					if o.principle_due > 0 and kitty > 0:
						if kitty >= o.principle_due:
							o.principle_paid = o.principle_due
							kitty -= fee_record.principle_paid
						else:
							o.principle_paid = kitty
							kitty = 0
						fee_record.principle_paid += o.principle_paid
						self.principle_paid += o.principle_paid

					# pay off interest
					if o.interest_due >0 and kitty >0:
						if kitty >= o.interest_due:
							o.interest_paid = o.interest_due
							kitty -= fee_record.interest_paid
						else:
							o.interest_paid = kitty
							kitty =0
						fee_record.interest_paid += o.interest_paid
						self.interest_paid += o.interest_paid

					# pay off penalty
					if o.penalty_due >0 and kitty >0:
						if kitty >= o.penalty_due:
							o.penalty_paid = o.penalty_due
							kitty -= fee_record.penalty_paid
						else:
							o.penalty_paid = kitty
							kitty =0
						fee_record.penalty_paid += o.penalty_paid
						self.penalty_paid += o.penalty_paid


			if isinstance(t, AccountFee):
				fee_record = fee_record_dict.get(t.pk)
				self.balance += t.amount
				t.balance = self.balance
				#accrue previous fee penalties
				overdue =  sorted([f for f in fees if f.principle_due > 0 and f.due_date < t.trans_date], key=lambda x:x.due_date)
				for od in overdue:
					#calc interest
					penalties_paid_until_now = od.interest_due + od.penalty_due
					interest, penalty, calc_string = od.calc_late_fee(t.to_date)
					od_copy = copy.copy(od)
					penalties = (interest + penalty) - penalties_paid_until_now
					if penalties > 0:
						od_copy.description = "<span style=\"color:red\">Interest on %s %s<br/><span class=\"calc_string\">%s</span></span>" % (od_copy.fee_type, od_copy.to_date, calc_string)
						od_copy.trans_date = t.to_date
						od_copy.amount = penalties
						fee_record.interest_total = interest
						self.interest_total += interest
						fee_record.penalty_total += penalty
						self.penalty_total += penalty
						self.balance += penalties
						od_copy.balance = self.balance
						penalty_list.append(od_copy)


			elif isinstance(t, BankDeposit):
				t.amount = abs(t.amount) * -1
				kitty += abs(t.amount)
				self.balance += t.amount
				t.balance = self.balance

			i += 1

		if update:
			for fee_record in fee_records:
				fee_record.save()
			overdue_fees = [fee.principle_due for fee in fees if fee.principle_due > 0 and fee.due_date < self.period_ending]
			if overdue_fees:
				self.overdue = reduce(lambda x,y:x + y, overdue_fees)
			else:
				self.overdue = Decimal(0)
			self.save() # save account

		trans_list = sorted(trans_list + penalty_list, key=lambda x:x.trans_date)

		return trans_list



class AccountHolder(models.Model):
	account = models.ForeignKey(Account, related_name='holders')
	holder_type = models.ForeignKey(ContentType)
	holder_id = models.PositiveIntegerField()
	holder = GenericForeignKey('holder_type', 'holder_id')


class BankDeposit(models.Model):
	bank = models.CharField(max_length=30)
	branch = models.CharField(max_length=30, null=True, blank=True)
	amount = models.PositiveIntegerField(default=0)
	bank_receipt_no = models.CharField(max_length=50, null=True, help_text='bank deposit record amounts will be adjusted<br/> according to the receipt number entered. <br/>Make sure  the receipt number is correct. ')
	depositor_name = models.CharField(max_length=50, null=True, blank=True)
	user = models.ForeignKey(User, null=True)
	date_banked = models.DateField()
	created = models.DateTimeField(auto_now_add=True, null=True)
	rra_receipt = models.CharField(max_length=40, null=True, blank=True, verbose_name='RRA Receipt')
	account = models.ForeignKey(Account, null=True, related_name='account_payments')
	sector_receipt = models.CharField(max_length=40, null=True, blank=True, verbose_name='RRA Receipt')
	note = models.TextField(null=True, blank=True)
	old_receipt_id = models.PositiveIntegerField(null=True)


class Contact(models.Model):
	account = models.ForeignKey(Account, null=True)
	first_name = models.CharField(max_length = 100, help_text="Contact name.", null=True, blank=True)
	last_name = models.CharField(max_length = 100, help_text="Contact name.", null=True)
	email = models.EmailField(max_length = 100, help_text="Contact email.", null=True, blank=True)
	phone = models.CharField(max_length = 100, help_text="Contact phone.", null=True, blank=True)

	def __unicode__(self):
		return "%s %s" % (self.first_name, self.last_name)



def get_rate(period, category, sub_category=None, village=None, cell=None, sector=None):
	rates = Rate.objects.filter(category=category, date_from__lte=period)
	if sub_category:
		rates = rates.filter(sub_category=sub_category)
	if village:
		rates = rates.filter(Q(village=village)| Q(cell=village.cell)|Q(sector=village.cell.sector))
	elif cell:
		rates = rates.filter(village__isnull=True).filter(Q(cell=cell)| Q(sector=cell.sector))
	elif sector:
		rates = rates.filter(village__isnull=True, cell__isnull=True, sector=sector)

	rates = rates.order_by('-date_from', '-village', '-cell', '-sector')
	if rates:
		rate = rates[0]
		calc_string = "%s" % rate.amount
		if rate.village:
			calc_string += " (%s village)" % rate.village
		elif rate.cell:
			calc_string += " (%s cell)" % rate.cell
		elif rate.sector:
			calc_string += " (%s sector)" % rate.sector

		return rate.amount, calc_string
	else:
		return Decimal(0), 'No Rate Found'


class AccountFee(models.Model):
	"""
	Manual fee entries for accounts, used for if `Generate Fees Manually`
	selected in fee register
	"""
	account = models.ForeignKey(Account, related_name='account_fees')
	from_date = models.DateField(null=True)
	to_date = models.DateField(null=True)
	amount = models.DecimalField(max_digits=16, decimal_places=2, default=0) #must be static
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
	due_days = models.PositiveSmallIntegerField(default=0, null=True)
	sector = models.ForeignKey(Sector, null=True, blank=True)
	cell = models.ForeignKey(Cell, null=True, blank=True)
	village = models.ForeignKey(Village, null=True, blank=True)

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


	def calc_rate(self, period_ending):
		quantity = Decimal(1)
		if self.prop and not self.village:
			self.village = self.prop.village
			self.cell = self.prop.cell
			self.sector = self.cell.sector
			self.district = self.cell.sector.district
			self.save()

		if self.prop and not self.quantity:
			self.quantity = quantity = Decimal(str(round(self.prop.area,4)))
		elif self.quantity:
			quantity = Decimal(str(self.quantity))

		rate, calc_string = get_rate(period_ending, self.fee_type, village=self.village)
		total = Decimal(round(rate * quantity))
		calc_string += " * size: %s" % (quantity)
		if self.account.start_date > self.from_date or self.account.period_ending < self.to_date:
			if self.account.start_date > self.from_date:
				from_date = self.account.start_date
			else:
				from_date = self.from_date
			if self.account.period_ending < self.to_date:
				to_date = self.account.period_ending
			else:
				to_date = self.to_date
			part_days = (to_date - from_date).days + 1
			if part_days < 0:
				part_days = 0
			total_days = (self.to_date - self.from_date).days + 1
			day_fraction = Decimal(str(round(float(part_days)/ total_days, 4)))
			total = Decimal(str(round(day_fraction * total)))
			calc_string += "* %s (%s / %s days)" % (day_fraction, part_days, total_days)


		return (total, calc_string)


	def calc_late_fee(self, pay_date=None):
		interest =  0
		penalty = 0
		calc_string = ''

		if self.fee_type.code in ('land_lease', 'cleaning', 'market'):

			if self.to_date <= date(2012,12,31) and self.fee_type.code == 'land_lease':
				years_late = pay_date.year - self.due_date.year
				interest = round(years_late * 0.08 * float(self.principle_due))
				calc_string = "interest %s (0.08 * %s years * %s)" % ('{0:,}'.format(interest), years_late, '{0:,}'.format(self.principle_due))
				penalty = 0

			elif pay_date > self.due_date and self.principle_due > 0:
				penalty_limit = 10000
				months_late = (pay_date.year - self.due_date.year ) * 12 + (pay_date.month - self.due_date.month) + 1
				interest = round(0.015 * float(self.principle_due) * months_late)
				calc_string = "interest %s (0.015 * %s months * %s)" % ('{0:,}'.format(interest), months_late, '{0:,}'.format(self.principle_due))
				if not self.penalty_total:
					penalty = round(0.1 * float(self.principle_due))
					if penalty > penalty_limit:
						penalty = penalty_limit
					self.penalty_total = Decimal(str(penalty))
					calc_string += " +penalty %s (0.1 * %s)" % ('{0:,}'.format(penalty), '{0:,}'.format(self.principle_due))

		return Decimal(str(interest)), Decimal(str(penalty)), calc_string


	def __unicode__(self):
		return "%s for period %s" % (self.fee_type, self.to_date)





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
	prop = models.ForeignKey(Property, null=True, related_name="property_media")
	created_on = models.DateField(auto_now_add=True)
	title = models.TextField(null=True, blank=True)
	size = models.PositiveIntegerField(null=True, blank=True)
	user = models.ForeignKey(User, null=True, blank=True)
	file_type = models.TextField(max_length=4, null=True, blank=True)
	item = models.FileField(upload_to='uploads', null=True)
	record_type = models.ForeignKey(ContentType,null=True)
	record_id = models.PositiveIntegerField(null=True)
	record = GenericForeignKey('record_type', 'record_id')
	old_media_id = models.PositiveIntegerField(null=True)

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


