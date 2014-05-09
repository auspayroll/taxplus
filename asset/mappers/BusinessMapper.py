from asset.models import Business, Ownership
from django.db.models import Q
from annoying.functions import get_object_or_None


class BusinessMapper:
		  
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get all Businesses
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""	
	@staticmethod
	def getAllBusinesses():
		return Business.objects.all()
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get Business by TIN number
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""	
	@staticmethod
	def getBusinessesByTIN(tin):
		return get_object_or_None(Business,tin = tin)
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get Business by id
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""	
	@staticmethod
	def getBusinessesById(id):
		return get_object_or_None(Business,id = id)
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get Business by name
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""	
	@staticmethod
	def getBusinessesByName(name):
		return get_object_or_None(Business,name = name)
	
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	search Business by keyword
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""	
	@staticmethod
	def searchBusinessesByKeyword(keyword):
		businesses = Business.objects.filter(name__icontains=keyword)
		return businesses


	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get Business owners by business id
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""	
	@staticmethod
	def getOwnersByBusinessID(business_id):
		ownerships = Ownership.objects.filter(owner_citizen__isnull = False, asset_business__id = business_id)
		if len(ownerships) == 0:
			return None
		else:
			return ownerships
	
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get Business owners by sub business id
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""	
	@staticmethod
	def getOwnersBySubBusinessID(subbusiness_id):
		ownerships = Ownership.objects.filter(owner_citizen__isnull = False, asset_subbusiness__id = subbusiness_id)
		if len(ownerships) == 0:
			return None
		else:
			return ownerships
	
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get Business owners by business
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""	
	@staticmethod
	def getOwnersByBusiness(business):
		ownerships = Ownership.objects.filter(owner_citizen__isnull = False, asset_business__id = business.id)
		if len(ownerships) == 0:
			return None
		else:
			return ownerships	
		
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get Business owners by sub business id
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""	
	@staticmethod
	def getOwnersBySubBusiness(subbusiness):
		ownerships = Ownership.objects.filter(owner_citizen__isnull = False, asset_subbusiness__id = subbusiness.id)
		if len(ownerships) == 0:
			return None
		else:
			return ownerships
		
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get Business or SubBusiness by citizen id (not national ID)
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""	
	@staticmethod
	def getBusinessOwnershipByCitizenId(citizen_id):
		ownerships = Ownership.objects.filter(owner_citizen__id = citizen_id).filter(Q(asset_business__isnull = True)|Q(asset_subbusiness__isnull=True))
		if len(ownerships) == 0:
			return None
		else:
			return ownerships

	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get businesses by conditions
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""	
	@staticmethod
	def getBusinessByConditions(conditions):
		businesses = None
		count = 0
		for key, value in conditions.iteritems():
			if key == 'tin' and value and value!="":
				if count > 0:
					businesses= businesses.filter(tin__iexact = value)
				else:
					businesses = Business.objects.filter(tin__iexact = value)
				count = count + 1
			if key == 'name' and value and value!="":
				if count > 0:
					businesses = businesses.filter(name__iexact = value)
				else:
					businesses = Business.objects.filter(name__iexact = value)
				count = count + 1	
			if key == 'owner_id' and value and value!="" and type(value) == int:				
				business_ids = Ownership.objects.filter(asset_business__isnull=False, owner_citizen__id = int(value)).values('asset_business')
				if count > 0:
					businesses = businesses.filter(id__in = business_ids)
				else:
					businesses = Business.objects.filter(id__in = business_ids)
				count = count + 1
			if key == 'owner_name' and value and value!="":
				from citizen.mappers.CitizenMapper import CitizenMapper
				citizens = CitizenMapper.getCitizensByConditions({'name':value})
				if citizens:
					citizen_ids = citizens.values('id')
				else:
					citizen_ids = []

				business_ids = Ownership.objects.filter(asset_business__isnull = False, owner_citizen__id__in = citizen_ids).values('asset_business')
				if count > 0:
					businesses = businesses.filter(id__in = business_ids)
				else:
					businesses = Business.objects.filter(id__in = business_ids)
				count = count + 1

		if businesses:
			businesses = businesses.filter(i_status='active')
		return businesses


	
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get businesses by conditions or return all
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""	
	@staticmethod
	def getBusinessTinFigures(conditions):
		businesses = None
		count = 0
		for key, value in conditions.iteritems():
			if key == 'district' and value and value!="":
				if count > 0:
					businesses= businesses.filter(sector__district = value)
				else:
					businesses = Business.objects.filter(sector__district = value)
				count = count + 1
			if key == 'sector' and value and value!="":
				if count > 0:
					businesses= businesses.filter(sector = value)
				else:
					businesses = Business.objects.filter(sector = value)
				count = count + 1
			if key == 'cell' and value and value!="":
				if count > 0:
					businesses= businesses.filter(cell = value)
				else:
					businesses = Business.objects.filter(cell = value)
				count = count + 1
		if count == 0:
			businesses = Business.objects.all()
		no_tin_number = None
		with_tin_number = None 
		if businesses:
			no_tin_number = businesses.filter(Q(tin__isnull = True)|Q(tin__exact = '')).count()
			with_tin_number = businesses.filter(tin__isnull = False).filter(~Q(tin__exact ='')).count()
		if not no_tin_number:
			no_tin_number = 0
		if not with_tin_number:
			with_tin_number = 0
		result = {}
		result['with_tin_number'] = with_tin_number
		result['without_tin_number'] = no_tin_number
		return result

	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get businesses by conditions or return all
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""	
	@staticmethod
	def getBusinessByConditionsOrAllByPage(conditions,num_of_records_in_page = 20, page_no = 1):
		businesses = None
		count = 0
		for key, value in conditions.iteritems():
			if key == 'tin' and value and value!="":
				if count > 0:
					if value == 'null':
						businesses= businesses.filter(Q(tin__isnull = True)|Q(tin__exact = ''))
					else:
						businesses= businesses.filter(tin__iexact = value)
				else:
					if value == 'null':
						businesses= Business.objects.filter(Q(tin__isnull = True)|Q(tin__exact = ''))
					else:
						businesses = Business.objects.filter(tin__iexact = value)
				count = count + 1
			if key == 'district' and value and value!="":
				if count > 0:
					businesses= businesses.filter(sector__district = value)
				else:
					businesses = Business.objects.filter(sector__district = value)
				count = count + 1
			if key == 'sector' and value and value!="":
				if count > 0:
					businesses= businesses.filter(sector = value)
				else:
					businesses = Business.objects.filter(sector = value)
				count = count + 1
			if key == 'cell' and value and value!="":
				if count > 0:
					businesses= businesses.filter(cell = value)
				else:
					businesses = Business.objects.filter(cell = value)
				count = count + 1
			if key == 'name' and value and value!="":
				if count > 0:
					businesses = businesses.filter(name_iexact = value)
				else:
					businesses = Business.objects.filter(name_iexact = value)
				count = count + 1	
			if key == 'owner_id' and value and value!="":
				business_ids = Ownership.objects.filter(asset_business__isnull=False, owner_citizen__id = value).values('asset_business')
				if count > 0:
					businesses = businesses.filter(id__in = business_ids)
				else:
					businesses = Business.objects.filter(id__in = business_ids)
				count = count + 1
			if key == 'owner_name' and value and value!="":
				from citizen.mappers.CitizenMapper import CitizenMapper
				citizens = CitizenMapper.getCitizensByConditions({'name':value})
				if citizens:
					citizen_ids = citizens.values('id')
				else:
					citizen_ids = []

				business_ids = Ownership.objects.filter(asset_business__isnull = False, owner_citizen__id__in = citizen_ids).values('asset_business')
				if count > 0:
					businesses = businesses.filter(id__in = business_ids)
				else:
					businesses = Business.objects.filter(id__in = business_ids)
				count = count + 1
		if page_no == 0:
			return businesses.order_by('name')
		else:
			start_record = (page_no-1)*num_of_records_in_page
			end_record = page_no * num_of_records_in_page
			return businesses[start_record:end_record]
