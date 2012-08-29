from django.db import models
from django import forms
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
from admin.common import Tools
from datetime import datetime
import string
import random
import md5


status_choices = (('deleted','deleted'), ('active','active'), ('inactive','inactive'))

##############################################################################################    
# Module
############################################################################################## 
class Module(models.Model):
    name = models.CharField(max_length = 50, help_text = 'Module name')
    image = models.ImageField(upload_to='module_images')
    description = models.CharField(max_length = 200, blank=True, help_text = 'Module description')
    def __unicode__(self):
        return self.name
    
    def get_access_link(self):
        """
        The url used to access this module
        """
        return '/admin/' + self.name + '/'
    
    @staticmethod
    def getModule(modulename):
        """
        Static method to get module by provided module name
        """
        try:
           module = Module.objects.get(name = modulename)
           return module
        except ObjectDoesNotExist: 
           return None
##############################################################################################    
# ContentType
##############################################################################################        
class ContentType(models.Model):
    name = models.CharField(max_length = 50, help_text = 'Content type name')
    image = models.ImageField(upload_to='content_type_images')
    model_name = models.CharField(max_length = 50, help_text = 'Model name')
    module = models.ForeignKey(Module)
    class Meta:
        ordering = ['name']
    def __unicode__(self):
        return self.name
    def get_access_link(self):
        return '/admin/' + self.module.name + '/' + self.name + '/'
    
    @staticmethod
    def getContentType(name,module):
        try:
            contentType = ContentType.objects.get(name = name, module = module)
            return contentType
        except ObjectDoesNotExist: 
            return None
##############################################################################################    
# Permission
##############################################################################################  
class Permission(models.Model):
    name = models.CharField(max_length = 50, help_text = 'The name of the permission shown to users')
    codename = models.CharField(max_length = 50, help_text = 'The name of the permission used in code')
    contenttype = models.ForeignKey(ContentType)
    def __unicode__(self):
        return self.name
    def get_access_link(self):
        return '/admin/' + self.contenttype.module.name + '/' + self.contenttype.name + '/' + self.codename + '/'
    def get_display_name(self):
        names = self.codename.split('_')
        names[0] = names[0].capitalize()
        names[0] = names[0] + ' '
        return ''.join(names)
    
    @staticmethod    
    def getPermission(name, contentType):
        """
        As different contentType may have same permission name, contentType is needed
        """
        try:
            permission = Permission.objects.get(name = name, contenttype = contentType)
            return permission
        except ObjectDoesNotExist: 
            return None
    
    @staticmethod
    def getPermissionByCodeName(codename):
        try:
           permission = Permission.objects.get(codename = codename)
           return permission
        except ObjectDoesNotExist: 
           return None
       
    @staticmethod
    def wrap_permissions(permissions):
        permissions_final=[]
        for per in permissions:
            per.access_link = per.get_access_link()
            per.display_name = per.get_display_name()
            permissions_final.append(per)
        return permissions_final
