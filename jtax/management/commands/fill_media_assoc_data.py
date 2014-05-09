"""
This script process attemp to fill all the log data associated object info for old log records with missing data.
"""
from django.conf import settings
from dev1 import variables
from django.core.management.base import BaseCommand, CommandError 
from jtax.models import *
from media.models import *
from datetime import date, datetime, time, timedelta
import dateutil.parser
from jtax.mappers.TaxMapper import TaxMapper
import os

class Command(BaseCommand):
	args = ''
	help = 'Fill all the media data associated object info for old media records with missing data.'
	name= 'Fill media data Cron Job'

	def handle(self, *args, **options):
		#get list of logs with no associated objects
		medias = Media.objects.filter(citizen__isnull=True,business__isnull=True,property__isnull=True)
		print "Processing " + str(len(medias)) + " media records......."
		if medias:
			for i in medias:
				#fetch data from tax / fee
				if i.tax_id or i.payment_id:
					try:
						if i.tax_id:
							if i.tax_type == 'fee':
								tax = Fee.objects.get(pk=i.tax_id)
								i.business = tax.business
								i.subbusiness = tax.subbusiness
								i.property = tax.property
							elif i.tax_type == 'fixed_asset':
								tax = PropertyTaxItem.objects.get(pk=i.tax_id)
								i.property = tax.property

							elif i.tax_type == 'trading_license':
								tax = TradingLicenseTax.objects.get(pk=i.tax_id)
								i.business = tax.business
								i.subbusiness = tax.subbusiness
							elif i.tax_type == 'rental_income':
								tax = RentalIncomeTax.objects.get(pk=i.tax_id)
								i.property = tax.property

						elif i.payment_id:
							if i.payment_type == 'pay_fee':
								payment = PayFee.objects.get(pk=i.payment_id)
								tax = payment.fee
								i.business = tax.business
								i.subbusiness = tax.subbusiness
								i.property = tax.property
							elif i.payment_type == 'pay_fixed_asset':
								payment = PayFixedAssetTax.objects.get(pk=i.payment_id)
								tax = payment.property_tax_item
								i.property = tax.property
							elif i.payment_type == 'pay_trading_license':
								payment = PayTradingLicenseTax.objects.get(pk=i.payment_id)
								tax = payment.trading_license_tax
								i.business = tax.business
								i.subbusiness = tax.subbusiness
							elif i.payment_type == 'pay_rental_income':
								payment = PayRentalIncomeTax.objects.get(pk=i.payment_id)
								tax = payment.rental_income_tax
								i.property = tax.property
					except Exception:
						continue

				i.save()
			#except Exception as e:
			#	print ' - Error at ' + str(i.id)
			#	print '%s (%s)' % (e.message, type(e))
			#	exit()
		print "Done"