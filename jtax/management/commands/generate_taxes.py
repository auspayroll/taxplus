"""
This script generate tax items for all citizens & businesses in the system for current year.
SHOULD BE USED WITH CAUTION AS LOT OF LEGACY DATA IS MISSING ATM.
"""

from django.core.management.base import BaseCommand, CommandError 
from jtax.models import Property
from asset.models import Business
from datetime import date, datetime, time, timedelta
import dateutil.parser
from django import db


def update_property_taxes(year, district=None, sector=None, cell=None, village=None):

	properties = Property.objectsIgnorePermission.filter(status__name='Active')
	if village:
		if isinstance(village, basestring):
			properties = properties.filter(village__name=village)
		else:
			properties = properties.filter(village=village)
	elif cell:
		if isinstance(cell, basestring):
			properties = properties.filter(cell__name=cell)
		else:
			properties = properties.filter(cell=cell)
	elif sector:
		if isinstance(sector, basestring):
			properties = properties.filter(sector__name=sector)
		else:
			properties = properties.filter(sector=sector)
	elif district:
		if isinstance(district, basestring):
			properties = properties.filter(sector__district__name=district)
		else:
			properties = properties.filter(sector__district=district)

	start_year = date(year, 1, 1)
	for property in properties:
		property.calc_taxes(start_year)
		# print "updated property taxes %s %s  [ OK ]" % (property.pk, property)
		db.reset_queries()


def update_business_taxes(year, district=None, sector=None, cell=None):
	businesses = Business.objects.filter(i_status='active')
	if cell:
		if isinstance(cell, basestring):
			businesses = businesses.filter(cell__name=cell)
		else:
			businesses = businesses.filter(cell=cell)
	elif sector:
		if isinstance(sector, basestring):
			businesses = businesses.filter(sector__name=sector)
		else:
			businesses = businesses.filter(sector=sector)
	elif district:
		if isinstance(district, basestring):
			businesses = businesses.filter(sector__district__name=district)
		else:
			businesses = businesses.filter(sector__district=district)

	start_year = date(year, 1, 1)
	i = 0 
	for business in businesses:
		# print ("business %s" % i)
		i += 1
		business.calc_taxes(start_year)
		# print "updated business taxes %s %s  [ OK ]" % (business.pk, business)
		db.reset_queries()


class Command(BaseCommand):
	#fixed_asset/rental_income/trading_license/cleaning_fee/market_fee/land_lease_fee
	args = '<type (all/property/business) - default to "all" > <year (e.g 2013) - default value is current year> <sector - default is all sectors>'
	help = 'Generate taxes & fees items'
	name= 'Generate Tax Cron Job'
	#import argparse
	#parser = argparse.ArgumentParser(description='Year to process')
	#parser.add_argument('year', type=int, help='the financial year to process')

	def handle(self, *args, **options):
		#default
		try:
			from_year = int(args[0])
		except ValueError:
			print 'Invalid from year inputted. Example format: 2013'
			exit()

		update_property_taxes(from_year)

		update_business_taxes(from_year)