##############################################################################################    
# Group
############################################################################################## 
class Group(models.Model):
    name = models.CharField(max_length=80, unique=True)
    i_status = models.CharField(max_length=10, choices=status_choices, default="active", blank = True)
    permissions = models.ManyToManyField(Permission, verbose_name='permissions', blank=True)
    
    class Meta:
        verbose_name ='group'
        ordering = ['name']
        verbose_name_plural ='groups'
        
    def __unicode__(self):
        return self.name
    
    
    def save(self, *args, **kwargs):
        """
        The status of a group is set to "active" by default
        """
        if not self.i_status:
            self.i_status = 'active'
        models.Model.save(self)


    def has_permission(self, permission):
        """
        check where this group has given permission
        """
        sql = "select ap.* from auth_permission ap \
            inner join auth_group_permissions agp on agp.permission_id = ap.id \
            where agp.group_id = %i " % self.pk
        if permission in Permission.objects.raw(sql):
            return True
        else:
            return False
        
    def can_access_content_type(self, content_type):
        """
        check if this group has the permission to access given contentType
        """
        sql = "select ct.* from  auth_contenttype ct \
               inner join auth_permission ap on ap.contenttype_id = ct.id \
               inner join auth_group_permissions agp on agp.permission_id = ap.id \
               where agp.group_id = %i " % self.pk
        if content_type in ContentType.objects.raw(sql):
            return True
        else:
            return False
    
    def getLogMessage(self,old_data=None,new_data=None,action=None):
        """
        return tailored log message for different actions taken on this group
        """
        if action == "view":
            return "view " + self.__class__.__name__ + " [" + self.__unicode__() + "]"
        if action == "delete":
            return "delete " + self.__class__.__name__ + " [" + self.__unicode__() + "]"
        if action == "add":
            return "add " + self.__class__.__name__ + " [" + self.__unicode__() + "]"
        if action == "change":
            message=""
            count = 0
            for key, value in old_data.iteritems():
                if old_data[key] != new_data[key]:
                    if count != 0:
                        message = message + ","
                    count = count + 1
                    if type(value) is not list:
                        message = message + " change "+key + " from '"+ str(value) + "' to '"+str(new_data[key])+"'"
                    else:
                        extraFields = Tools.getExtraItems(old_data[key], new_data[key])
                        lessFields = Tools.getLessItems(old_data[key], new_data[key])
                        if key == "permissions":
                            extraFields_display = []
                            lessFields_display = []
                            for permission_id in extraFields:
                                extraFields_display.append(str(Permission.objects.get(id=permission_id).name))
                            for permission_id in lessFields:
                                lessFields_display.append(str(Permission.objects.get(id=permission_id).name))
                            comma_needed = True
                            if len(extraFields_display) > 0:
                                message = message + " remove permissions " +  str(extraFields_display)
                                comma_needed = True
                            if len(lessFields_display) > 0:
                                if comma_needed:
                                    message = message + ','
                                message = message + " add permissions " +  str(lessFields_display)
            if message == "":
                message = "No change made"
            message = message + " on " + self.__class__.__name__ + " [" + self.__unicode__() + "]"
            return message
    

    @staticmethod
    def getGroup(groupname):
        """
        return group with given group name
        """
        try:
            group = Group.objects.get(name = groupname)
            return group
        except ObjectDoesNotExist: 
            return None 
        
    @staticmethod
    def getGroupNames():
        """
        return a list of group names
        """
        names = []
        groups = Group.objects.all()
        for group in groups:
            names.append(group.name)
        return names
