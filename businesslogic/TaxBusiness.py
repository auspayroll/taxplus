from jtax.mappers.DeclaredValueMapper import DeclaredValueMapper
from jtax.mappers.PropertyTaxMapper import PropertyTaxMapper
from jtax.mappers.LandRentalTaxMapper import LandRentalTaxMapper
from property.models import Ownership

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
            
        if PropertyTaxMapper.hasPropertyTax(plotid):
            summaryInfo["propertyTaxDue"] = PropertyTaxMapper.isPropertyTaxDue(plotid)
            summaryInfo["propertyTaxDueDate"] = PropertyTaxMapper.getPropertyTaxDueDate(plotid)
        else:
            summaryInfo["propertyTaxDue"] = 'N/A'
            summaryInfo["propertyTaxDueDate"] = 'N/A'
        if LandRentalTaxMapper.hasRentalTax(plotid):
            summaryInfo["rentalTaxDue"] = LandRentalTaxMapper.isRentalTaxDue(plotid)
            summaryInfo["rentalTaxDueDate"] = LandRentalTaxMapper.getRentalTaxDueDate(plotid)
        else:
            summaryInfo["rentalTaxDue"] = 'N/A'
            summaryInfo["rentalTaxDueDate"] = 'N/A'
        
        
        ownerships = Ownership.objects.filter(property__plotid=plotid).filter(active=True)
        if len(ownerships) > 0:
            for ownership in ownerships:
                citizen = ownership.citizen                
                owners.append(citizen)
        summaryInfo['owners']=owners
        
        return summaryInfo
 