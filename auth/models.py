from django.db import models
from django.utils import timezone
from admin.ListCompare import ListCompare
from datetime import datetime
from dev1 import variables
from property.models import Council
import md5


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
        return '/admin/' + self.name + '/'
 
    
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
   

##############################################################################################    
# Group
############################################################################################## 
class Group(models.Model):
    name = models.CharField(max_length=80, unique=True)
    i_status = models.CharField(max_length=10, choices=variables.status_choices, default="active", blank = True)
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
                        extraFields = ListCompare.getExtraItems(old_data[key], new_data[key])
                        lessFields = ListCompare.getLessItems(old_data[key], new_data[key])
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
    
##############################################################################################    
# User
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
    council = models.ForeignKey(Council, null=True, blank=True, help_text="Council the sector belongs to.")
    datejoined = models.DateTimeField(default=timezone.now, help_text='date joined')
    groups = models.ManyToManyField(Group, verbose_name='groups', \
        blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.')
    permissions = models.ManyToManyField(Permission, verbose_name='user permissions', blank=True,help_text='Specific permissions for this user.')
    i_status = models.CharField(max_length= 10, choices=variables.status_choices, default="active", blank = True) 
    
    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def __unicode__(self):
        return self.username
    
    
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
                        extraFields = ListCompare.getExtraItems(old_data[key], new_data[key])
                        lessFields = ListCompare.getLessItems(old_data[key], new_data[key])
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