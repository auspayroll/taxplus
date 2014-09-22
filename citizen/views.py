from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404, HttpResponseRedirect
from django.forms import model_to_dict
from pmauth.models import PMContentType
from django.contrib.auth.decorators import login_required

from citizen.modelforms.modelforms import CitizenCreationForm, CitizenChangeForm
from property.forms.forms import *


from citizen.forms.forms import select_citizen_form

from log.mappers.LogMapper import LogMapper
from property.mappers.PropertyMapper import PropertyMapper
from property.mappers.OwnershipMapper import OwnershipMapper
from jtax.mappers.DeclaredValueMapper import DeclaredValueMapper
from businesslogic.TaxBusiness import TaxBusiness
from citizen.mappers.CitizenMapper import CitizenMapper
from pmauth.mappers.ModuleMapper import ModuleMapper
from pmauth.mappers.ContentTypeMapper import ContentTypeMapper
from pmauth.mappers.GroupMapper import GroupMapper
from citizen.models import Citizen, Status
from admin.views import login
from media.mappers.MediaMapper import MediaMapper
from asset.mappers.BusinessMapper import BusinessMapper

from django.contrib import messages
from admin.Common import Common


@login_required
def view_citizen(request, obj_id, part):
	if not obj_id:
		return redirect('/admin/citizen/citizen/add_citizen/')
	else:
		try:
			citizen = Citizen.objects.get(pk=int(obj_id))
		except Exception:
			raise Http404
		request.session['citizen'] = citizen
		if not part or part == 'properties':
			ownerships = OwnershipMapper.getOwnershipsByCitizenNativeId(citizen.id)
			return render_to_response('citizen/citizen_citizen_ownership.html', {'citizen':citizen, 'ownerships':ownerships,},
				context_instance=RequestContext(request))
		elif part == 'business':
			ownerships = BusinessMapper.getBusinessOwnershipByCitizenId(citizen.id)
			businesses = []
			if ownerships:
				for i in ownerships:
					if i.asset_business:
						tmp = i.asset_business
						tmp.share = i.share
						businesses.append(tmp)
			return render_to_response('citizen/citizen_citizen_business.html', {'citizen':citizen, 'businesses':businesses,},
				context_instance=RequestContext(request))
		#elif part == "add_property":
		#	property_form = select_property_upi_form()
		#	return render_to_response('citizen/citizen_citizen_addproperty.html', {'citizen':citizen, 'form':property_form,},
		#		context_instance=RequestContext(request))
		elif part == "media":
			request.session['citizen_url'] = request.get_full_path()
			media = MediaMapper.getMedia('citizen',citizen)
			return render_to_response('citizen/citizen_citizen_media.html', {'citizen':citizen,'media':media,},
				context_instance=RequestContext(request))
		elif part == 'edit_citizen':
			user = request.session.get('user')
			
			if not user.has_action_by_name('citizen','citizen','change_citizen'):
				return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
			
			
			if request.method == 'GET':
				form = CitizenChangeForm(instance = citizen, initial={'obj_id':citizen.id})
				photo_url = None
				if citizen.photo:
					photo_url = citizen.photo.url
				return render_to_response('citizen/citizen_citizen_editcitizen.html', {'photo_url':photo_url,'citizen':citizen,'form':form,'user':user},
				context_instance=RequestContext(request))
			else:
				form = CitizenChangeForm(request.POST, request.FILES,instance = citizen)
				if form.is_valid():
					old_data = model_to_dict(citizen)
					form.save(request)
					citizen=CitizenMapper.getCitizenById(citizen.id)
					new_data = model_to_dict(citizen)
					LogMapper.createLog(request,object=citizen,action="change", citizen = citizen,new_data=new_data,old_data=old_data)

					#redirect back to whatever url set in session at the moment
					if request.GET.has_key('redirect'):
						redirect_url = request.GET['redirect']
						if request.session.has_key(redirect_url + '_url'):
							return HttpResponseRedirect(request.session[redirect_url + '_url'])
					else:
						return_url = "/admin/citizen/citizen/view_citizen/"+str(citizen.id)+"/"
						return redirect(return_url)
				else:
					return render_to_response('citizen/citizen_citizen_editcitizen.html', {'citizen':citizen,'form':form,'user':user},
						context_instance=RequestContext(request))

		elif part == "logs":
			GET = request.GET
			logs_results = LogMapper.getLogsByConditions({"citizen":citizen,})
			logs =  None
			if logs_results and len(logs_results):
				logs = list(logs_results)
				logs.sort(key=lambda x:x.date_time, reverse=True)
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
					if log.property:
						log.upi = log.property.getUPI()
					else:
						log.upi = None
			LogMapper.createLog(request,object=citizen,action="view", citizen=citizen)
			page = 1
			if GET.has_key('page'):
				page = GET["page"]
			if logs and len(logs) > 0:
				paginator = Paginator(logs, 25)
				logs = paginator.page(page)
			return render_to_response('citizen/citizen_citizen_logs.html', {'citizen':citizen, 'logs':logs,},
							context_instance=RequestContext(request))
		else:
			raise Http404

