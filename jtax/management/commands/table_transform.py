"""
This script generate tax items for all citizens & businesses in the system for current year.
SHOULD BE USED WITH CAUTION AS LOT OF LEGACY DATA IS MISSING ATM.
"""

from django.core.management.base import BaseCommand, CommandError 
from jtax.models import *
from dev1.variables import banks, tax_and_fee_types, miscellaneous_fee_types, currency_types


class Command(BaseCommand):
	#fixed_asset/rental_income/trading_license/cleaning_fee/market_fee/land_lease_fee
	def handle(self, *args, **options):
		for bank in banks:
			Bank.objects.get_or_create(code=bank[0], name=bank[1])

		tax_types = [(a,b) for (a,b) in tax_and_fee_types]
		#import pdb
		#pdb.set_trace()
		for tax_type in tax_types:
			TaxType.objects.get_or_create(code=tax_type[0], name=tax_type[1])

		tax_types = [(a,b) for (a,b) in miscellaneous_fee_types if a != 'misc_fee']
		for tax_type in tax_types:
			TaxType.objects.get_or_create(code=tax_type[0], name=tax_type[1])
		
		for currency in currency_types:
			Currency.objects.get_or_create(code=currency[0], name=currency[1])

		for tax in LandRentalTax.objects.all():
			tax.save()


			
