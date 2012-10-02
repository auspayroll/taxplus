from auth.models import Permission,ContentType,Module,User,Group
from citizen.models import Citizen
from django.http import HttpResponse
from django.utils import simplejson
from jtax.models import DeclaredValue
from property.models import Property, Boundary, Sector, District, Council
from django.contrib.gis.geos import Point, GEOSGeometry, Polygon
from django.forms import model_to_dict
from log.mappers.LogMapper import LogMapper
from property.mappers.DistrictMapper import DistrictMapper
from property.mappers.SectorMapper import SectorMapper
from property.mappers.CouncilMapper import CouncilMapper
from jtax.mappers.PropertyTaxItemMapper import PropertyTaxItemMapper
from jtax.mappers.DeclaredValueMapper import DeclaredValueMapper
from datetime import datetime
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from jtax.models import PropertyTaxItem
from businesslogic.TaxBusiness import TaxBusiness
from admin.Common import Common






def declare_value(request):
    if request.method == 'GET':
        GET = request.GET
        plotid = GET['plotid']
        citizenid = GET['citizenid']
        citizen = Citizen.objects.filter(citizenid = citizenid)
        if len(citizen) == 0:
            return HttpResponse('Citizen ID is not found.')        
        citizen = citizen[0]
        citizenid = citizen.id
        amount = GET['amount']
        user=request.session.get('user')
        
        declareValue = DeclaredValue()
        declareValue.PlotId = plotid
        declareValue.DeclaredValueCitizenId = citizenid
        declareValue.DeclaredValueAmount = amount
        declareValue.DeclaredValueAmountCurrencey = "AUD"
        declareValue.DeclaredValueStaffId = user.id  
        declareValue.DeclaredValueAccepted = 'YE'
        
        declareValue.save()
        LogMapper.createLog(request, object=declareValue, plotid=plotid, citizenid=citizen.citizenid, action="add")
        return HttpResponse('OK')


def getPropertySector(request):
    if request.method == 'POST':
        POST = request.POST
        boundary = POST['boundary']
        plist=[]
        points = boundary.split('#')
        for point in points:
            parts = point.split(',')
            point_x=parts[0]
            point_y=parts[1]
            plist.append(GEOSGeometry('POINT(%s %s)' %(point_x, point_y)))
        plist.append(plist[0])
        polygon = Polygon(plist)
        sectors = Sector.objects.all()
        sectors_results = []
        for sector in sectors:
            boundary = sector.boundary
            if boundary.polygon.intersects(polygon):
                sectors_results.append(sector)
        if len(sectors_results) == 0:
            return HttpResponse('')
        else:
            return HttpResponse(sectors_results[0].name)




def add_property(request):
    """
    Add property and create a log for this action
    """
    if request.method == 'POST':
        POST = request.POST
        plotid = POST['plotid']
        streetno = POST['streetno']
        streetname = POST['streetname']
        suburb = POST['suburb']
        boundary = POST['boundary']
        sector = SectorMapper.getSectorByName(suburb)
        if not sector:
            return HttpResponse('NO')

        plist=[]
        points = boundary.split('#')
        for point in points:
            parts = point.split(',')
            point_x=parts[0]
            point_y=parts[1]
            plist.append(GEOSGeometry('POINT(%s %s)' %(point_x, point_y)))
        plist.append(plist[0])
        polygon = Polygon(plist)
        boundary = Boundary.objects.create(polygon=polygon, type = "manual", i_status="active")
        property = Property()
        property.plotid = plotid
        property.streetno = streetno
        property.streetname = streetname
        property.suburb = suburb
        property.boundary = boundary
        property.i_status="active"
        property.sector = sector
        property.save()
        new_data = model_to_dict(property)
        LogMapper.createLog(request,object=property,action="add", plotid=plotid)
        return HttpResponse('OK')


