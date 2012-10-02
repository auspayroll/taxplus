from jtax.models import PropertyTaxItem
from admin.Common import Common
from citizen.mappers.CitizenMapper import CitizenMapper
from auth.mappers.UserMapper import UserMapper

class PropertyTaxItemMapper:
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    The following methods to be complted later...
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @staticmethod
    def getPropertyTaxItem(plotid):
        return None
    @staticmethod
    def hasPropertyTaxItem(plotid):
        return False
    @staticmethod
    def isPropertyTaxItemDue(plotid):
        return False
    @staticmethod
    def getPropertyTaxItemDueDate(plotid):
        return "N/A"
    
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Get property tax items of a property with a specified plot ID
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""    
    @staticmethod        
    def getPropertyTaxItemsByPlotId(plotid):
        propertyTaxItems = PropertyTaxItem.objects.filter(plotid = plotid)
        if len(propertyTaxItems) == 0:
            return None
        else:
            propertyTaxItems = list(propertyTaxItems)
            propertyTaxItems.sort(key=lambda x:x.enddate, reverse=True)
            return propertyTaxItems
    
    
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Get property tax items of a property with a specified plot ID
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""    
    @staticmethod        
    def getPropertyTaxItemsByPlotIdAsc(plotid):
        propertyTaxItems = PropertyTaxItem.objects.filter(plotid = plotid)
        if len(propertyTaxItems) == 0:
            return None
        else:
            propertyTaxItems = list(propertyTaxItems)
            propertyTaxItems.sort(key=lambda x:x.enddate, reverse=False)
            return propertyTaxItems
    
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Get property tax items of a property with a specified plot ID
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""    
    @staticmethod        
    def getPropertyTaxItemByPlotId(plotid):
        propertyTaxItems = PropertyTaxItemMapper.getPropertyTaxItemsByPlotId(plotid)
        if propertyTaxItems is None:
            return None
        else:
            return propertyTaxItems[0]
         
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Get property tax history of a property with extra info:
    1) DeclaredBy
    2) DeclaredValueOfficial
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""   
    @staticmethod   
    def getCleanPropertyTaxItemsByPlotId(plotid):
        propertyTaxItems = PropertyTaxItemMapper.getPropertyTaxItemsByPlotIdAsc(plotid)
        if not propertyTaxItems:
            return None
        else:
            propertyTaxItems = Common.objToJson(propertyTaxItems)
            propertyTaxItems_new = []
            for propertyTaxItem in propertyTaxItems:
                staffid = propertyTaxItem['staffid']
                user = UserMapper.getUserById(int(staffid))
                propertyTaxItem['staffid'] = UserMapper.getFullName(user)
                propertyTaxItems_new.append(propertyTaxItem)
            return propertyTaxItems_new
    
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Get property tax history of a property with extra info:
    1) DeclaredBy
    2) DeclaredValueOfficial
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""   
    @staticmethod   
    def getCleanPropertyTaxItems(propertyTaxItems):
        if not propertyTaxItems:
            return None
        else:    
            propertyTaxItems = Common.objToJson(propertyTaxItems)
            propertyTaxItems_new = []
            for propertyTaxItem in propertyTaxItems:
                staffid = propertyTaxItem['staffid']
                user = UserMapper.getUserById(int(staffid))
                propertyTaxItem['staffid'] = UserMapper.getFullName(user)
                propertyTaxItems_new.append(propertyTaxItem)
            return propertyTaxItems_new
    
    
           
 