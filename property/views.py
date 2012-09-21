from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.gis.geos import Point, GEOSGeometry, Polygon
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from django.forms import model_to_dict


from property.modelforms.modelforms import PropertyCreationForm, DistrictCreationForm, SectorCreationForm, CouncilCreationForm
from property.forms.forms import select_property_form, select_district_form, select_council_form, select_sector_form


from log.mappers.LogMapper import LogMapper
from property.mappers.PropertyMapper import PropertyMapper
from property.mappers.SectorMapper import SectorMapper
from property.mappers.DistrictMapper import DistrictMapper
from property.mappers.CouncilMapper import CouncilMapper
from property.mappers.PropertyCommonMapper import PropertyCommonMapper
from jtax.mappers.DeclaredValueMapper import DeclaredValueMapper
from businesslogic.TaxBusiness import TaxBusiness
from auth.mappers.ModuleMapper import ModuleMapper
from auth.mappers.ContentTypeMapper import ContentTypeMapper
from auth.mappers.PermissionMapper import PermissionMapper
from auth.mappers.UserMapper import UserMapper
from admin.views import login


def access_content_type(request, content_type_name, action = None, content_type_name1 = None):
    """
    This function direct request to the correspodding {module}_{contenttype}_default page
    """    
    
    if not request.session.get('user'):
        return login(request);
    id = request.session.get('user').id
    user = UserMapper.getUserById(id)
    module = ModuleMapper.getModuleByName("property")
    content_type = ContentTypeMapper.getContentTypeByModuleAndName(content_type_name, module)
    permissions=UserMapper.getAllPermissionsByContentType(user,content_type)
    permissions=PermissionMapper.wrap_permissions(permissions)
    
    if content_type_name == 'property':
        return property_default(request, permissions, action, content_type_name1)
    if content_type_name == 'district':
        return district_default(request, permissions, action, content_type_name1)
    if content_type_name == 'sector':
        return sector_default(request, permissions, action, content_type_name1)
    if content_type_name == 'council':
        return council_default(request, permissions, action, content_type_name1)




def council_default(request, permissions, action, content_type_name1):
    if not action:
        return render_to_response('property/property_council_default.html', {\
                             'permissions':permissions},
                              context_instance=RequestContext(request))
    elif action == 'add':
        if request.method != 'POST':
            form =  CouncilCreationForm(initial={'i_status':'active',})
            return render_to_response('property/property_council_add.html', {'form':form,},
                              context_instance=RequestContext(request))
    elif action == 'view':
        if request.method != 'POST' and not request.GET.has_key("name"):
            form = select_council_form(initial={'superuser':request.session.get('user').superuser,})
            return render_to_response('property/property_council_view.html', {'form':form,},
                              context_instance=RequestContext(request))
        else:
            councils = []
            if request.method == 'POST':
                POST = request.POST
                if POST.has_key("showall"):
                    councils_result = CouncilMapper.getAllCouncils()
                    if councils_result:
                        councils = councils_result
                else:
                    form = select_council_form(request.POST)
                    if form.is_valid():
                        name = form.cleaned_data["name"]                
                        LogMapper.createLog(request,action="search", search_object_class_name="council", search_conditions = {"name":name})
                        council=CouncilMapper.getCouncilByName(name)
                        councils.append(council)
                    else:
                        return render_to_response('property/property_council_view.html', {'form':form, },
                                  context_instance=RequestContext(request))
            else:
                name = request.GET['name']
                LogMapper.createLog(request,action="search", search_object_class_name="council", search_conditions = {"name":name,})
                council = CouncilMapper.getCouncilByName(name)
                councils.append(council)
                
            if not councils or len(councils) == 0:
                        error_message = "No council found!"
                        return render_to_response('property/property_council_view.html', {'form':form, 'error_message': error_message},
                                  context_instance=RequestContext(request))
            else:
                to_json = {}
                sectors_json = {}
                to_json['councils']=PropertyCommonMapper.getGeoData(councils)
                if len(councils) == 1:
                    #LogMapper.createLog(request,action="view",object=districts[0])
                    sectors = SectorMapper.getSectorsByCouncilName(councils[0].name)
                    sectors = PropertyCommonMapper.getGeoData(sectors)
                    sectors_json['sectors']=sectors
                    return render_to_response('property/property_council_view1.html', {'council': councils[0], 'councils':to_json, 'sectors':sectors_json,},
                                                  context_instance=RequestContext(request))
                else:
                    #LogMapper.createLog(request,search_message_all="view all districts", object = districts[0])
                    return render_to_response('property/property_council_view1.html', { 'councils':to_json},
                          context_instance=RequestContext(request))
                







