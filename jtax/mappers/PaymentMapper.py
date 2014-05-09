from django.forms import model_to_dict
from datetime import datetime
from django.utils import timezone
from django.http import Http404,HttpResponse
from django.template.loader import get_template
from django.template import Context

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

import cStringIO as StringIO
import ho.pisa as pisa

from cgi import escape
from django.shortcuts import render_to_response, get_object_or_404
from dev1 import variables
from jtax.models import IncompletePayment
from django.db.models import Sum

class PaymentMapper:

	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Generate Incomplete Payment Pdf
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""    
	@staticmethod
	def generateIncompletePaymentPdf(payments):

		now = timezone.make_aware(datetime.now(), timezone.get_default_timezone())
		name = 'IncompletePaymentPDF_' + now.strftime("%Y_%m_%d_%H_%M")

		response = PaymentMapper.render_to_pdf(
				'tax/tax_tax_incompletepaymentpdf.html',
				{
					'pagesize':'A4',
					'title': name,
					'payments': payments,
					'now':now
				}
			)

		response['Content-Disposition'] = 'attachment; filename="' + name + '"'
		return response


	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Generate Payment Pdf
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""    
	@staticmethod
	def generatePaymentPdf(payments):

		now = timezone.make_aware(datetime.now(), timezone.get_default_timezone())
		name = 'PaymentPDF_' + now.strftime("%Y_%m_%d_%H_%M")
		"""
		return render_to_response('tax/tax_tax_paymentpdf.html',{'pagesize':'A4',
					'title':'PaymentPDF_' + now.strftime("%Y_%m_%d_%H_%M"),
					'payments': payments,
					'now':now})
		"""
		response = PaymentMapper.render_to_pdf(
				'tax/tax_tax_paymentpdf.html',
				{
					'pagesize':'A4',
					'title': name,
					'payments': payments,
					'now':now
				}
			)

		response['Content-Disposition'] = 'attachment; filename="' + name + '"'
		return response

	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Generate Invoice Id by apply tax type prefix
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""    
	@staticmethod
	def generateInvoiceId(tax_type, payment):
		if tax_type != 'misc_fee' and tax_type.find('fee') >= 0:
			fee_type = payment.fee.fee_type
			#if is cleaning fee and payment is associated with multipay receipt, use multipay invoice marking
			if fee_type == 'cleaning':
				receipt_relations = payment.receipt_relations.all().select_related('receipt')
				if receipt_relations:
					return 'MP' + str(receipt_relations[0].receipt.id)

			#otherwise use normal invoice marking
			tax_type = fee_type + "_fee"
		for i in variables.tax_and_fee_invoice_prefixes:
			if tax_type == i[1]:
				return i[0] + str(payment.id)

	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Generate ePay Number by apply tax type prefix - in exception for Cleaning Fee
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""    
	@staticmethod
	def generateEpayNo(tax_type, tax):
		if tax_type == 'fee':
			tax_type = tax.fee_type + "_fee"

		mark = 'E'
		for i in variables.tax_and_fee_invoice_prefixes:
			if tax_type == i[1]:
				mark = mark + i[0]

		#for cleaning fee, link the ePay number with the business instead so all cleaning fee
		#for a business will use the same ePay Number
		if tax_type == 'fee' and tax.fee_type == 'cleaning':
			return mark + tax.business.id
		else:
			return mark + str(tax.id)

	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Convert ePay Number back to Tax - with exception of Cleaning Fee
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""    
	@staticmethod
	def convertEpayNoToTax(epay_no):


		#for cleaning fee, link the ePay number with the business instead so all cleaning fee
		#for a business will use the same ePay Number
		if tax_type == 'fee' and tax.fee_type == 'cleaning':
			return mark + tax.business.id
		else:
			return mark + str(tax.id)


	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Function to convert Html to Pdf file
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""    
	@staticmethod
	def render_to_pdf(template_src, context_dict):
		template = get_template(template_src)
		context = Context(context_dict)
		html  = template.render(context)
		result = StringIO.StringIO()

		pdf = pisa.pisaDocument(StringIO.StringIO(html.encode("ISO-8859-1")), result)
		if not pdf.err:
			return HttpResponse(result.getvalue(), mimetype='application/pdf')
		return HttpResponse('We had some errors<pre>%s</pre>' % escape(html))


	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Function to get Unallocated Payment statistic for Report
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""    
	@staticmethod
	def getUnallocatedPaymentStatistic(conditions):
		items = IncompletePayment.objects.filter(i_status="active")

		if conditions.has_key('district'):
			items = items.filter(sector__district = conditions['district'])
		if conditions.has_key('sector'):
			items = items.filter(sector = conditions['sector'])
		if conditions.has_key('cell'):
			items = items.filter(cell = conditions['cell'])
		if conditions.has_key('calendar_year'):
			items = items.filter(period_from__year= int(conditions['calendar_year']))
		if conditions.has_key('month_range'):
			items = items.filter(period_from__range= conditions['month_range'])
		if conditions.has_key('fee_type'):
			items = items.filter(tax_type=(conditions['fee_type'] + "_fee"))
		if conditions.has_key('tax_type'):
			items = items.filter(tax_type=conditions['tax_type'])


		total = 0
		total_count = 0
		if items:
			total = items.aggregate(Sum('paid_amount'))['paid_amount__sum']
			total_count = items.count()

		return {'amount':total,'count':total_count}


