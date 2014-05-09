from django.core.management.base import BaseCommand, CommandError 
from jtax.models import *
from log.models import CronLog
from datetime import date, datetime, time, timedelta
import dateutil.parser
from datetime import date
from jtax.mappers.TaxMapper import TaxMapper
from django.utils import timezone
from django import db
from dateutil.relativedelta import relativedelta


class Command(BaseCommand):
	#fixed_asset/rental_income/trading_license/cleaning_fee/market_fee/land_lease_fee
	args = ''
	help = 'Convert tax periods from timestamps to dates for simplicity'
	name= 'Convert tax dates'
	
	def handle(self, *args, **options):
		errors = []


		for fee in Fee.objects.filter(fee_type__in=['land_lease','land_lease_fee'], land_lease_type__isnull=True, property__land_lease_type__isnull=False).select_related('property').order_by('pk'): #filter(date_from__isnull=True):
			if fee.property.land_lease_type == 'Rural Area':
				fee.land_lease_type = fee.property.land_lease = LandUse.objects.get(code='RUR')
			elif fee.property.land_lease_type == 'Agriculture':
				fee.land_lease_type = fee.property.land_lease = LandUse.objects.get(code='AGR')
			elif fee.property.land_lease_type == 'Urban Area':
				fee.land_lease_type = fee.property.land_lease = LandUse.objects.get(code='URB')
			elif fee.property.land_lease_type == 'Trading Centre':
				fee.land_lease_type = fee.property.land_lease = LandUse.objects.get(code='COM')
			else:
				raise Exception("Could not find land lease type %s for lease %s" % (fee.property.land_lease_type, fee.pk))
			fee.save()
			fee.property.save()
			self.stdout.write("updated land lease %s %s" % (fee, fee.pk))
			db.reset_queries()
		

		for property in Property.objectsIgnorePermission.filter(land_use_type__isnull=False, land_use_types__isnull=True):
			if property.land_use_type == 'Residential':
				property.land_use_types = LandUse.objects.filter(code='RES')
			if property.land_use_type == 'Industrial':
				property.land_use_types = LandUse.objects.filter(code='IND')
			if property.land_use_type == 'Commercial':
				property.land_use_types = LandUse.objects.filter(code='COM')
			if property.land_use_type == 'Agricultural':
				property.land_use_types = LandUse.objects.filter(code='AGR')
			else:
				continue
				raise Exception("Could not find land use %s for property %s" % (property.land_use_type, property.pk))
			property.save()
			db.reset_queries()




