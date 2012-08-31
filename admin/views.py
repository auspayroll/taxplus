from django.shortcuts import render_to_response
from django.template import RequestContext
from auth.models import Permission,ContentType,Module,User,Group
from auth.forms import select_group_form, select_user_form
from admin.forms import LoginForm, LogSearchForm
from admin.modelforms import UserCreationForm, GroupCreationForm, GroupChangeForm, UserChangeForm
from citizen.modelforms import CitizenCreationForm, CitizenChangeForm
from property.modelforms import PropertyCreationForm
from admin.functions import initializeAuthData
from django.shortcuts import redirect
import dev1.settings
from property.models import Property
from citizen.models import Citizen
from log.models import Log
import ast
from citizen.forms import select_citizen_form
from django.forms import model_to_dict
import md5
    
def login(request):
    """
    Show login form if user hasn't yet logged in. Otherwise, go to home page
    """
    if request.method == 'POST':
        form = LoginForm(request.POST)
        errorMessageType = 0
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = User.getUser(email = username, password = password)
            if user is not None:
                if user.active:
                    content_types = user.getContentTypes()
                    request.session['user'] = user
                    Log.objects.createLog(request.session.get('user'),None,None,None,"login")
                    return render_to_response('admin/admin.html', {\
                         'content_types':content_types,},
                          context_instance=RequestContext(request))
                else:
                    errorMessageType = 1 #"Your account has been disabled!"
            else:
                errorMessageType = 2 #"Your username and password were incorrect."  
        else:
            errorMessageType = 2 #"Your username and password were incorrect."  
        return render_to_response('admin/login.html', {'form':form,'errorMessageType':errorMessageType,}, context_instance=RequestContext(request))
    elif request.session.get('user') is not None:
        # since user has logged in, go to home page
        username = request.session.get('user').username
        user = User.objects.get(username = username)
        content_types = user.getContentTypes()
        return render_to_response('admin/admin.html', {\
                         'content_types':content_types,},
                          context_instance=RequestContext(request))
    else:
        form = LoginForm()
    return render_to_response('admin/login.html', {'form': form}, context_instance=RequestContext(request))

def logout(request):
    # logout and clear session
    Log.objects.createLog(request.session.get('user'),None,None,None,"logout")
    for key in request.session.keys():
        del request.session[key]
    return login(request)     
                     
def auth_user_default(request,permissions, action, content_type_name1):
    """
    This funcion manages the following actions related to users. 1)add, 2)change, 3)delete 
    """
    
    all_users = User.objects.all()
    if not action:
        # show user default page
        return render_to_response('admin/auth_user_default.html', {\
                         'users':all_users, 'permissions':permissions},
                          context_instance=RequestContext(request))
    elif action == 'add':
        # add user
        if request.method == 'POST':
            # save user info to database if user info is valid
            form = UserCreationForm(request.POST)
            if form.is_valid(): 
                form.save(request)
                return render_to_response('admin/auth_user_default.html', {\
                         'users':all_users, 'permissions':permissions},
                          context_instance=RequestContext(request))
                
            else:
                # show user creation form
                return render_to_response('admin/auth_user_add.html', {'form':form,},
                              context_instance=RequestContext(request))
        else:            
            groups = Group.getGroupNames()
            form = UserCreationForm(initial={'groups':groups,})
            return render_to_response('admin/auth_user_add.html', {'form':form,'groups':groups,},
                              context_instance=RequestContext(request))
    elif action == 'change':
        # change user
        if request.method != 'POST':
            # select user before changing user info
            form = select_user_form()
            return render_to_response('admin/auth_user_change.html', {'form':form,},
                              context_instance=RequestContext(request)) 
        else:
            if content_type_name1 == 'user': 
                form = select_user_form(request.POST)
                if form.is_valid():
                    user_id = form.cleaned_data['user_id']
                    user= User.objects.get(id = user_id)
                    Log.objects.createLog(request.session.get('user'),user,None,None,"view")
                    form = UserChangeForm(instance = user,initial={'user_id':user_id, 'email':user.email,'password':user.password,})
                    return render_to_response('admin/auth_user_change1.html', {'form':form,},
                                  context_instance=RequestContext(request))
                else:
                    return render_to_response('admin/auth_user_change.html', {'form':form,},
                                  context_instance=RequestContext(request))
            elif content_type_name1 == 'user1': 
                form = UserChangeForm(request.POST);
                if form.is_valid():
                    form.save(request)
                    return access_content_type(request, "auth", "user", None, None)
                else:
                    return render_to_response('admin/auth_user_change1.html', {'form':form,},
                                  context_instance=RequestContext(request))
    elif action == 'delete':
        # delete user
        if request.method != 'POST':
            form = select_user_form()
            return render_to_response('admin/auth_user_delete.html', {'form':form,},
                              context_instance=RequestContext(request))
        else:
            form = select_user_form(request.POST)
            if form.is_valid():
                user_id=form.cleaned_data['user_id']
                user=User.objects.get(id = user_id)
                Log.objects.createLog(request.session.get('user'),user,None,None,"delete")
                user.delete()
                return access_content_type(request, "auth", "user", None, None)
            else: 
                return render_to_response('admin/auth_user_delete.html', {'form':form,},
                                  context_instance=RequestContext(request))

