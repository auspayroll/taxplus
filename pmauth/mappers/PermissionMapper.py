from pmauth.models import PMPermission


class PermissionMapper:
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Display Permission name
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @staticmethod
    def getDisplayName(permission):
        names = permission.codename.split('_')
        names[0] = names[0].capitalize()
        names[0] = names[0] + ' '
        return ''.join(names)
    

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Get Permission by ID
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @staticmethod
    def getPermissionById(id):
        permission = PMPermission.objects.filter(id = id)
        if len(permission) == 0:
            return None
        else:
            return permission[0]
    
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Get Permission by Code name
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @staticmethod
    def getPermissionByCodeName(codename):
        permission = PMPermission.objects.filter(codename = codename)
        if len(permission) == 0:
            return None
        else:
            return permission[0]
    
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Get Permission by Permission name and ContentType
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @staticmethod
    def getPermissionByContentTypeAndName(name, contentType):
        permission = PMPermission.objects.filter(name = name, contenttype = contentType)
        if len(permission) == 0:
            return None
        else:
            return permission[0]

    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Get all Permissions
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @staticmethod
    def getAllPermissions():
        return PMPermission.objects.all()
    
    
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Attach extra fiels into each permission
    1) access_link
    2) display_name
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @staticmethod
    def wrap_permissions(permissions):
        permissions_final=[]
        for per in permissions:
            per.access_link = per.get_access_link()
            per.display_name = PermissionMapper.getDisplayName(per)
            permissions_final.append(per)
        return permissions_final
    
  

    