from django.core.management.base import BaseCommand, CommandError
from taxplus.models import Property, Citizen, Business, Log, LogRelation, Media
from datetime import date
from django import db
from dev1.loginBackend import CustomLoginBackend
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
import ast
import json

backend = CustomLoginBackend()

def convert_old_log(log):
	if type(log) is int:
		log = Log.objects.get(pk=log)

	#-----update staff user
	if log.user and not log.staff:
		log.staff = backend.authenticate(username=log.user.email, check_password=False)
		log.save(update_fields=['staff'])

	#--------tag
	tags = []
	if log.media_id:
		try:
			media = Media.objects.get(pk=str(log.media_id))
		except:
			pass
		else:
			for tag in media.tags:
				tags.append(tag)
			ct = ContentType.objects.get_for_model(media)
			log.modified_objects = True
			log.save(update_fields=['modified_objects'])
			LogRelation.objects.create(content_type=ct, object_id=media.pk, log_id=log.pk, crud=1)

	elif log.payfee_id:
		receipt = log.payfee.receipt
		for tag in receipt.tags:
			tags.append(tag)
		ct = ContentType.objects.get_for_model(receipt)
		log.modified_objects = True
		log.save(update_fields=['modified_objects'])
		LogRelation.objects.create(content_type=ct, object_id=receipt.pk, log_id=log.pk, crud=1)

	elif log.receipt_id:
		for tag in log.receipt.tags:
			tags.append(tag)
		ct = ContentType.objects.get_for_model(log.receipt)
		if 'reversed' in log.message:
			crud = 3
		else:
			crud = 1
		log.modified_objects = True
		log.save(update_fields=['modified_objects'])
		LogRelation.objects.create(content_type=ct, object_id=log.receipt.pk, log_id=log.pk, crud=crud)

	if log.fee_id:
		try:
			fee = Fee.objects.get(pk=str(log.fee_id))
		except:
			pass
		else:
			for tag in fee.tags:
				tags.append(tag)

	if not tags and not log.business_id and not log.citizen_id and not log.prop and log.table == "jtax_fee" and log.tax_id is not None:
		try:
			fee = Fee.objects.get(pk=int(log.tax_id))
		except:
			pass
		else:
			for tag in fee.tags:
				tags.append(tag)

	for tag in tags:
		if type(tag) is Business and not log.business:
			log.business= tag

		if type(tag) is Property and not log.prop:
			log.prop = tag

		if type(tag) is Citizen and not log.citizen:
			log.citizen = tag

	if tags:
		log.save(update_fields=['prop', 'citizen', 'business'])

	#--------------change log
	if log.old_data or log.new_data:
		log.modified_objects = True
		log.save(update_fields=['modified_objects'])
		model = None
		object_id = None
		if log.table == 'property_property' and log.prop:
			model = Property
			object_id = log.prop.pk

		elif log.table == 'citizen_citizen' and log.citizen_id:
			model = Citizen
			object_id = log.citizen_id

		elif log.table == 'asset_business' and log.business_id:
			model = Business
			object_id = log.business_id

		if model and object_id:
			try:
				model.objects.get(pk=object_id)
			except model.DoesNotExist:
				return
			ct = ContentType.objects.get_for_model(model)
			if log.old_data:
				try:
					log.old_data = ast.literal_eval(log.old_data)
				except ValueError:
					log.old_data = {}
			else:
				log.old_data = {}

			if log.new_data:
				try:
					log.new_data = ast.literal_eval(log.new_data)
				except ValueError:
					log.new_data = {}
			else:
				log.new_data = {}

			for k,v in log.new_data.items():
				if v == log.old_data.get(k):
					del(log.new_data[k])
					del(log.old_data[k])

			old_data = json.dumps(log.old_data)
			new_data = json.dumps(log.new_data)
			LogRelation.objects.create(content_type=ct, object_id=object_id, old_object=old_data, new_object=new_data, log_id=log.id, crud=3)

class Command(BaseCommand):
	#fixed_asset/rental_income/trading_license/cleaning_fee/market_fee/land_lease_fee
	args = ''
	help = """
	Adds entity relationship to fees
	This will be the entity responsible for fee payment

	"""
	name= 'Convert land use types'

	def handle(self, *args, **options):
		#table_map = dict([ (ct.model_class()._meta.db_table, ct.model_class() ) for ct in ContentType.objects.all() if ct.model_class()])

		#create missing media logs
		last_media_log = Log.objects.filter(media_id__isnull=False).order_by('-id')[0]
		ct = ContentType.objects.get_for_model(last_media_log)
		first_media_log = None
		for media in Media.objects.filter(id__gt=int(last_media_log.media_id)).order_by('id'):
			staff = backend.authenticate(username=last_media_log.user.email, check_password=False)
			log = Log.objects.create(user=last_media_log.user, staff=staff, media_id=media.pk, citizen=media.citizen, business=media.business, prop=media.prop, date_time=media.date_created, modified_objects=True, message="New Media %s" % media)
			if not first_media_log:
				first_media_log = log
			log.date_time = media.date_created
			LogRelation.objects.create(log=log, object_id=media.pk, content_type=ct, crud=1)
			print "New for created for %s" % media

		for log in Log.objects.all().select_related('user'):
				print log.message or log.pk
				try:
					convert_old_log(log)
				except:
					print "Problem with log %s" % log.pk
					break