##############################################################################################    
# ContentType
##############################################################################################                    
class User(models.Model):
    username = models.CharField(max_length=30, help_text='Required. Maximum 30 characters.')
    firstname = models.CharField(max_length=30, help_text='Enter first name.')
    lastname = models.CharField(max_length=30, help_text='Enter last name.')
    contactnumber = models.CharField(max_length=30, blank=True, help_text='Telephone number or mobile number.')
    email = models.EmailField(unique=True,help_text='Enter email address.')
    password = models.CharField(max_length=128, help_text='Enter password.')
    active = models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.')
    superuser = models.BooleanField(default=False,help_text='Designates that this user has all permissions without explicitly assigning them.')
    lastlogin = models.DateTimeField(default=timezone.now, help_text='last login')
    datejoined = models.DateTimeField(default=timezone.now, help_text='date joined')
    groups = models.ManyToManyField(Group, verbose_name='groups', \
        blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.')
    permissions = models.ManyToManyField(Permission, verbose_name='user permissions', blank=True,help_text='Specific permissions for this user.')
    i_status = models.CharField(max_length= 10, choices=status_choices, default="active", blank = True) 
    
    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __unicode__(self):
        return self.username
      
    def getModules(self):
        """
        Get all the modules that the user has permission to access
        Both user specific permissions and group permissions are considered
        """
        if self.superuser:
            return Module.objects.all()
        else:
            modules = []
            sql1 = "select distinct m.* from auth_module m \
                inner join auth_contenttype ct on m.id = ct.module_id \
                inner join auth_permission ap on ct.id = ap.contenttype_id \
                inner join auth_user_permissions aup on aup.permission_id = ap.id \
                inner join auth_user au on au.id = aup.user_id \
                where au.username = '%s' " % self.username
            sql2 = " union select distinct m.* from auth_module m \
                inner join auth_contenttype ct on m.id = ct.module_id \
                inner join auth_permission ap on ct.id = ap.contenttype_id \
                inner join auth_group_permissions agp on agp.permission_id = ap.id \
                inner join auth_group ag  on agp.group_id = ag.id \
                inner join auth_user_groups ug on ag.id = ug.group_id \
                inner join auth_user au on au.id = ug.user_id \
                where au.username = '%s' " % self.username
    
            sql = sql1 + sql2
            for module in Module.objects.raw(sql):
                if module not in modules:
                    modules.append(module)            
            return modules
        
    def getContentTypes1(self,module=None):
        """
        Get all the contentTypes within a given module that the user has permission to access
        if module is None, then get all the contenttypes that the user has permission to access 
        Both user specific permissions and group permissions are considered
        The returned contenttypes are not sorted
        """
        if self.superuser:
            if module is None:
                return ContentType.objects.all()
            else:
                return ContentType.objects.filter(module = module)
        else:
            contentTypes = []
            sql1 = "select distinct ct.* from auth_contenttype ct \
                inner join auth_permission ap on ct.id = ap.contenttype_id \
                inner join auth_user_permissions aup on aup.permission_id = ap.id \
                inner join auth_user au on au.id = aup.user_id \
                where au.username = '%s' " % self.username
            sql2 = " union select distinct ct.* from auth_contenttype ct \
                inner join auth_permission ap on ct.id = ap.contenttype_id \
                inner join auth_group_permissions agp on agp.permission_id = ap.id \
                inner join auth_group ag  on agp.group_id = ag.id \
                inner join auth_user_groups ug on ag.id = ug.group_id \
                inner join auth_user au on au.id = ug.user_id \
                where au.username = '%s' " % self.username
            sql = sql1 + sql2    
            for contentType in ContentType.objects.raw(sql):
                if contentType not in contentTypes:
                    contentTypes.append(contentType)
            if module is None:
                return contentTypes
            else:
                allowed_content_types = ContentType.objects.filter(module = module)
                final_content_types = []
                for content_type in contentTypes:
                    if content_type in allowed_content_types:
                        final_content_types.append(content_type)
                return final_content_types
    
    def getContentTypes(self, module=None):
        """
        Get all the contentTypes within a given module that the user has permission to access
        if module is None, then get all the contenttypes that the user has permission to access 
        Both user specific permissions and group permissions are considered
        The returned contenttypes are sorted
        """
        content_types=self.getContentTypes1(module)
        ct=[]
        for content_type in content_types:
            content_type.access_link=content_type.get_access_link()
            ct.append(content_type)
        ct.sort(key=lambda x:x.name, reverse=False)
        return ct
    
    def getGroups(self):
        """
        Get all the groups this user is associated with
        """
        sql = "select distinct ag.* from auth_group ag \
            inner join auth_user_groups ug on ag.id = ug.group_id \
            inner join auth_user au on au.id = ug.user_id \
            where au.username = '%s' " % self.username
        groups = []
        for group in Group.objects.raw(sql):
            groups.append(group)
        return groups
  
    def getGroupPermissions(self):
        """
        Get all the group permissions this user has
        """
        final_permissions = []
        if self.superuser:
            final_permissions = Permission.objects.all()
        else:
            sql = "select distinct ap.* from auth_permission ap \
                inner join auth_group_permissions agp on agp.permission_id = ap.id \
                inner join auth_group ag on agp.group_id = ag.id \
                inner join auth_user_groups ug on ag.id = ug.group_id \
                inner join auth_user au on au.id = ug.user_id \
                where au.username = '%s' " % self.username
            for permission in Permission.objects.raw(sql):
                final_permissions.append(permission)
        return final_permissions
    
    def getAllPermissions(self):
        """
        Get all the permissions this user has
        including user-specific permissions and group permissions
        """
        all_permissions =  []    
        permissions = self.getAdditionalPermissions()
        if permissions is not None:
            for per in permissions:
                all_permissions.append(per)        
        grouppermissions=self.getGroupPermissions()
        if grouppermissions is not None:
            for per in grouppermissions:
                if per not in all_permissions:
                    all_permissions.append(per)            
        return all_permissions
        
    def getAdditionalPermissions(self):
        """
        Get only user-specific permissions
        """
        final_permissions = []
        if self.superuser:
            return None
        else:
            sql = "select distinct ap.* from auth_permission ap \
                inner join auth_user_permissions aup on aup.permission_id = ap.id \
                inner join auth_user au on au.id = aup.user_id \
                where au.username = '%s' " % self.username    
            for permission in Permission.objects.raw(sql):
                final_permissions.append(permission)   
        return final_permissions
        
    def getAllPermissionsByContentType(self,content_type):
        """
        Get all the permissions the user has associated with this contenttype
        """
        all_permissions=self.getAllPermissions()
        final_permissions=[]
        for per in all_permissions:
            if per.contenttype == content_type:
                final_permissions.append(per)    
        return final_permissions
    
    def getProfile(self):
        """
        Get all the modules the user can access, and
        all the contenttypes the user can access, and
        all the permissions the user has
        pack these infomation in a complex dictionary with the following hierachy: 
        {
            {{Module name}} => {
                {{contentType name1}}=>[permission1, permission2,...],
                {{contentType name2}}=>[permission1, permission2,...],
                ...
                },
            {{Module name}} => {
                {{contentType name1}}=>[permission1, permission2,...],
                {{contentType name2}}=>[permission1, permission2,...],
                ...
                },
            ...
        }
        """
        all_modules = self.getModules()
        profile = {}
        for module in all_modules:
            module_dict = {}
            all_content_types = self.getContentTypes(module)
            for content_type in all_content_types:
                content_type_dict = {}
                all_permissions = self.getAllPermissionsByContentType(content_type)
                can_view = 0
                can_add = 0
                can_change = 0
                can_delete = 0
                for permission in all_permissions:
                    if permission.codename == 'view_' + content_type.name:
                        can_view = 1
                    if permission.codename == 'change_' + content_type.name:
                        can_change = 1
                    if permission.codename == 'add_' + content_type.name:
                        can_add = 1
                    if permission.codename == 'delete_' + content_type.name:
                        can_delete = 1
                if can_view:
                    content_type_dict['can_view'] = True
                else:
                    content_type_dict['can_view'] = False
                if can_add:
                    content_type_dict['can_add'] = True
                else:
                    content_type_dict['can_add'] = False
                if can_change:
                    content_type_dict['can_change'] = True
                else:
                    content_type_dict['can_change'] = False
                if can_delete:
                    content_type_dict['can_delete'] = True
                else:
                    content_type_dict['can_delete'] = False
                module_dict[content_type.name]=content_type_dict
            module_dict=sorted(module_dict.items())
            profile[module.name]= module_dict
        profile=sorted(profile.items())
        return profile
    
    def getProfileByModule(self, module):
        """
        Get all the contenttypes the user can access within the given module, and
        all the permissions the user has
        return the above info with the same structure as the above function
        """
        module_dict = {}
        all_content_types = self.getContentTypes(module)
        for content_type in all_content_types:
            content_type_dict = {}
            all_permissions = self.getAllPermissionsByContentType(content_type)
            can_view = 0
            can_add = 0
            can_change = 0
            can_delete = 0
            for permission in all_permissions:
                if permission.codename == 'view_' + content_type.name:
                    can_view = 1
                if permission.codename == 'change_' + content_type.name:
                    can_change = 1
                if permission.codename == 'add_' + content_type.name:
                    can_add = 1
                if permission.codename == 'delete_' + content_type.name:
                    can_delete = 1
            if can_view:
                content_type_dict['can_view'] = True
            else:
                content_type_dict['can_view'] = False
            if can_add:
                content_type_dict['can_add'] = True
            else:
                content_type_dict['can_add'] = False
            if can_change:
                content_type_dict['can_change'] = True
            else:
                content_type_dict['can_change'] = False
            if can_delete:
                content_type_dict['can_delete'] = True
            else:
                content_type_dict['can_delete'] = False
            module_dict[content_type.name]=content_type_dict
        module_dict=sorted(module_dict.items())
        return module_dict
    
    def has_permission(self,permission):
        """
        check if this user has the given permission or not
        """
        permissions = self.getAllPermissions()
        if permission in permissions:
            return True
        else:
            return False
    
    def has_module(self, module):
        """
        check if this user has the permission to access this module or not
        """
        modules = self.getModules()
        if module in modules:
            return True
        else:
            return False
        
    def has_group(self, group):
        """
        Check if this user is associated with this group or not
        """
        groups = self.getGroups()
        if group in groups:
            return True
        else:
            return False
      
    def getLogMessage(self,old_data=None,new_data=None, action = None):
        """
        return tailored log message for different actions taken on this user
        """
        if action == "view":
            return "view " + self.__class__.__name__ + " [" + self.__unicode__() + "]"
        if action == "delete":
            return "delete " + self.__class__.__name__ + " [" + self.__unicode__() + "]"
        if action == "add":
            return "add " + self.__class__.__name__ + " [" + self.__unicode__() + "]"
        if action == "change":
            message=""
            count = 0
            for key, value in old_data.iteritems():
                if old_data[key] != new_data[key]:
                    if count != 0:
                        message = message + ","
                    count = count + 1
                    if type(value) is not list:
                        message = message + " change "+key + " from '"+ str(value) + "' to '"+str(new_data[key])+"'"
                    else:
                        extraFields = Tools.getExtraItems(old_data[key], new_data[key])
                        lessFields = Tools.getLessItems(old_data[key], new_data[key])
                        if key == "permissions":
                            extraFields_display = []
                            lessFields_display = []
                            for permission_id in extraFields:
                                extraFields_display.append(str(Permission.objects.get(id=permission_id).name))
                            for permission_id in lessFields:
                                lessFields_display.append(str(Permission.objects.get(id=permission_id).name))
                            comma_needed = True
                            if len(extraFields_display) > 0:
                                message = message + " remove permissions " +  str(extraFields_display)
                                comma_needed = True
                            if len(lessFields_display) > 0:
                                if comma_needed:
                                    message = message + ','
                                message = message + " add permissions " +  str(lessFields_display)
                        if key == "groups":
                            extraFields_display = []
                            lessFields_display = []
                            for group_id in extraFields:
                                extraFields_display.append(str(Group.objects.get(id=group_id).name))
                            for group_id in lessFields:
                                lessFields_display.append(str(Group.objects.get(id=group_id).name))
                            comma_needed = False
                            if len(extraFields_display) > 0:
                                message = message + " detatch from groups " +  str(extraFields_display)
                                comma_needed = True
                            if len(lessFields_display) > 0:
                                if comma_needed:
                                    message = message + ','
                                message = message + " associate with groups " +  str(lessFields_display)       
            if message == "":
                message = "No change made"
            message = message + " on " + self.__class__.__name__ + " [" + self.__unicode__() + "]"
            return message
        
    def save(self, *args, **kwargs):
        """
        user status is set active by default
        check whether password is encrypted,
        if not, encrypt the password
        """
        if not self.i_status:
            self.i_status = 'active'
        if self.password and len(self.password) < 32:
            self.password = md5.new(self.password).hexdigest()    
        user = super(User,self).save(*args, **kwargs)
        return user
    
        
    @staticmethod
    def getUser(email, password):
        """
        return a user having the given email and password
        """
        try:
            user = User.objects.get(email  = email, password = md5.new(password).hexdigest())
            return user
        except ObjectDoesNotExist: 
            return None
    
    @staticmethod
    def getUserPermissionsByContentType(request, module_name, content_type_name):
        """
        Return permissions the user has asssociated with the given contenttype,
        Return additional info regarding permissions like, permission name and permission access link info
        """
        username = request.session.get('user').username
        user = User.objects.get(username = username)
        module = User.getModule(module_name)
        content_type = ContentType.getContentType(content_type_name, module)
        permissions_new=user.getAllPermissionsByContentType(content_type)
        permissions_new=wrap_permissions(permissions_new)