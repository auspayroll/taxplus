from jtax.models import DeclaredValue
from citizen.mappers.CitizenMapper import CitizenMapper
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
	def getDeclaredValuesByProperty(property):
		declareValues = DeclaredValue.objects.filter(property = property)
		if len(declareValues) == 0:
			return None
		else:
			declareValues = list(declareValues)
			declareValues.sort(key=lambda x:x.date_time, reverse=True)
			return declareValues




	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get the most recent declared value of a property
	return {{DeclaredValue object}}
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""    
	@staticmethod    
	def getDeclaredValueByProperty(property):
		declaredValues=DeclaredValueMapper.getDeclaredValuesByProperty(property)
		if not declaredValues:
			return None
		else:
			return declaredValues[0]


	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get the most recent declared value of a property
	return {{DeclaredValue object}}
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""    
	@staticmethod    
	def getLastSecondDeclaredValueByProperty(property):
		declaredValues=DeclaredValueMapper.getDeclaredValuesByProperty(property)
		if not declaredValues or len(declaredValues) < 2:
			return None
		else:
			return declaredValues[1]

	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get the most recent declared value of a property
	Format: {{currency}} {{amount}}
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""    
	@staticmethod    
	def getDeclaredValueAmountByProperty(property):
		declaredValue=DeclaredValueMapper.getDeclaredValueByProperty(property)
		if not declaredValue:
			return None
		else:
			return declaredValue.currency + ' '+ str(declaredValue.amount)

	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get declared value history of a property with extra info:
    1) DeclaredBy
    2) DeclaredValueOfficial
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""    
	@staticmethod   
	def getCleanDeclaredValuesByProperty(property):
		declaredValues=DeclaredValueMapper.getDeclaredValuesByProperty(property)
		if not declaredValues:
			return None
		else:
			declaredValues = list(declaredValues)
			declaredValues.sort(key=lambda x:x.date_time, reverse=True)
			declaredValues = Common.formatObject(declaredValues)
			declaredValues_new = []
			for declaredValue in declaredValues:
				declaredValue.DeclaredBy = CitizenMapper.getDisplayName(declaredValue.citizen)
				declaredValue.DeclaredValueOfficial = declaredValue.user.getFullName()
				declaredValues_new.append(declaredValue)
			return declaredValues_new


	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Check whether the property associated with a plot ID has declared history
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def hasDeclaredValue(property):
		declaredValues = DeclaredValueMapper.getDeclaredValuesByProperty(property)
		if declaredValues:
			return True
		else:
			return False


	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get the declared value due date of a property with the specified plot ID
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def getDeclaredValueDueDate(property):
		declaredValue = DeclaredValueMapper.getDeclaredValueByProperty(property)
		if declaredValue:
			dueDate = declaredValue.date_time + relativedelta(years=4)
			return dueDate.strftime('%Y-%m-%d')		
		else:
			return "N/A"


	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Check whether declared value of a property with a specified plot ID is due
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod            
	def isDeclaredValueDue(property):
		declaredValue = DeclaredValueMapper.getDeclaredValueByProperty(property)
		if declaredValue:
			dueDate = declaredValue.date_time + relativedelta(years=4)
			now = datetime.now()
			now = timezone.make_aware(now, timezone.get_default_timezone())
			if dueDate >= now:
				return True
			else:
				return False
		return "N/A"