'''
We are not going to delete citizen any more once a citizen is created
'''

'''
def delete_citizen(request, permissions, obj_id):
	if request.method != 'POST':
		form = select_citizen_form()
		return render_to_response('citizen/citizen_citizen_delete.html', {'form':form,},
							context_instance=RequestContext(request))
	else:
		form = select_citizen_form(request.POST)
		if form.is_valid():
			citizen_id=form.cleaned_data['citizen_id']
			citizen = CitizenMapper.getCitizenById(citizen_id)
			LogMapper.createLog(request,object=citizen,old_data=model_to_dict(citizen), action="delete", citizen_id=citizen.citizen_id)
			citizen.delete();
			return access_content_type(request, "citizen", None, None)
		else:
			return render_to_response('citizen/citizen_citizen_delete.html', {'form':form,},
							context_instance=RequestContext(request))
'''
@login_required
def citizen_default(request, action, content_type_name1, obj_id, part):
	"""
	This function adds or updates citizen entity accouding to the passed parameter "action"
	"""

	# check whether this content type is allowed to be accessed
	if not request.session['user'].has_content_type_by_name('citizen','citizen'):
		return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
	
	if not action:
		# show citizen default page
		if request.method != 'POST':
			return render_to_response('citizen/citizen_citizen_list.html', {},context_instance=RequestContext(request))
	elif action == 'add':
		# check whether add citizen action is allowed
		
		if not request.session['user'].has_action_by_name('citizen','citizen','add_citizen'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
		
		if request.method != 'POST':
			form = CitizenCreationForm(initial={'gender':'Male',})
			return render_to_response('citizen/citizen_citizen_add.html', {'form':form, 'action':'add'},
								context_instance=RequestContext(request))
		else:
			form = CitizenCreationForm(request.POST, request.FILES)
			if form.is_valid():
				form.save(request)
				if request.GET.has_key('redirect'):
					if request.GET.has_key("redirect"):
						redirect_url = '/'+request.GET['redirect']
						return HttpResponseRedirect(redirect_url)
				#messages.success(request, 'New citizen added successfully.')
				form = CitizenCreationForm(initial={'gender':'Male',})
				message = 'New citizen added successfully'
				return render_to_response('citizen/citizen_citizen_add.html', {'form':form, 'action':'add', 'message':message,},
									context_instance=RequestContext(request))
			else: 
				return render_to_response('citizen/citizen_citizen_add.html', {'form':form, 'action':'add'},
									context_instance=RequestContext(request))
	elif action == 'view':
		if not request.session['user'].has_action_by_name('citizen','citizen','view_citizen'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
		return view_citizen(request, obj_id, part)
	else:
		raise Http404


@login_required			
def access_content_type(request, content_type_name, action = None, content_type_name1 = None, obj_id = None, part= None):
	"""
	This function direct request to the correspodding {module}_{contenttype}_default page
	"""	
	from django.db import connection
	connection._rollback()
	if not request.session.get('user'):
		return login(request);
	if content_type_name == 'citizen':
		return citizen_default(request, action, content_type_name1, obj_id, part)
	else:
		raise Http404

	
def construction(request):
	#return HttpResponse('Unauthorized', status=401)
	raise Http404
	#return render_to_response('admin/construction.html', {}, context_instance=RequestContext(request))
	
	