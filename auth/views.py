from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import Http404
from django.forms import model_to_dict

from auth.modelforms.modelforms import UserCreationForm, GroupCreationForm, GroupChangeForm, UserChangeForm
from auth.forms.forms import select_group_form, select_user_form, LoginForm

from log.mappers.LogMapper import LogMapper
from auth.mappers.ModuleMapper import ModuleMapper
from auth.mappers.ContentTypeMapper import ContentTypeMapper
from auth.mappers.PermissionMapper import PermissionMapper
from auth.mappers.GroupMapper import GroupMapper
from auth.mappers.UserMapper import UserMapper

 
def user_default(request,permissions, action, content_type_name1):
    """
    This funcion manages the following actions related to users. 1)add, 2)change, 3)delete 
    """
    
    all_users = UserMapper.getAllUsers()
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
            groups = GroupMapper.getGroupNames()
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
                    user= UserMapper.getUserById(user_id)
                    LogMapper.createLog(request,object=user,action="view")
                    form = UserChangeForm(instance = user,initial={'user_id':user_id, 'council':user.council.id, 'email':user.email,'password':user.password,})
                    return render_to_response('admin/auth_user_change1.html', {'form':form,},
                                  context_instance=RequestContext(request))
                else:
                    return render_to_response('admin/auth_user_change.html', {'form':form,},
                                  context_instance=RequestContext(request))
            elif content_type_name1 == 'user1': 
                form = UserChangeForm(request.POST);
                if form.is_valid():
                    form.save(request)
                    return access_content_type(request, "user", None, None)
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
                user=UserMapper.getUserById(user_id)
                LogMapper.createLog(request,object=user,old_data=model_to_dict(user),action="delete")
                user.delete()
                return access_content_type(request, "user", None, None)
            else: 
                return render_to_response('admin/auth_user_delete.html', {'form':form,},
                                  context_instance=RequestContext(request))
    elif action == "view":
        return construction(request)

def group_default(request, permissions, action, content_type_name1):
    """
    This funcion adds, changes or deletes group according to the passed parameter "action" 
    """
    if not action:
        # show group default page
        all_groups = GroupMapper.getAllGroups()
        all_content_types = ContentTypeMapper.getAllContentTypes()
        data = {}
        for group in all_groups:
            per_dict= {}
            for content_type in all_content_types:
                if GroupMapper.canAccessContentType(group,content_type):
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
                return access_content_type(request, "group", None, None)
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
                    group=GroupMapper.getGroupById(group_id)
                    LogMapper.createLog(request,object=group,action="view")
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
                    return access_content_type(request, "group", None, None)
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
                group=GroupMapper.getGroupById(group_id)
                LogMapper.createLog(request,object=group,old_data=model_to_dict(group),action="delete")    
                group.delete()
                return access_content_type(request, "group", None, None)
            else: 
                return render_to_response('admin/auth_group_delete.html', {'form':form,},
                                  context_instance=RequestContext(request))
    elif action == "view":
        return construction(request)

                    
def access_content_type(request, content_type_name, action = None, content_type_name1 = None):
    """
    This function direct request to the correspodding {module}_{contenttype}_default page
    """    
    
    if not request.session.get('user'):
        return login(request);
    id = request.session.get('user').id
    user = UserMapper.getUserById(id)
    module = ModuleMapper.getModuleByName('auth')
    content_type = ContentTypeMapper.getContentTypeByModuleAndName(content_type_name, module)
    permissions=UserMapper.getAllPermissionsByContentType(user,content_type)
    permissions=PermissionMapper.wrap_permissions(permissions)
    if content_type_name == 'group':
        return group_default(request, permissions, action, content_type_name1)
    if content_type_name == 'user':
        return user_default(request, permissions, action, content_type_name1)
    
def construction(request):
    #return HttpResponse('Unauthorized', status=401)
    raise Http404
    #return render_to_response('admin/construction.html', {}, context_instance=RequestContext(request))
    
    