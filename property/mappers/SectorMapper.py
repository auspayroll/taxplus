from django.utils import simplejson
from property.models import Sector


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
        
        
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Get Sector by name
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""    
    @staticmethod
    def getSectorByName(name):
        sector = Sector.objects.filter(name = name)
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
        if user.superuser:
            return Sector.objects.filter(name__icontains=keyword)
        else:
            council = user.council
            return Sector.objects.filter(name__icontains=keyword).filter(council = council)
    
   
    
    
    