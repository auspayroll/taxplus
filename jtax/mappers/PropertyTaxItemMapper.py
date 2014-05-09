from jtax.models import PropertyTaxItem
from admin.Common import Common
from pmauth.models import PMUser
from citizen.mappers.CitizenMapper import CitizenMapper

class PropertyTaxItemMapper:
	
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	The following methods to be complted later...
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	
	@staticmethod
	def hasPropertyTaxItem(plot_id):
		return False
	@staticmethod
	def isPropertyTaxItemDue(plot_id):
		return False
	@staticmethod
	def getPropertyTaxItemDueDate(plot_id):
		return "N/A"
	
	
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get property tax items of a property with a specified plot ID
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""	
	@staticmethod		
	def getPropertyTaxItems(property):
		propertyTaxItems = PropertyTaxItem.objects.filter(property=property)
		if len(propertyTaxItems) == 0:
			return None
		else:
			propertyTaxItems = list(propertyTaxItems)
			propertyTaxItems.sort(key=lambda x:x.period_to, reverse=True)
			return propertyTaxItems
	
	
	
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get property tax items of a property with a specified plot ID
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""	
	@staticmethod		
	def getPropertyTaxItemsByPlotIdAsc(plot_id):
		objects = PropertyTaxItem.objects.filter(plot_id__iexact = plot_id)
		propertyTaxItems = PropertyTaxItem.objects.filter(plot_id__iexact = plot_id)
		if len(propertyTaxItems) == 0:
			return None
		else:
			propertyTaxItems = list(propertyTaxItems)
			propertyTaxItems.sort(key=lambda x:x.period_to, reverse=False)
			return propertyTaxItems
	
	
	
	
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get property tax items of a property with a specified plot ID
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""	
	@staticmethod		
	def getPropertyTaxItemsAsc(property):
		propertyTaxItems = PropertyTaxItem.objects.filter(property = property)
		if len(propertyTaxItems) == 0:
			return None
		else:
			propertyTaxItems = list(propertyTaxItems)
			propertyTaxItems.sort(key=lambda x:x.period_to, reverse=False)
			return propertyTaxItems
	
	
	
	
	
	
	
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get property tax items of a property with a specified plot ID
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""	
	@staticmethod		
	def getPropertyTaxItem(property):
		propertyTaxItems = PropertyTaxItemMapper.getPropertyTaxItems(property)
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
	def getCleanPropertyTaxItems(property):
		propertyTaxItems = PropertyTaxItemMapper.getPropertyTaxItemsAsc(property)
		if not propertyTaxItems:
			return None
		else:
			propertyTaxItems = Common.objToJson(propertyTaxItems)
			propertyTaxItems_new = []
			for propertyTaxItem in propertyTaxItems:
				staff_id = propertyTaxItem['staff_id']
				user = PMUser.getUserById(int(staff_id))
				propertyTaxItem['staff_id'] = user.getFullName()
				propertyTaxItems_new.append(propertyTaxItem)
			return propertyTaxItems_new
	
	
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get property tax history of a property with extra info:
	1) DeclaredBy
	2) DeclaredValueOfficial
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""   
	"""
	@staticmethod   
	def getCleanPropertyTaxItems(propertyTaxItems):
		if not propertyTaxItems:
			return None
		else:	
			propertyTaxItems = Common.objToJson(propertyTaxItems)
			propertyTaxItems_new = []
			for propertyTaxItem in propertyTaxItems:
				staff_id = propertyTaxItem['staff_id']
				user = UserMapper.getUserById(int(staff_id))
				propertyTaxItem['staff_id'] = UserMapper.getFullName(user)
				propertyTaxItems_new.append(propertyTaxItem)
			return propertyTaxItems_new
	"""