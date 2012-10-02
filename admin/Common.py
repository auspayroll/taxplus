from datetime import datetime
from django.db.models.fields.files import ImageFieldFile
from pytz import timezone
from datetime import datetime
import pytz
from django.conf import settings

class Common:
            
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    For an istance or a list of instance, replace datetime type field value with this
    format: 2000-12-26
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @staticmethod
    def formatObject(obj):
        if type(obj) == list:
            result = []
            for object in obj:
                for key, value in object.__dict__.iteritems():
                    if type(value) == datetime:
                        value = Common.localize(value)
                        setattr(object, key, value.strftime('%Y-%m-%d'))
                result.append(object)
            return result
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
                    object_json[key] = str(value)
                result.append(object_json)
            return result
        else:
            object_json = {}
            for key, value in object.__dict__.iteritems():
                object_json[key] = str(value)
            return object_json
            
    
    """
    convert object to string
    """
    @staticmethod
    def objToStr(dict):
        if dict is None:
            return str("")
        for key, value in dict.iteritems():
            if type(value) is datetime:
                dict[key] = value.strftime('%Y-%m-%d %H:%M:%S')
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
        dtime_new = datetime(dtime_new.year, dtime_new.month, dtime_new.day, tzinfo=dtime_new.tzinfo)
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
                
            
    
    
    
    
    
    
   