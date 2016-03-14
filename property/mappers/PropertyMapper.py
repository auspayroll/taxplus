import json
from property.models import *
from asset.models import Ownership
from django.db.models.query import QuerySet
import calendar
from log.models import *
import datetime
from dateutil.relativedelta import relativedelta
from django.db import connection
from django.http import HttpResponse
from django.db.models import Q,Sum


class PropertyMapper:

	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get all properties
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def getAllProperties():
		return Property.objects.all()


	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get Property by Property ID
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def getPropertyById(id):
		property = Property.objects.filter(id = id)
		if not property:
			return None
		else:
			return property[0]


	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get property by plot ID
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def getPropertyByPlotId(plot_id):
		property = Property.objects.filter(plot_id = plot_id)
		if not property:
			return None
		else:
			return property[0]



	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get UPI by plot id
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def getUPIByPropertyId(property_id):
		property = PropertyMapper.getPropertyById(property_id)
		if not property:
			return None
		if not property.cell:
			return None
		cell_code = property.cell.code
		return cell_code[1:2] + "/" + cell_code[2:4] + "/" + cell_code[4:6] + "/" + cell_code[6:8] + "/" + str(property.parcel_id)


	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get property by UPI
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def getPropertyByUPI(upi):
		#info = Common.getInfoFromUPI(upi)
		property = Property.objectsIgnorePermission.filter(upi=upi)
		if not property:
			return None
		else:
			return property[0]


	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get property by conditions
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def getPropertiesByConditions(conditions):
		properties = None
		kwargs = {}
		excludes = {}
		for key, value in conditions.iteritems():
			if key == 'upi' and value and value!="":
				info = Common.getInfoFromUPI(value)
				if info:
					kwargs['cell__code__exact'] = info['cell_code']
					kwargs['parcel_id'] =  info['parcel_id']
				else:
					return None
			if key == 'plot_id' and value and value!="":
				kwargs['plot_id'] = value
			if key == 'sector' and value and value!="":
				kwargs['sector'] = value
			if key == 'parcel_id' and value and value!="":
				kwargs['parcel_id'] = int(value)
			if key == 'village' and value and value!="":
				kwargs['village'] = value
			if key == 'cell' and value and value!="":
				kwargs['cell'] = value
			if key == 'cell_code' and value and value!="":
				kwargs['cell__code__iexact'] = value
			if key == 'citizen' and value:
				property_id_sets = []
				for obj in value.property_set.all():
					property_id_sets.append(obj.id)
				kwargs['pk__in'] = property_id_sets
			if key == 'has_ownership' and value:
				if value == "all":
					continue
				elif value == "with":
					kwargs['owners__isnull'] = False
					kwargs['owners__i_status'] = 'active'
				elif value == "without":
					kwargs['owners__isnull'] = True

		properties = Property.objects.filter(**kwargs).distinct().order_by('sector__name', 'cell__code', 'parcel_id')
		print properties.query
		print '======='
		"""
		print conditions
		print '----------------------'
		print kwargs
		print '----------------------'
		print 'Results: ' + conditions['has_ownership'] + ' - ' + str(properties.count())
		print '==================='
		"""
		if properties and len(properties) > 1:
			for count in range(0,len(properties)):
				properties[count].upi = PropertyMapper.getUPIByPropertyId(properties[count].id)


		return properties




	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get property by conditions to get properties with contact
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def getNumOfPropertiesWithContact(conditions):
		properties = None
		both = 0
		properties_with_contact = 0
		count = 0
		for key, value in conditions.iteritems():
			if key == 'district' and value and value!="":
				if count > 0:
					properties = properties.filter(sector__district = value)
				else:
					properties = Property.objects.filter(sector__district = value)
				count = count + 1
			if key == 'sector' and value and value!="":
				if count > 0:
					properties = properties.filter(sector = value)
				else:
					properties = Property.objects.filter(sector = value)
				count = count + 1
			if key == 'cell' and value and value!="":
				if count > 0:
					properties = properties.filter(cell = value)
				else:
					properties = Property.objects.filter(cell = value)
				count = count + 1

			'''
			if key == 'village' and value and value!="":
				if count > 0:
					properties = properties.filter(village__iexact = value)
				else:
					properties = Property.objects.filter(village__iexact = value)
				count = count + 1
			'''
		if count == 0:
			both = Property.objects.all().count()
			properties_with_contact = Ownership.objects.exclude(i_status='inactive',owner_citizen__phone_1 = '',owner_citizen__phone_1__isnull=True).values_list('asset_property__id').distinct().count()
		if properties and len(properties) > 1:
			both = len(properties)
			properties_with_contact = Ownership.objects.filter(asset_property__in = properties,i_status='active').exclude(owner_citizen__phone_1 = '',owner_citizen__phone_1__isnull=True).values_list('asset_property__id').distinct().count()

		result = {}
		result['both'] = both
		result['with'] = properties_with_contact

		return result


	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get log activities in the past 12 month
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def getLogActivities(conditions = None):
		print conditions
		logs = None
		property = None
		district = None
		sector = None
		cell = None
		year = None
		result = {}
		labels = []
		values = []
		if conditions.has_key("upi") and conditions['upi'] and conditions['upi']!='':
			property = PropertyMapper.getPropertyByUPI(conditions['upi'])
			if not property:
				property = None
		if conditions.has_key('district'):
			district = conditions['district']
		if conditions.has_key('sector'):
			sector = conditions['sector']
		if conditions.has_key('cell'):
			cell = conditions['cell']
		year = int(conditions['calendar_year'])

		for count in range(1,13):
			month_range = Common.get_month_time_range(year, count)
			labels.append(month_range[0].strftime('%B'))
			logs = Log.objects.filter(date_time__range=month_range)
			if property:
				logs = logs.filter(property = property)
			if district:
				logs = logs.filter(Q(property__sector__district = district)|Q(business__sector__district = district)|Q(subbusiness__sector__district=district))
			if sector:
				logs = logs.filter(Q(property__sector = sector)|Q(business__sector = sector)|Q(subbusiness__sector=sector))
			if cell:
				logs = logs.filter(Q(property__cell = cell)|Q(business__cell = cell)|Q(subbusiness__cell=cell))

			values.append(logs.count())

		result['labels'] = labels
		result['values'] = values
		return result

	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get Geographic data of property or peroperties.
	1) The returned data is of Json format
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def getPropertyGeoData(properties):
		data = {}
		properties_new = []
		if type(properties) == list:
			properties_new = properties
		elif type(properties) == QuerySet:
			for property in properties:
				properties_new.append(property)
		else:
			properties_new.append(properties)

		properties = []

		# return json
		for property in properties_new:
			points_json = []
			property_json = {}
			boundary=property.boundary
			if boundary:
				str1 = None
				if boundary.polygon_imported:
					str1=str(boundary.polygon_imported.wkt)
				else:
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
					property_json['points']=points_json
			property_json['plot_id']=property.plot_id
			property_json['upi']=property.getUPI()
			property_json['parcel_id']=property.parcel_id
			if property.cell:
				property_json['cell']=property.cell.name
			else:
				property_json['cell']=""
			if property.village:
				property_json['village']=property.village.name
			else:
				property_json['village']=""
			property_json['sector']=property.sector.name
			properties.append(property_json)
		data['properties'] = properties
		return simplejson.dumps(data)
