from django.shortcuts import render_to_response
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404
from django.forms import model_to_dict

from log.forms.forms import LogSearchForm
from log.models import Log
from log.mappers.LogMapper import LogMapper
from property.mappers.PropertyMapper import PropertyMapper
from citizen.mappers.CitizenMapper import CitizenMapper
from pmauth.mappers.ModuleMapper import ModuleMapper
from pmauth.mappers.ContentTypeMapper import ContentTypeMapper
from pmauth.mappers.PermissionMapper import PermissionMapper
from pmauth.mappers.GroupMapper import GroupMapper
from datetime import date, datetime, time
from django.utils import timezone
import dateutil.parser
from admin.views import login
from asset.models import Business
from django.core.paginator import *
  
def log_log_default(request, action, content_type_name1):
	"""
	Search logs by 1)username, 2)UPI
	"""
	
	form = LogSearchForm()
	logs = []
	pagination_url = request.get_full_path().rsplit('?&page')[0]
	if request.GET.get('submit_search',None) != None:
		form = LogSearchForm(request.GET)
		if form.is_valid():
			username = form.cleaned_data['username']
			#transactionid = form.cleaned_data['transactionid']
			#plot_id = form.cleaned_data['plot_id']
			upi = form.cleaned_data['upi']
			citizen_id = form.cleaned_data['citizen_id']
			period_from = form.cleaned_data['period_from']
			period_to = form.cleaned_data['period_to']
			messsage =  form.cleaned_data['message']
			business = form.cleaned_data['business']
			tin = form.cleaned_data['tin']
			conditions = {}
			logs = []
			if citizen_id is not None and citizen_id.strip() !='':
				citizen = CitizenMapper.getCitizenByCitizenId(citizen_id)
				if citizen:
					conditions['citizen'] = citizen
				else:
					LogMapper.createLog(request,action="search", search_object_class_name="log", search_conditions = {"username": username,"upi":upi,'citizenid':citizen_id,"period_from":period_from, "period_to":period_to})
					return render_to_response('admin/log_log_default.html', {'logs':logs, 'form':form},
							context_instance=RequestContext(request))

			if username is not None and username.strip() !='':
				conditions['username'] = username.strip()
			if upi is not None and upi.strip() !='':
				conditions['upi'] = upi.strip()
			if messsage and messsage.strip() != '':
				conditions['message'] = messsage.strip()
			if business and business.strip() != '':
				conditions['business_name'] = business.strip()
			if tin and tin.strip() != '':
				conditions['tin'] = tin.strip()

			if period_from is not None:
				conditions['period_from'] = timezone.make_aware(datetime.combine(period_from, time(0,0,0)), timezone.get_default_timezone())
			if period_to is not None:
				conditions['period_to'] = timezone.make_aware(datetime.combine(period_to, time(23,59,59)), timezone.get_default_timezone())
			if conditions:
				logs = LogMapper.getLogsByConditions(conditions)
				if not logs:
					logs = [] 
				else:
					page = request.GET.get('page', 1)
					records_in_page = 100
					paginator = Paginator(logs, records_in_page)
					try:
						logs = paginator.page(page)
					except PageNotAnInteger:
						# If page is not an integer, deliver first page.
						logs = paginator.page(1)
					except EmptyPage:
						# If page is out of range (e.g. 9999), deliver last page of results.
						logs = paginator.page(paginator.num_pages)

					for log in logs.object_list:
						log.message=log.message.replace("User [","<span class='loguser'>User [")
						log.message=log.message.replace("User[","<span class='loguser'>User [")					
						log.message=log.message.replace("Property [","<span class='logproperty'>Property [")
						log.message=log.message.replace("property [","<span class='logproperty'>Property [")
						log.message=log.message.replace("Citizen [","<span class='logcitizen'>Citizen [")
						log.message=log.message.replace("citizen [","<span class='logcitizen'>Citizen [")
						log.message=log.message.replace("Group [","<span class='loggroup'>Group [")
						log.message=log.message.replace("group [","<span class='loggroup'>Group [")
						log.message=log.message.replace("]","]</span>")
					
						###### replace append upi to log #####
						if log.property:
							log.upi = log.property.getUPI()
						else:
							log.upi = None
					
						if log.citizen:
							log.citizen_id = log.citizen.citizen_id
						else:
							log.citizen_id = None
					
						#format business info for display
						if log.business:
							log.business_id = log.business.name + " (TIN: " + log.business.tin + ")"
						else:
							log.business_id = None
			else:
				logs = []
			LogMapper.createLog(request,action="search", search_object_class_name="log", search_conditions = {"username": username,"upi":upi,'citizenid':citizen_id,"period_from":period_from, "period_to":period_to})

	return render_to_response('admin/log_log_default.html', {'logs':logs, 'form':form,'pagination_url':pagination_url},
						context_instance=RequestContext(request))

					
def access_content_type(request, content_type_name, action = None, content_type_name1 = None):
	"""
	This function direct request to the correspodding {module}_{contenttype}_default page
	"""	
	
	if not request.session.get('user'):
		return login(request);
	if content_type_name == 'log':
		return log_log_default(request, action, content_type_name1)
	raise Http404

def construction(request):
	#return HttpResponse('Unauthorized', status=401)
	raise Http404
	#return render_to_response('admin/construction.html', {}, context_instance=RequestContext(request))
	
	