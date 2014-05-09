from datetime import datetime
from django.db.models.fields.files import ImageFieldFile
from pytz import timezone
from datetime import datetime, date
import pytz
from django.forms import models
from django.db import models as db_model
from django.conf import settings
from django.db.models.query import QuerySet
from django.db.models.fields.files import ImageFieldFile
import datetime
from dateutil.relativedelta import relativedelta
from calendar import monthrange


class Common:
	
	
	"""
	Calculate the number of months between these two dates within the same year, and date2 > date1
	"""
	@staticmethod
	def num_of_months_between_dates(date1,date2):
		num_of_months = date2.month - date1.month
		if date2.day > date1.day:
			num_of_months = num_of_months + 1
		if not num_of_months:
			num_of_months =  1
		return num_of_months
		
	
	@staticmethod
	def strptime(time_str):
		import datetime
		date_time = ''
		try:
			date_time = datetime.datetime.strptime(time_str,'%Y-%m-%d').date()
		except:
			try:
				date_time = datetime.datetime.strptime(time_str,'%d/%m/%Y').date()
			except:
				pass
		return date_time
	
	@staticmethod
	def to_custom_date(date_str):
		import datetime
		date_str = Common.strptime(date_str)
		if date_str:
			date_str = datetime.datetime.strftime(datetime.datetime(date_str.year,date_str.month,date_str.day,0,0,0),'%d/%m/%Y')
		else:
			date_str = ''
		return date_str
	
	@staticmethod
	def to_standard_date(date_str):
		import datetime
		date_str = Common.strptime(date_str)
		if date_str:
			date_str = datetime.datetime.strftime(datetime.datetime(date_str.year,date_str.month,date_str.day,0,0,0),'%Y-%m-%d')
		else:
			date_str = ''
		return date_str	
	
	
	@staticmethod
	def get_object_or_none(kclass, *args, **kwargs):
		try:
			return kclass._default_manager.get(*args,**kwargs)
		except kclass.DoesNotExist:
			return None
	
	
	@staticmethod
	def formatCurrency(val):
		try:
			return '{:20,.2f}'.format(int(val))
		except:
			return None
	

	"""
	convert date string to be with format DD/MM/YYYY
	"""
	@staticmethod
	def cleanCurrencyInput(input):
		result = float(input.replace(",",''))
		return int(result)

	"""
	convert date string to be with format DD/MM/YYYY
	"""
	@staticmethod
	def get_value_list(value_list,column_name):
		if value_list and column_name:
			list_to_return = []
			for value in value_list:
				list_to_return.append(value[column_name])
			if len(list_to_return) == 0:
				return None
			else:
				return list_to_return
				
	"""
	convert date string to be with format DD/MM/YYYY
	"""
	@staticmethod
	def formalize_date_string(str):
		if '/' in str:
			tmp = str.split('/')
			return ""+tmp[2]+"-"+tmp[1]+"-"+tmp[0]
		elif '-' in str:
			return str
	
	"""
	convert date string to be with format YYYY-MM-DD
	"""
	@staticmethod
	def formalize_date_string_for_html(str):
		if '-' in str:
			tmp = str.split('-')
			return ""+tmp[2]+"/"+tmp[1]+"/"+tmp[0]
		elif '/' in str:
			return str
	
			
	@staticmethod
	def get_upi_prefix(upi):
		upi = str(upi)
		index = upi.rfind('/')
		upi_prefix = upi[:index]
		return upi_prefix + '/'

	@staticmethod
	def getDayRange():
		list = range(1,32)
		data = []
		data.append(('','Day'))
		for i in list:
			data.append((i,i))
		return data

	@staticmethod
	def getMonthRange():
		list = range(1,13)
		data = []
		data.append(('','Month'))
		for i in list:
			data.append((i,i))
		return data

	@staticmethod
	def getYearRange():
		list = range(1920,datetime.datetime.now().year)
		data = []
		data.append(('','Year'))
		for i in list:
			data.append((i,i))
		return data


	@staticmethod
	def getDaysInMonth(year,month):
		month_range = monthrange(year,month)
		return int(month_range[1])
	
	@staticmethod
	def getDaysInYear(year):
		days = 0
		for month in range(1,13):
			days = days + Common.getDaysInMonth(year,month)
		return days

	@staticmethod
	def getDaysInCurrentYear(year):
		days = 0
		year = datetime.datetime.now().year
		for month in range(1,13):
			days = days + Common.getDaysInMonth(year,month)
		return days
	

	@staticmethod
	def getDaysInYearTillNow():
		days = 0
		year = datetime.datetime.now().year
		current_month = datetime.datetime.now().month
		for month  in range(1,current_month):
			days = days + Common.getDaysInMonth(year,month)
		days = days + datetime.datetime.now().day
		return days
	
	@staticmethod
	def getDayRangeInYearTillNow():
		today = datetime.datetime.now()
		start = datetime.datetime(today.year,1,1,0,0,0)
		end = datetime.datetime(today.year,today.month,today.day,23,59,59)
		return (start,end)

	@staticmethod
	def getDayRangeInYearFromNow():
		today = datetime.datetime.now()
		start = datetime.datetime(today.year,today.month,today.day,0,0,0)
		start = start + relativedelta(days = +1)
		end = datetime.datetime(today.year,12,31,23,59,59)
		return (start,end)


	@staticmethod
	def get_previous_month_time_range(num_of_month = 1):
		today = datetime.datetime.now()
		today = datetime.datetime(today.year,today.month,1,0,0,0)
		start = today - relativedelta(months=+num_of_month)
		end = Common.get_month_last_day(start)
		return (start,end)
	
	@staticmethod
	def get_month_time_range(year,month):
		start = datetime.datetime(year,month,1,0,0,0)
		end = Common.get_month_last_day_with_time(start)
		return (start,end)
	

	'''
	This function returns time range of current date
	Example [2013-02-03 00:00:00,2013-02-03 23:59:59]
	'''
	@staticmethod
	def get_today_time_range():
		today = datetime.datetime.now()
		start = datetime.datetime(today.year,today.month,today.day,0,0,0)
		end = datetime.datetime(today.year,today.month,today.day,23,59,59)
		return (start,end)

	'''
	This function returns time range of the last 7 days
	Example [2013-02-17 00:00:00,2013-02-20 23:59:59]
	'''
	@staticmethod
	def get_last7_days_time_range():
		today = datetime.datetime.now()
		end = datetime.datetime(today.year,today.month,today.day,23,59,59)
		day7before = today - relativedelta(days=6)
		start = datetime.datetime(day7before.year,day7before.month,day7before.day,0,0,0)
		return (start,end)
	
	'''
	This function returns time range of the last 30 days
	Example [2013-03-02 00:00:00,2013-03-31 23:59:59]
	'''
	@staticmethod
	def get_last30_days_time_range():
		today = datetime.datetime.now()
		end = datetime.datetime(today.year,today.month,today.day,23,59,59)
		day30before = today - relativedelta(days=29)
		start = datetime.datetime(day30before.year,day30before.month,day30before.day,0,0,0)
		return (start,end)
	
	'''
	This function returns time range of the last 30 days
	Example [2013-04-01 00:00:00,2013-03-31 23:59:59]
	'''
	@staticmethod
	def get_past_year_time_range():
		today = datetime.datetime.now()
		end = datetime.datetime(today.year,today.month,today.day,23,59,59)
		day1yearbefore = today + relativedelta(years = -1, days=+1)
		start = datetime.datetime(day1yearbefore.year,day1yearbefore.month,day1yearbefore.day,0,0,0)
		return (start,end)

	@staticmethod
	def get_month_first_day(date_obj):
		first_day = date_obj + relativedelta(day=1)
		return datetime.datetime(first_day.year,first_day.month,first_day.day,0,0,0)

	@staticmethod
	def get_month_last_day(date_obj):
		last_day = date_obj + relativedelta(day=1, months=+1, days=-1)
		return last_day
	
	@staticmethod
	def get_month_last_day_with_time(date_obj):
		last_day = date_obj + relativedelta(day=1, months=+1, days=-1)
		last_day = datetime.datetime(last_day.year,last_day.month,last_day.day,23,59,59)
		return last_day
	
	@staticmethod
	def isIterable(obj): 
		try:
			object_iterator = iter(obj)
			return True
		except TypeError:
			return False

	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	For an istance or a list of instance, replace datetime type field value with this
	format: 2000-12-26
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def formatObject(obj):
		
		if type(obj) == QuerySet:
			obj_list = []
			for object in obj:
				obj_list.append(object)
			obj = obj_list
		
		if type(obj) == list and len(obj) >= 1:
			result = []
			for object in obj:
				for key, value in object.__dict__.iteritems():
					if type(value) == datetime:
						value = Common.localize(value)
						setattr(object, key, value.strftime('%Y-%m-%d'))
				result.append(object)
			return result
		else:
			if type(obj) == list and len(obj) == 0:
				return None
			else:
				for key, value in obj.__dict__.iteritems():
					if type(value) == datetime:
						value = Common.localize(value)
						setattr(obj, key, value.strftime('%Y-%m-%d'))
				return obj
	
	
	@staticmethod
	def objToJson(obj):
		obj = Common.formatObject(obj)
		obj_type = type(obj)
		if obj_type == list:
			result = []
			for object in obj:
				object_json = {}
				for key, value in object.__dict__.iteritems():
					if key != '_state':
						if type(value) != datetime and type(value) != datetime.datetime:
							object_json[key] = str(value)
						else:
							object_json[key] = value.strftime('%Y-%m-%d')
				result.append(object_json)
			return result
		else:
			object_json = {}
			for key, value in obj.__dict__.iteritems():
				if key != '_state':
					if type(value) != datetime and type(value) != datetime.datetime:
						object_json[key] = str(value)
					else:
						object_json[key] = value.strftime('%Y-%m-%d')
			return object_json
			
	
	
	@staticmethod
	def cleanObjForApi(obj):
		if type(obj) == QuerySet:
			objects = []
			for object in obj:
				objects.append(object)
			obj = objects
		if type(obj) != list:
			objects = []
			objects.append(obj)
			obj = objects
		
		# cleaning starts from here   
		for object in obj:
			for key, value in object.__dict__.iteritems():
				if type(value) == datetime:
					value = Common.localize(value)
					setattr(object, key, value.strftime('%Y-%m-%d'))
				if key == '_state':
					del object._state
		return obj
	
	
	"""
	convert object to string
	"""
	@staticmethod
	def objToStr(dict):
		if dict is None:
			return str("")
		for key, value in dict.iteritems():
			if type(value) is datetime or type(value) is datetime.datetime:
				dict[key] = value.strftime('%Y-%m-%d %H:%M:%S')
			if type(value) is date:
				dict[key] = value.isoformat()
			if type(value) is ImageFieldFile:
				dict[key] = value.name
		dict = str(dict)
		return dict
	
	
	
	"""
	localize time to Australia/Sydney, which is specified in settins.py
	"""
	@staticmethod
	def localize(dtime):
		local_tz = timezone(str(settings.TIME_ZONE))
		dtime_new = None
		if dtime.tzinfo is None:
			dtime_new = local_tz.localize(dtime)
		else:
			dtime_new = local_tz.normalize(dtime.astimezone(local_tz))
		return dtime_new
	
	
	@staticmethod
	def localizeDate(dtime):
		local_tz = timezone(str(settings.TIME_ZONE))
		dtime_new = None
		if dtime.tzinfo is None:
			dtime_new = local_tz.localize(dtime)
		else:
			dtime_new = local_tz.normalize(dtime.astimezone(local_tz))
		dtime_new = datetime.datetime(dtime_new.year, dtime_new.month, dtime_new.day, tzinfo=dtime_new.tzinfo)
		return dtime_new
	
	
	@staticmethod
	def getDefaultTimeZone():
		local_tz = timezone(str(settings.TIME_ZONE))
		return local_tz
	
	
	
	@staticmethod
	def floatToDecimal(f):
		return "{0:.2f}".format(f)
		
		
	@staticmethod
	def reverse(list_var):
		if type(list_var) is not list:
			return list_var
		else:
			return list_var[::-1]
	
					
	@staticmethod
	def getInfoFromUPI(upi):
		tmp = upi.split('/')
		if len(tmp) != 5:
			return None
		info = {}
		info['cell_code'] = "0"+tmp[0] + tmp[1] + tmp[2] + tmp[3]
		try:
			info['parcel_id'] = int(tmp[4])
		except:
			#replace with invalid parcel_id to return empty property
			info['parcel_id'] = 99999999999999
		return info
