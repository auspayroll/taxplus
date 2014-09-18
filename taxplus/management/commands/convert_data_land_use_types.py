from django.core.management.base import BaseCommand, CommandError 
from datetime import date, datetime, time, timedelta
import dateutil.parser
from datetime import date
from django.utils import timezone
from django import db
from dateutil.relativedelta import relativedelta


class Command(BaseCommand):
	#fixed_asset/rental_income/trading_license/cleaning_fee/market_fee/land_lease_fee
	args = ''
	help = """
	Transform old payment relational tables from jtax

	"""
	name= 'Convert land use types'
	
	def handle(self, *args, **options):
		errors = []

		cursor = db.connection.cursor()
		query = """
		begin;
		insert into property_property_landuse_types(property_id, categorychoice_id)
		select property_property.id, choice.id 
		from property_property join ( select * from pmeval_categorychoice 
		where category_id = 'land_use') choice on choice.name = property_property.land_use_type;
		commit;
		"""
		cursor.execute(query)