def generate_property_tax(request):
    if request.method == 'GET' and request.GET.has_key("plotid"):
        to_json = {}
        to_json['message']=''
        plotid = request.GET['plotid']
        
        ## No declared values at all.
        declaredValues = DeclaredValueMapper.getDeclaredValuesByPlotId(plotid)
        if declaredValues is None:
            to_json['message']='Sorry! No declared value for this property.'
            to_json['propertytaxitems'] = []
            return HttpResponse(simplejson.dumps(to_json), mimetype='application/json')
        
        ## No usable declared values to generate tax due form.
        declaredValueDueDate = None
        declaredValue = DeclaredValueMapper.getDeclaredValueByPlotId(plotid)
        declaredValueDueDate = declaredValue.DeclaredValueDateTime + relativedelta(years=3)
        now = datetime.now()
        now = timezone.make_aware(now, timezone.get_default_timezone())
        if now > declaredValueDueDate:
            to_json['message']='No usable declared values to generate tax due form.'
            to_json['propertytaxitems'] = []
            return HttpResponse(simplejson.dumps(to_json), mimetype='application/json')
        
        tax_items = TaxBusiness.generatePropertyTax(request,plotid)
        tax_items = PropertyTaxItemMapper.getCleanPropertyTaxItems(tax_items)
        to_json = {}
        to_json['propertytaxitems']=tax_items
        return HttpResponse(simplejson.dumps(to_json), mimetype='application/json')


def add_district(request):
    """
    Add property and create a log for this action
    """
    if request.method == 'POST':
        POST = request.POST
        name = POST['name']
        boundary = POST['boundary']
        
        plist=[]
        points = boundary.split('#')
        for point in points:
            parts = point.split(',')
            point_x=parts[0]
            point_y=parts[1]
            plist.append(GEOSGeometry('POINT(%s %s)' %(point_x, point_y)))
        plist.append(plist[0])
        polygon = Polygon(plist)
        boundary = Boundary.objects.create(polygon=polygon, type = "manual", i_status="active")
        district = District()
        district.name = name
        district.boundary = boundary
        district.i_status="active"
        district.save()
        new_data = model_to_dict(district)
        LogMapper.createLog(request,object=district,action="add")
        return HttpResponse('OK')

def add_sector(request):
    """
    Add property and create a log for this action
    """
    if request.method == 'POST':
        POST = request.POST
        name = POST['name']
        district = POST['district']
        boundary = POST['boundary']
        council = POST['council']
        
        plist=[]
        points = boundary.split('#')
        for point in points:
            parts = point.split(',')
            point_x=parts[0]
            point_y=parts[1]
            plist.append(GEOSGeometry('POINT(%s %s)' %(point_x, point_y)))
        plist.append(plist[0])
        polygon = Polygon(plist)
        boundary = Boundary.objects.create(polygon=polygon, type = "manual", i_status="active")
        sector = Sector()
        sector.name = name
        sector.boundary = boundary
        sector.district = DistrictMapper.getDistrictById(district)
        sector.council = CouncilMapper.getCouncilById(council)
        sector.i_status="active"
        sector.save()
        new_data = model_to_dict(sector)
        LogMapper.createLog(request,object=sector,action="add")
        return HttpResponse('OK')

def add_council(request):
    """
    Add property and create a log for this action
    """
    if request.method == 'POST':
        POST = request.POST
        name = POST['name']
        address = POST['address']
        boundary = POST['boundary']
        
        plist=[]
        points = boundary.split('#')
        for point in points:
            parts = point.split(',')
            point_x=parts[0]
            point_y=parts[1]
            plist.append(GEOSGeometry('POINT(%s %s)' %(point_x, point_y)))
        plist.append(plist[0])
        polygon = Polygon(plist)
        boundary = Boundary.objects.create(polygon=polygon, type = "manual", i_status="active")
        council = Council()
        council.name = name
        council.boundary = boundary
        council.address = address
        council.i_status="active"
        council.save()
        new_data = model_to_dict(council)
        LogMapper.createLog(request,object=council,action="add")
        return HttpResponse('OK')




