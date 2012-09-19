from django.utils import simplejson
from property.models import District


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
    Get district by name
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""    
    @staticmethod
    def getDistrictByName(name):
        district = District.objects.filter(name = name)
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