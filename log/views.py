from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from django.forms import model_to_dict

from log.forms.forms import LogSearchForm, LogRefineSearchForm

from log.mappers.LogMapper import LogMapper
from citizen.mappers.CitizenMapper import CitizenMapper
from auth.mappers.ModuleMapper import ModuleMapper
from auth.mappers.ContentTypeMapper import ContentTypeMapper
from auth.mappers.PermissionMapper import PermissionMapper
from auth.mappers.GroupMapper import GroupMapper
from auth.mappers.UserMapper import UserMapper

  
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
                logs = LogMapper.getLogsByConditions({'plotid':plotid, 'transactionid':transactionid, 'username':username})          
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
                LogMapper.createLog(request,action="search", search_object_class_name="log", search_conditions = {"username": username, "transactionid":transactionid,"plotid":plotid})
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
            logs_results = LogMapper.raw(sql)
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
            LogMapper.createLog(request,action="search", search_message_action="refine log search", search_conditions = {'plotid':new_plotid,'transactionid':new_transactionid,'citizenid':new_citizenid})
            return render_to_response('admin/log_log_default.html', {'logs':logs, 'form':form1},
                              context_instance=RequestContext(request))
                    
def access_content_type(request, content_type_name, action = None, content_type_name1 = None):
    """
    This function direct request to the correspodding {module}_{contenttype}_default page
    """    
    
    if not request.session.get('user'):
        return login(request);
    id = request.session.get('user').id
    user = UserMapper.getUserById(id)
    module = ModuleMapper.getModuleByName("log")
    content_type = ContentTypeMapper.getContentTypeByModuleAndName(content_type_name, module)
    permissions=UserMapper.getAllPermissionsByContentType(user,content_type)
    permissions=PermissionMapper.wrap_permissions(permissions)
    if content_type_name == 'log':
        return log_log_default(request, permissions, action, content_type_name1)
    
def construction(request):
    #return HttpResponse('Unauthorized', status=401)
    raise Http404
    #return render_to_response('admin/construction.html', {}, context_instance=RequestContext(request))
    
    