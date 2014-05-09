from citizen.models import Citizen

class CitizenMapper:
	@staticmethod
	def getDisplayName(citizen):
		if citizen.middle_name and citizen.middle_name != '':
			return citizen.first_name.capitalize() +' '+ citizen.middle_name.capitalize() +' '+ citizen.last_name.capitalize()
		else: 
			return citizen.first_name.capitalize() + " " + citizen.last_name.capitalize()
	@staticmethod
	def getCitizenById(id):
		citizen = Citizen.objects.filter(id = id)
		if len(citizen) == 0:
			return None
		else:
			return citizen[0]
	@staticmethod
	def getCitizenByCitizenId(id):
		citizen = Citizen.objects.filter(citizen_id = id)
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
			if key == 'citizen_id' and value and value!="":
				if count > 0:
					logs = logs.filter(citizen_id = value)
				else:
					logs = Citizen.objects.filter(citizen_id = value)
				count = count + 1
		return logs
	
