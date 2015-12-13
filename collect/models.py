from datetime import date, datetime, timedelta
from dateutil import parser
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.contrib.gis.db import models as gis_models
from django.db import models
from django.db.models import Q
from django.db.models import Sum
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.core import serializers
from property.models import Sector
import ast
import binascii
import json
import os
from dev1.ThreadLocal import get_current_request_log
from random import randint

class CollectionGroup(models.Model):
	name = models.CharField(max_length = 30)
	sector = models.ManyToManyField(Sector, null=True)	
	def __unicode__(self):
		return self.name

class Collector(models.Model):
	user = models.OneToOneField(User)
	collection_group = models.ForeignKey(CollectionGroup, null=True)

class Epay(models.Model):
	random = models.IntegerField()
	collector = models.ForeignKey(Collector, null=True, related_name='epays')
	creator = models.ForeignKey(User, null=True, related_name='epay_set')
	used = models.BooleanField(default=False)
	alt = models.CharField(max_length = 30, blank = True, null = True, help_text = 'Alternative EPAY number.')
	used_on = models.DateTimeField(null=True)
	created = models.DateTimeField(auto_now_add=True)
	collection_point = gis_models.PointField(blank =True, null=True)
	
	def __unicode__(self):
		return "%s-%s" % (self.pk, self.random)

	def save(self, *args, **kwargs):
		if not self.pk:
			self.random = randint(1000, 9999)
		return super(LoggedModel, self).save(*args, **kwargs)


