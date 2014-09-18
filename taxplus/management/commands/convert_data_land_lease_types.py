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
		update property_property set landlease_type_id = (select id from taxplus_categorychoice 
		where category_id = 'land_lease_type' and code = property_property.land_lease_type)
		where landlease_type_id is null;
		commit;
		"""
		cursor.execute(query)






