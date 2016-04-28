from __future__ import unicode_literals
from datetime import date, timedelta, datetime
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
from django.db.models import Q, F

from django.core.cache import cache


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



class Business(models.Model):
	name = models.CharField(max_length=100,help_text='Business Name')
	tin = models.CharField(max_length=50, help_text='TIN RRA',null=True,  blank = True)
	date_started = models.DateField(blank = True, null=True, help_text='Date Business Started')
	address = models.CharField(max_length = 255, null = True, blank = True, help_text="Contact address")
	phone1 = models.CharField(max_length=50,help_text='')
	phone2 = models.CharField(max_length=50, blank = True,help_text='')
	email = models.CharField(max_length=50,help_text='', blank = True)
	po_box = models.TextField(help_text='Business PO Box', blank = True)
	vat_register = models.BooleanField(help_text="Whether business is VAT registered.", default=False)
	business_type = models.CharField(max_length = 50, blank = True, null = True)
	district = models.ForeignKey(District, null=True, blank=True, related_name='biz_districts')
	sector = models.ForeignKey(Sector, null=True, blank=True, related_name="biz_sectors")
	cell = models.ForeignKey(Cell, null=True, blank=True,help_text="", related_name="biz_cells")
	village = models.ForeignKey(Village, null=True, blank=True, related_name="biz_villages")
	date_created = models.DateTimeField(help_text='Date this record is saved',auto_now_add=True)
	closed_date = models.DateField(blank=True, null=True)
	#business_category = models.ForeignKey(BusinessCategory, null=True, blank=True, db_column='business_subcategory_id')
	#cleaning_category = models.ForeignKey(CleaningCategory, null=True, blank=True, db_column='business_category_id')
	business_category_id = models.IntegerField(null=True) #models.ForeignKey(BusinessCategory, null=True, blank=True)
	business_subcategory_id = models.IntegerField(null=True) #models.ForeignKey(BusinessSubCategory, null=True, blank=True)
	location = gis_models.PointField(blank =True, null=True)
	objects = gis_models.GeoManager()

	class Meta:
		db_table = 'asset_business'
		managed = False


	def __unicode__(self):
		return self.name

	@property
	def phone(self):
		return self.phone1 or self.phone2

	@property
	def identifier(self):
		return self.tin




class LandPlot(models.Model):
	class Meta:
		db_table = 'property_property'
		managed = False

	identifier = models.TextField(null=True, max_length=30, db_column='upi')
	boundary = models.ForeignKey(Boundary, null=True)


