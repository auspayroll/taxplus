from datetime import datetime
from django.db.models.fields.files import ImageFieldFile

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
                        setattr(object, key, value.strftime('%Y-%m-%d'))
                result.append(object)
            return result
        else:
            for key, value in obj.__dict__.iteritems():
                    if type(value) == datetime:
                        setattr(obj, key, value.strftime('%Y-%m-%d'))
            return obj
    
    
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
    
    
   