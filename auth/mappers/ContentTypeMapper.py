from auth.models import ContentType


class ContentTypeMapper:
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Display ContentType name
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @staticmethod
    def getDisplayName(contentType):
        return contentType.name
    

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Get ContentType by ID
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @staticmethod
    def getContentTypeById(id):
        contentType = ContentType.objects.filter(id = id)
        if len(contentType) == 0:
            return None
        else:
            return contentType[0]
    
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Get ContentType by ContentType name and module
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @staticmethod
    def getContentTypeByModuleAndName(name, module):
        contentType = ContentType.objects.filter(name = name, module = module)
        if len(contentType) == 0:
            return None
        else:
            return contentType[0]
        
    """ 
    Action replace ContentType.getContentType with:
    ContentTypeMapper.getContentTypeByModuleAndName
    methods to be changed
    1) getUserPermissionsByContentType in auth.models
    """
        
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Get all ContentTypes
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @staticmethod
    def getAllContentTypes():
        return ContentType.objects.all()    
    
  

    