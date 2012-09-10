from django.shortcuts import render_to_response
from django.template import RequestContext
from auth.models import Permission,ContentType,Module,User,Group
from auth.forms import select_group_form, select_user_form
from admin.forms import LoginForm
from log.forms import LogSearchForm, LogRefineSearchForm
from admin.modelforms import UserCreationForm, GroupCreationForm, GroupChangeForm, UserChangeForm
from citizen.modelforms import CitizenCreationForm, CitizenChangeForm
from property.modelforms import PropertyCreationForm
from admin.functions import initializeAuthData
from django.shortcuts import redirect
import dev1.settings
from citizen.models import Citizen
from log.models import Log
import ast
from citizen.forms import select_citizen_form
from property.forms import select_property_form
from django.forms import model_to_dict
import md5
from property.models import Property, Boundary
from django.contrib.gis.geos import Point, GEOSGeometry, Polygon
from jtax.models import DeclaredValue
from django.http import Http404
    
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
                    Log.objects.createLog(request,action="login")
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
    Log.objects.createLog(request,action="logout")
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
                    Log.objects.createLog(request,object=user,action="view")
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
                Log.objects.createLog(request,object=user,action="delete")
                user.delete()
                return access_content_type(request, "auth", "user", None, None)
            else: 
                return render_to_response('admin/auth_user_delete.html', {'form':form,},
                                  context_instance=RequestContext(request))
    elif action == "view":
        return construction(request)

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
                    Log.objects.createLog(request,object=group,action="view")
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
                Log.objects.createLog(request,object=group,action="delete")    
                group.delete()
                return access_content_type(request, "auth", "group", None, None)
            else: 
                return render_to_response('admin/auth_group_delete.html', {'form':form,},
                                  context_instance=RequestContext(request))
    elif action == "view":
        return construction(request)

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
                for log in logs:
                    log.message=log.message.replace("User [","<span class='loguser'>User [")
                    log.message=log.message.replace("User[","<span class='loguser'>User [")                    
                    log.message=log.message.replace("Property [","<span class='logproperty'>Property [")
                    log.message=log.message.replace("property [","<span class='logproperty'>Property [")
                    log.message=log.message.replace("Citizen [","<span class='logcitizen'>Citizen [")
                    log.message=log.message.replace("citizen [","<span class='logcitizen'>Citizen [")
                    log.message=log.message.replace("Group [","<span class='loggroup'>Group [")
                    log.message=log.message.replace("group [","<span class='loggroup'>Group [")
                    log.message=log.message.replace("]","]</span>")
                form1 = LogRefineSearchForm(initial={'username':username,'transactionid':transactionid,'plotid':plotid,})
                Log.objects.createLog(request,action="search", search_object_class_name="log", search_conditions = {"username": username, "transactionid":transactionid,"plotid":plotid})
                return render_to_response('admin/log_log_default.html', {'logs':logs, 'form':form1},
                                  context_instance=RequestContext(request))
    elif action == "refinesearch":
        form = LogRefineSearchForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            transactionid = form.cleaned_data['transactionid']
            plotid = form.cleaned_data['plotid']
            new_transactionid = form.cleaned_data['new_transactionid']
            new_plotid = form.cleaned_data['new_plotid']
            new_citizenid = form.cleaned_data['new_citizenid']
            
            count = 0
            sql = "select * from log_log where 1"
            #if username is not None:
            #    sql = sql + " and lower(username) like '%" + str(username).lower() + "%'"
            #    count = count + 1
            if plotid is not None:
                
                sql = sql + " and plotid = " + str(plotid)
                count = count + 1
            if new_plotid is not None:
                sql = sql + " and plotid = " + str(new_plotid)
                count = count + 1
            if transactionid is not None:
                sql = sql + " and transactionid = " + str(transactionid)
                count = count + 1
            if new_transactionid is not None:
                sql = sql + " and transactionid = " + str(new_transactionid)
                count = count + 1
            if new_citizenid is not None:
                sql = sql + " and citizenid = " + str(new_citizenid)
                
            logs = []
            logs_results = Log.objects.raw(sql)
            logs_results = list(logs_results)
            for log in logs_results:
                if username.lower() in log.username.lower():
                    logs.append(log)
            logs.sort(key=lambda x:x.datetime, reverse=True)
            for log in logs:
                log.message=log.message.replace("User [","<span class='loguser'>User [")
                log.message=log.message.replace("User[","<span class='loguser'>User [")                    
                log.message=log.message.replace("Property [","<span class='logproperty'>Property [")
                log.message=log.message.replace("property [","<span class='logproperty'>Property [")
                log.message=log.message.replace("Citizen [","<span class='logcitizen'>Citizen [")
                log.message=log.message.replace("citizen [","<span class='logcitizen'>Citizen [")
                log.message=log.message.replace("Group [","<span class='loggroup'>Group [")
                log.message=log.message.replace("group [","<span class='loggroup'>Group [")
                log.message=log.message.replace("]","]</span>")
            form1 = LogRefineSearchForm(initial={'username':username,'transactionid':transactionid,'plotid':plotid,'new_plotid':new_plotid,'new_transactionid':new_transactionid,'new_citizenid':new_citizenid,})
            Log.objects.createLog(request,action="search", search_message_action="refine log search", search_conditions = {'plotid':new_plotid,'transactionid':new_transactionid,'citizenid':new_citizenid})
            return render_to_response('admin/log_log_default.html', {'logs':logs, 'form':form1},
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
            form = CitizenCreationForm(request.POST, request.FILES)
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
                    Log.objects.createLog(request,object=citizen,action="view", citizenid = citizen.citizenid)
                    form = CitizenChangeForm(instance = citizen,initial={'citizen_id':citizen_id, 'citizenid':citizen.citizenid,})
                    return render_to_response('citizen/citizen_citizen_change1.html', {'form':form,},
                                  context_instance=RequestContext(request))
                else:
                    return render_to_response('citizen/citizen_citizen_change.html', {'form':form,},
                                  context_instance=RequestContext(request))
            elif content_type_name1 == 'citizen1': 
                form = CitizenChangeForm(request.POST, request.FILES);
                if form.is_valid():
                    form.save(request)
                    return access_content_type(request, "citizen", "citizen", None, None)
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
                citizen = Citizen.objects.get(id = citizen_id)
                Log.objects.createLog(request,object=citizen,action="view", citizenid=citizen.citizenid)
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
                citizen = Citizen.objects.get(id = citizen_id)
                Log.objects.createLog(request,object=citizen,action="delete", citizenid=citizen.citizenid)
                citizen.delete();
                return access_content_type(request, "citizen", "citizen", None, None)
            else:
                return render_to_response('citizen/citizen_citizen_delete.html', {'form':form,},
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
                Log.objects.createLog(request,action="search", search_object_class_name="property", search_conditions = {"plotid": plotid, "streetno":streetno,"streetname":streetname,"suburb":suburb})
                error_message = ""
                property = None
                if plotid:
                    property = Property.objects.filter(plotid=plotid)
                else:
                    property = Property.objects.filter(streetno = streetno).filter(streetname = streetname).filter(suburb=suburb)
                if not property:
                        error_message = "No property found!"
                        return render_to_response('property/property_property_view.html', {'form':form, 'error_message': error_message},
                                  context_instance=RequestContext(request))
                else:
                    property = property[0]
                    declarevalues_json=[]
                    declarevalues = DeclaredValue.objects.filter(PlotId = property.plotid).order_by("-DeclairedValueDateTime")
                    for declare_value in declarevalues:
                        declare_value_json = {}
                        declare_value_json['accepted']=declare_value.DeclairedValueAccepted
                        declare_value_json['datetime']=declare_value.DeclairedValueDateTime.strftime('%Y-%m-%d')
                        declare_value_json['staffid']=declare_value.DeclairedValueStaffId
                        declare_value_json['amount']=str(declare_value.DeclairedValueAmountCurrencey) + " " +str(declare_value.DeclairedValueAmount)
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
                    Log.objects.createLog(request,action="view",object=property)
                    return render_to_response('property/property_property_view1.html', {'property': property, 'points':points_json, 'declarevalues':declarevalues_json},
                              context_instance=RequestContext(request))
            else: 
                return render_to_response('property/property_property_view.html', {'form':form,},
                              context_instance=RequestContext(request))
    elif action == "change":
        return construction(request)
    elif action == "delete":
        return construction(request)
                
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
    elif action == 'paytax':
        return construction(request)
                    
def access_content_type(request, module_name, content_type_name, action = None, content_type_name1 = None):
    """
    This function direct request to the correspodding {module}_{contenttype}_default page
    """    
    
    if not request.session.get('user'):
        return login(request);
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
    
def construction(request):
    #return HttpResponse('Unauthorized', status=401)
    raise Http404
    #return render_to_response('admin/construction.html', {}, context_instance=RequestContext(request))
    
    
    
    