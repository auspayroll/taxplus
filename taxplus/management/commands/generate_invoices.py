from django.core.management.base import BaseCommand, CommandError
from datetime import date, datetime, time, timedelta
from taxplus.models import Property, Fee, PropertyOwnership, PropertyTitle, District, CategoryChoice, Village
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

import os
stylesheet=getSampleStyleSheet()
normalStyle = stylesheet['Normal']


def generate_invoice(canvas, pagesize, title, fees):
	width, height = pagesize
	border_x = 2.5
	border_y = 1
	kigali_icon = os.path.join(settings.PROJECT_DIR, 'static', 'images', 'sectors', 'kigali_icon.gif')

	p = canvas

	p.setFont("Helvetica-Bold", 16)
	p.drawCentredString(width/2.0, height - (border_y * cm), 'LAND LEASE FEE OVERDUES')

	p.setFont("Helvetica", 12)
	p.drawRightString(width - border_x * cm, height - (border_y * cm), 'No: KK%s' % title.id)

	frame1_y_offset = height - 2.3 * cm
	frame1_y_line_diff = 0.5 * cm

	p.setStrokeColor(colors.grey)
	p.line(border_x * cm, height - ( (border_y + 0.5) * cm), width - border_x * cm, height - ( (border_y + 0.5) * cm))

	p.setFont("Helvetica", 11)
	p.drawString(border_x * cm, frame1_y_offset, 'Republic of Rwanda')

	p.drawImage(kigali_icon, border_x * cm, height - 5 *cm, width=2.5*cm, height=2.5*cm)


	p.setFont("Helvetica", 11)
	p.drawString(border_x * cm, frame1_y_offset - 6.4 * frame1_y_line_diff, 'Kigali City')
	p.drawString(border_x * cm, frame1_y_offset - 7.4 * frame1_y_line_diff, 'Kicukiro District')



	p.setFont("Helvetica", 11)
	display_name = None
	ownerships = title.title_ownership.all()
	if ownerships:
		to_line = 9
		for ownership in ownerships:
			display_name = "%s ( Citizen ID: %s )" % (ownership.owner.name, ownership.owner.identifier)
			if to_line == 9:
				p.drawString(border_x * cm, frame1_y_offset - to_line * frame1_y_line_diff, "To: %s" % display_name)
			else:
				p.drawString(border_x * cm + 18.5, frame1_y_offset - to_line * frame1_y_line_diff, display_name)
			to_line += 1

	elif not ownerships and title.last_name:
		display_name = ("%s %s %s " % (title.first_name or '', title.middle_name or '', title.last_name or '')).replace('  ', '').strip()
		p.drawString(border_x * cm, frame1_y_offset - 9 * frame1_y_line_diff, 'To: %s' % display_name)


	frame1_y_offset -= 2*cm
	p.setFont("Helvetica-Bold", 9)
	p.drawString(border_x * cm, frame1_y_offset - 11 * frame1_y_line_diff, 'LAND LEASE - PROPERTY LOCATION AND DESCRIPTION')
	p.setFont("Helvetica", 11)
	p.drawString(border_x * cm, frame1_y_offset - 12 * frame1_y_line_diff, 'UPI: %s' % title.prop.upi)
	p.drawString(border_x * cm, frame1_y_offset - 13 * frame1_y_line_diff, 'Area: %s sqm' % intcomma('%.f' % title.prop.area))
	p.drawString(border_x * cm, frame1_y_offset - 14 * frame1_y_line_diff, 'Land use: %s' % title.prop.land_zone.name)


	#p.drawString(border_x * cm, frame1_y_offset - 14 * frame1_y_line_diff, 'UPI: 12/312/21/42342')

	address_info_x = width * 2 / 3.0 - 2 * cm
	p.drawString(address_info_x, frame1_y_offset - 12 * frame1_y_line_diff, 'Cell: %s' % title.prop.village.cell.name)
	p.drawString(address_info_x, frame1_y_offset - 13 * frame1_y_line_diff, 'Sector: %s' % title.prop.village.cell.sector)
	p.drawString(address_info_x, frame1_y_offset - 14 * frame1_y_line_diff, 'District: %s' % title.prop.village.cell.sector.district)


	# right column
	x_offset = width  * ( 1 -   33.0 / 100.0 )
	p.setFont("Helvetica", 11)
	p.drawRightString(width - border_x * cm, frame1_y_offset, 'As at %s' % date.today().strftime('%d %B %Y'))


	data = [
	['Tax/Fee', 'Period', 'Rate', 'Principle', 'Penalty', 'Interest', 'Total'],

	]

	total = 0
	for tax in fees:
		penalty, interest = tax.calc_penalty(date.today())
		subtotal = float(tax.remaining_amount) + penalty + interest
		total += subtotal

		if tax.date_from.month != 1 and tax.date_from.day != 1 or tax.date_to.month != 12 and tax.date_to.day != 31:
			period = '%s - %s' % (tax.date_from.strftime('%d/%m/%Y'), tax.date_to.strftime('%d/%m/%Y'))
		else:
			period = str(tax.date_from.year)

		data.append(['LL', period, intcomma(tax.rate), intcomma('%.f' % tax.remaining_amount), intcomma('%.f' % penalty), intcomma('%.f' % interest), intcomma('%.f' % subtotal) ])

	data.append(['', '', '', '', '', '', 'Total outstanding   %s Rwf' % intcomma('%.f' % total)],)


	table_style = TableStyle(
		[('LINEBELOW', (0,0), (-1,0), 1, colors.grey),
		('FONT', (0,0), (-1,0), 'Helvetica-Bold', 10),
		('FONT', (0,1), (-1,-1), 'Helvetica', 10),
		('ALIGN', (-1,0), (-1,-1,), 'RIGHT'),
		('LINEABOVE', (-2,-1), (-1,-1), 1, colors.grey),
		('FONT', (-2,-1), (-1,-1), 'Helvetica-Bold', 10),
		]
	)
	table = Table(data, colWidths=(1.5*cm, 4*cm, 2*cm, 2*cm, 2.5*cm, 2*cm, 2*cm), style=table_style)
	table.wrapOn(p, width, height)
	table.drawOn(p, border_x*cm, height / 2.0 - 1*cm )
	#--------------------------------signatures
	sig_y_height = height / 3.0
	p.setStrokeColor(colors.grey)

	p.setDash(1)
	p.line(border_x * cm, sig_y_height -  0.3 *cm, 9 * cm, sig_y_height -  0.3 *cm)
	p.setDash(1,2)
	p.setFont("Helvetica-Bold", 11)
	p.drawString(border_x * cm, sig_y_height, 'On behalf of the District')
	p.setFont("Helvetica", 11)
	p.drawString(border_x * cm, sig_y_height - 3 * frame1_y_line_diff, 'Done by:')
	p.line(4.5 * cm, sig_y_height - 3 * frame1_y_line_diff, 9 * cm, sig_y_height - 3 * frame1_y_line_diff)
	p.drawString(border_x * cm, sig_y_height - 5 * frame1_y_line_diff, 'Signature:')
	p.line(4.5 * cm, sig_y_height - 5 * frame1_y_line_diff, 9 * cm, sig_y_height - 5 * frame1_y_line_diff)
	p.drawString(border_x * cm, sig_y_height - 7 * frame1_y_line_diff, 'Title:')
	p.line(3.5 * cm, sig_y_height - 7 * frame1_y_line_diff, 9 * cm, sig_y_height - 7 * frame1_y_line_diff)


	p.setDash(1)
	p.line(address_info_x, sig_y_height -  0.3 *cm, width - border_x * cm, sig_y_height -  0.3 *cm)
	p.setDash(1,2)
	p.setFont("Helvetica-Bold", 11)
	p.drawString(address_info_x, sig_y_height , 'On behalf of Propertmode Rwanda')
	p.setFont("Helvetica", 11)
	p.drawString(address_info_x, sig_y_height - 3 * frame1_y_line_diff, 'Done by:')
	p.line(14 * cm, sig_y_height - 3 * frame1_y_line_diff, 18.5 * cm, sig_y_height - 3 * frame1_y_line_diff)
	p.drawString(address_info_x, sig_y_height - 5 * frame1_y_line_diff, 'Signature:')
	p.line(14* cm, sig_y_height - 5 * frame1_y_line_diff, 18.5 * cm, sig_y_height - 5 * frame1_y_line_diff)
	p.drawString(address_info_x, sig_y_height - 7 * frame1_y_line_diff, 'Title:')
	p.line(13 * cm, sig_y_height - 7 * frame1_y_line_diff, 18.5 * cm, sig_y_height - 7 * frame1_y_line_diff)


	#----------------------------------------footer
	p.setFont("Helvetica-Bold", 9)
	p.drawString(border_x * cm, 5.1 *cm, 'PAYMENT METHODS')
	payment_text = """
	Only payments made to District bank accounts will be deemed valid payments.
	Bank receipts must be presented to District/Sector for receipting by council
	for transaction to be complete.
	"""
	normalStyle.fontSize = 9
	normalStyle.fontName = 'Helvetica-Oblique'
	#normalStyle.textColor = 'grey'
	footer = Paragraph(payment_text, normalStyle)
	footer.wrap(width - address_info_x - border_x * cm, 4 * cm)
	footer.drawOn(p, border_x * cm, border_y * 2.9 * cm)

	data = [
		['BANK:', 'ACCOUNT NO:'],
		['Bank of Kigali', '0299403-94'],
		['Popular Bank of Rwanda (BPR)', '400-1007454-11'],
		['Ecobank (EB)', '00101338800873101'],
	]

	table_style = TableStyle([
		('FONT', (0,0), (-1,0), 'Helvetica-Bold', 9),
		('FONT', (0,1), (-1,-1), 'Helvetica', 9),
		('LEADING', (0,0), (-1,-1), 6),
		]
	)
	table = Table(data, colWidths=(4.7*cm, 4*cm), style=table_style)
	table.wrapOn(p, width - address_info_x - border_x * cm, 4 * cm)
	table.drawOn(p, border_x*cm -5, 1 * cm )


	p.setFont("Helvetica-Bold", 9)
	p.drawString(address_info_x, border_y * 4.1 * cm, 'LATE FEES AND PENALTIES')
	footer_text = """
	Additional late fees and penalties will be calculated on date of payment. Failure to pay by due date will result in further
	action being taken. Interest on late payment calculated at 1.5% per month (or equivalent to half month). Penalties calculated
	at 10% of payment amount due (not exceeding 10,000 Rwf).

	"""
	normalStyle.fontSize = 9
	normalStyle.fontName = 'Helvetica-Oblique'
	footer = Paragraph(footer_text, normalStyle)
	footer.wrap(width - address_info_x - border_x/2.0 * cm, 4 * cm)
	footer.drawOn(p, address_info_x, border_y * 1.5 * cm)


	p.showPage()
	p.save()
	PageBreak()

