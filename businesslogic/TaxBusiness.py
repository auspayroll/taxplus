from jtax.mappers.DeclaredValueMapper import DeclaredValueMapper
from jtax.mappers.PropertyTaxItemMapper import PropertyTaxItemMapper
from jtax.mappers.LandRentalTaxMapper import LandRentalTaxMapper
from property.models import Ownership
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
    def getTaxSummary(plotid):
        summaryInfo = {}
        owners = []
        
        if DeclaredValueMapper.hasDeclaredValue(plotid):
            summaryInfo["declaredValueIsDue"] = DeclaredValueMapper.isDeclaredValueDue(plotid)
            summaryInfo["declaredValueDueDate"] = DeclaredValueMapper.getDeclaredValueDueDate(plotid)
            if DeclaredValueMapper.getDeclaredValueByPlotId(plotid):
                summaryInfo["declaredValue"] = DeclaredValueMapper.getDeclaredValueAmountByPlotId(plotid)
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
        
        ownerships = Ownership.objects.filter(property__plotid=plotid).filter(active=True)
        if len(ownerships) > 0:
            for ownership in ownerships:
                citizen = ownership.citizen                
                owners.append(citizen)
        summaryInfo['owners']=owners
        
        return summaryInfo



    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Generate new property tax for a property.
    Return newly generated tax items.
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @staticmethod
    def generatePropertyTax(request,plotid):
        declaredValues = DeclaredValueMapper.getDeclaredValuesByPlotId(plotid)
        
        # No declared values at all
        if declaredValues is None:
            return None
        
        ## No usable declared values to generate tax due form.
        declaredValueDueDate = None
        declaredValue = DeclaredValueMapper.getDeclaredValueByPlotId(plotid)
        lastSecondDeclaredValue = DeclaredValueMapper.getLastSecondDeclaredValueByPlotId(plotid)
        declaredValueDueDate = declaredValue.DeclaredValueDateTime + relativedelta(years=3)
        now = datetime.now()
        now = timezone.make_aware(now, timezone.get_default_timezone())
        d = Common.localizeDate(declaredValue.DeclaredValueDateTime)
        
        #imezone.make_aware(d, timezone.get_default_timezone())
        
        if now > declaredValueDueDate:
            return None
        
        ## get the start day to generate new proeprty tax.
        financial_year_start_date = None
        financial_year_end_date = None
        
        propertytaxitem = PropertyTaxItemMapper.getPropertyTaxItemByPlotId(plotid)            
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
            financial_year_start_date = propertytaxitem.enddate + relativedelta(days = 1)
            financial_year_end_date = propertytaxitem.enddate + relativedelta(years = 1)
        
        
       
        financial_year_start_date=Common.localizeDate(financial_year_start_date)
        financial_year_end_date=Common.localizeDate(financial_year_end_date)
   
        tax_items = []
        if d > financial_year_start_date:
            part1_days = (d - financial_year_start_date).days
            part2_days = (financial_year_end_date -d).days + 2
            total_days = (financial_year_end_date - financial_year_start_date).days + 1
            
            if lastSecondDeclaredValue is None:
                tax_item = PropertyTaxItem()
                tax_item.plotid = plotid
                tax_item.amount = 0.00
                tax_item.currency = declaredValue.DeclaredValueAmountCurrencey
                tax_item.startdate = financial_year_start_date
                tax_item.enddate = d - relativedelta(days = 1)   
                tax_item.staffid = request.session['user'].id
                tax_item.isaccepted = False
                tax_item.ispaid = False
                tax_item.isReviewed = False
                tax_item.isChallenged = False
                tax_item.dategenerated = now
                tax_item.save()
                tax_items.append(tax_item)
                
                tax_item1 = PropertyTaxItem()
                tax_item1.plotid = plotid
                tax_item1.amount = declaredValue.DeclaredValueAmount * 0.02 * part2_days / total_days
                tax_item1.amount = Common.floatToDecimal(tax_item1.amount)
                tax_item1.currency = declaredValue.DeclaredValueAmountCurrencey
                tax_item1.startdate = d
                tax_item1.enddate = financial_year_end_date    
                tax_item1.staffid = request.session['user'].id
                tax_item1.isaccepted = False
                tax_item1.ispaid = False
                tax_item1.isReviewed = False
                tax_item1.isChallenged = False
                tax_item1.dategenerated = now
                tax_item1.save()
                tax_items.append(tax_item1)
            else:
                tax_item = PropertyTaxItem()
                tax_item.plotid = plotid
                tax_item.amount = 0.2 * declaredValue.DeclaredValueAmount * part1_days / total_days + 0.2 * declaredValue.DeclaredValueAmount * part2_days / total_days
                tax_item.amount = Common.floatToDecimal(tax_item.amount)
                tax_item.currency = declaredValue.DeclaredValueAmountCurrencey
                tax_item.startdate = financial_year_start_date
                tax_item.enddate = financial_year_end_date    
                tax_item.staffid = request.session['user'].id
                tax_item.isaccepted = False
                tax_item.ispaid = False
                tax_item.isReviewed = False
                tax_item.isChallenged = False
                tax_item.dategenerated = now
                tax_item.save()
                tax_items.append(tax_item)
            financial_year_start_date = financial_year_start_date + relativedelta(years = 1)
            financial_year_end_date = financial_year_end_date + relativedelta(years = 1)
        
        while(financial_year_start_date <= now + relativedelta(years = 2)): 
            tax_item = PropertyTaxItem()
            tax_item.plotid = plotid
            tax_item.amount = declaredValue.DeclaredValueAmount * 0.02
            tax_item.amount = Common.floatToDecimal(tax_item.amount)
            tax_item.currency = declaredValue.DeclaredValueAmountCurrencey
            tax_item.startdate = financial_year_start_date
            tax_item.enddate = financial_year_end_date    
            tax_item.staffid = request.session['user'].id
            tax_item.isaccepted = False
            tax_item.ispaid = False
            tax_item.isReviewed = False
            tax_item.isChallenged = False
            tax_item.dategenerated = now
            tax_item.save()
            tax_items.append(tax_item)
            financial_year_start_date = financial_year_start_date + relativedelta(years=1)
            financial_year_end_date = financial_year_end_date + relativedelta(years=1)
        return tax_items



 


























 