def search_user(request):
    """
    search user with entered keyword, case-insensitive.
    Return a list of users having full name contains the entered keyword
    """
    result =""
    match_count = 0
    if request.method == 'GET':
        GET = request.GET
        if GET.has_key('keyword'):      
            keyword = GET['keyword'].lower()
            users = User.objects.all()
            for user in users:
                fullname = user.firstname.lower() + ' ' + user.lastname.lower()
                match = keyword in fullname                 
                if match:
                    match_count = match_count + 1
                    if match_count == 1:
                        result = ''+str(user.id)+':'+user.firstname.capitalize()+' '+user.lastname.capitalize()
                    else:
                        result = result + '#'+str(user.id)+':'+user.firstname.capitalize()+' '+user.lastname.capitalize()
    return HttpResponse(result)


def search_district(request):
    """
    search district with entered keyword, case-insensitive.
    Return a list of district having name contains the entered keyword
    """
    result =""
    match_count = 0
    if request.method == 'GET':
        GET = request.GET
        if GET.has_key('keyword'):
            districts = DistrictMapper.searchDistrictsByKeyword(GET['keyword'])
            match_count = 0      
            for district in districts:
                match_count = match_count + 1
                if match_count == 1:
                    result = ''+str(district.id)+':'+district.name
                else:
                    result = result + '#'+str(district.id)+':'+district.name
    return HttpResponse(result)



def search_object_names(request):
    """
    search district with entered keyword, case-insensitive.
    Return a list of district having name contains the entered keyword
    """
    
    result =""
    match_count = 0
    objects = None
    if request.method == 'GET':
        GET = request.GET
        if GET.has_key('keyword'):
            object_name = GET['object_name']
            if object_name == "district":
                objects = DistrictMapper.searchDistrictsByKeyword(GET['keyword'])
            elif object_name == "council":
                objects = CouncilMapper.searchCouncilsByKeyword(GET['keyword'])
            elif object_name == "sector":
                objects = SectorMapper.searchSectorsByKeyword(request,GET['keyword'])
            match_count = 0
            if objects:
                for obj in objects:
                    match_count = match_count + 1
                    if match_count == 1:
                        result = ''+str(obj.id)+':'+obj.name
                    else:
                        result = result + '#'+str(obj.id)+':'+obj.name
    return HttpResponse(result)






def search_citizen(request):
    """
    search citizen with entered keyword, case-insensitive.
    Return a list of citizens having full name contains the entered keyword
    """
    result =""
    match_count = 0
    if request.method == 'GET':
        GET = request.GET
        if GET.has_key('keyword'):         
            keyword = GET['keyword'].lower()
            citizens = Citizen.objects.all()
            for citizen in citizens:
                fullname = citizen.firstname.lower() + ' ' + citizen.lastname.lower()
                match = keyword in fullname                 
                if match:
                    match_count = match_count + 1
                    if match_count == 1:
                        result = ''+str(citizen.id)+':'+citizen.firstname.capitalize()+' '+citizen.lastname.capitalize()
                    else:
                        result = result + '#'+str(citizen.id)+':'+citizen.firstname.capitalize()+' '+citizen.lastname.capitalize()
    return HttpResponse(result)