def auth_group_default(request, permissions, action, content_type_name1):
    """
    This funcion adds, changes or deletes group according to the passed parameter "action" 
    """
    if not action:
        # show group default page
        all_groups = Group.objects.all()
        all_content_types = ContentType.objects.all()
        data = {}
        for group in all_groups:
            per_dict= {}
            for content_type in all_content_types:
                if group.can_access_content_type(content_type):
                    per_dict[content_type.name]='Yes'
                else:
                    per_dict[content_type.name]='No'
            per_dict = sorted(per_dict.iteritems(), key = lambda(k,v):(k,v),reverse = False)
            data[group.name]=per_dict      
        return render_to_response('admin/auth_group_default.html', {\
                             'content_types':all_content_types, 'groups':all_groups, 'data':data,'permissions':permissions},
                              context_instance=RequestContext(request))
    elif action == 'add':
        #add group
        if request.method == 'POST':
            form = GroupCreationForm(request.POST)
            if form.is_valid():
                form.save(request)
                return access_content_type(request, "auth", "group", None, None)
            else:
                return render_to_response('admin/auth_group_add.html', {'form':form,},
                              context_instance=RequestContext(request))           
        else:
            form = GroupCreationForm()
            return render_to_response('admin/auth_group_add.html', {'form':form,},
                              context_instance=RequestContext(request))
    elif action == 'change':
        #change group
        if request.method != 'POST':
            form = select_group_form()
            return render_to_response('admin/auth_group_change.html', {'form':form,},
                              context_instance=RequestContext(request)) 
        else:
            if content_type_name1 == 'group': 
                form = select_group_form(request.POST)
                if form.is_valid():
                    group_id=form.cleaned_data['group_id']
                    group=Group.objects.get(id = group_id)
                    Log.objects.createLog(request.session.get('user'),group, None, None,"view")
                    form = GroupChangeForm(instance = group,initial={'group_id':group_id, 'name':group.name,})
                    return render_to_response('admin/auth_group_change1.html', {'form':form,},
                                  context_instance=RequestContext(request))
                else:
                    return render_to_response('admin/auth_group_change.html', {'form':form,},
                                  context_instance=RequestContext(request))
            elif content_type_name1 == 'group1': 
                form = GroupChangeForm(request.POST);
                if form.is_valid():
                    form.save(request)
                    return access_content_type(request, "auth", "group", None, None)
                else:
                    return render_to_response('admin/auth_group_change1.html', {'form':form,},
                                  context_instance=RequestContext(request))
    elif action == 'delete':
        # delete group
        if request.method != 'POST':
            form = select_group_form()
            return render_to_response('admin/auth_group_delete.html', {'form':form,},
                              context_instance=RequestContext(request))
        else:
            form = select_group_form(request.POST)
            if form.is_valid():
                group_id=form.cleaned_data['group_id']
                group=Group.objects.get(id = group_id)
                Log.objects.createLog(request.session.get('user'),group, None, None,"delete")    
                group.delete()
                return access_content_type(request, "auth", "group", None, None)
            else: 
                return render_to_response('admin/auth_group_delete.html', {'form':form,},
                                  context_instance=RequestContext(request))

