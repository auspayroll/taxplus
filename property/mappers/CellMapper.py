from django.utils import simplejson
from property.models import *
from django.db.models.query import QuerySet


class CellMapper:	
 

	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get cell by code
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""	
	@staticmethod
	def getCellByCode(code):
		cell = Cell.objects.filter(code__iexact = code)
		if not cell:
			return None
		else:
			return cell[0]
		
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get cell by id
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""	
	@staticmethod
	def getCellById(id):
		cell = Cell.objects.filter(pk = id)
		if not cell:
			return None
		else:
			return cell[0]
		
	@staticmethod
	def getById(id):
		return CellMapper.getCellById(id)

	@staticmethod
	def getCellsBySector(sector):
		objects = Property.objects.filter(sector = sector).distinct('cell').values('cell')
		cells = []
		for obj in objects:
			cells.append(obj['cell'])
		return cells


	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	get geodata of Sector
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""	
	@staticmethod
	def getCellGeoDataBySector(sector):
		cells = []
		cells = CellMapper.getCellsBySector(sector)
		data = {}

		count = 0

		# return json  
		for cell in cells:
			cell_json = {}
			cell_json['cell'] = cell
			points_json = []
			points = []
			properties = Property.objects.filter(sector = sector).filter(cell = cell)
			for property in properties:
				count = count + 1
				print count
				point = property.boundary.central_point
				point_json = {}
				str1 =  str(point)
				str1=str1.replace('POINT ', '').replace('(', '').replace(')', '')
				point_parts = str1.split(' ')
				point_x_parts=point_parts[0].replace(' ','').split('.')
				point_x=point_x_parts[0]+'.'+point_x_parts[1][:5]
				point_y_parts=point_parts[1].replace(' ','').split('.')
				point_y=point_y_parts[0]+'.'+point_y_parts[1][:5]
				point_json['x']=point_x
				point_json['y']=point_y
				points_json.append(point_json)
			cell_json['points']=points_json
			cells.append(cell_json)
		data['cells'] = cells
		return simplejson.dumps(data)