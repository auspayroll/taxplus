"""
This script process attemp to fill all the log data associated object info for old log records with missing data.
"""
from django.conf import settings
from dev1 import variables
from django.core.management.base import BaseCommand, CommandError 
from jtax.models import *
from media.models import *
from log.models import CronLog, Log
from datetime import date, datetime, time, timedelta
import dateutil.parser
from jtax.mappers.TaxMapper import TaxMapper
import os

class Command(BaseCommand):
	args = ''
	help = 'Fill all the log data associated object info for old log records with missing data.'
	name= 'Fill log data Cron Job'
	import_folder = settings.MEDIA_ROOT + 'epay_feeds/'

	def handle(self, *args, **options):
		#get list of logs with no associated objects
		logs = Log.objects.filter(citizen__isnull=True,business__isnull=True,property__isnull=True)
		print "Processing " + str(len(logs)) + " logs......."
		if logs:
			for i in logs:
				#try:
					#if there is media associated, use media saved info to fill log data
					if i.media_id and i.media_id != '':
						medias = list(Media.objects.raw('select * from media_media where id =' + i.media_id))
						if medias:
							media = medias[0]
						else:
							print ' - Error at ' + str(i.id)
							continue

						i.business = media.business
						i.citizen = media.citizen
						i.property = media.property
						i.tax_type = media.tax_type
						i.tax_id = media.tax_id
						i.payment_type = media.payment_type
						i.payment_id = media.payment_id
					elif 'User [' + i.username + '] view Property ' in i.message:
						#remove the user name part
						message = i.message.replace('User [' + i.username + '] ','')
						address = message.replace('view Property [','').replace(']','').strip()
						parts = address.split(',')
						tmp = parts[0].split(' ')

						sql = 'select property_property.id from property_property INNER JOIN "property_village" ON ("property_property"."village_id" = "property_village"."id")  INNER JOIN "property_cell" ON ("property_property"."cell_id" = "property_cell"."id") INNER JOIN "property_sector" ON ("property_property"."sector_id" = "property_sector"."id") INNER JOIN "property_district" ON ("property_sector"."district_id" = "property_district"."id") where status_id = 1'
						if tmp:
							parcel_id = parts[0].split(' ')[0].strip()
							sql = sql + ' and property_property.parcel_id = ' + parcel_id
							if len(tmp) > 1:
								village = parts[0].split(' ')[1].strip()
								sql = sql + ' and UPPER(property_village.name) = UPPER(\'' + village + '\')'

						if len(parts) > 1:
							cell = parts[1].strip()
							sql = sql + ' and UPPER(property_cell.name) = UPPER(\'' + cell + '\')'

						if len(parts) > 2:
							sector = parts[2].strip()
							sql = sql + ' and UPPER(property_sector.name) = UPPER(\'' + sector + '\')'
								
						if len(parts) > 3:
							district = parts[3].strip()
							sql = sql + ' and UPPER(property_district.name) = UPPER(\'' + district + '\')'

						properties = list(Property.objectsIgnorePermission.raw(sql))
						if properties:
							i.property = properties[0]

					#fetch data from tax / fee
					if not i.business and not i.citizen and not i.property and (i.tax_id or i.payment_id):
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