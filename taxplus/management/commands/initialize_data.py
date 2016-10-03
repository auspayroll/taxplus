from django.core.management.base import BaseCommand, CommandError
from datetime import date, datetime, time, timedelta
from taxplus.models import Category, CategoryChoice, Fee, Rate
import dateutil.parser
from datetime import date
from django.utils import timezone
from django import db
from dateutil.relativedelta import relativedelta
from datetime import date


categories = (
	('status', 'status'),
	('cycle', 'cycle'),
	('market_status', 'market type'),
	('property_type', 'property type'),
	('occupancy_status', 'occupancy status'),
	('fee_type', 'fee type'),
	('utility_type', 'utility type'),
	('land_use', 'land use'),
	('land_lease_type', 'land lease'),
	('entity_type', 'entity type'),
	('deactivate_reason', 'deactivate reason'),
	('cleaning_rate', 'cleaning rate')

	)

category_choices = {

	'status':(('active', 'active'), ('inactive','inactive'), ('pending','pending')),

	'cycle':((0,'One off'), (12, 'Monthly'), (1,'Yearly'), (26, 'Fortnightly'), (52,'Weekly')),

	'fee_type':(('land_lease', 'Land Lease Fee'),('cleaning', 'Cleaning Fee'), ('quarry', 'Quarry Fee'), ('cemetery', 'Cemetery Fee'),
		('market', 'Market Fee'), ('tower', 'Tower Fee'), ('marriage','Marriage Licence'), ('sign', 'Billboard & Sign')),

	'utility_type':(('property', 'Property'), ('quarry', 'Quarry'), ('cemetery', 'Cemetery'), ('market', 'Market'),
	   ('tower', 'Tower'), ('district', 'District'), ('sector', 'Sector'), ('cell', 'Cell'), ('village', 'Village'),
	   ('sign', 'Billboard/Sign')),

	'land_use':(('rural', 'Rural'),('urban', 'Urban'), ('forestry', 'Forestry'),
		('quarry', 'Quarry Purpose'), ('industrial', 'Industrial'), ('residential', 'Residential'), ('cultural', 'Cultural (other)'),
		('cultural_np', 'Cultural (non profit)'), ('commercial', 'Commercial'), ('agricultural', 'Agricultural')),

	'entity_type':(('individual', 'Individual'), ('business', 'Business'), ('subsiduary', 'Branch')),

	'deactivate_reason':(('deceased','Deceased'),('double entry','Double Entry'),('expat','Expat'),('ceased', 'ceased trading')),

	'cleaning_rate':[('cat%s' % (i+1), 'Category %s' % (i+1)) for i in range(8)],

}


class Command(BaseCommand):
	#fixed_asset/rental_income/trading_license/cleaning_fee/market_fee/land_lease_fee
	args = ''
	help = """
	Transform old payment relational tables from jtax

	"""
	name= 'Convert tax dates'

	def handle(self, *args, **options):
		for code, name in categories:
			category, created = Category.objects.update_or_create(code=code, defaults=dict(name=name))


		# set category choices
		for key, choices in category_choices.items():
			for code, name in choices:
				categorychoice, created = CategoryChoice.objects.update_or_create(category__code=key, code=code, defaults=dict(name=name, category_id=key))
				print 'created %s' % categorychoice


		#add cleaning fee rates
		cleaning_rates = {'cat1':10000, 'cat2':10000, 'cat3':10000, 'cat4':10000, 'cat5':10000, 'cat6':10000, 'cat7':5000, 'cat8':3000}
		category = CategoryChoice.objects.get(category__code='fee_type', code='cleaning')
		for code, rate in cleaning_rates.items():
			sub_category = CategoryChoice.objects.get(category__code='cleaning_rate', code=code)
			instance, created = Rate.objects.update_or_create(category=category, sub_category=sub_category, defaults=dict(amount=rate, date_from=date(2000,1,1)))


