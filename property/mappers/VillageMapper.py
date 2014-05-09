from property.models import Village
from annoying.functions import get_object_or_None

class VillageMapper:	

	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get village by code
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""	
	@staticmethod
	def getVillageByCode(code):
		village = Village.objects.filter(code__iexact = code)
		if not village:
			return None
		else:
			return village[0]
	
	@staticmethod
	def getVillageById(obj_id):
		return get_object_or_None(Village, id = obj_id)
	
	@staticmethod
	def getById(id):
		return VillageMapper.getVillageById(id)