def sector_default(request, permissions, action, content_type_name1):
    if not action:
        return render_to_response('property/property_sector_default.html', {\
                             'permissions':permissions},
                              context_instance=RequestContext(request))
    elif action == 'add':
        if request.method != 'POST':
            form = SectorCreationForm(request,initial={'i_status':'active',})
            return render_to_response('property/property_sector_add.html', {'form':form,},
                              context_instance=RequestContext(request))
    elif action == 'view':
        if request.method != 'POST':
            form = select_sector_form()
            return render_to_response('property/property_sector_view.html', {'form':form,},
                              context_instance=RequestContext(request))
        else:
            form = select_sector_form(request.POST)
            if form.is_valid():
                id = form.cleaned_data["id"]
                name = form.cleaned_data["name"]                
                LogMapper.createLog(request,action="search", search_object_class_name="sector", search_conditions = {"name":name})
                error_message = ""
                sector = SectorMapper.getSectorById(id)
                if not sector:
                        error_message = "No sector found!"
                        return render_to_response('property/property_sector_view.html', {'form':form, 'error_message': error_message},
                                  context_instance=RequestContext(request))
                else:
                    boundary = sector.boundary
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
                    LogMapper.createLog(request,action="view",object=sector)
                    return render_to_response('property/property_sector_view1.html', {'sector': sector, 'points':points_json},
                              context_instance=RequestContext(request))
            else: 
                return render_to_response('property/property_sector_view.html', {'form':form,},
                              context_instance=RequestContext(request))








def district_default(request, permissions, action, content_type_name1):
    if not action:
        return render_to_response('property/property_district_default.html', {\
                             'permissions':permissions},
                              context_instance=RequestContext(request))
    elif action == 'add':
        if request.method != 'POST':
            form = DistrictCreationForm(initial={'i_status':'active',})
            return render_to_response('property/property_district_add.html', {'form':form,},
                              context_instance=RequestContext(request))
    elif action == 'view':
        if request.method != 'POST' and not request.GET.has_key("name"):
            form = select_district_form(initial={'superuser':request.session.get('user').superuser,})
            return render_to_response('property/property_district_view.html', {'form':form,},
                              context_instance=RequestContext(request))
        else:
            districts = []
            if request.method == 'POST':
                POST = request.POST
                if POST.has_key("showall"):
                    districts_result = DistrictMapper.getAllDistricts()
                    if districts_result:
                        districts = districts_result
                else:
                    form = select_district_form(request.POST)
                    if form.is_valid():
                        name = form.cleaned_data["name"]                
                        LogMapper.createLog(request,action="search", search_object_class_name="district", search_conditions = {"name":name,})
                        district = DistrictMapper.getDistrictByName(name)
                        districts.append(district)
                    else: 
                        return render_to_response('property/property_district_view.html', {'form':form,},
                              context_instance=RequestContext(request))
            else:
                name = request.GET['name']
                LogMapper.createLog(request,action="search", search_object_class_name="district", search_conditions = {"name":name,})
                district = DistrictMapper.getDistrictByName(name)
                districts.append(district)
                       
            if not districts or len(districts) == 0:
                        error_message = "No district found!"
                        return render_to_response('property/property_district_view.html', {'form':form, 'error_message': error_message},
                                  context_instance=RequestContext(request))
            else:
                to_json = {}
                sectors_json = {}
                to_json['districts']=PropertyCommonMapper.getGeoData(districts)
                if len(districts) == 1:
                    #LogMapper.createLog(request,action="view",object=districts[0])
                    sectors = SectorMapper.getSectorsByDistrictName(districts[0].name)
                    sectors = PropertyCommonMapper.getGeoData(sectors)
                    sectors_json['sectors']=sectors
                    return render_to_response('property/property_district_view1.html', {'district': districts[0], 'districts':to_json, 'sectors':sectors_json,},
                                                  context_instance=RequestContext(request))
                else:
                    #LogMapper.createLog(request,search_message_all="view all districts", object = districts[0])
                    return render_to_response('property/property_district_view1.html', { 'districts':to_json},
                          context_instance=RequestContext(request))
            


 
