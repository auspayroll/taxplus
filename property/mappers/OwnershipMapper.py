#from django.utils import simplejson
import json as simplejson
from property.models import Property
from asset.models import Ownership
from property.mappers.PropertyMapper import PropertyMapper
from citizen.mappers.CitizenMapper import CitizenMapper
from django.db.models.query import QuerySet

class OwnershipMapper:	
		  
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get all properties
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""	
	@staticmethod
	def addOwnership(plot_id, citizen_id, share):
		property = PropertyMapper.getPropertyByPlotId(plot_id)
		citizen = CitizenMapper.getCitizenByCitizenId(citizen_id)
		i_status = 'active'
		
		ownerships = Ownership.objects.filter(asset_property =property, owner_citizen = citizen, i_status =i_status)
		if len(ownerships) >= 1:
			return "already exists"
		else:
			Ownership.objects.create(asset_property =property, owner_citizen = citizen, share = share, date_started=now(), i_status = i_status)
			return OwnershipMapper.getOwnershipsByCitizenNativeId(citizen.id)
	
		
	@staticmethod
	def getOwnershipsByCitizenId(citizen_id):
		citizen = CitizenMapper.getCitizenByCitizenId(citizen_id)
		ownerships = Ownership.objects.filter(owner_citizen = citizen, asset_property__status__name = 'Active',i_status = 'active').select_related('owner_citizen','asset_property')
		new_ownerships = []
		for ownership in ownerships:
			ownership.upi = PropertyMapper.getUPIByPropertyId(ownership.asset_property.id)
			new_ownerships.append(ownership)
		return new_ownerships

	@staticmethod
	def getOwnershipsByCitizenNativeId(native_id):
		citizen = CitizenMapper.getCitizenById(native_id)
		ownerships = Ownership.objects.filter(owner_citizen = citizen, asset_property__status__name = 'Active',i_status = 'active').select_related('owner_citizen','asset_property')
		new_ownerships = []
		for ownership in ownerships:
			ownership.upi = PropertyMapper.getUPIByPropertyId(ownership.asset_property.id)
			new_ownerships.append(ownership)
		return new_ownerships

	@staticmethod
	def getOwnershipsByPlotId(plot_id):
		property = PropertyMapper.getPropertyByPlotId(plot_id)
		ownerships = None
		if property:
			ownerships = Ownership.objects.filter(asset_property = property,i_status = 'active').select_related('owner_citizen','asset_property')
		return ownerships

	@staticmethod
	def getCurrentOwnershipsByPropertyId(property_id):
		ownerships = None
		ownerships = Ownership.objects.filter(asset_property__id = int(property_id),i_status = 'active').select_related('owner_citizen','asset_property')
		return ownerships

	############### including current and past owners of this property #####################
	@staticmethod
	def getAllOwnershipsByProperty(property):
		ownerships = Ownership.objects.filter(asset_property = property,i_status = 'active').order_by("-startdate").order_by('-pk').select_related('owner_citizen','asset_property')
		return ownerships

