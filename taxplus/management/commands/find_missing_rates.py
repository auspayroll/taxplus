from django.core.management.base import BaseCommand, CommandError
from datetime import date, datetime, time, timedelta
from taxplus.models import Property, Fee, PropertyOwnership, PropertyTitle, District, CategoryChoice, Village, Rate, RateNotFound
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
		f = open("%s/missing_rates_complete.csv" % settings.ROOT_PATH, 'wb')
		writer = csv.writer(f)
		writer.writerow(['Id', 'District', 'Sector', 'Cell', 'Village', 'Category', 'Year' ])
		land_lease = CategoryChoice.objects.get(category__code='fee_type', code='land_lease')

		"""
		for title in PropertyTitle.objects.filter(prop__village__cell__sector__district__name__iexact="Kicukiro", title_fees__remaining_amount__gt=0, title_fees__due_date__lt=date.today(), title_fees__status__code='active').distinct().order_by('prop__village__pk'):
			prop = title.prop
			print title.pk
			cut_off_start = date(2012,1,1)
			cut_off_end = date(2013,12,31)
			for fee in title.title_fees.exclude(prop__land_zone__code='agricultural').filter(date_from__gte=cut_off_start, date_to__lte=cut_off_end):
				rates = Rate.objects.filter(date_from__lte=fee.date_to, date_to__gte=fee.date_from, village=fee.prop.village, category=land_lease, sub_category=fee.prop.land_zone)
				if not rates:
						miss_rate, created = RateNotFound.objects.get_or_create(date_from=date(fee.date_from.year,1,1), date_to=date(fee.date_from.year,12,31), village=fee.prop.village, category=land_lease, sub_category=fee.prop.land_zone)
						if created:
							writer.writerow([miss_rate.village.pk, miss_rate.village.cell.sector.district.name, miss_rate.village.cell.sector.name, miss_rate.village.cell.name, miss_rate.village.name, miss_rate.sub_category.code, '%s' % (fee.date_from.strftime('%Y'))])
							print 'created new rate for village %s' % prop.village.name
		"""


		for village in Village.objects.filter(cell__sector__district__name__iexact="Kicukiro").order_by('pk'):
			cut_off_start = date(2012,1,1)
			cut_off_end = date(2013,12,31)

			check = (('commercial',date(2012,1,1), date(2012,12,31)),  ('commercial',date(2013,1,1), date(2013,12,31)),
				('residential',date(2012,1,1), date(2012,12,31)),  ('residential',date(2013,1,1), date(2013,12,31)),
			)

			for land_zone, date_from, date_to in check:
				rates = Rate.objects.filter(date_from__lte=date_to, date_to__gte=date_from, village=village, category=land_lease, sub_category__code=land_zone)
				if not rates:
					writer.writerow([village.pk, village.cell.sector.district.name, village.cell.sector.name, village.cell.name, village.name, land_zone, '%s' % (date_from.strftime('%Y'))])
					print 'created new rate for village %s' % village.name

		f.close()











