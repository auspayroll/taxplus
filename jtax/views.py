from django.shortcuts import render_to_response
from django.template import RequestContext
from django.contrib.gis.geos import Point, GEOSGeometry, Polygon
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from django.forms import model_to_dict


from property.modelforms.modelforms import PropertyCreationForm


from property.forms.forms import select_property_form
from jtax.forms.forms import tax_search_property_form


from log.mappers.LogMapper import LogMapper
from property.mappers.PropertyMapper import PropertyMapper
from jtax.mappers.DeclaredValueMapper import DeclaredValueMapper
from jtax.mappers.PropertyTaxItemMapper import PropertyTaxItemMapper
from businesslogic.TaxBusiness import TaxBusiness
from citizen.mappers.CitizenMapper import CitizenMapper
from auth.mappers.ModuleMapper import ModuleMapper
from auth.mappers.ContentTypeMapper import ContentTypeMapper
from auth.mappers.PermissionMapper import PermissionMapper
from auth.mappers.GroupMapper import GroupMapper
from auth.mappers.UserMapper import UserMapper

 
def tax_default(request, permissions, action, content_type_name1):
    """
    This function enable users to search property within an area, or search by suburb, street name, street no or plot id.
    """
    if not action:
        return render_to_response('tax/tax_tax_default.html', {\
                             'permissions':permissions},
                              context_instance=RequestContext(request))
    elif action == 'search1':
        if request.method != 'POST':
            GET = request.GET
            if GET.has_key('page'):
                page = GET["page"]
                paginator = Paginator(request.session.get('properties'), 20)
                properties = paginator.page(page)
                geodata = PropertyMapper.getPropertyGeoData(properties.object_list)
                form = tax_search_property_form(initial={"suburb":request.session['suburb'], "streetname":request.session['streetname'], "streetno":request.session['streetno'], "plotid":request.session['plotid'], "citizenid":request.session['citizenid'], })
                return render_to_response('tax/tax_tax_search1.html', {'form':form,'properties':properties,'geodata':geodata},
                                  context_instance=RequestContext(request))
            elif GET.has_key('plotid'):
                plotid = GET["plotid"]
                property = PropertyMapper.getPropertyByPlotId(plotid)
                summaryInfo = TaxBusiness.getTaxSummary(plotid)
                declaredValues = DeclaredValueMapper.getCleanDeclaredValuesByPlotId(plotid)
                propertyTaxes = PropertyTaxItemMapper.getCleanPropertyTaxItemsByPlotId(plotid)
                geodata = PropertyMapper.getPropertyGeoData(property)
                # summary infomation about this property
                form = tax_search_property_form(initial={"suburb":request.session['suburb'], "streetname":request.session['streetname'], "streetno":request.session['streetno'], "plotid":request.session['plotid'], "citizenid":request.session['citizenid'], })
                return render_to_response('tax/tax_tax_search1.html', {'form':form,'declaredValues':declaredValues,'propertyTaxes':propertyTaxes,'property':property, 'summary':summaryInfo,'geodata':geodata},
                                  context_instance=RequestContext(request))
            else:
                form = tax_search_property_form()
                return render_to_response('tax/tax_tax_search1.html',{'form':form,},
                              context_instance=RequestContext(request))   
        else:
            form = tax_search_property_form(request.POST)
            if form.is_valid():
                suburb = form.cleaned_data['suburb']
                streetname = form.cleaned_data['streetname']
                streetno = form.cleaned_data['streetno']
                plotid = form.cleaned_data['plotid']
                citizenid = form.cleaned_data['citizenid']
                
                request.session['suburb'] = suburb
                request.session['streetname'] = streetname
                request.session['streetno'] = streetno
                request.session['plotid'] = plotid
                request.session['suburb'] = suburb
                request.session['citizenid'] = citizenid
                
                
                citizen = None
                properties = None
                error_message = None
                
                if citizenid:
                    citizen = CitizenMapper.getCitizenByCitizenId(citizenid)
                    if not citizen:
                        error_message = "No citizen found!"
                        return render_to_response('tax/tax_tax_search1.html',{'form':form,'error_message':error_message},
                              context_instance=RequestContext(request))
                
                properties = PropertyMapper.getPropertiesByConditions({'plotid':plotid,'suburb':suburb,'streetname':streetname,'streetno':streetno,'citizen':citizen})
                if properties is None or len(properties) == 0:
                    error_message = "No property found!"
                    return render_to_response('tax/tax_tax_search1.html',{'form':form,'error_message':error_message},
                              context_instance=RequestContext(request))               
                elif len(properties) == 1:
                    property = properties[0]
                    summaryInfo = TaxBusiness.getTaxSummary(property.plotid)
                    geodata = PropertyMapper.getPropertyGeoData(property)
                    declaredValues = DeclaredValueMapper.getCleanDeclaredValuesByPlotId(property.plotid)
                    form = tax_search_property_form(initial={"suburb":request.session['suburb'], "streetname":request.session['streetname'], "streetno":request.session['streetno'], "plotid":request.session['plotid'], "citizenid":request.session['citizenid'], })
                    return render_to_response('tax/tax_tax_search1.html', {'form':form,'declaredValues':declaredValues,'property':property, 'summary':summaryInfo,'geodata':geodata},
                                      context_instance=RequestContext(request))
                else:
                    request.session['properties'] = properties
                    request.session['form'] = form
                    paginator = Paginator(properties, 20)
                    properties = paginator.page(1)
                    geodata = PropertyMapper.getPropertyGeoData(properties.object_list)
                    return render_to_response('tax/tax_tax_search1.html', {'form':form,'properties':properties,'geodata':geodata},
                                  context_instance=RequestContext(request))
                return render_to_response('tax/tax_tax_search1.html', {'form':form,},
                                  context_instance=RequestContext(request))
                
            else: 
                return render_to_response('tax/tax_tax_search1.html',{'form':form,},
                              context_instance=RequestContext(request))
        
    elif action == 'search':
        if request.method != 'POST':
            return render_to_response('tax/tax_tax_search.html',{},
                              context_instance=RequestContext(request))
        else:
            form = PropertyCreationForm(request.POST)
            if form.is_valid():
                form.save()
                return access_content_type(request, "property", None, None)
            else: 
                return render_to_response('property/property_property_add.html', {'form':form,},
                                  context_instance=RequestContext(request))
                
                
                
    elif action == 'declarevalue':
        if request.method != 'POST':
            return render_to_response('tax/tax_tax_declarevalue.html',{},
                              context_instance=RequestContext(request))
    elif action == 'manage':
        if request.method != 'POST':
            return render_to_response('tax/tax_tax_managetax.html',{},
                              context_instance=RequestContext(request))
                    
def access_content_type(request,  content_type_name, action = None, content_type_name1 = None):
    """
    This function direct request to the correspodding {module}_{contenttype}_default page
    """    
    
    if not request.session.get('user'):
        return login(request);
    id = request.session.get('user').id
    user = UserMapper.getUserById(id)
    module = ModuleMapper.getModuleByName('tax')
    content_type = ContentTypeMapper.getContentTypeByModuleAndName(content_type_name, module)
    permissions=UserMapper.getAllPermissionsByContentType(user,content_type)
    permissions=PermissionMapper.wrap_permissions(permissions)
    
    if content_type_name == 'tax':
        return tax_default(request, permissions, action, content_type_name1)
    
def construction(request):
    #return HttpResponse('Unauthorized', status=401)
    raise Http404
    #return render_to_response('admin/construction.html', {}, context_instance=RequestContext(request))
    
    