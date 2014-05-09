from citizen.models import Citizen
from django.db.models import Q

class CitizenMapper:
	@staticmethod
	def getDisplayName(citizen):
		if citizen.middle_name and citizen.middle_name != '':
			return citizen.first_name.capitalize() +' '+ citizen.middle_name.capitalize() +' '+ citizen.last_name.capitalize()
		else: 
			return citizen.first_name.capitalize() + " " + citizen.last_name.capitalize()
	@staticmethod
	def getCitizenById(obj_id):
		citizen = Citizen.objects.filter(id = obj_id)
		if len(citizen) == 0:
			return None
		else:
			return citizen[0]
	@staticmethod
	def getCitizenByCitizenId(nation_id):
		citizen = Citizen.objects.filter(citizen_id = nation_id)
		if len(citizen) == 0:
			return None
		else:
			return citizen[0]
	@staticmethod
	def getAllCitizens():
		return Citizen.objects.all()


	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get citizens by conditions
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""	
	@staticmethod
	def getCitizensByConditions(conditions):
		logs = None
		count = 0
		for key, value in conditions.iteritems():
			if key == 'first_name' and value and value!="":
				if count > 0:
					logs = logs.filter(first_name__iexact = value)
				else:
					logs = Citizen.objects.filter(first_name__iexact = value)
				count = count + 1
			if key == 'last_name' and value and value!="":
				if count > 0:
					logs = logs.filter(last_name__iexact = value)
				else:
					logs = Citizen.objects.filter(last_name__iexact = value)
				count = count + 1
			if key == 'middle_name' and value and value!="":
				if count > 0:
					logs = logs.filter(middle_name__iexact = value)
				else:
					logs = Citizen.objects.filter(middle_name__iexact = value)
				count = count + 1
			
			if key == 'name' and value and value!="":
				terms = []
				names = []
				if ' ' in value:
					terms = value.split(' ')
				else:
					terms.append(value)
				for term in terms:
					names.append(term)
				if len(names) == 1:
					if count > 0:
						logs = logs.filter(Q(first_name__istartswith=names[0]) | Q(last_name__istartswith=names[0]) | Q(middle_name__istartswith=names[0])).order_by('first_name','last_name','citizen_id')
					else:
						logs = Citizen.objects.filter(Q(first_name__istartswith=names[0]) | Q(last_name__istartswith=names[0]) | Q(middle_name__istartswith=names[0])).order_by('first_name','last_name','citizen_id')
				elif len(names) == 2:
					if count > 0:
						logs = logs.filter(Q(first_name__iexact=names[0], middle_name__istartswith=names[1]) | \
														  Q(middle_name__iexact=names[0], first_name__istartswith=names[1]) | \
														  Q(first_name__iexact=names[0], last_name__istartswith=names[1]) | \
														  Q(last_name__iexact=names[0], first_name__istartswith=names[1]) | \
														  Q(last_name__iexact=names[0], middle_name__istartswith=names[1]) | \
														  Q(middle_name__iexact=names[0], last_name__istartswith=names[1])).order_by('first_name','last_name','citizen_id')
					else:
						logs = Citizen.objects.filter(Q(first_name__iexact=names[0], middle_name__istartswith=names[1]) | \
													  Q(middle_name__iexact=names[0], first_name__istartswith=names[1]) | \
													  Q(first_name__iexact=names[0], last_name__istartswith=names[1]) | \
													  Q(last_name__iexact=names[0], first_name__istartswith=names[1]) | \
													  Q(last_name__iexact=names[0], middle_name__istartswith=names[1]) | \
													  Q(middle_name__iexact=names[0], last_name__istartswith=names[1])).order_by('first_name','last_name','citizen_id')
				elif len(names) == 3:
					if count > 0:
						logs = logs.filter(Q(first_name__iexact=names[0], middle_name__iexact=names[1], last_name__istartswith=names[2]) | \
														  Q(middle_name__iexact=names[0], first_name__iexact=names[1], last_name__istartswith=names[2]) | \
														  Q(first_name__iexact=names[0], last_name__iexact=names[1], middle_name__istartswith=names[2]) | \
														  Q(middle_name__iexact=names[0], last_name__iexact=names[1], first_name__istartswith=names[2]) | \
														  Q(last_name__iexact=names[0], middle_name__iexact=names[1], first_name__istartswith=names[2]) | \
														  Q(last_name__iexact=names[0], first_name__iexact=names[1], middle_name__istartswith=names[2])).order_by('first_name','last_name','citizen_id')
					else:
						logs = Citizen.objects.filter(Q(first_name__iexact=names[0], middle_name__iexact=names[1], last_name__istartswith=names[2]) | \
														  Q(middle_name__iexact=names[0], first_name__iexact=names[1], last_name__istartswith=names[2]) | \
														  Q(first_name__iexact=names[0], last_name__iexact=names[1], middle_name__istartswith=names[2]) | \
														  Q(middle_name__iexact=names[0], last_name__iexact=names[1], first_name__istartswith=names[2]) | \
														  Q(last_name__iexact=names[0], middle_name__iexact=names[1], first_name__istartswith=names[2]) | \
														  Q(last_name__iexact=names[0], first_name__iexact=names[1], middle_name__istartswith=names[2])).order_by('first_name','last_name','citizen_id')
				count = count + 1
			if key == 'citizen_id' and value and value!="":
				if count > 0:
					logs = logs.filter(citizen_id = value)
				else:
					logs = Citizen.objects.filter(citizen_id = value)
				count = count + 1
		return logs
	
