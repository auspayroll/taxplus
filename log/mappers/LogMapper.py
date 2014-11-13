from django.forms import model_to_dict
from datetime import datetime
from django.utils import timezone
from admin.Common import Common
import ast, pytz
from property.mappers.PropertyMapper import PropertyMapper
from log.models import Log
from property.models import Property
from asset.models import Business
from citizen.models import Citizen
from django.db.models import Q


class LogMapper:

	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get logs by conditions
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def getLogsByConditions(conditions):
		logs = None
		count = 0
		for key, value in conditions.iteritems():
			if key == 'upi' and value and value!="":
				property = PropertyMapper.getPropertyByUPI(value)
				if property:
					if count > 0:
						logs = logs.filter(property = property)
					else:
						logs = Log.objects.filter(property = property)
					count = count + 1
				else:
					return None

			if key == 'transaction_id' and value and value!="":
				if count > 0:
					logs = logs.filter(transaction_id = value)
				else:
					logs = Log.objects.filter(transaction_id = value)
				count = count + 1
			if key == 'username' and value and value!="":
				if count > 0:
					logs = logs.filter(username__icontains = value)
				else:
					logs = Log.objects.filter(username__icontains = value)
				count = count + 1
			if key == 'citizen' and value and value!="":
				if count > 0:
					logs = logs.filter(citizen = value)
				else:
					logs = Log.objects.filter(citizen = value)
				count = count + 1
			if key == 'citizen_id' and value and value!="":
				if count > 0:
					logs = logs.filter(citizen__citizen_id__iexact = value)
				else:
					logs = Log.objects.filter(citizen__citizen_id__iexact = value)
				count = count + 1
			if key == 'business' and value and value!="":
				#also include logs of subbusinesses belong to this business
				subbusinesses = value.subbusiness_set.all()
				if count > 0:
					logs = logs.filter(Q(business = value)|Q(subbusiness__in=subbusinesses))
				else:
					logs = Log.objects.filter(Q(business = value)|Q(subbusiness__in=subbusinesses))
				count = count + 1
			if key == 'property' and value and value!="":
				if count > 0:
					logs = logs.filter(property = value)
				else:
					logs = Log.objects.filter(property = value)
				count = count + 1
			if key == 'tax_id' and value and value!="":
				if count > 0:
					logs = logs.filter(tax_id__iexact = value, tax_type__iexact=conditions['tax_type'])
				else:
					logs = Log.objects.filter(tax_id__iexact = value, tax_type__iexact=conditions['tax_type'])
				count = count + 1
			if key == 'payment_id' and value and value!="":
				if count > 0:
					logs = logs.filter(payment_id__iexact = value, payment_type__iexact=conditions['payment_type'])
				else:
					logs = Log.objects.filter(payment_id__iexact = value, payment_type__iexact=conditions['payment_type'])
				count = count + 1
			if key == 'media_id' and value and value!="":
				if count > 0:
					logs = logs.filter(media_id__iexact = value)
				else:
					logs = Log.objects.filter(media_id__iexact = value)
				count = count + 1
			if key == 'period_from' and value and value!="":
				if count > 0:
					logs = logs.filter(date_time__gte = value)
				else:
					logs = Log.objects.filter(date_time__gte = value)
				count = count + 1
			if key == 'period_to' and value and value!="":
				if count > 0:
					logs = logs.filter(date_time__lte = value)
				else:
					logs = Log.objects.filter(date_time__lte = value)
				count = count + 1
			if key == 'message' and value and value!="":
				if count > 0:
					logs = logs.filter(message__icontains = value)
				else:
					logs = Log.objects.filter(message__icontains = value)
				count = count + 1
			if key == 'business_name' and value and value!="":
				if count > 0:
					logs = logs.filter(business__name__icontains = value)
				else:
					logs = Log.objects.filter(business__name__icontains = value)
				count = count + 1
			if key == 'tin' and value and value!="":
				if count > 0:
					logs = logs.filter(business__tin__exact = value)
				else:
					logs = Log.objects.filter(business__tin__exact = value)
				count = count + 1

		logs = logs.order_by('-date_time').select_related('citizen','business','property','property__cell')
		return logs


	@staticmethod
	def raw(sql):
		return Log.objects.raw(sql)



	@staticmethod
	def getTransactionId():
		"""
		Generate a new transactionid by using max transactionid + 1
		"""
		count = Log.objects.all().count()
		if count == 0:
			return None
		else:
			return None
			#log = Log.objects.all().order_by("-transactionid")[0]
			#return log.transactionid + 1


	# action could be: 1)view 2)add 3)change 4)delete 5)login 6)logout
	@staticmethod
	def createLog(request,**kwargs):
		"""
		Given the action taken on the object, create a log for this action
		Make a copy of the old data and new data as strings in databse
		"""
		user = None
		property = None
		citizen = None
		business = None
		subbusiness = None
		object = None
		old_data = None
		new_data = None
		action = None
		message_all = None
		search_message_all = None
		search_message_action =None
		search_message_purpose =None
		search_object_class_name = None
		search_conditions = {}

		log = Log()
		log.transaction_id = LogMapper.getTransactionId()
		if request.session.has_key("user"):
			user = request.session.get('user')
			log.setUser(user)
		message = ""

		# get parameters from arguments
		for key, value in kwargs.iteritems():
			if key == "user":
				user = kwargs['user']
				log.setUser(user)
			if key == "username":
				log.username = kwargs['username']
			if key == "action":
				action = kwargs["action"]
			if key == "object":
				object = kwargs["object"]
			if key == "old_data":
				old_data = kwargs["old_data"]
			if key == "new_data":
				new_data = kwargs["new_data"]
			if key == "property":
				property = kwargs["property"]
			if key == "citizen":
				citizen = kwargs["citizen"]
			if key == "business":
				business = kwargs["business"]
			if key == "subbusiness":
				subbusiness = kwargs["subbusiness"]
			if key == "message_all":
				message_all = kwargs["message_all"]
			if key == "search_message_all":
				search_message_all = kwargs["search_message_all"]
			if key == "search_message_action":
				search_message_action = kwargs["search_message_action"]
			if key == "search_message_purpose":
				search_message_purpose = kwargs["search_message_purpose"]
			if key == "search_object_class_name":
				search_object_class_name = kwargs["search_object_class_name"]
			if key == "search_conditions":
				search_conditions = kwargs["search_conditions"]
			if key == "message":
				message = kwargs['message']
			if key in ('tax_id','payment_id','media_id','payment_type','tax_type'):
				setattr(log, key, value)
			if key == 'payment_id':
				setattr(log, 'payfee_id', int(value))
			if key == 'tax_id':
				setattr(log, 'fee_id', int(value))

		if action == "login" or action == "logout":
			message = action
			log.setTable(user._meta.db_table)
		elif message_all:
			message = message_all
		elif action == "search":
			# we can provide customized message for a search
			if search_message_all:
				message = search_message_all
			# normal search: we need search object class name and conditions
			else:
				if search_message_action:
					message = search_message_action
				else:
					message = "search " + search_object_class_name
				if search_message_purpose:
					message  = message + " for " + search_message_purpose + " purpose"
				if search_conditions:
					message = message + " with conditions("
					count = 0
					for key, value in search_conditions.iteritems():
						if value:
							if count > 0:
								message = message + ", "
							message = message + key + "=" + str(value)
							count = count + 1
					message = message + ")"
		else:
			if message == "":
				message = LogMapper.getLogMessage(object,old_data, new_data, action)
			if new_data is not None:
				for key, value in new_data.iteritems():
					if type(value) is datetime:
						new_data[key]=value.astimezone(pytz.utc)
			log.setOldObj(old_data)
			log.setNewObj(new_data)
			if not log.table and object:
				log.setTable(object._meta.db_table)


		if type(object) is Property:
			log.property = object
		elif type(object) is Business:
			log.business = object
		elif type(object) is Citizen:
			log.citizen = object

		if property:
			log.property = property
		if citizen:
			log.citizen = citizen
		if business:
			log.business = business
		if subbusiness:
			log.subbusiness = subbusiness


		log.setMessage("User ["+user.firstname+" "+user.lastname+"] "+message)
		log.save()

	# create logs from Command Apps
	@staticmethod
	def createLogCommand(**kwargs):
		"""
		Given the action taken on the object, create a log for this action
		Make a copy of the old data and new data as strings in databse
		"""
		property = None
		citizen = None
		business = None
		subbusiness = None
		object = None
		old_data = None
		new_data = None
		action = None
		message_all = None

		log = Log()

		message = ""

		# get parameters from arguments
		for key, value in kwargs.iteritems():
			if key == "username":
				log.username = kwargs['username']
			if key == "user_id":
				log.user_id = kwargs['user_id']
			if key == "action":
				action = kwargs["action"]
			if key == "object":
				object = kwargs["object"]
			if key == "old_data":
				old_data = kwargs["old_data"]
			if key == "new_data":
				new_data = kwargs["new_data"]
			if key == "property":
				property = kwargs["property"]
			if key == "citizen":
				citizen = kwargs["citizen"]
			if key == "business":
				business = kwargs["business"]
			if key == "subbusiness":
				subbusiness = kwargs["subbusiness"]
			if key == "message_all":
				message_all = kwargs["message_all"]
			if key == "message":
				message = kwargs['message']
			if key in ('tax_id','payment_id','media_id','payment_type','tax_type'):
				setattr(log, key, value)

		if message == "":
			message = LogMapper.getLogMessage(object,old_data, new_data, action)
		if new_data is not None:
			for key, value in new_data.iteritems():
				if type(value) is datetime:
					new_data[key]=value.astimezone(pytz.utc)
		log.setOldObj(old_data)
		log.setNewObj(new_data)
		if not log.table and object:
			log.setTable(object._meta.db_table)

		if property:
			log.property = property
		if citizen:
			log.citizen = citizen
		if business:
			log.business = business
		if subbusiness:
			log.subbusiness = subbusiness

		log.setMessage("User ["+log.username+"] "+message)
		log.save()

	@staticmethod
	def getLogMessage(obj,olddata=None,newdata=None,action=None):
		"""
		Call getLogMessage function from each object
		"""
		old_data = None
		new_data = None
		if olddata is not None:
			old_data=ast.literal_eval(Common.objToStr(olddata))
		if newdata is not None:
			new_data=ast.literal_eval(Common.objToStr(newdata))
		return obj.getLogMessage(old_data,new_data,action)
