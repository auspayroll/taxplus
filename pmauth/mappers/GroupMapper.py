from pmauth.models import PMGroup,PMPermission,PMContentType


class GroupMapper:
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Display Group name
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @staticmethod
    def getDisplayName(group):
        return group.name
    

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Get Group by ID
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @staticmethod
    def getGroupById(id):
        group = PMGroup.objects.filter(id = id)
        if len(group) == 0:
            return None
        else:
            return group[0]
    
   
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Get Group by name
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @staticmethod
    def getGroupByName(groupname):
        group = PMGroup.objects.filter(name = groupname)
        if len(group) == 0:
            return None
        else:
            return group[0]
    
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Get the names of all the groups
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @staticmethod
    def getGroupNames():
        names = []
        groups = PMGroup.objects.all()
        for group in groups:
            names.append(group.name)
        return names
    
    
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Get all Groups
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @staticmethod
    def getAllGroups():
        return PMGroup.objects.all()
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Get all active groups
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @staticmethod
    def getActiveGroups():
        return PMGroup.objects.filter(i_status = 'active')
    


    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Check whether group has permission
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @staticmethod
    def hasPermission(group, permission):
        sql = "select ap.* from auth_pmpermission ap \
            inner join auth_pmgroup_permissions agp on agp.permission_id = ap.id \
            where agp.pmgroup_id = %i " % group.id
        if permission in PMPermission.objects.raw(sql):
            return True
        else:
            return False
    
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Check whether a group is able to access the given ContentType
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @staticmethod
    def canAccessContentType(group, content_type):
        sql = "select ct.* from  auth_pmcontenttype ct \
               inner join auth_pmpermission ap on ap.contenttype_id = ct.id \
               inner join auth_pmgroup_permissions agp on agp.pmpermission_id = ap.id \
               where agp.pmgroup_id = %i " % group.id
        if content_type in PMContentType.objects.raw(sql):
            return True
        else:
            return False
    
    
    