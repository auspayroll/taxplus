from jtax.models import DeclaredValue
from citizen.mappers.CitizenMapper import CitizenMapper
from auth.mappers.UserMapper import UserMapper
from citizen.mappers.CitizenMapper import CitizenMapper
from datetime import datetime
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from admin.Common import Common

class DeclaredValueMapper:    
          
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Get declared value history of a property
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""    
    @staticmethod        
    def getDeclaredValuesByPlotId(plotid):
        declareValues = DeclaredValue.objects.filter(PlotId = plotid)
        if len(declareValues) == 0:
            return None
        else:
            declareValues = list(declareValues)
            declareValues.sort(key=lambda x:x.DeclaredValueDateTime, reverse=True)
            return declareValues
    
        
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Get the most recent declared value of a property
    return {{DeclaredValue object}}
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""    
    @staticmethod    
    def getDeclaredValueByPlotId(plotid):
        declaredValues=DeclaredValueMapper.getDeclaredValuesByPlotId(plotid)
        if not declaredValues:
            return None
        else:
            return declaredValues[0]
        
        
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Get the most recent declared value of a property
    Format: {{currency}} {{amount}}
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""    
    @staticmethod    
    def getDeclaredValueAmountByPlotId(plotid):
        declaredValue=DeclaredValueMapper.getDeclaredValueByPlotId(plotid)
        if not declaredValue:
            return None
        else:
            return declaredValue.DeclaredValueAmountCurrencey + ' '+ str(declaredValue.DeclaredValueAmount)
    
        
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Get declared value history of a property with extra info:
    1) DeclaredBy
    2) DeclaredValueOfficial
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""    
    @staticmethod   
    def getCleanDeclaredValuesByPlotId(plotid):
        declaredValues=DeclaredValueMapper.getDeclaredValuesByPlotId(plotid)
        if not declaredValues:
            return None
        else:
            declaredValues = list(declaredValues)
            declaredValues.sort(key=lambda x:x.DeclaredValueDateTime, reverse=True)
            declaredValues = Common.formatObject(declaredValues)
            declaredValues_new = []
            for declaredValue in declaredValues:
                citizen = CitizenMapper.getCitizenById(declaredValue.DeclaredValueCitizenId)
                declaredValue.DeclaredBy = CitizenMapper.getDisplayName(citizen)
                user = UserMapper.getUserById(declaredValue.DeclaredValueStaffId)
                declaredValue.DeclaredValueOfficial = UserMapper.getFullName(user)
                declaredValues_new.append(declaredValue)
            return declaredValues_new
    
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Check whether the property associated with a plot ID has declared history
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @staticmethod
    def hasDeclaredValue(plotid):
        declaredValues = DeclaredValueMapper.getDeclaredValuesByPlotId(plotid)
        if declaredValues:
            return True
        else:
            return False
    
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Get the declared value due date of a property with the specified plot ID
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @staticmethod
    def getDeclaredValueDueDate(plotid):
        declaredValue = DeclaredValueMapper.getDeclaredValueByPlotId(plotid)
        if declaredValue:
            dueDate = declaredValue.DeclaredValueDateTime + relativedelta(years=4)
            return dueDate.strftime('%Y-%m-%d')
        else:
            return "N/A"
        
        
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Check whether declared value of a property with a specified plot ID is due
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @staticmethod            
    def isDeclaredValueDue(plotid):
        declaredValue = DeclaredValueMapper.getDeclaredValueByPlotId(plotid)
        if declaredValue:
            dueDate = declaredValue.DeclaredValueDateTime + relativedelta(years=4)
            now = datetime.now()
            now = timezone.make_aware(now, timezone.get_default_timezone())
            if dueDate >= now:
                return True
            else:
                return False
        return "N/A"
    
