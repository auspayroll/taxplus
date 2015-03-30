from django.core.management.base import BaseCommand, CommandError
from taxplus.models import LogOld, Property, Citizen, Business
from datetime import date
from django import db
from dev1.loginBackend import CustomLoginBackend
from dev1.ThreadLocal import LogRelation, LogTag
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
import ast
import json

backend = CustomLoginBackend()

def convert_old_log(log):

	if type(log) is int:
		log = LogOld.objects.get(pk=log)

	#-----update staff user
	if log.user and not log.staff:
		log.staff = backend.authenticate(username=log.user.email, check_password=False)
		log.save(update_fields=['staff'])

	#--------tag
	if not log.old_data and not log.new_data:
		if log.prop:
			ct = ContentType.objects.get_for_model(log.prop)
			LogRelation.objects.create(content_type=ct, object_id=log.prop.pk, log_id=log.pk, crud=2)

		if log.business_id:
			ct = ContentType.objects.get_for_model(log.business)
			LogRelation.objects.create(content_type=ct, object_id=log.business_id, log_id=log.pk, crud=2)

		if log.citizen_id:
			ct = ContentType.objects.get_for_model(log.citizen)
			LogRelation.objects.create(content_type=ct, object_id=log.citizen_id, log_id=log.pk, crud=2)

		if log.media_id:
			try:
				media = Media.objects.get(pk=str(log.media_id))
			except:
				pass
			else:
				ct = ContentType.objects.get_for_model(log.media)
				LogRelation.objects.create(content_type=ct, object_id=log.media.pk, log_id=log.pk, crud=1)
				for tag in log.media.tags:
					ct = ContentType.objects.get_for_model(tag)
					LogRelation.objects.create(content_type=ct, object_id=tag.pk, log_id=log.pk, crud=2)

		if log.fee_id:
			ct = ContentType.objects.get_for_model(log.fee)
			LogRelation.objects.create(content_type=ct, object_id=log.fee_id, log_id=log.pk, crud=2)

		if log.payfee_id:
			receipt = log.payfee.receipt
			ct = ContentType.objects.get_for_model(receipt)
			LogRelation.objects.create(content_type=ct, object_id=receipt.pk, log_id=log.pk, crud=1)
			for tag in receipt.tags:
				ct = ContentType.objects.get_for_model(receipt)
				LogRelation.objects.create(content_type=ct, object_id=tag.pk, log_id=log.pk, crud=2)

		elif log.receipt_id:
			ct = ContentType.objects.get_for_model(log.receipt)
			LogRelation.objects.create(content_type=ct, object_id=log.receipt_id	, log_id=log.pk, crud=1)
			for tag in log.receipt.tags:
				ct = ContentType.objects.get_for_model(tag)
				LogRelation.objects.create(content_type=ct, object_id=tag.pk, log_id=log.pk, crud=2)

	#--------------change log
	if log.old_data or log.new_data:
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

			except AttributeError:
				import pdb
				pdb.set_trace()

			except model.DoesNotExist:
				pass

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

		for log in LogOld.objects.all().select_related('user'):
			try:
				convert_old_log(log)
			except:
				raise Exception('Error in log %s' % log)
			else:
				print log.message or log.pk
