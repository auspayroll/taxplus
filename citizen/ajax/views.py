from pmauth.models import PMPermission,PMContentType,PMModule,PMUser,PMGroup
from citizen.models import Citizen
from django.http import HttpResponse
#from django.utils import simplejson
import json as simplejson
from jtax.models import DeclaredValue
from property.models import Property, Boundary, Sector, District, Council
from django.contrib.gis.geos import Point, GEOSGeometry, Polygon
from django.forms import model_to_dict
from log.mappers.LogMapper import LogMapper
from property.mappers.DistrictMapper import DistrictMapper
from property.mappers.SectorMapper import SectorMapper
from property.mappers.CouncilMapper import CouncilMapper
from property.mappers.PropertyMapper import PropertyMapper
from property.mappers.OwnershipMapper import OwnershipMapper
from jtax.mappers.PropertyTaxItemMapper import PropertyTaxItemMapper
from jtax.mappers.DeclaredValueMapper import DeclaredValueMapper
from citizen.mappers.CitizenMapper import CitizenMapper
from datetime import datetime
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from jtax.models import PropertyTaxItem
from businesslogic.TaxBusiness import TaxBusiness
from admin.Common import Common
from property.models import *

def searchSingleProperty(request):
	if request.method == 'GET':
		GET = request.GET
		conditions = {}
		if GET.has_key("plot_id"):
			conditions['plot_id'] = GET['plot_id']
		else:
			conditions["parcel_id"] = GET['parcel_id']
			conditions["sector"] = SectorMapper.getSectorById(int(GET['sector']))
			cells = Cell.objects.filter(sector=conditions["sector"],name__iexact=GET['cell'])
			if cells:
				conditions["cell"] = cells[0]
			villages = Village.objects.filter(cell=conditions["cell"],name__iexact=GET['village'])
			if villages:
				conditions["village"] = villages[0]
			
		properties = PropertyMapper.getPropertiesByConditions(conditions)
		if request.session.has_key('citizen'):
			LogMapper.createLog(request,action="search",search_object_class_name="property",citizen = request.session['citizen'],search_conditions=conditions)
		else:
			LogMapper.createLog(request,action="search",search_object_class_name="property",search_conditions=conditions)
		if properties == None or len(properties) == 0:
			return HttpResponse('No property found!')
		elif len(properties) > 1:
			return HttpResponse('Multiple properties found!')
		else:
			to_json = PropertyMapper.getPropertyGeoData(properties)
			return HttpResponse(simplejson.dumps(to_json), mimetype='application/json')
		
def addPropertyToCitizen(request):
	if request.method == 'GET':
		GET = request.GET
		plot_id = GET['plot_id']
		citizen_id = GET['citizen_id']
		share = GET['share']
		ownerships = OwnershipMapper.addOwnership(plot_id, citizen_id, share)
		search_message_all = "attempt to assign "+share+"% ownership of property ["+PropertyMapper.getPropertyByPlotId(plot_id).getDisplayName()+"] to Citizen [" + CitizenMapper.getCitizenByCitizenId(citizen_id).getDisplayName()+"]"
		LogMapper.createLog(request,action="search",search_message_all=search_message_all,citizen = request.session['citizen'])
		to_json={}
		if ownerships == 'already exists':
			return HttpResponse(ownerships)
		else:
			to_json={}
			ownerships_json = []
			for ownership in ownerships:
				ownership_json = {}
				ownership_json['plot_id'] = ownership.asset_property.plot_id
				ownership_json['parcel_id'] = ownership.asset_property.parcel_id
				ownership_json['village'] = str(ownership.asset_property.village)
				ownership_json['cell'] = str(ownership.asset_property.cell)
				ownership_json['sector'] = str(ownership.asset_property.sector.name)
				ownership_json['share'] = ownership.share
				ownerships_json.append(ownership_json)
			to_json['ownerships'] = ownerships_json
			search_message_all = "assigned "+share+"% ownership of property ["+PropertyMapper.getPropertyByPlotId(plot_id).getDisplayName()+"] to Citizen [" + CitizenMapper.getCitizenByCitizenId(citizen_id).getDisplayName()+"]"
			LogMapper.createLog(request,action="search",search_message_all=search_message_all,citizen = request.session['citizen'])
			return HttpResponse(simplejson.dumps(to_json), mimetype='application/json')
		
		
		


