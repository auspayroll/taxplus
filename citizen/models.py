from django.db import models
from datetime import datetime
from dev1.variables import *
from common.models import Status
from taxplus.models import CategoryChoice
from django.db.models.signals import post_save
from django.dispatch import receiver

##############################################################################################
# Module
##############################################################################################

class Citizen(models.Model):
	first_name = models.CharField(max_length = 50, help_text = 'First name')
	last_name = models.CharField(max_length = 50, help_text = 'Last name')
	middle_name = models.CharField(max_length = 50, blank = True, null = True, help_text = 'Middle name')
	date_of_birth = models.DateField(blank = True, null = True, help_text="Date of birth")
	year_of_birth = models.CharField(max_length = 4,blank = True, null = True, help_text="Year of birth")
	citizen_id = models.CharField(max_length=50, blank=False,  unique=True, help_text = 'unique ID for citizen')
	phone_1 = models.CharField(max_length = 30, blank = True, null = True, help_text = 'Primary Phone Number')
	phone_2 = models.CharField(max_length = 50, blank = True, null = True, help_text = 'Secondary Phone Number')
	email = models.EmailField(max_length = 50, blank = True, null = True, help_text = 'Email')
	address = models.CharField(max_length = 255, null = True, blank = True, help_text ='Address')
	po_box = models.CharField(max_length = 50, blank = True, null = True, help_text = 'PO Box')
	gender = models.CharField(max_length = 50, help_text = 'Gender', choices = gender_types)
	foreign_identity_type = models.CharField(max_length = 50, blank = True, null = True, help_text = 'Foreign identity type. For example: passport.')
	foreign_identity_number = models.CharField(max_length = 50, blank = True, null = True, help_text = 'Foreign identity ID.')
	status = models.ForeignKey(Status,  blank=False, default=1, help_text="status")
	deactivate_reason = models.CharField(max_length = 50, blank=False, default=1, null = True, choices = citizen_deactivate_reasons)
	note = models.TextField(null=True, blank=True)
	photo = models.ImageField(upload_to='citizenphotos', blank = True, null = True, help_text='Photo of The Citizen')
	foreign_record_id = models.CharField(max_length = 50, blank = True, null = True, help_text = 'Foreign id from the old DB.')
	cp_password = models.CharField(max_length=128, help_text='Enter password.', blank = True, null = True)
	contact_details_confirmed = models.DateField(null=True, blank=True, help_text="dd/mm/yyyy")
	status_new_id = models.IntegerField(null=True)
	entity_id = models.IntegerField(null=True)

	def __unicode__(self):
		if self.middle_name and self.middle_name!='' and self.middle_name !='null':
			return self.first_name +' '+ self.middle_name +' '+ self.last_name
		else:
			return self.first_name + ' ' + self.last_name

	def getDisplayName(self):
		if self.middle_name and self.middle_name!='' and self.middle_name !='null':
			return self.first_name +' '+ self.middle_name +' '+ self.last_name
		else:
			return self.first_name + ' ' + self.last_name

	def save(self, *args, **kwargs):
		"""
		set status to be "active" by default
		"""
		try:
			self.status
		except Exception:
			self.status = Status.objects.get(id = 1)
		try:
			self.deactivate_reason
		except Exception:
			self.deactivate_reason = 'deceased'
		if not self.deactivate_reason:
			self.deactivate_reason = 'deceased'
		if not self.gender:
			self.gender = 'Unknown'

		#strip whitespaces before save
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

	def get_properties(self):
		from property.models import Property
		return Property.objectsIgnorePermission.filter(owners__owner_citizen=self)