class Account(models.Model):
	name = models.CharField(max_length=150, null=True)
	start_date = models.DateField(null=True)
	end_date = models.DateField(null=True)
	comments = models.TextField(null=True)
	phone = models.CharField(max_length=50, null=True)
	email = models.EmailField(null=True)
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
	business = models.ForeignKey(Business, null=True)
	created = models.DateTimeField(null=True, auto_now_add=True)
	modified = models.DateTimeField(null=True, auto_now=True)
	period_ending = models.DateField(null=True)
	balance =  models.DecimalField(max_digits=16, decimal_places=2, default=0) # or no. collections taken, manual entry only
	tin = models.BigIntegerField(null=True)
	citizen_id = models.BigIntegerField(null=True)
	bf = models.DecimalField(max_digits=16, decimal_places=2,default=0)
	closed_off = models.DateField(null=True)
	no_payments = models.IntegerField(default=0)

	@property
	def principle_due(self):
		return self.principle_total - self.principle_paid

	@property
	def interest_due(self):
		return self.interest_total - self.interest_paid

	@property
	def penalty_due(self):
		return self.penalty_total - self.penalty_paid

	@property
	def total_due(self):
		return self.principle_due + self.interest_due + self.penalty_due

	def __unicode__(self):
		return self.name or self.account_no or "%s" % self.pk

	def update_contact_details(self):
		current_emails = [h.holder.email for h in self.holders.all()]
		current_phones = [h.holder.phone for h in self.holders.all()]
		citizen_ids = [h.holder.citizen_id for h in self.holders.all() if hasattr(h.holder, 'citizen_id')]
		tins = [h.holder.tin for h in self.holders.all() if hasattr(h.holder, 'tin')]

		if citizen_ids:
			self.citizen_id = citizen_ids[0]

		if tins:
			self.tin = tins[0]

		if current_emails:
			self.email = current_emails[0]

		if current_phones:
			self.phone = current_phones[0]

	def utility_list(self):
		"""
		returns utilities as html string
		"""
		utilities  = []
		for u in self.utilities.all():
			s = '<a href="' + reverse('edit_location', args=[u.pk]) +'">%s</a> ' % u.__unicode__()
			utilities.append(s)

		return '<BR/>'.join(utilities)

	def close_off_period(self, period_ending=None, write_off=False):
		if self.end_date:
			period_ending = self.end_date
		#fees = [f for f in self.account_fees.filter(from_date__lte=period_ending, closed__isnull=True).filter(Q(to_date__isnull=True) | Q(to_date__gte=period_ending)).order_by('-to_date')]
		fees = self.account_fees.all()

		for fee in fees:
			if not self.no_payments and write_off and fee.from_date < period_ending and (not fee.to_date or fee.to_date > period_ending):
					fee.from_date = period_ending + timedelta(days=1)
					fee.save()

			elif fee.from_date < period_ending and (not fee.to_date or fee.to_date > period_ending):
				from_date = period_ending + timedelta(days=1)
				AccountFee.objects.update_or_create(account=self, fee_type=fee.fee_type,
					from_date=from_date,
					defaults=dict(to_date=fee.to_date, amount=fee.amount,rate=fee.rate,quantity=fee.quantity,user=fee.user,
						due_days=fee.due_days, fee_subtype=fee.fee_subtype, auto=True,
					district=fee.district, sector=fee.sector, cell=fee.cell, village=fee.village, utility=fee.utility,
					period=fee.period, parcel_id=fee.parcel_id, upi=fee.upi, prop=fee.prop)
				)
				fee.to_date = period_ending
				if write_off:
					fee.closed = period_ending
				fee.save()

			elif fee.to_date and fee.to_date <= period_ending and write_off:
				fee.closed = period_ending
				fee.save()

		if write_off:
			self.closed_off = period_ending
			self.save(update_fields=['closed_off'])

		if write_off and fees:
			self.account_payments.filter(trans_date__lte=period_ending, closed__isnull=True).update(closed=period_ending)




	def fee_transactions(self, period_ending=None):
		fee_list = []
		fees = self.account_fees.select_related('fee_type', 'fee_subtype').filter(status__code='active', from_date__lte=period_ending).order_by('from_date')

		self.principle_total = self.interest_total = self.penalty_total =  0
		self.principle_paid = self.interest_paid = self.penalty_paid =  0
		for fee in fees:
			fee.interest_total = fee.interest_paid = fee.penalty_total = 0
			fee.penalty_paid = fee.principle_paid = fee.balance = fee.overdue =  0

			fee.amount = 0
			if fee.period == 1:
				period_end = fee.from_date - relativedelta(years=1)
			elif fee.period in (12,4,3):
				period_end = fee.from_date - relativedelta(months=1)
			else:
				period_end = fee.from_date - timedelta(days=1)

			while period_end < (fee.to_date or self.end_date or period_ending):
				af = copy.copy(fee)
				af.from_date, period_end = get_next_period(period_end, fee.period)
				af.to_date = period_end
				af.trans_date = af.from_date
				af.due_date =  af.to_date + timedelta(days=(af.due_days or 5))
				af.amount, calc_string = af.calc_rate()
				fee.amount += Decimal(af.amount)
				af.description = "%s<br/><span class=\"calc_string\">%s</font>" % (af, calc_string)
				fee_list.append(af)


		fee_list = sorted(fee_list, key=lambda x:x.trans_date)

		return fee_list, fees


	def payment_transactions(self, period_ending):
		payments = [p for p in self.account_payments.filter(status__code='active', trans_date__lte=period_ending)]

		for payment in payments:
			payment.description = "<span style=\"color:green\">Payment %s %s</span>" % ((payment.bank_receipt_no or payment.sector_receipt or payment.rra_receipt), payment.note or '')

		return payments


	def current_transactions(self):
		return_list = []
		self.balance = -1 * self.bf
		"""
		class BroughtForward(object):
			pass
		bf = BroughtForward()
		if self.bf and self.closed_off:
			bf.trans_date = self.closed_off + timedelta(days=1)
			bf.amount = bf.balance = self.balance
			bf.description = "Balance Brought Forward"
			bf.closed = None
			return_list.append(bf)
		"""

		transactions, fees = self.transactions()
		if self.closed_off:
			active_transactions = [t for t in transactions if t.trans_date > self.closed_off]
		else:
			active_transactions = transactions
		active_fees = [f for f in fees if not f.closed]
		return_list += active_transactions
		return return_list, active_fees


	def transactions(self, update=False, period_ending=None, verbose=False): #all transactions
		if period_ending and self.period_ending:
				#assert period_ending >= self.period_ending, 'period %s is less than %s' % (period_ending, self.period_ending)
				self.period_ending = period_ending
		elif period_ending:
			self.period_ending = period_ending
		else:
			self.period_ending = date.today()
		fees, fee_records = self.fee_transactions(self.period_ending)
		fee_record_dict = dict([(f.pk, f) for f in fee_records])
		class AccountTrans(object):
			pass
		account_opened = AccountTrans()
		account_opened.trans_date = self.start_date
		account_opened.description = 'Account opened'
		account_opened.amount = 0
		account_opened.closed = None

		account_transactions = []
		if self.end_date:
			account_closed = AccountTrans()
			account_closed.description = 'Account closed'
			account_closed.trans_date = self.end_date
			account_closed.amount = 0
			account_closed.closed = None
			account_transactions.append(account_closed)

		trans_list = sorted([account_opened] + fees + self.payment_transactions(self.period_ending) + account_transactions, key=lambda x:x.trans_date)

		#pay off allocated payments
		return_list = []
		self.balance = kitty = 0
		close_off_next_iter = None
		for t in trans_list:
			if close_off_next_iter and (t.trans_date >= close_off_next_iter and not t.closed or (t.closed and t.closed > close_off_next_iter)):
				#charge closed off late fees
				overdue_closed_fees = [f for f in fees if f.closed == close_off_next_iter and f.principle_due > 0 and f.due_date <= close_off_next_iter]
				close_off_next_iter = None
				total_closed_penalties = 0
				for f in overdue_closed_fees:
					interest_balance, penalty_balance, calc_string = f.calc_late_fee_balance(self.closed_off)
					fee_record = fee_record_dict.get(f.pk)
					fee_record.interest_total += interest_balance
					fee_record.penalty_total += penalty_balance
					closed_penalties = (interest_balance + penalty_balance)
					fee_record.balance += closed_penalties
					total_closed_penalties += closed_penalties
					fee_record = fee_record_dict.get(f.pk)
					# pay off interest
					if f.interest_due >0 and kitty >0:
						if kitty >= f.interest_due:
							interest_paid = f.interest_due
							kitty -= interest_paid
						else:
							interest_paid = kitty
							kitty =0
						f.interest_paid += interest_paid
						fee_record.interest_paid += interest_paid

					# pay off penalty
					if f.penalty_due >0 and kitty >0:
						if kitty >= f.penalty_due:
							penalty_paid = f.penalty_due
							kitty -= penalty_paid
						else:
							penalty_paid = kitty
							kitty =0
						f.penalty_paid += penalty_paid
						fee_record.penalty_paid += penalty_paid

				if total_closed_penalties > 0:
					class Transaction(object):
						pass
					st = Transaction()
					self.balance += total_closed_penalties
					st.description = "<span style=\"color:red\">Late charges period ending %s</span>" % (self.closed_off)
					st.trans_date = self.closed_off
					st.amount = total_closed_penalties
					st.closed = self.closed_off
					st.balance = self.balance
					st.kitty = kitty
					return_list.append(st)

				class ClosedOff(object):
					pass
				co = ClosedOff()
				#import pdb
				#pdb.set_trace()
				co.trans_date = self.closed_off
				co.description = 'Balance Closed Off'
				co.closed = self.closed_off
				co.kitty = kitty
				co.amount = -1 * self.balance
				return_list.append(co)
				co.balance = 0
				#add carried forward
				if kitty > 0:
					class BroughtForward(object):
						pass
					bf = BroughtForward()
					bf.kitty = kitty
					bf.trans_date = self.closed_off + timedelta(days=1)
					bf.description = 'Left over payments'
					bf.balance = bf.amount = -1 * kitty
					bf.closed = None
					return_list.append(bf)
				else:
					self.balance = 0

			if isinstance(t, AccountTrans):
				t.balance = self.balance
				t.kitty = kitty
				return_list.append(t)

			if isinstance(t, AccountFee):
				self.balance += t.amount
				#add closed off
				if t.closed:
					close_off_next_iter = t.closed

				if kitty > 0:
					o = t
					fee_record = fee_record_dict.get(o.pk)

					# pay off principle
					if o.principle_due >  0 and kitty > 0:
						if kitty >= o.principle_due:
							principle_paid = o.principle_due
							kitty -= principle_paid
						else:
							principle_paid = kitty
							kitty = 0

						o.principle_paid += principle_paid
						fee_record.principle_paid += principle_paid

						if principle_paid:
							t.description += ' -paid %s principle' % principle_paid
							interest_balance, penalty_balance, calc_string = o.calc_late_fee_balance(t.trans_date, principle_paid)
							if interest_balance + penalty_balance > 0:
								fee_record.interest_total += interest_balance
								fee_record.penalty_total += penalty_balance
								self.balance += (interest_balance + penalty_balance)
								if interest_balance + penalty_balance > 0:
									od_copy = copy.copy(o)
									od_copy.description = "<span style=\"color:red\">Late charges on %s<br/><span class=\"calc_string\">%s</span></span>" % (od_copy, calc_string)
									od_copy.trans_date = t.trans_date
									od_copy.amount = (interest_balance + penalty_balance)
									od_copy.balance = self.balance
									return_list.append(od_copy)

				t.balance = self.balance
				t.kitty = kitty
				return_list.append(t)


			elif isinstance(t, BankDeposit):
				t.amount = abs(t.amount) * -1
				deposit_amount = abs(t.amount)
				self.balance += t.amount
				t.balance = self.balance
				return_list.append(t)
				late_charge_transactions = []

				allocated_fees = [f for f in fees if f.from_date in t.allocated_dates and f.from_date <= t.trans_date]
				to_pay = allocated_fees + [f for f in fees if f.from_date <= t.trans_date and t.closed == f.closed]
				total_penalties_sum = 0

				for o in to_pay:
					principle_paid = 0
					if o.principle_due >  0 and deposit_amount > 0:
						fee_record = fee_record_dict.get(o.pk)
						if deposit_amount >= o.principle_due:
							principle_paid = o.principle_due
							deposit_amount -= principle_paid
						else:
							principle_paid = deposit_amount
							deposit_amount = 0

						o.principle_paid += principle_paid
						fee_record.principle_paid += principle_paid

					if principle_paid: #incure penalties
						t.description += ' <br/>paid %s for %s' % (principle_paid, o)
						interest_balance, penalty_balance, calc_string = o.calc_late_fee_balance(t.trans_date, o.principle_paid)
						if interest_balance + penalty_balance > 0:
							fee_record.interest_total += interest_balance
							fee_record.penalty_total += penalty_balance
							total_penalties = (interest_balance + penalty_balance)
							total_penalties_sum += total_penalties
							self.balance += total_penalties

							if total_penalties > 0:
								od_copy = copy.copy(t)
								late_charge_transactions.append(od_copy)
								od_copy.description = "<span style=\"color:red\">Late charges on payment for %s<br/><span class=\"calc_string\">%s</span></span>" % (o, calc_string)
								od_copy.trans_date = t.trans_date
								od_copy.amount = total_penalties
								od_copy.balance = self.balance
								return_list.append(od_copy)

				kitty += deposit_amount
				t.kitty = kitty
				for lct in late_charge_transactions:
					lct.kitty = kitty


		#then pay off any other outstanding for period ending
		for f in [f for f in fees if f.total_due > 0 and not f.closed]:
			interest_balance, penalty_balance, calc_string = f.calc_late_fee_balance(self.period_ending)
			fee_record = fee_record_dict.get(f.pk)
			fee_record.interest_total += interest_balance
			fee_record.penalty_total += penalty_balance
			self.balance += (interest_balance + penalty_balance)
			fee_record.balance += (interest_balance + penalty_balance)
			if interest_balance + penalty_balance > 0:
				od_copy = copy.copy(f)
				od_copy.description = "<span style=\"color:red\">Late charges on %s<br/><span class=\"calc_string\">%s</span></span>" % (od_copy, calc_string)
				od_copy.trans_date = self.period_ending
				od_copy.amount = interest_balance + penalty_balance
				od_copy.balance = self.balance
				return_list.append(od_copy)

			fee_record = fee_record_dict.get(f.pk)
			# pay off interest
			if f.interest_due >0 and kitty >0:
				if kitty >= f.interest_due:
					interest_paid = f.interest_due
					kitty -= interest_paid
				else:
					interest_paid = kitty
					kitty =0
				f.interest_paid += interest_paid
				fee_record.interest_paid += interest_paid

			# pay off penalty
			if f.penalty_due >0 and kitty >0:
				if kitty >= f.penalty_due:
					penalty_paid = f.penalty_due
					kitty -= penalty_paid
				else:
					penalty_paid = kitty
					kitty =0
				f.penalty_paid += penalty_paid
				fee_record.penalty_paid += penalty_paid

			#calc overdue
			if f.principle_due > 0 and f.due_date < self.period_ending:
							fee_record.overdue += f.principle_due

		for fee_record in [f for f in fee_records if not f.closed]:
			self.interest_paid += fee_record.interest_paid
			self.interest_total += fee_record.interest_total
			self.penalty_paid += fee_record.penalty_paid
			self.penalty_total += fee_record.penalty_total
			self.principle_paid += fee_record.principle_paid
			self.principle_total += fee_record.amount
			fee_record.balance = fee_record.interest_due + fee_record.penalty_due + fee_record.principle_due

			if update:
				fee_record.save()

		overdue = [fee.principle_due for fee in fees if fee.principle_due > 0 and fee.due_date < self.period_ending and not fee.closed]
		if overdue:
			self.overdue = reduce(lambda x,y:x + y, overdue)
		else:
			self.overdue = 0
		if update:
			self.save() # save account

		return return_list, fees



