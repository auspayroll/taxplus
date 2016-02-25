from django.core.management.base import BaseCommand, CommandError
from datetime import date, datetime, time, timedelta
from taxplus.models import Category, CategoryChoice, Fee
import dateutil.parser
from datetime import date
from django.utils import timezone
from django import db
from dateutil.relativedelta import relativedelta


categories = (
	('status', 'status'),
	('market_status', 'market type'),
	('property_type', 'property type'),
	('occupancy_status', 'occupancy status'),
	('fee_type', 'fee type'),
	('utility_type', 'utility type'),
	('land_use', 'land use'),
	('land_lease_type', 'land lease'),
	('entity_type', 'entity type'),
	('deactivate_reason', 'deactivate reason')

	)

category_choices = {

	'status':(('active', 'active'), ('inactive','inactive'), ('pending','pending')),

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

