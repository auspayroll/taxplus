from django.db import models
from dev1 import variables
import os.path

class Form(models.Model):
	title = models.CharField(max_length = 150, null=True, blank = True, help_text = 'Display name of the form')
	language = models.CharField(max_length = 25, choices =variables.languages, default="English", help_text="Language of the form")
	description = models.TextField(null=True, blank = True, help_text = 'Notes/Reminder')
	path = models.CharField(max_length = 255)
	user_id = models.IntegerField(help_text="")
	i_status = models.CharField(max_length = 10, choices = variables.status_choices, default='active', blank = True)
	date_created = models.DateTimeField(help_text='Date this record is saved',auto_now_add=True)
	def __unicode__(self):
		return self.title + " - " + self.path
	def getLogMessage(self,old_data=None,new_data=None, action=None):
		return getLogMessage(self,old_data,new_data, action)
	def getFileName(self):
		return os.path.basename(self.path)

#General functions used in many models
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
		if old_data != None:
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