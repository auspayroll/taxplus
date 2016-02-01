#from django.utils import simplejson
import json as simplejson
from property.models import Sector
from django.db.models.query import QuerySet


class SectorMapper:

	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get all Sectors
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def getAllSectors():
		return Sector.objects.all()


	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get Sector by id
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def getSectorById(id):
		sector = Sector.objects.filter(id = id)
		if not sector:
			return None
		else:
			return sector[0]


	@staticmethod
	def getById(id):
		return SectorMapper.getSectorById(id)


	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get Sector by code
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def getSectorByCode(code):
		sector = Sector.objects.filter(code_iexact = code)
		if not sector:
			return None
		else:
			return sector[0]
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get Sector by name
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def getSectorByName(name):
		sector = Sector.objects.filter(name__iexact = name)
		if not sector:
			return None
		else:
			return sector[0]



	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get Sectors by district name
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def getSectorsByDistrictName(name):
		return Sector.objects.filter(district__name = name)


	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get Sectors by district name and sector name
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def getSectorsByDistrictAndName(districtName, sectorName):
		return Sector.objects.filter(district__name__iexact = districtName, name__iexact = sectorName)


	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get Sectors by district name and sector name
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def getSectorByDistrictNameAndSectorName(districtName, sectorName):
		sector = Sector.objects.filter(district__name__iexact = districtName, name__iexact = sectorName)
		if not sector:
			return None
		else:
			return sector[0]


	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get Sectors by council name
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def getSectorsByCouncilName(name):
		return Sector.objects.filter(council__name = name)


	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	search Sector by keyword
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def searchSectorsByKeyword(request, keyword):
		user = request.session.get("user")
		if user.is_superuser:
			return Sector.objects.filter(name__icontains=keyword)
		else:
			council = user.council
			return Sector.objects.filter(name__icontains=keyword).filter(council = council)


	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	get geodata of Sector
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def getSectorGeoData(sectors):
		data = {}
		sectors_new = []
		if type(sectors) == list:
			sectors_new = sectors
		elif type(sectors) == QuerySet:
			for sector in sectors:
				sectors_new.append(sector)
		else:
			sectors_new.append(sectors)

		sectors = []

		# return json
		for sector in sectors_new:
			points_json = []
			sector_json = {}
			boundary=sector.boundary
			str1=str(boundary.polygon.wkt)
			str1=str1.replace('POLYGON', '').replace('((', '').replace('))', '')[1:]
			points = str1.split(', ')
			for point in points:
				point_json={}
				point_parts = point.split(' ')
				point_x_parts=point_parts[0].replace(' ','').split('.')
				point_x=point_x_parts[0]+'.'+point_x_parts[1][:5]
				point_y_parts=point_parts[1].replace(' ','').split('.')
				point_y=point_y_parts[0]+'.'+point_y_parts[1][:5]
				point_json['x']=point_x
				point_json['y']=point_y
				points_json.append(point_json)
			sector_json['points']=points_json
			sector_json['name']=sector.name
			sectors.append(sector_json)
		data['sectors'] = sectors
		return simplejson.dumps(data)



