from property.models import District
import logging

class DistrictMapper:	
		  
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get all Districts
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""	
	@staticmethod
	def getAllDistricts():
		districts = District.objects.all()
		return District.objects.all()
	
	
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get district by id
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""	
	@staticmethod
	def getDistrictById(id):
		district = District.objects.filter(id = id)
		if not district:
			return None
		else:
			return district[0]
		

	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get district by code
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""	
	@staticmethod
	def getDistrictByCode(code):
		district = District.objects.filter(code__iexact = code)
		if not district:
			return None
		else:
			return district[0]


	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get district by id
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""	
	@staticmethod
	def getDistrictById(id):
		district = District.objects.filter(id = id)
		if not district:
			return None
		else:
			return district[0]
		
	@staticmethod
	def getById(id):
		return DistrictMapper.getDistrictById(id)
		
		
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get district by name
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""	
	@staticmethod
	def getDistrictByName(name):
		district = District.objects.filter(name__iexact = name)
		logging.debug("name is " + name)
		if not district:
			return None
		else:
			return district[0]
	
	
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	search district by keyword
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""	
	@staticmethod
	def searchDistrictsByKeyword(keyword):
		districts = District.objects.filter(name__icontains=keyword)
		return districts
