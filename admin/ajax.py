from auth.models import Permission,ContentType,Module,User,Group
from citizen.models import Citizen
from django.http import HttpResponse
from django.utils import simplejson
from jtax.models import DeclaredValue
from property.modelforms import PropertyCreationForm
from property.models import Property, Boundary
from django.contrib.gis.geos import Point, GEOSGeometry, Polygon
from django.forms import model_to_dict
from log.models import Log


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
        declareValue.DeclairedValueCitizenId = citizenid
        declareValue.DeclairedValueAmount = amount
        declareValue.DeclairedValueAmountCurrencey = "AUD"
        declareValue.DeclairedValueStaffId = user.id  
        declareValue.DeclairedValueAccepted = 'YE'
        
        declareValue.save()
        Log.objects.createLog(request, object=declareValue, plotid=plotid, citizenid=citizen.citizenid, action="add")
        return HttpResponse('OK')

def add_property(request):
    """
    Add property and create a log for this action
    """
    if request.method == 'POST':
        POST = request.POST
        plotid = POST['plotid']
        print plotid
        streetno = POST['streetno']
        streetname = POST['streetname']
        suburb = POST['suburb']
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
        property = Property()
        property.plotid = plotid
        property.streetno=streetno
        property.streetname = streetname
        property.suburb = suburb
        property.boundary = boundary
        property.i_status="active"
        property.save()
        new_data = model_to_dict(property)
        Log.objects.createLog(request,object=property,action="add", plotid=plotid)
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
                property = Property.objects.get(boundary = boundary)
                property_json['plotid']=property.plotid
                property_json['streetno']=property.streetno
                property_json['streetname']=property.streetname
                property_json['suburb']=property.suburb
                
                declarevalues_json=[]
                declarevalues = DeclaredValue.objects.filter(PlotId = property.plotid).order_by("-DeclairedValueDateTime")
                for declare_value in declarevalues:
                    declare_value_json = {}
                    declare_value_json['accepted']=declare_value.DeclairedValueAccepted
                    declare_value_json['datetime']=declare_value.DeclairedValueDateTime.strftime('%Y-%m-%d')
                    declare_value_json['staffid']=declare_value.DeclairedValueStaffId
                    declare_value_json['amount']=str(declare_value.DeclairedValueAmountCurrencey) + " " +str(declare_value.DeclairedValueAmount)
                    declarevalues_json.append(declare_value_json)
                property_json['declarevalues']=declarevalues_json                
                
                properties.append(property_json)
            to_json['properties'] = properties
    search_message_all = "does a map search of properties for " + purpose + " purpose."
    Log.objects.createLog(request,action="search", search_message_all=search_message_all)
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
            
            declarevalues_json=[]
            declarevalues = DeclaredValue.objects.filter(PlotId = property.plotid).order_by("-DeclairedValueDateTime")
            for declare_value in declarevalues:
                declare_value_json = {}
                declare_value_json['accepted']=declare_value.DeclairedValueAccepted
                declare_value_json['datetime']=declare_value.DeclairedValueDateTime.strftime('%Y-%m-%d')
                user = User.objects.get(id = declare_value.DeclairedValueStaffId)
                username = user.firstname + ' '+ user.lastname
                declare_value_json['staff']=username
                citizen = Citizen.objects.get(id = declare_value.DeclairedValueCitizenId)
                declare_value_json['citizen']= citizen.firstname + ' '+citizen.lastname
                declare_value_json['amount']=str(declare_value.DeclairedValueAmountCurrencey) + " " +str(declare_value.DeclairedValueAmount)
                declarevalues_json.append(declare_value_json)
            property_json['declarevalues']=declarevalues_json
            properties.append(property_json)            
        to_json['properties'] = properties
        
        if int(refresh) == 0:
            Log.objects.createLog(request,action="search", search_message_action=" does a text search of properties", search_message_purpose=purpose, search_conditions={"plotid":plotid,"streetno":streetno,"streetname":streetname,"suburb":suburb})
        else:
            matched_properties = Property.objects.filter(plotid=plotid)
            matched_property = matched_properties[0]
            property_info = str(matched_property.streetno)+" " +matched_property.streetname+", "+matched_property.suburb
            search_message_action = " views property ["+property_info+"]"
            Log.objects.createLog(request,action="search", search_message_action=search_message_action, search_message_purpose=purpose)
        return HttpResponse(simplejson.dumps(to_json), mimetype='application/json')

        
        