class AccountHolder(models.Model):
	account = models.ForeignKey(Account, related_name='holders')
	holder_type = models.ForeignKey(ContentType)
	holder_id = models.PositiveIntegerField()
	holder = GenericForeignKey('holder_type', 'holder_id')


class BankDeposit(models.Model):
	bank = models.CharField(max_length=30)
	branch = models.CharField(max_length=30, null=True, blank=True)
	amount = models.PositiveIntegerField(default=0)
	bank_receipt_no = models.CharField(max_length=50, null=True, help_text='')
	depositor_name = models.CharField(max_length=150, null=True, blank=True)
	user = models.ForeignKey(User, null=True)
	date_banked = models.DateField()
	created = models.DateTimeField(auto_now_add=True, null=True)
	rra_receipt = models.CharField(max_length=40, null=True, blank=True, verbose_name='RRA Receipt')
	account = models.ForeignKey(Account, null=True, related_name='account_payments')
	sector_receipt = models.CharField(max_length=50, null=True, blank=True, verbose_name='RRA Receipt')
	note = models.TextField(null=True, blank=True)
	status = models.ForeignKey(CategoryChoice, default=1)
	non_pm_payment = models.BooleanField(default=False)
	old_receipt_id = models.PositiveIntegerField(null=True)
	closed = models.DateField(null=True)
	created = models.DateTimeField(auto_now_add=True, null=True)
	trans_date = models.DateField(null=True)

	@property
	def allocated_dates(self):
		if not self.note:
			return []
		months = re.findall(r'(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)',self.note,re.I)
		match = re.search(r'20\d{2}',self.note,re.I)
		if match:
			year = match.group()
		else:
			year = self.date_banked.year

		if months:
			dates = []
			return_dates = []
			for month in months:
				dates.append(datetime.strptime("01 %s %s" % (month, year), '%d %b %Y').date())
			dates = sorted(dates)
			d = dates[0]
			while d <= dates[-1]:
			  return_dates.append(d)
			  d = d + relativedelta(months=1)
			return return_dates
		elif year:
			return [date(int(year), 1, 1)]
		else:
			return []

	def save(self, *args, **kwargs):
		self.trans_date = self.date_banked
		if self.allocated_dates and self.allocated_dates[0] > self.date_banked: #payment in advance
			self.trans_date = self.allocated_dates[0]

		if self.account.closed_off and self.trans_date <= self.account.closed_off:
			self.closed = self.account.closed_off
		return super(BankDeposit, self).save(*args, **kwargs)


