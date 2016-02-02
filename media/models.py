from django.db import models
from dev1 import variables
from citizen.models import Citizen
from asset.models import *
from jtax.models import IncompletePayment, Fee, PayFee
from taxplus.models import PaymentReceipt


class MediaManager(models.Manager):
	def get_query_set(self):
		return super(MediaManager,self).get_query_set().exclude(restored=False, missing=1)


class Media(models.Model):
	tags = models.CharField(max_length = 150, help_text = 'Tags for the Media', null=True, blank = True)
	title = models.CharField(max_length = 150, null=True, blank = True, help_text = 'Display name of the media')
	description = models.TextField(null=True, blank = True, help_text = 'Notes/Reminder')
	file_name = models.CharField(max_length = 150)
	path = models.CharField(max_length = 255)
	file_type = models.CharField(max_length = 50)
	file_size = models.CharField(max_length = 50)
	citizen = models.ForeignKey(Citizen,  null=True, blank=True)
	business = models.ForeignKey(Business,  null=True, blank=True)
	property = models.ForeignKey(Property,  null=True, blank=True)
	billboard = models.ForeignKey(Billboard,  null=True, blank=True)
	tax_type = models.CharField(max_length = 50,  help_text = 'Type of Tax/Fee Associated with this Media', null=True, blank = True)
	tax_id = models.IntegerField(help_text="", null=True, blank = True)
	payment_type = models.CharField(max_length = 50, help_text = 'Type of Payment Associated with this Media', null=True, blank = True)
	payment_id = models.IntegerField(help_text="", null=True, blank = True)
	incomplete_payment = models.ForeignKey(IncompletePayment, null=True, blank=True, related_name="incomplete_payment_medias")
	user_id = models.IntegerField(null=True, blank=True, help_text="")
	#user_id = models.IntegerField(max_length = 10, help_text="")
	i_status = models.CharField(max_length = 10, choices = variables.status_choices, default='active', blank = True)
	date_created = models.DateTimeField(help_text='Date this record is saved',auto_now_add=True)
	missing = models.IntegerField(null=True)
	restored = models.NullBooleanField()
	payfee = models.ForeignKey(PayFee, null=True, blank=True)
	fee = models.ForeignKey(Fee, null=True, blank=True)
	receipt = models.ForeignKey(PaymentReceipt, null=True, blank=True, related_name='media_receipt')

	objects = MediaManager()

	def __unicode__(self):
		return str(self.file_name) + " " + str(self.title)
	def getLogMessage(self,old_data=None,new_data=None, action=None):
		return getLogMessage(self,old_data,new_data, action)


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