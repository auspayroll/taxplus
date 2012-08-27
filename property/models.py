from django.db import models
from django.contrib.gis.db import models
from citizen.models import Citizen
from datetime import datetime

status_choices = (('deleted','deleted'), ('active','active'), ('inactive','inactive'))

class Boundary(models.Model):
    boundary_types = (('official','official'), ('manual','manual'))
    polygon = models.PolygonField(srid=4326)
    type = models.CharField(max_length = 10, choices = status_choices, blank=True, null=True, default='official')
    i_status = models.CharField(max_length = 10, choices = status_choices, default='active')
    objects = models.GeoManager()

class Property(models.Model):
    plotid = models.IntegerField(blank = False)
    streetno = models.IntegerField(null = True, blank = True)
    streetname = models.CharField(max_length = 30 ,null = True, blank = True)
    suburb = models.CharField(max_length = 50, null = False, blank = False)
    boundary = models.ForeignKey(Boundary)
    citizens = models.ManyToManyField(Citizen, through = 'Ownership')
    i_status = models.CharField(max_length = 10, choices = status_choices, default='active', blank = True)
    def __unicode__(self):
        return str(self.streetno)+" " +self.streetname+", "+self.suburb
    def getLogMessage(self,old_data=None,new_data=None,action=None):
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
    
class Ownership(models.Model):
    property = models.ForeignKey(Property)
    citizen = models.ForeignKey(Citizen)
    share = models.FloatField()
    startdate = models.DateField(default=datetime.now(), blank = False, null = False)
    enddate = models.DateField(blank=True, null=True)
    i_status = models.CharField(max_length = 10, choices = status_choices, default='active', blank = True)