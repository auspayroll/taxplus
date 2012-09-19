from django.db import models
from property.models import Property
from citizen.models import Citizen
from datetime import datetime
from dev1 import variables


"""
The DeclaredValue Models are based around Declared Values Supplied by Property Owners 
These need to be checked against the Valuration system and checked if the supplied value is in line 
If it is not it needs to be flaged and manually checked. 
The Goverment / Council only has 6 months to Challange this value before it is automatticly accepted. 
"""
class DeclaredValue(models.Model):
	"""
	This is the base class for the Delcated Values of a Plot of Land in Rwandap
	"""
	PlotId = models.IntegerField(help_text='This is the ID of the Plot that the Declared Value is for.')
	DeclaredValueCitizenId = models.IntegerField(help_text='This is the Nation Id of the Cirizen Making the Delcared Value.')
	DeclaredValueAmount = models.IntegerField(help_text='This is the amount The Declared Value is been Made for.')
	DeclaredValueAmountCurrencey = models.CharField(max_length=4,choices=variables.currency_types,help_text='This is the Currencey the Amount has been specified in.')
	DeclaredValueDateTime = models.DateTimeField(help_text='This is the Date and Time the Entry has been entered into the database.',auto_now_add=True,auto_now=True)
	DeclaredValueStaffId = models.IntegerField(help_text='This is the Id of the Staff Member that Added the Declared Value for the Property.')
	DeclaredValueAccepted = models.CharField(max_length=4,choices=variables.value_accepted,help_text='This is whether the Declaired Value has been Accepted, rejected, or needs review.')
	
	def getLogMessage(self,old_data=None,new_data=None,action=None):
	    """
	    return tailored log message for different actions taken on this group
	    """
	    if action == "add":
	    	citizen = Citizen.objects.get(id = self.DeclaredValueCitizenId)
	    	citizen_fullname = citizen.firstname + " " + citizen.lastname
	    	property = Property.objects.get(plotid = self.PlotId)
	    	property_info = str(property.streetno)+" " +property.streetname+", "+property.suburb
	    	message = "approves Citizen ["+citizen_fullname+ "] to declare a value of "+ self.DeclaredValueAmountCurrencey + " " + str(self.DeclaredValueAmount) + " on Property ["+ property_info + "]"
	      	return message


class PropertyTax(models.Model):
	PlotId = models.IntegerField()
	PropertyTaxCitizenId = models.IntegerField()
	PropertyTaxAmount = models.IntegerField()
	PropertyTaxAmountCurrency = models.CharField(max_length=4, choices=variables.currency_types)
	PropertyTaxDateTime = models.DateTimeField(auto_now_add=True,auto_now=True)
	PropertyTaxStaffId = models.IntegerField()
	PropertyTaxAccepted = models.CharField(max_length=4,choices=variables.value_accepted)
	PropertyTaxStartDate = models.DateTimeField()
	PropertyTaxEndDate = models.DateTimeField()
	PropertyTaxIsGenerated = models.BooleanField()
	PropertyTaxIsPayed = models.BooleanField()
	PropertyTaxIsChallenged = models.BooleanField()
	PropertyTaxIsReviewed = models.BooleanField()
	

class DeclaredValueNotes(models.Model):
	"""
	This is a table of notes Related to the Declared Values model
	"""
	DeclaredValueId = models.ForeignKey('DeclaredValue')
	DeclaredValueNoteStaffId = models.IntegerField(help_text='This is the Id of the Staff Member that Added the Note.')
	DeclaredValueNote = models.TextField(help_text='This is the Note that is been left for the Declared Value')
	DeclaredValueNoteDateTime = models.DateTimeField(help_text='This is the Date and Time the Note was added to the Declared Value in the system.',auto_now_add=True,auto_now=True)

class DeclaredValueMedia(models.Model):
	"""
	This is a list of media files that have been attached to the Declared Value Application / Item directly. 
	"""
	DeclaredValueId = models.ForeignKey('DeclaredValue')
	DeclaredValueMediaType = models.CharField(max_length=4,choices=variables.media_types,help_text='This is the type of media the file is')
	DeclaredValueMediaFile = models.FileField(help_text='This is the location of the file on the file system.',upload_to='tmp')
	DelcaredValueMediaStaffId = models.IntegerField(help_text='The ID of the Staff Member who uploaded the file')
	DeclaredValueMediaDateTime = models.DateTimeField(help_text='This is the date and time the file was uploaded',auto_now_add=True,auto_now=True)

"""
The Assigned Value models are for the assigned Values to a property, this would be the official price of the land/property accepted by the Goverment. All Tax Items based off Property Value should use this table. 
These values are apparently accepted for 4 years from timme of acceptance. 
"""
class AssignedValue(models.Model):
	"""
	This model is for the offically assigned Values of a plot for the purpose of taxation
	"""
	PlotId = models.IntegerField()
	AssignedValueAmount = models.IntegerField(help_text='This is the Offical Property Price')
	AssignedValueDateTime = models.DateTimeField(help_text='This is the Date and time that the record for this assigned value was created',auto_now=True,auto_now_add=True)
	AssignedValueAmountCurrencey = models.CharField(max_length=4,choices=variables.currency_types,help_text='this is the Currencey that the assigned Value Amount is in')
	AssignedValueStaffId = models.IntegerField(help_text='This is the System Staff id of the staff member that entered the assigned value into the system.')
	AssignedValueCitizenId = models.IntegerField(help_text='This is the ID of the Citizen That Provided the Delcared Value that was accepted')
	AssignedValueValidUntil = models.DateTimeField('This is when the Assigned Value Record Runs Out.')
	AssignedValueOnHold = models.CharField(max_length=4,choices=variables.on_hold,help_text='this will put the record on hold if needed.')


"""
Land Rental Tax Models
"""
class LandRentalTax(models.Model):
	PlotId = models.IntegerField(help_text='This is the ID of the Plot that the Declared Value is for.')


class LandRentalTaxNotes(models.Model):
	LandRentalTaxId = models.ForeignKey('LandRentalTax')
	LandRentalTaxNoteStaffId = models.IntegerField(help_text='This is the Id of the Staff Member that created the note.')
	LandRentalTaxNote = models.TextField(help_text='This is the Note for the LandRental Tax Record Itself.')
	LandRentalTaxNoteDateTime = models.DateTimeField(help_text='This is the Date and Time the Note Was Created',auto_now_add=True,auto_now=True)
	
	


class LandRentalTaxMedia(models.Model):
	LandRentalTaxId = models.ForeignKey('LandRentalTax')


"""
The following Models are Related to the Rental Income Tax Collection and Evalutional 
"""
class rentalIncomeTax(models.Model):
	PlotId = models.IntegerField(help_text='This is the ID of the Plot that the Declared Value is for.')

class rentalIncomeTaxNotes(models.Model):
		rentalIncomeTaxId = models.ForeignKey('rentalIncomeTax')