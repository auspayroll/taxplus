from django.core.management.base import BaseCommand, CommandError 
from datetime import date, datetime, time, timedelta
from taxplus.models import Fee, Entity
import dateutil.parser
from datetime import date
from django.utils import timezone
from django import db
from dateutil.relativedelta import relativedelta


class Command(BaseCommand):
	#fixed_asset/rental_income/trading_license/cleaning_fee/market_fee/land_lease_fee
	args = ''
	help = """
	Adds entity relationship to fees
	This will be the entity responsible for fee payment

	"""
	name= 'Convert land use types'
	
	def handle(self, *args, **options):
		errors = []

		for fee in Fee.objects.filter(entity_id__isnull=True):
			if fee.business_id:
				fee.entity = Entity.objects.get(business_id=fee.business_id)
			if fee.subbusiness_id:
				fee.entity = Entity.objects.get(subbusiness_id=fee.subbusiness_id)
			if fee.citizen_id:
				fee.entity = Entity.objects.get(citizen_id=fee.citizen_id)

			fee.save(update_fields=['entity_id'])