def search_property_in_area(request):
    """
    search properties within a specified area.
    For each property satisfying the above requirement, info is returned including plotid, street no, street name, suburb 
    and shape (This is represented by a polygon with known vertice coordinates).
    The above info is returned with json format
    """
    to_json = {}
    properties=[]
    purpose = None
    if request.method == 'GET':
        GET = request.GET
        if GET.has_key('purpose'):
            purpose = GET['purpose']
        if GET.has_key('boundary'):         
            boundary = GET['boundary']
            plist=[]
            points = boundary.split('#')
            for point in points:
                parts = point.split(',')
                point_x=parts[0]
                point_y=parts[1]
                plist.append(GEOSGeometry('POINT(%s %s)' %(point_x, point_y)))
            plist.append(plist[0])
            polygon = Polygon(plist)
            boundaries = Boundary.objects.filter(polygon__intersects=polygon.wkt)
            match_polygon = 0
            for boundary in boundaries:
                property = Property.objects.filter(boundary = boundary)
                if len(property) == 0:
                    continue
                else:
                    property = property[0]
                property_json = {}
                points_json = []
                str1=str(boundary.polygon.wkt)
                str1=str1.replace('POLYGON', '').replace('((', '').replace('))', '')[1:]
                points = str1.split(', ')
                poly = ''
                for point in points:
                    point_json={}
                    point_parts = point.split(' ')
                    point_x_parts=point_parts[0].replace(' ','').split('.')
                    point_x=point_x_parts[0]+'.'+point_x_parts[1][:5]
                    point_y_parts=point_parts[1].replace(' ','').split('.')
                    point_y=point_y_parts[0]+'.'+point_y_parts[1][:5]
                    point_json['x']=point_x
                    point_json['y']=point_y
                    points_json.append(point_json)
                property_json['points']=points_json
                
                property_json['plotid']=property.plotid
                property_json['streetno']=property.streetno
                property_json['streetname']=property.streetname
                property_json['suburb']=property.suburb
                
                
                
                propertytaxitems_json=[]
                propertytaxitems = PropertyTaxItemMapper.getCleanPropertyTaxItemsByPlotId(property.plotid)
                property_json['propertytaxitems'] = propertytaxitems
                
                    
                declarevalues_json=[]
                declarevalues = DeclaredValue.objects.filter(PlotId = property.plotid).order_by("-DeclaredValueDateTime")
                for declare_value in declarevalues:
                    declare_value_json = {}
                    declare_value_json['accepted']=declare_value.DeclaredValueAccepted
                    declare_value_json['datetime']=declare_value.DeclaredValueDateTime.strftime('%Y-%m-%d')
                    declare_value_json['staffid']=declare_value.DeclaredValueStaffId
                    declare_value_json['amount']=str(declare_value.DeclaredValueAmountCurrencey) + " " +str(declare_value.DeclaredValueAmount)
                    declarevalues_json.append(declare_value_json)
                property_json['declarevalues']=declarevalues_json                
                properties.append(property_json)
            to_json['properties'] = properties
    search_message_all = "does a map search of properties for " + purpose + " purpose."
    LogMapper.createLog(request,action="search", search_message_all=search_message_all)
    return HttpResponse(simplejson.dumps(to_json), mimetype='application/json')


def search_property_field(request):
    """
    Give the user a list of suburb names or street names with given entered words.
    The above info is returned with json format
    """
    if request.method == 'GET':
        GET = request.GET
        if GET.has_key('suburb'):         
            keyword = GET['suburb']
            matched_properties = Property.objects.filter(suburb__istartswith=keyword)
            if len(matched_properties) == 0:
                return HttpResponse("")
            result = []
            for property in matched_properties:
                if property.suburb not in result:
                    result.append(property.suburb)
            return HttpResponse(simplejson.dumps(result), mimetype='application/json')
        if GET.has_key('streetname'):         
            keyword = GET['streetname']
            matched_properties = Property.objects.filter(streetname__istartswith=keyword)
            if len(matched_properties) == 0:
                return HttpResponse("")
            result = []
            for property in matched_properties:
                if property.streetname not in result:
                    result.append(property.streetname)
            return HttpResponse(simplejson.dumps(result), mimetype='application/json')
        
