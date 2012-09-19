from auth.models import Group,Permission,ContentType


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
        group = Group.objects.filter(id = id)
        if len(group) == 0:
            return None
        else:
            return group[0]
    
   
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Get Group by name
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @staticmethod
    def getGroupByName(groupname):
        group = Group.objects.filter(name = name)
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
        groups = Group.objects.all()
        for group in groups:
            names.append(group.name)
        return names
    
    
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Get all Groups
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @staticmethod
    def getAllGroups():
        return Group.objects.all()
    
    
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Check whether group has permission
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @staticmethod
    def hasPermission(group, permission):
        sql = "select ap.* from auth_permission ap \
            inner join auth_group_permissions agp on agp.permission_id = ap.id \
            where agp.group_id = %i " % group.id
        if permission in Permission.objects.raw(sql):
            return True
        else:
            return False
    
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Check whether a group is able to access the given ContentType
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @staticmethod
    def canAccessContentType(group, content_type):
        sql = "select ct.* from  auth_contenttype ct \
               inner join auth_permission ap on ap.contenttype_id = ct.id \
               inner join auth_group_permissions agp on agp.permission_id = ap.id \
               where agp.group_id = %i " % group.id
        if content_type in ContentType.objects.raw(sql):
            return True
        else:
            return False
    
    
    