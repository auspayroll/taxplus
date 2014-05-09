from django.utils import simplejson
from property.models import Council


class CouncilMapper:    
          
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Get all Councils
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""    
    @staticmethod
    def getAllCouncils():
        return Council.objects.all()
    
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Get Council by id
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""    
    @staticmethod
    def getCouncilById(id):
        council = Council.objects.filter(id = id)
        if not council:
            return None
        else:
            return council[0]
        
        
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Get Council by name
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""    
    @staticmethod
    def getCouncilByName(name):
        council = Council.objects.filter(name = name)
        if not council:
            return None
        else:
            return council[0]
    
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    search Council by keyword
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""    
    @staticmethod
    def searchCouncilsByKeyword(keyword):
        councils = Council.objects.filter(name__icontains=keyword)
        return councils