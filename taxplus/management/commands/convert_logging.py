from django.core.management.base import BaseCommand, CommandError
from taxplus.models import LogOld, Property
from datetime import date
from django import db
from dev1.loginBackend import CustomLoginBackend
from dev1.ThreadLocal import LogRelation, LogTag
from django.contrib.contenttypes import generic
from django.contrib.contenttypes.models import ContentType
import ast
import json

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
		backend = CustomLoginBackend()

		for log in LogOld.objects.all().select_related('user'):
			try:
				print log.message or log.pk

				#-----update staff user
				if log.user and not log.staff:
					log.staff = backend.authenticate(username=log.user.email, check_password=False)
					log.save(update_fields=['staff'])

				#--------tag
				ct = None
				object_id = None
				if log.prop:
					ct = ContentType.objects.get_for_model(log.prop)
					object_id = log.prop.pk

				if log.business_id:
					ct = ContentType.objects.get_for_model(log.business)
					object_id = log.business_id

				if log.citizen_id:
					ct = ContentType.objects.get_for_model(log.citizen)
					object_id = log.citizen_id

				if log.media_id:
					try:
						media = Media.objects.get(pk=str(log.media_id))
					except:
						pass
					else:
						object_id = str(log.media_id)
						ct = ContentType.objects.get_for_model(media)

				if log.fee_id:
					ct = ContentType.objects.get_for_model(log.fee)
					object_id = log.fee_id

				if log.payfee_id:
					receipt = log.payfee.receipt
					object_id = receipt.pk
					ct = ContentType.objects.get_for_model(log.fee)

				elif log.receipt_id:
					object_id = log.receipt_id
					ct = ContentType.objects.get_for_model(log.receipt)

				if ct and object_id:
					try:
						ct.model_class().objects.get(pk=object_id)
					except:
						pass
					else:
						LogTag.objects.create(content_type=ct, object_id=object_id, log_id=log.pk)

			except:
				import pdb
				pdb.set_trace()

			#--------------change log
			if log.old_data or log.new_data:
				model = None
				object_id = None
				if log.table == 'property_property' and (log.prop or log.object_id):
					model = Property
					object_id = log.prop.pk or str(log.object_id)

				elif log.table == 'citizen_citizen' and (log.citizen_id or log.object_id):
					model = Citizen
					object_id = log.citizen_id or str(log.object_id)

				elif log.table == 'business_business' and (log.business_id or log.object_id):
					model = Business
					object_id = log.business_id or str(log.object_id)


				if model and object_id:
					try:
						print "match found--------------------"
						model.objects.get(pk=object_id)
						ct = ContentType.objects.get_for_model(model)
						old_data = json.dumps(ast.literal_eval(log.old_data))
						new_data = json.dumps(ast.literal_eval(log.new_data))
						LogRelation.objects.create(content_type=ct, object_id=object_id, old_object=old_data, new_object=new_data, log_id=log.id)

					except:
						print "*** No match found ************"
						pass





