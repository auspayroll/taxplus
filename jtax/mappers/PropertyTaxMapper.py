from jtax.models import PropertyTax
from admin.Common import Common
from citizen.mappers.CitizenMapper import CitizenMapper
from auth.mappers.UserMapper import UserMapper

class PropertyTaxMapper:
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    The following methods to be complted later...
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @staticmethod
    def getPropertyTax(plotid):
        return None
    @staticmethod
    def hasPropertyTax(plotid):
        return False
    @staticmethod
    def isPropertyTaxDue(plotid):
        return False
    @staticmethod
    def getPropertyTaxDueDate(plotid):
        return "N/A"
    
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Get property tax history of a property with a specified plot ID
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""    
    @staticmethod        
    def getPropertyTaxesByPlotId(plotid):
        propertyTaxes = PropertyTax.objects.filter(PlotId = plotid)
        if len(propertyTaxes) == 0:
            return None
        else:
            propertyTaxes = list(propertyTaxes)
            propertyTaxes.sort(key=lambda x:x.PropertyTaxDateTime, reverse=True)
            return propertyTaxes
    
    
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Get property tax history of a property with extra info:
    1) DeclaredBy
    2) DeclaredValueOfficial
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""   
    @staticmethod   
    def getCleanPropertyTaxesByPlotId(plotid):
        propertyTaxes = PropertyTaxMapper.getPropertyTaxesByPlotId(plotid)
        if not propertyTaxes:
            return None
        else:
            propertyTaxes = Common.formatObject(propertyTaxes)
            propertyTaxes_new = []        
            for propertyTax in propertyTaxes:
                citizen = CitizenMapper.getCitizenById(propertyTax.PropertyTaxCitizenId)
                propertyTax.PaidBy = CitizenMapper.getDisplayName(citizen)
                user = UserMapper.getUserById(propertyTax.PropertyTaxStaffId)
                propertyTax.PropertyTaxOfficial = UserMapper.getFullName(user)
                propertyTaxes_new.append(propertyTax)
            return propertyTaxes_new
           
 