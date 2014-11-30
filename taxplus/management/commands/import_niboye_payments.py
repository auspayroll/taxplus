from django.core.management.base import BaseCommand, CommandError
from datetime import date, datetime, time, timedelta
from taxplus.models import Property, Fee, PropertyOwnership, PropertyTitle, District, CategoryChoice, \
	Village, Rate, RateNotFound, Sector, Cell, Citizen, PayFee
import dateutil.parser
from datetime import date, datetime
from django.utils import timezone
from django import db
from dateutil.relativedelta import relativedelta
from django.db import connection
from django.db.models import Q
from jtax.models import FormulaData
from log.models import Log

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import Paragraph, Table, TableStyle, Frame, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from django.conf import settings
from django.contrib.humanize.templatetags.humanize import intcomma
import csv

import os

class Command(BaseCommand):
	#fixed_asset/rental_income/trading_license/cleaning_fee/market_fee/land_lease_fee
	args = ''
	help = """
	Transform old payment relational tables from jtax

	"""
	name= 'Convert land use types'

	def handle(self, *args, **options):
		f = open("%s/taxplus/excel/niboye-payments.csv" % settings.PROJECT_DIR, 'rb')
		niboye = Sector.objects.get(name='Niboye')
		reader = csv.DictReader(f)
		line_no = 2
		not_found = 0
		found = 0
		invalid = 0
		process = 0
		unprocessed = 0
		name_matches = 0
		name_not_found = 0

		for line in reader:
			try:
				cell = Cell.objects.get(name__iexact=line['cell'].strip(), sector=niboye)
			except Cell.DoesNotExist:
				raise Exception('cant find cell %s' % cell)

			try:
				village = Village.objects.get(name__iexact=line['village'].strip(), cell=cell)

			except Village.DoesNotExist:
				raise Exception('line %s: cant find village %s, cell %s' % (line['village'], line['cell'], line_no))

			try:
				prop = Property.objects.get(cell=cell, parcel_id=line['plot'].strip())

			except ValueError:
				print 'line %s: invalid plot no %s' % (line_no, line['plot'])
				invalid += 1

			except Property.DoesNotExist:
				print "line %s: name: %s: can't find property in cell %s with parcel id %s" % (line_no, line['name'], cell, line['plot'])
				not_found += 1
				line_no += 1
				continue

			else:
				#pass
				found += 1
				#print 'line %s: processing payments for property %s' % (line_no, prop)

			name = line['name'].replace(' ', ' ')
			name_parts = name.split(' ')
			first_name = name_parts[-1]
			last_name = name_parts[0]
			try:
				citizen = Citizen.objects.get(first_name__iexact=first_name, last_name__iexact=last_name)

			except Citizen.DoesNotExist:
				citizen = None

			except Citizen.MultipleObjectsReturned:
				if len(name_parts) == 3:
					try:
						citizen = Citizen.objects.get(first_name__iexact=first_name, last_name__iexact=last_name, middle_name__iexact=name_parts[1])

					except Citizen.DoesNotExist:
						citizen = None

					except Citizen.MultipleObjectsReturned:
						citizen = None

			if citizen and line['phone']:
				citizen.phone_1 = line['phone']
				citizen.save()


			if citizen:
				name_matches += 1

			else:
				name_not_found += 1


			if line['phone']:
				name += ' ph - %s' % line['phone']


			for year in range(2011, 2015):
				if line['amount-%s' % year]:
					try:
						fee = Fee.all_objects.get(prop=prop, date_from__lte=date(year,12,31), date_to__gte=date(year,1,1), category__code='land_lease')
					except:
						print  'cant find fee for %s' % year
						unprocessed += 1
					else:
						fee.status = CategoryChoice.objects.get(category__code='status', code='active')
						fee.i_status = 'active'
						fee.save()
						process += 1
						try:
							PayFee.objects.get(fee=fee, manual_receipt=line['receipt-%s' % year] or str(year))

						except PayFee.DoesNotExist:
							if citizen:
								citizen_id = citizen.pk;
							else:
								citizen_id = None
							if fee.due_date < date.today():
								payment_date = fee.due_date
							else:
								payment_date = date.today()
							payment_amount = line['amount-%s' % year].strip().replace(',','')

							try:
								payment_amount = float(payment_amount)
							except ValueError:
								print 'line %s: invalid payment amount %s' % (line_no, ['amount-%s' % year])
								continue
							else:
								if not payment_amount:
									print 'line %s: invalid zero payment amount ' % (line_no)
									continue

							fee.process_payment(payment_date, sector_receipt=line['receipt-%s' % year] or str(year), payment_amount=payment_amount, staff_id=41, bank_receipt='-',
								payer_name=line['name'], bank='-', citizen_id=citizen_id, notes="csv import")



			line_no += 1

		print 'found %s, not found %s, invalid %s, processed %s, unprocessed %s, name_matches %s, name_not_found %s' % (found, not_found, invalid, process, unprocessed, name_matches, name_not_found)
		f.close()