def log_log_default(request,permissions, action, content_type_name1):
    """
    Search logs by 1)username, 2)plot id or 3)transaction id
    """   
    if not action:
        if request.method != 'POST':
            form = LogSearchForm()
            return render_to_response('admin/log_search_default.html', {'form':form,},
                              context_instance=RequestContext(request))
        else:
            form = LogSearchForm(request.POST)
            if form.is_valid():
                username = form.cleaned_data['username']
                transactionid = form.cleaned_data['transactionid']
                plotid = form.cleaned_data['plotid']
                logs = []
                if transactionid is None and plotid is None:
                    logs=Log.objects.filter(username__icontains = username)
                if transactionid is not None and plotid is None:
                    logs=Log.objects.filter(transactionid = transactionid).filter(username__icontains=username)
                if transactionid is None and plotid is not None:
                    logs=Log.objects.filter(plotid = plotid).filter(username__icontains=username)
                if transactionid is not None and plotid is not None:
                    logs=Log.objects.filter(transactionid = transactionid, plotid = plotid).filter(username__icontains=username)
                logs = list(logs)
                logs.sort(key=lambda x:x.datetime, reverse=True)
                return render_to_response('admin/log_log_default.html', {'logs':logs,},
                                  context_instance=RequestContext(request))

def citizen_citizen_default(request, permissions, action, content_type_name1):
    """
    This function adds or updates citizen entity accouding to the passed parameter "action"
    """
    
    if not action:
        # Go to default page for citizen
        citizens = Citizen.objects.all()
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
            form = CitizenCreationForm(request.POST)
            if form.is_valid():
                form.save(request)
                return access_content_type(request, "citizen", "citizen", None, None)
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
                    citizen = Citizen.objects.get(id = citizen_id)
                    Log.objects.createLog(request.session.get('user'),citizen,None,None,"view")
                    form = CitizenChangeForm(instance = citizen,initial={'citizen_id':citizen_id, 'citizenid':citizen.citizenid,})
                    return render_to_response('citizen/citizen_citizen_change1.html', {'form':form,},
                                  context_instance=RequestContext(request))
                else:
                    return render_to_response('citizen/citizen_citizen_change.html', {'form':form,},
                                  context_instance=RequestContext(request))
            elif content_type_name1 == 'citizen1': 
                form = CitizenChangeForm(request.POST);
                if form.is_valid():
                    form.save(request)
                    return access_content_type(request, "citizen", "citizen", None, None)
                else:
                    return render_to_response('citizen/citizen_citizen_change1.html', {'form':form,},
                                  context_instance=RequestContext(request))

def property_property_default(request, permissions, action, content_type_name1):
    """
    This function adds property entity
    """
    if not action:
        properties = Property.objects.all()
        return render_to_response('property/property_property_default.html', {\
                             'properties':properties, 'permissions':permissions},
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
                return access_content_type(request, "property", "property", None, None)
            else: 
                return render_to_response('property/property_property_add.html', {'form':form,},
                                  context_instance=RequestContext(request))
                
def tax_tax_default(request, permissions, action, content_type_name1):
    """
    This function enable users to search property within an area, or search by suburb, street name, street no or plot id.
    """
    if not action:
        return render_to_response('tax/tax_tax_default.html', {\
                             'permissions':permissions},
                              context_instance=RequestContext(request))
    elif action == 'search':
        if request.method != 'POST':
            return render_to_response('tax/tax_tax_search.html',{},
                              context_instance=RequestContext(request))
        else:
            form = PropertyCreationForm(request.POST)
            if form.is_valid():
                form.save()
                return access_content_type(request, "property", "property", None, None)
            else: 
                return render_to_response('property/property_property_add.html', {'form':form,},
                                  context_instance=RequestContext(request))
    elif action == 'declarevalue':
        if request.method != 'POST':
            return render_to_response('tax/tax_tax_declarevalue.html',{},
                              context_instance=RequestContext(request))
                    
def access_content_type(request, module_name, content_type_name, action = None, content_type_name1 = None):
    """
    This function direct request to the correspodding {module}_{contenttype}_default page
    """    
    username = request.session.get('user').username
    user = User.objects.get(username = username)
    module = Module.getModule(module_name)
    content_type = ContentType.getContentType(content_type_name, module)
    permissions=user.getAllPermissionsByContentType(content_type)
    permissions=Permission.wrap_permissions(permissions)
    function_name = module_name + '_' + content_type_name
    if function_name == 'auth_group':
        return auth_group_default(request, permissions, action, content_type_name1)
    if function_name == 'auth_user':
        return auth_user_default(request, permissions, action, content_type_name1)
    if function_name == 'log_log':
        return log_log_default(request, permissions, action, content_type_name1)
    if function_name == 'property_property':
        return property_property_default(request, permissions, action, content_type_name1)
    if function_name == 'citizen_citizen':
        return citizen_citizen_default(request, permissions, action, content_type_name1)
    if function_name == 'tax_tax':
        return tax_tax_default(request, permissions, action, content_type_name1)
    
def test(request):
    return render_to_response('admin/test.html', {}, context_instance=RequestContext(request))
    
    
    
    