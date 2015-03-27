# coding: utf-8
from django.contrib.auth.models import User
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
from django.core import serializers
from django.db import models
import ast
import json


"""
	threadlocals middleware
	~~~~~~~~~~~~~~~~~~~~~~~

	make the request object everywhere available (e.g. in model instance).

	based on: http://code.djangoproject.com/wiki/CookBookThreadlocalsAndUser

	Put this into your settings:
	--------------------------------------------------------------------------
		MIDDLEWARE_CLASSES = (
			...
			'django_tools.middlewares.ThreadLocal.ThreadLocalMiddleware',
			...
		)
	--------------------------------------------------------------------------


	Usage:
	--------------------------------------------------------------------------
	from django_tools.middlewares import ThreadLocal

	# Get the current request object:
	request = ThreadLocal.get_current_request()

	# You can get the current user directy with:
	user = ThreadLocal.get_current_user()
	--------------------------------------------------------------------------

	:copyleft: 2009-2011 by the django-tools team, see AUTHORS for more details.
	:license: GNU GPL v3 or above, see LICENSE for more details.
"""

try:
	from threading import local
except ImportError:
	from django.utils._threading_local import local

_thread_locals = local()

def get_current_request():
	""" returns the request object for this thead """
	return getattr(_thread_locals, "request", None)

def get_current_request_log():
	return getattr(_thread_locals, "log", None)

def get_locals():
	return _thread_locals

def get_current_user():
	""" returns the current user, if exist, otherwise returns None """
	request = get_current_request()
	if request:
		if  request.session.has_key('user'):
			from asset.models import Business
			from citizen.models import Citizen
			user = request.session['user']
			if isinstance(user, (Business,Citizen)):
				del request.session['user']
				return None
			else:
				return user
	return None


class ThreadLocalMiddleware(object):
	""" Simple middleware that adds the request object in thread local storage."""

	def process_request(self, request):
		log = Log(request_path=request.path)
		log.request_remote=request.META.get('REMOTE_ADDR')
		log.request_type={'GET':'G', 'POST':'P'}.get(request.method)
		if request.user.is_authenticated():
			log.staff = request.user
		log.save()
		_thread_locals.log = log
		_thread_locals.request = request

class Log(models.Model):
	"""
	keep log for each action taken by user.
	"""
	transaction_id = models.IntegerField(null = True, blank = True)
	#user_id = models.IntegerField(null=True, blank=True)
	staff = models.ForeignKey(User, help_text="",blank = True, null=True, related_name="staff_logs")
	tids = models.CharField(max_length = 200, null=True, blank = True)
	tax_type = models.CharField(max_length = 50, null=True, blank = True)
	tax_id = models.CharField(max_length = 50, null=True, blank = True)
	payment_type = models.CharField(max_length = 50, null=True, blank = True)
	payment_id = models.CharField(max_length = 50, null=True, blank = True)
	media_id = models.CharField(max_length = 50, null=True, blank = True)
	username = models.CharField(max_length=10, null=True, blank=True)
	table = models.CharField(blank=True, null=True, max_length=100)
	date_time = models.DateTimeField(auto_now_add=True)
	old_data = models.CharField(blank=True, null=True, max_length=1000)
	new_data = models.CharField(blank=True, null=True, max_length=1000)
	message = models.TextField(blank=True, null=True)
	request_type = models.CharField(blank=True, null=True, max_length=1)
	request_path = models.TextField(blank=True, null=True)
	request_remote	= models.TextField(blank=True, null=True)
	content_type = models.ForeignKey(ContentType, null=True)
	object_id = models.PositiveIntegerField(null=True)
	content_object = generic.GenericForeignKey('content_type', 'object_id')
	content_type2 = models.ForeignKey(ContentType, null=True, related_name="sub_logs")
	object_id2 = models.PositiveIntegerField(null=True)
	content_object = generic.GenericForeignKey('content_type', 'object_id')


	class Meta:
		db_table = 'log_log'
		app_label = 'taxplus'

	def __unicode__(self):
		if self.message:
			return self.message

		elif self.crud == 1: #created
			return "%s created" % self.content_object

		elif self.crud == 2: #update
			return "%s updated:" % self.whats_changed

	@classmethod
	def log(cls, target=None, target2=None, message=None):
		log = get_current_request_log()
		if not log:
			log = Log()

		log.message  = message
		if target:
			log.content_type = content_type = ContentType.objects.get_for_model(target)
			log.object_id = target.pk

		if target2:
			log.content_type2 = content_type = ContentType.objects.get_for_model(target2)
			log.object_id2 = target2.pk

		log.save()
		return log

class LogRelation(models.Model):
	content_type = models.ForeignKey(ContentType, null=True)
	object_id = models.PositiveIntegerField(null=True)
	content_object = generic.GenericForeignKey('content_type', 'object_id')
	log = models.ForeignKey(Log, related_name='log_objects')
	old_object = models.TextField(null=True)
	new_object = models.TextField(null=True)
	crud = models.PositiveSmallIntegerField(blank=True, default=2)

	class Meta:
		db_table = 'taxplus_logrelation'
		app_label = 'taxplus'

	@property
	def whats_changed(self):
		"""
		return a dictionary of whats changed in the format
		{'field_name':(old_value, new_value), ...}
		"""
		try:
			old_data = json.loads(self.old_object)
		except ValueError:
			old_data = ast.literal_eval(self.old_object)

		try:
			new_data = json.loads(self.new_object)
		except ValueError:
			new_data = ast.literal_eval(self.new_object)

		changed = {}
		for k,v in new_data.items():
			changed[k] = (v, old_data.get(k))

		return changed
