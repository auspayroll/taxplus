from django.shortcuts import render_to_response
from django.template import RequestContext
from auth.models import Permission,ContentType,Module,User,Group
from admin.forms import LoginForm
from admin.functions import authenticate
import dev1.settings

def login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        errorMessageType = 0
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(username = username, password = password)
            if user is not None:
                if user.is_active:
                    user_permissions = user.get_all_permissions()
                    
                    user_group_permissions = user.get_group_permissions()
                    user_content_types = getUserContentTypes(user)
                    user_modules = getUserModules(user)
                    return render_to_response('admin1/login_success.html', \
                        {'user_permissions':user_permissions,\
                         'user_group_permissions':user_group_permissions, \
                         'user_content_types':user_content_types, \
                         'user_modules':user_modules},
                          context_instance=RequestContext(request))
                else:
                    errorMessageType = 1 #"Your account has been disabled!"
            else:
                errorMessageType = 2 #"Your username and password were incorrect."  
            return render_to_response('admin1/login.html', {'form':form,'errorMessageType':errorMessageType,}, context_instance=RequestContext(request))
    else:
        form = LoginForm()
    return render_to_response('admin1/login.html', {'form': form}, context_instance=RequestContext(request))



def initializeTestingData():
    print "hello"


def getUserContentTypes(user):
    user_content_types = []
    if user.is_superuser:
        sql = "select distinct ct.* from django_content_type ct \
                where ct.app_label not in ('contenttypes','sessions','sites','admin')"
    else:
        sql = "select distinct ct.* from django_content_type ct \
                inner join auth_permission ap on ct.id = ap.content_type_id \
                inner join auth_user_user_permissions auup on auup.permission_id = ap.id \
                inner join auth_user au on au.id = auup.user_id \
                where ct.app_label not in ('contenttypes','sessions','sites','admin') and  au.username = '%s' " % user.username    
    for content_type in ContentType.objects.raw(sql):
        user_content_types.append(content_type)
    return user_content_types

def getUserModules(user):
    user_modules = []
    excluded_modules = ['django.contrib.contenttypes','django.contrib.sessions','django.contrib.sites',\
                        'django.contrib.messages','django.contrib.staticfiles','django.contrib.admin','admin1']
    for app in dev1.settings.INSTALLED_APPS:
        if app not in excluded_modules and user.has_module_perms(app):
            user_modules.append(app)
    return user_modules 
    
    
    