def generate_notice(canvas, pagesize):

	p = canvas
	width, height = pagesize
	kigali_icon = os.path.join(settings.PROJECT_DIR, 'static', 'images', 'sectors', 'kigali_icon.gif')
	border_x = 2.5
	border_y = 1

	p.setFont("Helvetica-Bold", 16)
	p.drawCentredString(width/2.0, height - (border_y * cm), 'LAND LEASE NOTICE')

	p.setFont("Helvetica", 12)
	p.drawRightString(width - border_x * cm, height - (border_y * cm), 'Invoice No: KKREM001')

	frame1_y_offset = height - 2.3 * cm
	frame1_y_line_diff = 0.5 * cm

	p.setStrokeColor(colors.grey)
	p.line(border_x * cm, height - ( (border_y + 0.5) * cm), width - border_x * cm, height - ( (border_y + 0.5) * cm))

	p.setFont("Helvetica", 11)
	p.drawString(border_x * cm, frame1_y_offset, 'Republic of Rwanda')

	p.drawImage(kigali_icon, border_x * cm, height - 5 *cm, width=2.5*cm, height=2.5*cm)


	p.setFont("Helvetica", 11)
	p.drawString(border_x * cm, frame1_y_offset - 6.4 * frame1_y_line_diff, 'Kigali City')
	p.drawString(border_x * cm, frame1_y_offset - 7.4 * frame1_y_line_diff, 'Kicukiro District')

	p.setFont("Helvetica-Bold", 9)
	p.drawString(border_x * cm, frame1_y_offset - 10 * frame1_y_line_diff, 'SUBJECT: WARNING LETTER')


	p.setFont("Helvetica", 11)
	p.drawString(border_x * cm, frame1_y_offset - 12 * frame1_y_line_diff, 'To: Mr Shane Dale')
	p.drawString(border_x * cm, frame1_y_offset - 13 * frame1_y_line_diff, 'Address: KN5 Road')
	p.drawString(border_x * cm, frame1_y_offset - 14 * frame1_y_line_diff, 'UPI: 12/312/21/42342')

	address_info_x = width * 2 / 3.0 - 2 * cm
	p.drawString(address_info_x, frame1_y_offset - 12 * frame1_y_line_diff, 'Cell: Rukiri 1')
	p.drawString(address_info_x, frame1_y_offset - 13 * frame1_y_line_diff, 'Sector: Remera')
	p.drawString(address_info_x, frame1_y_offset - 14 * frame1_y_line_diff, 'District: GASABO')


	# right column
	x_offset = width  * ( 1 -   33.0 / 100.0 )
	p.setFont("Helvetica", 11)
	p.drawRightString(width - border_x * cm, frame1_y_offset, '1st March 2014')


	#--------paragraph 1
	para1_text = """
	Referenece is made to the article 31 of the Presidential Order no. 25/01 of 09/07/2012 establishing
	the list of fees and other charges levied by decentralised entities and determining
	their thresholds, we hereby inform you that your debt relating to the fees on 1st March 2014 is now <b>8,000 Rwf</b>.
	According to the assessment notice received on 1 March 2014, this debt includes:

	"""
	normalStyle.fontSize = 11
	normalStyle.leading = 16
	normalStyle.fontName = 'Helvetica'

	para1 = Paragraph(para1_text, normalStyle)
	para1.wrap(width - 2 * border_x * cm, 5 * cm)
	para1.drawOn(p, border_x * cm, 16.5 * cm)

	bulletStyle = ParagraphStyle("bulletStyle")
	bulletStyle.fontSize = 11
	bulletStyle.leading = 16
	bulletStyle.fontName = 'Helvetica'
	bulletStyle.leftIndent = 1.5 * cm

	bull1 = Paragraph("&bull; Fees due of....<b>5,000 Rwf</b>", bulletStyle)
	bull1.wrap(width - 2 * border_x * cm, 0.5 * cm)
	bull1.drawOn(p, border_x * cm, 15.5 * cm)

	bull2 = Paragraph("&bull; Penalties of....<b>3,000 Rwf</b>", bulletStyle)
	bull2.wrap(width - 2 * border_x * cm, 0.5 * cm)
	bull2.drawOn(p, border_x * cm, 15 * cm)

	bull3 = Paragraph("&bull; Interest of.......<b>1,000 Rwf</b> as of 1st March 2014", bulletStyle)
	bull3.wrap(width - 2 * border_x * cm, 0.5 * cm)
	bull3.drawOn(p, border_x * cm, 14.5 * cm)

	para2_text = """
	This debt must be paid not later than five days (5) upon receipt of this letter.
	"""

	para2 = Paragraph(para2_text, normalStyle)
	para2.wrap(width - 2 * border_x * cm, 0.5 * cm)
	para2.drawOn(p, border_x * cm, 13.5 * cm)


	para3_text = """
	We also take this opportunity to remind you that from 1st March 2014, this debt is always being
	increased with interest on late payment of <b>1.5%</b> per month. You are therefore advised to
	comply with tis legal requirement in order to avoid further enforment actions that may be taken
	or be prosecuted by the competent courts.
	"""

	para3 = Paragraph(para3_text, normalStyle)
	para3.wrap(width - 2 * border_x * cm, 3 * cm)
	para3.drawOn(p, border_x * cm, 10 * cm)


	p.drawString(border_x * cm, 9 *cm, 'Regards')
	p.setFont("Helvetica-Bold", 10)
	p.drawString(border_x * cm, 8 *cm, 'Executive Secretary of Kicukiro District')

	#----------------------------------------body
	p.setFont("Helvetica-Bold", 9)
	p.drawString(border_x * cm, 3 *cm, 'LATE FEES AND PENALTIES')
	footer_text = """
	Additional late fees and penalties will be calculated on date of payment. Failure to pay by due date will result in further
	action being taken. Interest on late payment calculated at 1.5% per month (or equivalent to half month). Penalties calculated
	at 8% of payment amounts due prior to 9 July 2012, and 10% thereafter (not exceeding 10,000 Rwf).

	"""
	normalStyle.fontSize = 9
	normalStyle.fontName = 'Helvetica-Oblique'
	normalStyle.leading = 12
	#normalStyle.textColor = 'grey'
	footer = Paragraph(footer_text, normalStyle)
	footer.wrap(width - 2 * border_x * cm, border_y * cm)
	footer.drawOn(p, border_x * cm, border_y * 1.5 * cm)


	p.showPage()
	p.save()
	PageBreak()


