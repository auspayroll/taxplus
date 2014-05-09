from django.db import models
from datetime import datetime
from django.utils import timezone
from common.models import Status
from pmauth.models import PMUser
from citizen.models import Citizen
from asset.models import Business

query_types = (
	('payment dispute','payment dispute'),
	('technical issue','technical issue'),
	('general feedback','general feedback'),
	('customer support','customer support'),
	('complaints on council','complaints on council')
)

class Contact(models.Model):
	name = models.CharField(max_length = 100, help_text="Contact name.")
	email = models.EmailField(max_length = 100, help_text="Contact email.")
	phone = models.CharField(max_length = 100, help_text="Contact Phone.")
	query_type = models.CharField(max_length = 100, choices = query_types, help_text="Please select the type of query.")
	message = models.TextField(help_text="Please enter message here.")
	citizen = models.ForeignKey(Citizen, null=True, blank=True)
	business = models.ForeignKey(Business, null=True, blank=True)
	user = models.ForeignKey(PMUser, null=True, blank=True)

	date_time = models.DateTimeField(default=timezone.now)
	status = models.ForeignKey(Status)

	def save(self, *args, **kwargs):
		"""
		set status to be "active" by default
		"""
		try:
			self.status
		except Exception:
			self.status = Status.objects.get(id = 1)
		models.Model.save(self)

	def getLogMessage(self,old_data=None,new_data=None, action=None):
		"""
		return tailored log message for different actions taken on this citizen
		"""
		if action == "add":
			return "submit a query [" + self.message + "]"