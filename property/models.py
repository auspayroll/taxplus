from django.db import models
from django.contrib.gis.db import models
from citizen.models import Citizen
from datetime import datetime

status_choices = (('deleted','deleted'), ('active','active'), ('inactive','inactive'))

class Boundary(models.Model):
    """
    Boundary type is official by default.
    If the boundary of a property is mannually drawed from google map, then the boundary type is set to be "manual"
    """
    boundary_types = (('official','official'), ('manual','manual'))
    polygon = models.PolygonField(srid=4326)
    type = models.CharField(max_length = 10, choices = status_choices, blank=True, null=True, default='official')
    i_status = models.CharField(max_length = 10, choices = status_choices, default='active')
    objects = models.GeoManager()

class Property(models.Model):
    plotid = models.IntegerField(blank = False, help_text="Each plotid identifies a property.")
    streetno = models.IntegerField(null = True, blank = True, help_text="The street number of property. This could be empty.")
    streetname = models.CharField(max_length = 30 ,null = True, blank = True, help_text="The street name of property. This could be empty.")
    suburb = models.CharField(max_length = 50, null = False, blank = False, help_text="The suburb in which the property is located.")
    boundary = models.ForeignKey(Boundary, help_text="The boundary of property")
    citizens = models.ManyToManyField(Citizen, through = 'Ownership',help_text="a property could belong to multiple citizens")
    i_status = models.CharField(max_length = 10, choices = status_choices, default='active', blank = True)
    def __unicode__(self):
        return str(self.streetno)+" " +self.streetname+", "+self.suburb
    def getLogMessage(self,old_data=None,new_data=None,action=None):
        """
        return tailored log message for different actions taken on this property
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
    
class Ownership(models.Model):
    property = models.ForeignKey(Property)
    citizen = models.ForeignKey(Citizen)
    share = models.FloatField(help_text="The share of property the citizen possesses")
    startdate = models.DateField(default=datetime.now(), blank = False, null = False, help_text="The start date that the citizen owns this property")
    enddate = models.DateField(blank=True, null=True, help_text="The end date that the citizen owns this property")
    i_status = models.CharField(max_length = 10, choices = status_choices, default='active', blank = True)