def property_default(request, permissions, action, content_type_name1):
    """
    This function adds property entity
    """
    
    if not action:
        return render_to_response('property/property_property_default.html', {\
                             'permissions':permissions},
                              context_instance=RequestContext(request))
    elif action == 'add':
        if request.method != 'POST':
            form = PropertyCreationForm(initial={'i_status':'active',})
            return render_to_response('property/property_property_add.html', {'form':form,},
                              context_instance=RequestContext(request))
        else:
            form = PropertyCreationForm(request.POST)
            if form.is_valid():
                form.save(request)
                return access_content_type(request, "property", None, None)
            else: 
                return render_to_response('property/property_property_add.html', {'form':form,},
                                  context_instance=RequestContext(request))
    elif action == 'view':
        if request.method != 'POST':
            form = select_property_form()
            return render_to_response('property/property_property_view.html', {'form':form,},
                              context_instance=RequestContext(request))
        else:
            form = select_property_form(request.POST)
            if form.is_valid():
                plotid = form.cleaned_data["plotid"]
                streetno = form.cleaned_data["streetno"]
                streetname = form.cleaned_data["streetname"].strip()
                suburb = form.cleaned_data["suburb"].strip()                
                LogMapper.createLog(request,action="search", search_object_class_name="property", search_conditions = {"plotid": plotid, "streetno":streetno,"streetname":streetname,"suburb":suburb})
                error_message = ""
                property = None
                if plotid:
                    property = PropertyMapper.getPropertyByPlotId(plotid)
                else:
                    property = PropertyMapper.getPropertiesByConditions({'suburb':suburb,'streetname':streetname,'streetno':streetno,})
                if not property:
                        error_message = "No property found!"
                        return render_to_response('property/property_property_view.html', {'form':form, 'error_message': error_message},
                                  context_instance=RequestContext(request))
                else:
                    if type(property) is list:
                        property = property[0]
                    declarevalues_json=[]
                    declarevalues = DeclaredValueMapper.getDeclaredValuesByPlotId(property.plotid)
                    if declarevalues:
                        for declare_value in declarevalues:
                            declare_value_json = {}
                            declare_value_json['accepted']=declare_value.DeclaredValueAccepted
                            declare_value_json['datetime']=declare_value.DeclaredValueDateTime.strftime('%Y-%m-%d')
                            declare_value_json['staffid']=declare_value.DeclaredValueStaffId
                            declare_value_json['amount']=str(declare_value.DeclaredValueAmountCurrencey) + " " +str(declare_value.DeclaredValueAmount)
                            declarevalues_json.append(declare_value_json)
                    boundary = property.boundary
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
                    LogMapper.createLog(request,action="view",object=property)
                    return render_to_response('property/property_property_view1.html', {'property': property, 'points':points_json, 'declarevalues':declarevalues_json},
                              context_instance=RequestContext(request))
            else: 
                return render_to_response('property/property_property_view.html', {'form':form,},
                              context_instance=RequestContext(request))
    elif action == "change":
        return construction(request)
    elif action == "delete":
        return construction(request)
                    
    
def construction(request):
    #return HttpResponse('Unauthorized', status=401)
    raise Http404
    #return render_to_response('admin/construction.html', {}, context_instance=RequestContext(request))
    
    