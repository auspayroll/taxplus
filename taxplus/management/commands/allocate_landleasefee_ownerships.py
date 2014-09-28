from django.core.management.base import BaseCommand, CommandError 
from django.conf import settings
from dev1 import variables
import dateutil.parser
import os
from datetime import datetime, date, time
from django.core.exceptions import *
from taxplus.models import Fee, PropertyOwnership, CategoryChoice, PropertyOwnership
from django.db.models import Q

from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


sub_types=[]
class Command(BaseCommand):
	args = 'None'
	help = 'Import Businesses in Kicukiro from csv and calculates fees/taxes'
	name= 'Import Kicukiro'
	# @transaction.commit_on_success
	def handle(self, *args, **options):
		land_lease = CategoryChoice.objects.get(category__code='fee_type', code='land_lease')
		fees = Fee.objects.filter(category=land_lease)
		for fee in fees:
			ownerships = PropertyOwnership.objects.filter(prop=fee.prop, date_from__lte=fee.date_to).filter(Q(date_to__gte=fee.date_from) | Q(date_to__isnull=True))
			if ownerships:
				fee.prop_title = ownerships[0].prop_title
				fee.save()
				print 'property title updated'
			else:
				print 'no ownerships found'






