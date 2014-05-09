from django.db import models
from dev1 import variables

class Status(models.Model):
	name = models.CharField(max_length = 30, help_text = 'Status name')
	def __unicode__(self):
		return self.name

class TaxType(models.Model):
	displayname = models.CharField(max_length = 100, null = True, blank = True, verbose_name = 'Display name')
	codename = models.CharField(max_length = 100, null = True, blank = True, verbose_name = 'Code name')
	i_status = models.CharField(max_length = 10, choices = variables.status_choices, default='active', blank = True)