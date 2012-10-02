from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from django.forms import model_to_dict

from citizen.modelforms.modelforms import CitizenCreationForm, CitizenChangeForm


from citizen.forms.forms import select_citizen_form

from log.mappers.LogMapper import LogMapper
from property.mappers.PropertyMapper import PropertyMapper
from jtax.mappers.DeclaredValueMapper import DeclaredValueMapper
from businesslogic.TaxBusiness import TaxBusiness
from citizen.mappers.CitizenMapper import CitizenMapper
from auth.mappers.ModuleMapper import ModuleMapper
from auth.mappers.ContentTypeMapper import ContentTypeMapper
from auth.mappers.PermissionMapper import PermissionMapper
from auth.mappers.GroupMapper import GroupMapper
from auth.mappers.UserMapper import UserMapper

 

def citizen_default(request, permissions, action, content_type_name1):
    """
    This function adds or updates citizen entity accouding to the passed parameter "action"
    """
    
    if not action:
        # Go to default page for citizen
        citizens = CitizenMapper.getAllCitizens()
        return render_to_response('citizen/citizen_citizen_default.html', {\
                             'citizens':citizens, 'permissions':permissions},
                              context_instance=RequestContext(request))
    elif action == 'add':
        # add citizen
        if request.method != 'POST':
            form = CitizenCreationForm(initial={'i_status':'active',})
            return render_to_response('citizen/citizen_citizen_add.html', {'form':form,},
                              context_instance=RequestContext(request))
        else:
            form = CitizenCreationForm(request.POST, request.FILES)
            if form.is_valid():
                form.save(request)
                return access_content_type(request, "citizen", None, None)
            else: 
                return render_to_response('citizen/citizen_citizen_add.html', {'form':form,},
                                  context_instance=RequestContext(request))
    elif action == 'change':
        # change citizen
        if request.method != 'POST':
            form = select_citizen_form()
            return render_to_response('citizen/citizen_citizen_change.html', {'form':form,},
                              context_instance=RequestContext(request)) 
        else:
            if content_type_name1 == 'citizen': 
                form = select_citizen_form(request.POST)
                if form.is_valid():
                    citizen_id=form.cleaned_data['citizen_id']
                    citizen = CitizenMapper.getCitizenById(citizen_id)
                    LogMapper.createLog(request,object=citizen,action="view", citizenid = citizen.citizenid)
                    form = CitizenChangeForm(instance = citizen,initial={'citizen_id':citizen_id, 'citizenid':citizen.citizenid, 'citizenPhotoPath':citizen.citizenPhoto.url})
                    return render_to_response('citizen/citizen_citizen_change1.html', {'form':form,},
                                  context_instance=RequestContext(request))
                else:
                    return render_to_response('citizen/citizen_citizen_change.html', {'form':form,},
                                  context_instance=RequestContext(request))
            elif content_type_name1 == 'citizen1': 
                form = CitizenChangeForm(request.POST, request.FILES);
                if form.is_valid():
                    form.save(request)
                    return access_content_type(request, "citizen", None, None)
                else:
                    return render_to_response('citizen/citizen_citizen_change1.html', {'form':form,},
                                  context_instance=RequestContext(request))
    elif action == 'view':
        if request.method != 'POST':
            form = select_citizen_form()
            return render_to_response('citizen/citizen_citizen_view.html', {'form':form,},
                              context_instance=RequestContext(request))
        else:
            form = select_citizen_form(request.POST)
            if form.is_valid():
                citizen_id=form.cleaned_data['citizen_id']
                citizen = CitizenMapper.getCitizenById(citizen_id)
                LogMapper.createLog(request,object=citizen,action="view", citizenid=citizen.citizenid)
                return render_to_response('citizen/citizen_citizen_view1.html', {'citizen':citizen,},
                              context_instance=RequestContext(request))
            else:
                 return render_to_response('citizen/citizen_citizen_view.html', {'form':form,},
                              context_instance=RequestContext(request))
                
    elif action == 'delete':
        if request.method != 'POST':
            form = select_citizen_form()
            return render_to_response('citizen/citizen_citizen_delete.html', {'form':form,},
                              context_instance=RequestContext(request))
        else:
            form = select_citizen_form(request.POST)
            if form.is_valid():
                citizen_id=form.cleaned_data['citizen_id']
                citizen = CitizenMapper.getCitizenById(citizen_id)
                LogMapper.createLog(request,object=citizen,old_data=model_to_dict(citizen), action="delete", citizenid=citizen.citizenid)
                citizen.delete();
                return access_content_type(request, "citizen", None, None)
            else:
                return render_to_response('citizen/citizen_citizen_delete.html', {'form':form,},
                              context_instance=RequestContext(request))

                    
def access_content_type(request, content_type_name, action = None, content_type_name1 = None):
    """
    This function direct request to the correspodding {module}_{contenttype}_default page
    """    
    
    if not request.session.get('user'):
        return login(request);
    id = request.session.get('user').id
    user = UserMapper.getUserById(id)
    module = ModuleMapper.getModuleByName('citizen')
    content_type = ContentTypeMapper.getContentTypeByModuleAndName(content_type_name, module)
    permissions=UserMapper.getAllPermissionsByContentType(user,content_type)
    permissions=PermissionMapper.wrap_permissions(permissions)
    
    if content_type_name == 'citizen':
        return citizen_default(request, permissions, action, content_type_name1)
    
def construction(request):
    #return HttpResponse('Unauthorized', status=401)
    raise Http404
    #return render_to_response('admin/construction.html', {}, context_instance=RequestContext(request))
    
    