def search_property_by_fields(request):
    """
    Search a property or properties by provided conditions
    If plotid is given, the remaining conditions will not be considered, as each plotid corresponds to a property
    The above info is returned with json format
    """
    
    result = ""
    to_json = {}
    properties=[]
    plotid = None
    suburb = None
    streetname = None
    streetno = None
    purpose = None
    refresh = None
    matched_properties = []
    if request.method == 'GET':
        GET = request.GET
        if GET.has_key('purpose'):
            purpose = GET['purpose']
        if GET.has_key('refresh'):
            refresh = GET['refresh']
        if GET.has_key('plotid'):
            plotid = GET['plotid']
        if GET.has_key('suburb'):
            suburb = GET['suburb']
        if GET.has_key('streetname'):
            streetname = GET['streetname']
        if GET.has_key('streetno'):
            streetno = GET['streetno']
        
        if plotid is not None:
            matched_properties = Property.objects.filter(plotid=plotid)
        elif suburb is not None:
            if streetname is not None:
                if streetno is not None:
                    matched_properties = Property.objects.filter(suburb=suburb).filter(streetname=streetname).filter(streetno=streetno)
                else:
                    matched_properties = Property.objects.filter(suburb=suburb).filter(streetname=streetname)    
            else:
                if streetno is not None:
                    matched_properties = Property.objects.filter(suburb=suburb).filter(streetno=streetno)
                else:
                    matched_properties = Property.objects.filter(suburb=suburb)
        else:
            if streetname is not None:
                if streetno is not None:
                    matched_properties = Property.objects.filter(streetname=streetname).filter(streetno=streetno)
                else:
                    matched_properties = Property.objects.filter(streetname=streetname)    
            else:
                if streetno is not None:
                    matched_properties = Property.objects.filter(streetno=streetno)
        
        for property in matched_properties:
            points_json = []
            property_json = {}
            boundary=property.boundary
            str1=str(boundary.polygon.wkt)
            str1=str1.replace('POLYGON', '').replace('((', '').replace('))', '')[1:]
            points = str1.split(', ')
            for point in points:
                point_json={}
                point_parts = point.split(' ')
                point_x_parts=point_parts[0].replace(' ','').split('.')
                point_x=point_x_parts[0]+'.'+point_x_parts[1][:5]
                point_y_parts=point_parts[1].replace(' ','').split('.')
                point_y=point_y_parts[0]+'.'+point_y_parts[1][:5]
                point_json['x']=point_x
                point_json['y']=point_y
                points_json.append(point_json)
            property_json['points']=points_json
            property_json['plotid']=property.plotid
            property_json['streetno']=property.streetno
            property_json['streetname']=property.streetname
            property_json['suburb']=property.suburb
            
            
            
            propertytaxitems_json=[]
            propertytaxitems = PropertyTaxItemMapper.getCleanPropertyTaxItemsByPlotId(property.plotid)
            property_json['propertytaxitems'] = propertytaxitems
            
            
            declarevalues_json=[]
            declarevalues = DeclaredValue.objects.filter(PlotId = property.plotid).order_by("-DeclaredValueDateTime")
            for declare_value in declarevalues:
                declare_value_json = {}
                declare_value_json['accepted']=declare_value.DeclaredValueAccepted
                declare_value_json['datetime']=declare_value.DeclaredValueDateTime.strftime('%Y-%m-%d')
                user = User.objects.get(id = declare_value.DeclaredValueStaffId)
                username = user.firstname + ' '+ user.lastname
                declare_value_json['staff']=username
                citizen = Citizen.objects.get(id = declare_value.DeclaredValueCitizenId)
                declare_value_json['citizen']= citizen.firstname + ' '+citizen.lastname
                declare_value_json['amount']=str(declare_value.DeclaredValueAmountCurrencey) + " " +str(declare_value.DeclaredValueAmount)
                declarevalues_json.append(declare_value_json)
            property_json['declarevalues']=declarevalues_json
            properties.append(property_json)            
        to_json['properties'] = properties
        
        if int(refresh) == 0:
            LogMapper.createLog(request,action="search", search_message_action=" does a text search of properties", search_message_purpose=purpose, search_conditions={"plotid":plotid,"streetno":streetno,"streetname":streetname,"suburb":suburb})
        else:
            matched_properties = Property.objects.filter(plotid=plotid)
            matched_property = matched_properties[0]
            property_info = str(matched_property.streetno)+" " +matched_property.streetname+", "+matched_property.suburb
            search_message_action = " views property ["+property_info+"]"
            LogMapper.createLog(request,action="search", search_message_action=search_message_action, search_message_purpose=purpose)
        return HttpResponse(simplejson.dumps(to_json), mimetype='application/json')

        
        