class Contact(models.Model):
	account = models.ForeignKey(Account, null=True)
	first_name = models.CharField(max_length = 100, help_text="Contact name.", null=True, blank=True)
	last_name = models.CharField(max_length = 100, help_text="Contact name.", null=True)
	email = models.EmailField(max_length = 100, help_text="Contact email.", null=True, blank=True)
	phone = models.CharField(max_length = 100, help_text="Contact phone.", null=True, blank=True)

	def __unicode__(self):
		return "%s %s" % (self.first_name, self.last_name)



def get_rate(period, category, sub_category=None, village=None, cell=None, sector=None):
	#rates = cache.get('rate_pk')
	#if not rates:
	#	rates = [r for r in Rate.objects.select_related('village','cell','sector', 'category', 'sub_category').all()]
	#	cache.set('rates', rates, 60)
	#rates = [r for r in rates if r.category==category and r.sub_category==sub_category and r.date_from <= period]
	rates = Rate.objects.all()
	rates = rates.select_related('village','cell','sector', 'category', 'sub_category').filter(category=category, sub_category=sub_category, date_from__lte=period)

	if village:
		rates = rates.filter(Q(village=village)| Q(cell=village.cell)|Q(sector=village.cell.sector))
		#rates = [r for r in rates if r.village==village or r.cell==village.cell or r.sector==village.cell.sector]
	elif cell:
		rates = rates.filter(village__isnull=True).filter(Q(cell=cell)| Q(sector=cell.sector))
		#rates = [r for r in rates if not r.village or r.cell==cell or r.sector==cell.sector]
	elif sector:
		rates = rates.filter(village__isnull=True, cell__isnull=True, sector=sector)
		#rates = [r for r in rates if not r.village and not r.cell and r.sector==sector]

	#rates = rates.order_by('-date_from', '-village', '-cell', '-sector')
	if rates:
		rate = rates[0]
		calc_string = ''
		calc_string = "%s" % '{0:,}'.format(rate.amount)
		if rate.village:
			calc_string += " (%s village)" % rate.village
		elif rate.cell:
			calc_string += " (%s cell)" % rate.cell
		elif rate.sector:
			calc_string += " (%s sector)" % rate.sector


		if sub_category:
			calc_string += " %s" % sub_category

		return rate.amount, calc_string
	else:
		return 0, 'No Rate Found'


