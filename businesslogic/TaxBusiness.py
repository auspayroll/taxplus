from jtax.mappers.DeclaredValueMapper import DeclaredValueMapper
from jtax.mappers.PropertyTaxItemMapper import PropertyTaxItemMapper
from jtax.mappers.LandRentalTaxMapper import LandRentalTaxMapper
from property.mappers.OwnershipMapper import OwnershipMapper
from datetime import datetime
from django.utils import timezone
from admin.Common import Common
from dateutil.relativedelta import relativedelta
from jtax.models import PropertyTaxItem

class TaxBusiness:
	
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get tax summary for a property, including owners info.
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def getTaxSummary(property):
		summaryInfo = {}
		owners = []
		
		if DeclaredValueMapper.hasDeclaredValue(property):
			summaryInfo["declaredValueIsDue"] = DeclaredValueMapper.isDeclaredValueDue(property)
			summaryInfo["declaredValueDueDate"] = DeclaredValueMapper.getDeclaredValueDueDate(property)
			if DeclaredValueMapper.getDeclaredValueByProperty(property):
				summaryInfo["declaredValue"] = DeclaredValueMapper.getDeclaredValueAmountByProperty(property)
			else:
				summaryInfo["declaredValue"] = "N/A"
		else:
			summaryInfo["declaredValueIsDue"] = 'N/A'
			summaryInfo["declaredValueDueDate"] = 'N/A'
			summaryInfo["declaredValue"] = 'N/A'
			summaryInfo["declaredValue"] = None
			
		summaryInfo["propertyTaxDue"] = 'N/A'
		summaryInfo["propertyTaxDueDate"] = 'N/A'

		summaryInfo["rentalTaxDue"] = 'N/A'
		summaryInfo["rentalTaxDueDate"] = 'N/A'
		
		ownerships = OwnershipMapper.getAllOwnershipsByProperty(property)
		if len(ownerships) > 0:
			for ownership in ownerships:
				citizen = ownership.owner_citizen				
				owners.append(citizen)
		summaryInfo['owners']=owners
		
		return summaryInfo



	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Generate new property tax for a property.
	Return newly generated tax items.
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def generatePropertyTax(request,property):
		declaredValues = DeclaredValueMapper.getDeclaredValuesByProperty(property)
		
		# No declared values at all
		if declaredValues is None:
			return None
		
		## No usable declared values to generate tax due form.
		declaredValueDueDate = None
		declaredValue = DeclaredValueMapper.getDeclaredValueByProperty(property)
		lastSecondDeclaredValue = DeclaredValueMapper.getLastSecondDeclaredValueByProperty(property)
		declaredValueDueDate = declaredValue.date_time + relativedelta(years=3)
		now = datetime.now()
		now = timezone.make_aware(now, timezone.get_default_timezone())
		d = Common.localizeDate(declaredValue.date_time)
		
		#imezone.make_aware(d, timezone.get_default_timezone())
		
		if now > declaredValueDueDate:
			return None
		
		## get the start day to generate new proeprty tax.
		financial_year_start_date = None
		financial_year_end_date = None
		
		propertytaxitem = PropertyTaxItemMapper.getPropertyTaxItem(property)			
		if propertytaxitem is None:
			year = d.year
			month = d.month
			if month >= 7:
				financial_year_start_date = datetime(year, 7, 1)
				financial_year_end_date = datetime(year + 1, 6, 30)
			else:
				financial_year_start_date = datetime(year-1, 7, 1)
				financial_year_end_date = datetime(year, 6, 30)
		else:		   
			financial_year_start_date = propertytaxitem.period_to + relativedelta(days = 1)
			financial_year_end_date = propertytaxitem.period_to + relativedelta(years = 1)
		
		financial_year_start_date=Common.localizeDate(financial_year_start_date)
		financial_year_end_date=Common.localizeDate(financial_year_end_date)

		tax_items = []
		if d > financial_year_start_date:
			part1_days = (d - financial_year_start_date).days
			part2_days = (financial_year_end_date -d).days + 2
			total_days = (financial_year_end_date - financial_year_start_date).days + 1
			
			if lastSecondDeclaredValue is None:
				tax_item = PropertyTaxItem()
				tax_item.property = property
				tax_item.amount = 0.00
				tax_item.currency = declaredValue.currency
				tax_item.period_from = financial_year_start_date
				tax_item.period_to = d - relativedelta(days = 1)   
				tax_item.staff_id = request.session['user'].id
				tax_item.is_accepted = False
				tax_item.is_paid = False
				tax_item.is_reviewed = False
				tax_item.is_challenged = False
				tax_item.date_time = now
				tax_item.due_date = now + relativedelta(days = 14)   
				tax_item.save()
				tax_items.append(tax_item)
				
				tax_item1 = PropertyTaxItem()
				tax_item1.property = property
				tax_item1.amount = declaredValue.amount * 0.02 * part2_days / total_days
				tax_item1.amount = Common.floatToDecimal(tax_item1.amount)
				tax_item1.currency = declaredValue.currency
				tax_item1.period_from = d
				tax_item1.period_to = financial_year_end_date	
				tax_item1.staff_id = request.session['user'].id
				tax_item1.is_accepted = False
				tax_item1.is_paid = False
				tax_item1.is_reviewed = False
				tax_item1.is_challenged = False
				tax_item1.date_time = now
				tax_item.due_date = now + relativedelta(days = 14)   
				tax_item1.save()
				tax_items.append(tax_item1)
			else:
				tax_item = PropertyTaxItem()
				tax_item.property = property
				tax_item.amount = 0.2 * declaredValue.amount * part1_days / total_days + 0.2 * declaredValue.amount * part2_days / total_days
				tax_item.amount = Common.floatToDecimal(tax_item.amount)
				tax_item.currency = declaredValue.currency
				tax_item.period_from = financial_year_start_date
				tax_item.perod_to = financial_year_end_date	
				tax_item.staff_id = request.session['user'].id
				tax_item.is_accepted = False
				tax_item.is_paid = False
				tax_item.is_reviewed = False
				tax_item.is_challenged = False
				tax_item.date_time = now
				tax_item.due_date = now + relativedelta(days = 14)   
				tax_item.save()
				tax_items.append(tax_item)
			financial_year_start_date = financial_year_start_date + relativedelta(years = 1)
			financial_year_end_date = financial_year_end_date + relativedelta(years = 1)
		
		while(financial_year_start_date <= now + relativedelta(years = 2)): 
			tax_item = PropertyTaxItem()
			tax_item.property = property
			tax_item.amount = declaredValue.amount * 0.02
			tax_item.amount = Common.floatToDecimal(tax_item.amount)
			tax_item.currency = declaredValue.currency
			tax_item.period_from = financial_year_start_date
			tax_item.period_to = financial_year_end_date	
			tax_item.staff_id = request.session['user'].id
			tax_item.is_accepted = False
			tax_item.is_paid = False
			tax_item.is_reviewed = False
			tax_item.is_challenged = False
			tax_item.date_time = now
			tax_item.due_date = now + relativedelta(days = 14)   
			tax_item.save()
			tax_items.append(tax_item)
			financial_year_start_date = financial_year_start_date + relativedelta(years=1)
			financial_year_end_date = financial_year_end_date + relativedelta(years=1)
		return tax_items




























 