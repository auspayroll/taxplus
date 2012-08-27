from auth.models import Permission,ContentType,Module,User,Group
from citizen.models import Citizen
from django.http import HttpResponse
from property.models import Property, Boundary
from django.contrib.gis.geos import Point, GEOSGeometry, Polygon
from django.utils import simplejson


def search_user(request):
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
                #if user.firstname.lower() == keyword:
                #    match = True
                #if user.lastname.lower() == keyword:
                #    match = True
                #if user.firstname.lower() + ' ' + user.lastname.lower() == keyword:
                #    match = True
                if match:
                    match_count = match_count + 1
                    if match_count == 1:
                        result = ''+str(user.id)+':'+user.firstname.capitalize()+' '+user.lastname.capitalize()
                    else:
                        result = result + '#'+str(user.id)+':'+user.firstname.capitalize()+' '+user.lastname.capitalize()
    return HttpResponse(result)
def search_citizen(request):
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
                #if user.firstname.lower() == keyword:
                #    match = True
                #if user.lastname.lower() == keyword:
                #    match = True
                #if user.firstname.lower() + ' ' + user.lastname.lower() == keyword:
                #    match = True
                if match:
                    match_count = match_count + 1
                    if match_count == 1:
                        result = ''+str(citizen.id)+':'+citizen.firstname.capitalize()+' '+citizen.lastname.capitalize()
                    else:
                        result = result + '#'+str(citizen.id)+':'+citizen.firstname.capitalize()+' '+citizen.lastname.capitalize()
    return HttpResponse(result)

def search_property_in_area(request):
    to_json = {}
    properties=[]
    if request.method == 'GET':
        GET = request.GET
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
                properties.append(property_json)
            to_json['properties'] = properties
    return HttpResponse(simplejson.dumps(to_json), mimetype='application/json')


def search_property_field(request):
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
    result = ""
    to_json = {}
    properties=[]
    plotid = None
    suburb = None
    streetname = None
    streetno = None
    matched_properties = []
    if request.method == 'GET':
        GET = request.GET
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
            properties.append(property_json)
        to_json['properties'] = properties
        return HttpResponse(simplejson.dumps(to_json), mimetype='application/json')

        
        