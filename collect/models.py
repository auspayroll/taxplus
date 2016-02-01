from datetime import date, datetime, timedelta
from dateutil import parser
from dateutil.relativedelta import relativedelta
from decimal import Decimal
from django.contrib.auth.models import User
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
from taxplus.models import Sector
import ast
import binascii
import json
import os
from dev1.ThreadLocal import get_current_request_log
from random import randint
from datetime import datetime

class CollectionGroup(models.Model):
	name = models.CharField(max_length = 30)
	processed = models.IntegerField(default=0)
	unprocessed = models.IntegerField(default=0)
	no_collectors = models.IntegerField(default=0)

	def __unicode__(self):
		return self.name

	def allocate_epays(self, amount, sector, user=None):
		batch = EpayBatch.objects.create(creator=user, collection_group=self, amount=amount, sector=sector)
		no_employees = self.collectors.all().count()
		remainder = amount % no_employees
		batch_per_collector = amount / no_employees
		for collector in self.collectors.all():
			collector.allocate_epays(batch_per_collector, batch)
			self.unprocessed += batch_per_collector

			if remainder > 0:
				collector.allocate_epays(1, batch)
				remainder -= 1
				self.unprocessed += 1
		self.save()
		return True

class Collector(models.Model):
	user = models.OneToOneField(User)
	collection_group = models.ForeignKey(CollectionGroup, null=True, related_name="collectors")
	registration_no = models.CharField(max_length = 30, null=True, blank=True, help_text = "")
	processed = models.IntegerField(default=0)
	unprocessed = models.IntegerField(default=0)

	def __unicode__(self):
		return self.user.get_full_name()

	def allocate_epays(self, amount, batch=None):
		while amount > 0:
			epay = Epay.objects.create(collector=self, batch=batch)
			epay.alt = epay.__unicode__()
			epay.save()
			amount -= 1
			self.unprocessed += 1
		self.save()


	def save(self, *args, **kwargs):
		group = self.collection_group
		if not self.pk:
			group.no_collectors += 1
			group.save()
		else:
			db_object = get_object_or_404(Collector, pk=self.pk)
			db_group = db_object.collection_group
			if db_group.pk != group.pk:
				db_group.no_collectors -= 1
				db_group.save()
				group.no_collectors += 1
				group.save()

		return super(Collector, self).save(*args, **kwargs)



class EpayBatch(models.Model):
	creator = models.ForeignKey(User, null=True, related_name='epay_set')
	created = models.DateTimeField(auto_now_add=True)
	collection_group = models.ForeignKey(CollectionGroup, null=True)
	amount = models.IntegerField(default=0)
	sector = models.ForeignKey(Sector, null=True)

class Epay(models.Model):
	random = models.IntegerField()
	collector = models.ForeignKey(Collector, null=True, related_name='epays')
	used = models.BooleanField(default=False)
	alt = models.CharField(max_length = 30, blank = True, null = True, help_text = 'Alternative EPAY number.')
	used_on = models.DateTimeField(null=True)
	collection_point = gis_models.PointField(blank =True, null=True)
	batch = models.ForeignKey(EpayBatch, null=True)

	def __unicode__(self):
		return "%s-%s" % (self.pk, self.random)


	@property
	def epay(self):
		return self.__unicode__()

	def save(self, *args, **kwargs):
		if not self.pk:
			self.random = randint(1000, 9999)

		saved = super(Epay, self).save(*args, **kwargs)
		if not self.alt:
			self.alt = self.__unicode__()
		return saved


	def process(self, collection_point=None):
		self.used =True
		self.used_on = datetime.now()
		self.collection_point = collection_point
		collector = self.collector
		collector.processed += 1
		collector.unprocessed -= 1
		collector.save()
		collection_group = collector.collection_group
		collection_group.processed += 1
		collection_group.unprocessed -= 1
		self.save()





