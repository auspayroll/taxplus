from django.db import models
from admin.common import Tools
from datetime import datetime


status_choices = (('deleted','deleted'), ('active','active'), ('inactive','inactive'))

class Citizen(models.Model):
    firstname = models.CharField(max_length = 50, help_text = 'First name')
    lastname = models.CharField(max_length = 50, help_text = 'Last name')
    citizenid = models.IntegerField(blank=False, unique=True, help_text = 'unique ID for citizen')
    i_status = models.CharField(max_length = 10, choices = status_choices, default='active', blank = True)
    citizenPhoto = models.ImageField(upload_to='citizenphotos', help_text='Photo of The Citizen')
    
    def __unicode__(self):
        return self.firstname + ' ' + self.lastname
    
    def save(self):
        """
        set status to be "active" by default
        """
        if not self.i_status:
            self.i_status="active"
        models.Model.save(self) 
        
    
    
    def getLogMessage(self,old_data=None,new_data=None, action=None):
        """
        return tailored log message for different actions taken on this citizen
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
            if message == "":
                message = "No change made"
            message = message + " on " + self.__class__.__name__ + " [" + self.__unicode__() + "]"
            return message
    
    