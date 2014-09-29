from django.core.management.base import BaseCommand, CommandError 
from datetime import date, datetime, time, timedelta
from taxplus.models import Business, SubBusiness, Citizen, Entity, CategoryChoice, IdentityDocument, BusinessOwnership, PropertyOwnership, Ownership
import dateutil.parser
from datetime import date
from django.utils import timezone
from django import db
from dateutil.relativedelta import relativedelta


class Command(BaseCommand):
	#fixed_asset/rental_income/trading_license/cleaning_fee/market_fee/land_lease_fee
	args = ''
	help = """
	Transform businesses, subbusiness, citizens in to one Entity object/table

	"""
	name= ''
	
	def handle(self, *args, **options):
		errors = []
		active = CategoryChoice.objects.get(category__code='status', code='active')
		for citizen in Citizen.objects.filter(entity_id__isnull=True):
			try:
				entity = Entity.objects.get(identifier=citizen.citizen_id, entity_type=CategoryChoice.objects.get(category__code='entity_type', code='individual'))
			except Entity.DoesNotExist:
				try:
					entity = Entity.objects.get(citizen_id=citizen.pk)
					entity.identifier = citizen.citizen_id
					entity.save()
				except Entity.DoesNotExist:
					entity = Entity(citizen_id=citizen.pk, entity_type=CategoryChoice.objects.get(category__code='entity_type', code='individual'), status=active, identifier=citizen.citizen_id)
					entity.save()

			if entity.citizen_id != citizen.pk:
				citizen.status_id = 2
				citizen.status_new_id = CategoryChoice.objects.get(category__code='status', code='inactive')
				citizen.save()

			citizen.entity_id = entity.pk
			citizen.save(update_fields=['entity_id'])