class Command(BaseCommand):
	#fixed_asset/rental_income/trading_license/cleaning_fee/market_fee/land_lease_fee
	args = ''
	help = """
	Transform old payment relational tables from jtax

	"""
	name= 'Convert land use types'

	def handle(self, *args, **options):
		current_date = date.today()
		current_year = current_date.year
		start_year = date(current_year,1,1)
		end_year = date(current_year,12,31)

		limit = 0
		counter = 0
		pagesize = A4

		land_lease = CategoryChoice.objects.get(category__code='fee_type', code='land_lease')
		for village in Village.objects.filter(cell__sector__district__name__iexact='Kicukiro'):
			print "searching %s village" % village.name
			dir_name = "%s/invoices/Kicukiro/%s/%s/%s" % (settings.ROOT_PATH, date.today().strftime('%d %B %Y'), village.cell.sector.name, village.cell.name)
			if not os.path.exists(dir_name):
				os.makedirs(dir_name)
			filename = os.path.join( dir_name, "%s-%s-%s.pdf" % (village.cell.sector.name, village.cell.name, village.name))
			p = canvas.Canvas(filename, pagesize=pagesize)

			for title in PropertyTitle.objects.filter(prop__village=village).order_by('prop__parcel_id'):
				fees = title.title_fees.filter(remaining_amount__gt=0, category=land_lease, date_from__gte=date(2011,1,1), date_to__lte=date(2013,12,31)).order_by('date_from')
				if fees:
					counter += 1
					print 'creating invoice %s' % counter
					generate_invoice(canvas=p, pagesize=pagesize, title=title, fees=fees)
		print counter