class AccountFee(models.Model):
	"""
	Manual fee entries for accounts, used for if `Generate Fees Manually`
	selected in fee register
	"""
	account = models.ForeignKey(Account, related_name='account_fees')
	from_date = models.DateField(null=True)
	to_date = models.DateField(null=True)
	amount = models.DecimalField(max_digits=16, decimal_places=2, default=0) #total principle amount
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
	fee_subtype = models.ForeignKey(CategoryChoice, null=True, related_name='not_used')
	is_paid = models.BooleanField(default=False)
	utility = models.ForeignKey(Utility, null=True, blank=False)
	prop = models.ForeignKey(Property, null=True, blank=False)
	due_days = models.PositiveSmallIntegerField(default=0, null=True)
	district = models.ForeignKey(District, null=True, blank=True)
	sector = models.ForeignKey(Sector, null=True, blank=True)
	cell = models.ForeignKey(Cell, null=True, blank=True)
	village = models.ForeignKey(Village, null=True, blank=True)
	balance = models.DecimalField(max_digits=16, decimal_places=2,default=0)
	ytd_balance = models.DecimalField(max_digits=16, decimal_places=2,default=0)
	overdue = models.DecimalField(max_digits=16, decimal_places=2,default=0)
	parcel_id = models.IntegerField(null=True)
	upi = models.CharField(null=True, max_length=30, validators=[validate_upi],help_text="eg. 1/03/10/01/655", verbose_name="UPI", blank=True)
	#bf = models.DecimalField(max_digits=16, decimal_places=2,default=0)
	#cf = models.DecimalField(max_digits=16, decimal_places=2,default=0)
	status = models.ForeignKey(CategoryChoice, default=1, related_name='account_fee__status')
	closed = models.DateField(null=True)
	created = models.DateTimeField(auto_now_add=True, null=True)

	@property
	def site(self):
		site = self.utility or self.prop
		if not site:
			if sector:
				site = ' sector %s' % self.sector
			if cell:
				site += ', %s cell' % self.cell
			if village:
				site += ', %s village' % self.village

		return site

	def adjust_balance(self, period_ending):
		interest_total = self.interest_total
		penalty_total = self.penalty_total
		self.interest_total, self.penalty_balance, calc_string = f.calc_late_fee(period_ending)
		self.interest_balance, self.penalty_balance = self.interest_total - interest_total, self.penalty_balance - penalty_total
		return self.interest_balance, self.penalty_balance

	def save(self, *args, **kwargs):
		if not self.pk or not self.village:
			utility = self.prop or self.utility
			if utility:
				if utility.village:
					self.village = utility.village
					self.cell = utility.village.cell
					self.sector = utility.village.cell.sector
				elif utility.cell:
					self.cell = utility.cell
					self.sector = utility.cell.sector
				elif utility.sector:
					self.sector = utility.sector
		return super(AccountFee, self).save(*args, **kwargs)

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


	def calc_land_lease(self, sub_category, village):
		if not self.fee_subtype and self.prop:
				self.fee_subtype = self.prop.land_zone
				self.save()

		rate, calc_string = get_rate(self.from_date, category=self.fee_type, sub_category=self.fee_subtype, village=self.village)
		if not rate:
			if self.fee_subtype.code == 'agricultural':
				if self.quantity >= 20000:
					rate = Decimal(str(0.4))
					calc_string += 'Agricultural > 2 hectares'
			else:
				if self.from_date >= date(1998,2,1) and self.to_date <= date(2001,12,31):

					calc_string = 'pre 2001'
					if self.fee_subtype == 'residential':
						rate = 80
						calc_string += ' Residential'

					elif self.fee_subtype == 'commercial':
						calc_string += ' Commerical'
						rate = 100

				elif self.from_date >= date(2002,1,1) and self.from_date <= date(2002,12,31):
					calc_string = 'pre 2002, post 2001'
					if self.fee_subtype == 'residential':
						rate = 150
						calc_string += ' Residential'

					elif self.fee_subtype == 'commercial':
						rate = 200
						calc_string += ' Commercial'

				elif self.from_date >= date(2003,1,1) and self.to_date <= date(2012,12,31): #2003 to 2012
					calc_string = 'pre 2012, post 2002'
					if self.fee_subtype.code == 'residential' and village:

						calc_string += ' Residential'
						if village.cell.sector.district.name.lower() == 'kicukiro' and village.cell.sector.name.lower() in ('gahanga', 'masaka'):
							rate = 30
						elif village.cell.sector.district.name.lower() == 'kicukiro' and village.cell.name.lower() in ('muyange') and \
							village.cell.name.lower() in ('kamuna','mugeyo'):
								rate = 70
						else:
							rate = 80

					elif self.fee_subtype.code == 'commercial':
						calc_string += ' Commercial'
						rate = 150

		return rate, calc_string


	def calc_rate(self):
		quantity = 1
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

		if self.account.start_date > self.from_date:
			from_date = self.account.start_date
		else:
			from_date = self.from_date

		if (self.account.end_date or self.account.period_ending) < self.to_date:
			to_date = (self.account.end_date or self.account.period_ending)
		else:
			to_date = self.to_date


		if self.fee_type.code == 'land_lease':
			rate, calc_string = self.calc_land_lease(sub_category=self.fee_subtype, village=self.village)
		elif self.fee_type.code == 'cleaning':
			rate, calc_string = get_rate(self.from_date, category=self.fee_type, sub_category=self.fee_subtype, village=None)
		else:
			rate, calc_string = get_rate(self.from_date, category=self.fee_type, sub_category=self.fee_subtype, village=self.village)

		total = Decimal(round(rate * quantity))
		if quantity > 1:
			calc_string += " * size: %s" % (quantity)

		if to_date < self.to_date or from_date > self.from_date:
			part_days = (to_date - from_date).days + 1
			if part_days < 0:
				part_days = 0
			total_days = (self.to_date - self.from_date).days + 1
			day_fraction = Decimal(str(round(float(part_days)/ total_days, 4)))
			total = Decimal(str(round(day_fraction * total)))
			calc_string += "* %s (%s / %s days)" % (day_fraction, part_days, total_days)

		return (total, calc_string)

	def calc_late_fee_balance(self, pay_date, payment_amount=None):
		"""
		returns the balance of interest and penalty that needs to be paid for the period
		and sets the penalty and interest totals
		"""
		interest, penalty, interest_calc_string, penalty_calc_string = self.calc_late_fee(pay_date, payment_amount)
		calc_string = interest_calc_string
		if self.penalty_total:
			penalty_balance = 0
		else:
			penalty_balance = penalty

		if penalty_balance:
			calc_string += " + %s" % penalty_calc_string

		self.interest_total += interest
		self.penalty_total += penalty_balance
		return interest, penalty_balance, calc_string


	def calc_late_fee(self, pay_date, payment_amount=None):
		interest =  0
		penalty = 0
		interest_calc_string = penalty_calc_string = ''
		principle_due = self.principle_due
		if payment_amount:# calculate percentage only on part payment
			principle_due = payment_amount

		if self.fee_type.code in ('land_lease', 'cleaning', 'market'):
			if self.to_date <= date(2012,12,31) and self.fee_type.code == 'land_lease':
				years_late = pay_date.year - self.due_date.year
				if years_late > 0:
					interest = int(years_late * 0.08 * float(principle_due))
					interest_calc_string = "interest %s (0.08 * %s years * %s)" % ('{0:,}'.format(interest), years_late, '{0:,}'.format(principle_due))
					penalty = 0

			elif pay_date > self.due_date and principle_due > 0:
				penalty_limit = 10000
				months_late = (pay_date.year - self.due_date.year ) * 12 + (pay_date.month - self.due_date.month)
				interest = int(0.015 * float(principle_due) * months_late)
				interest_calc_string = "interest %s (0.015 * %s months * %s)" % ('{0:,}'.format(interest), months_late, '{0:,}'.format(principle_due))

				penalty = int(0.1 * float(self.amount))
				if penalty > penalty_limit:
					penalty = penalty_limit

				penalty_calc_string = "penalty %s (0.1 * %s)" % ('{0:,}'.format(penalty), '{0:,}'.format(self.amount))

		return Decimal(str(interest)), Decimal(str(penalty)), interest_calc_string, penalty_calc_string

	def update_name(self):
		self.name = "%s" % self.fee_type
		if self.prop:
			self.name += " for UPI %s" % (self.prop.upi)
		elif self.utility:
			self.name +=  " for %s" % (self.utility)

	def __unicode__(self):
		s = "%s" % self.fee_type

		if self.period == 1:
			s += " %s" % self.from_date.strftime("%Y")

		elif self.period == 12:
			s += " %s" % self.from_date.strftime("%b, %Y")

		return s


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
	account = models.ForeignKey(Account, null=True, related_name='account_collections')
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
		return self.user.__unicode__()


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


class CurrentOutstanding(models.Model):
	district = models.ForeignKey(District, related_name="district_outstanding", null=True)
	sector = models.ForeignKey(Sector, related_name="sector_outstanding", null=True)
	cell = models.ForeignKey(Cell, related_name="cell_outstanding", null=True)
	village = models.ForeignKey(Village, related_name="village_outstanding", null=True)
	accounts = models.IntegerField(default=0,null=True)
	fee_type = models.ForeignKey(CategoryChoice)
	balance = models.DecimalField(max_digits=16, decimal_places=2, default=0)
	overdue = models.DecimalField(max_digits=16, decimal_places=2, default=0)

	@property
	def name(self):
		if self.village:
			return "%s village" % self.village
		elif self.cell:
			return "%s cell" % self.cell
		elif self.sector:
			return "%s sector" % self.sector
		elif self.district:
			return "%s district" % self.district


