from django.shortcuts import render_to_response,get_object_or_404, redirect
from django.template import RequestContext
from django.http import Http404
from django.forms import model_to_dict
from django.contrib import messages
from django.core.exceptions import FieldError
from pmauth.modelforms.modelforms import UserCreationForm, GroupChangeForm, UserChangeForm
from pmauth.forms.forms import *
from pmauth.models import *
from log.mappers.LogMapper import LogMapper
from pmauth.mappers.ModuleMapper import ModuleMapper
from pmauth.mappers.ContentTypeMapper import ContentTypeMapper
from pmauth.mappers.PermissionMapper import PermissionMapper
from pmauth.mappers.GroupMapper import GroupMapper
from admin.views import login
from dev1 import ThreadLocal
from common.models import TaxType


def user_default(request, action, obj_id):
	"""
	This funcion manages the following actions related to users. 1)add, 2)change, 3)delete 
	"""	

	content_type = PMContentType.getContentTypeByName('auth','user')
	actions = Action.objects.filter(contenttype = content_type)
	
	if not actions:
		return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
	
	if not action:
		search_user_form = UserFilterForm()
		return render_to_response('admin/auth_user_list.html', {\
								'users':PMUser.objects.select_related('council').all(), 'search_user_form':search_user_form, 'action':'search',},
								context_instance=RequestContext(request))	
	elif action == 'search':
		search_user_form = UserFilterForm(request.POST)
		kwargs = {}
		if search_user_form.is_valid():
			conditions = search_user_form.cleaned_data
			for key,value in conditions.iteritems():
				if value != None and str(value).strip() != '':
					if key != 'filter_council_id':
						column_name = key[7:]
						kwargs[column_name + '__istartswith'] = value.strip()
					elif key == 'filter_council_id':
						kwargs['council'] = int(value.id)
		users = PMUser.objects.filter(**kwargs)
		return render_to_response('admin/auth_user_list.html', {'users':users, 'search_user_form':search_user_form,},
						context_instance=RequestContext(request))
		
	elif action == 'add':
		# add user+++
		if request.method == 'POST':
			# save user info to database if user info is valid
			form = UserCreationForm(request.POST)
			if form.is_valid(): 
				try:
					user = form.save(request)
				except FieldError, e:
					return render_to_response('admin/auth_user_list.html',{'form':form,'errorMessage': e.message,'action':'add'},\
											 context_instance=RequestContext(request))
				permission_ids = []
				POST = request.POST
				for key, value in POST.iteritems():
					if key[:9] == 'province_':
						id = key.replace('province_','')
						permission_ids.append(id)
				if len(permission_ids) > 0:
					for id in permission_ids:
						province = POST['province_'+id]
						district = POST['district_'+id]
						sector = POST['sector_'+id]
						
						actions = POST.getlist("selected_actions_"+id)
						tax_types = POST.getlist("tax_types_"+id+"[]")
						permission = PMPermission()
						if province:
							province = Province.objects.get(pk = int(province))
							permission.province = province
						if district:
							district = District.objects.get(pk = int(district))
							permission.district = district
						if sector:
							sector = int(sector)							
							sector = Sector.objects.get(pk=sector)
							permission.sector = sector
						permission.save()
						
						if tax_types and len(tax_types) > 0:
							for tax_type in tax_types:
								permission.tax_types.add(int(tax_type))
						if actions and len(actions) > 0:
							for action in actions:
								permission.actions.add(int(action))
						permission.save()
						user.permissions.add(permission)
				return redirect("/admin/auth/user/")
			else:
				# show user creation form
				search_user_form = UserFilterForm()
				return render_to_response('admin/auth_user_list.html', {'form':form,'search_user_form':search_user_form,'action':'add'},
								context_instance=RequestContext(request))
		else:
			groups = GroupMapper.getGroupNames()
			search_user_form = UserFilterForm()
			form = UserCreationForm(initial={'groups':groups,})
			provinces = Province.objects.all()
			actions = Action.objects.all()
			from common.models import TaxType
			tax_types = TaxType.objects.all()
			
			return render_to_response('admin/auth_user_list.html', {'provinces':provinces,'actions':actions,'tax_types':tax_types,'form':form,'search_user_form':search_user_form,'groups':groups,'action':'add'},
								context_instance=RequestContext(request))
	elif action == 'change':
		if obj_id != None:
			user = get_object_or_404(PMUser,pk=obj_id)
			LogMapper.createLog(request,object=user,action="view")
			form = UserChangeForm(instance = user,initial={'user_id':user.id, 'council':user.council, 'email':user.email,'password':user.password})
			search_user_form = UserFilterForm()
			
			provinces = Province.objects.all()
			actions = Action.objects.all()
			from common.models import TaxType
			tax_types = TaxType.objects.all()
			
			if request.method == 'POST':
				POST=request.POST
				form = UserChangeForm(POST)
				if form.is_valid():
					try:
						form.save(request)
					except FieldError as e:
						return render_to_response('admin/auth_user_list.html', {'form':form, 'user':user,'search_user_form':search_user_form,\
							'provinces':provinces,'actions':actions,'tax_types':tax_types,'action':'edit','errorMessage':e.message },
							context_instance=RequestContext(request))
					permission_ids_to_delete = user.permissions.all().values('id')
					permission_ids_to_delete = Common.get_value_list(permission_ids_to_delete,'id')
					permission_ids = []
					for key, value in POST.iteritems():
						if key[:9] == 'province_':
							id = key.replace('province_','')
							permission_ids.append(id)
					if len(permission_ids) > 0:
						for id in permission_ids:
							province = POST['province_'+id]
							district = POST['district_'+id]
							sector = POST['sector_'+id]
							actions = POST.getlist("selected_actions_"+id)
							tax_types = POST.getlist("tax_types_"+id+"[]")
							
							permission = PMPermission()
							if province:
								province = Province.objects.get(pk = int(province))
								permission.province = province
							if district:
								district = District.objects.get(pk = int(district))
								permission.district = district
							if sector:
								sector = Sector.objects.get(pk=int(sector))
								permission.sector = sector
							permission.save()
							
							if tax_types and len(tax_types) > 0:
								for tax_type in tax_types:
									permission.tax_types.add(int(tax_type))
							if actions and len(actions) > 0:
								for action in actions:
									permission.actions.add(int(action))
							permission.save()
							user.permissions.add(permission)
					if permission_ids_to_delete:
						for id in permission_ids_to_delete:
							user.permissions.remove(id)
							permission = PMPermission.objects.get(pk = id)
							if permission.actions.all():
								for action in permission.actions.all():
									permission.actions.remove(action.id)
							if permission.tax_types.all():
								for tax_type in permission.tax_types.all():
									permission.tax_types.remove(tax_type.id)
							PMPermission.objects.get(pk = id).delete()			
				return redirect("/admin/auth/user/")
				
			else:
				objects = user.permissions.all()
				permissions = []
				for obj in objects:
					province_list = Province.objects.all()
					obj.province_list = province_list
					if obj.province:
						obj.district_list = District.objects.filter(province = obj.province)
					if obj.district:
						obj.sector_list = Sector.objects.filter(district = obj.district)
					
					all_actions = Action.objects.all()
					non_selected_actons = []
					for action in all_actions:
						if action not in obj.actions.all():
							non_selected_actons.append(action)
					obj.non_selected_actions = non_selected_actons
					obj.selected_actions = obj.actions.all()
					
					from common.models import TaxType
					all_tax_types = TaxType.objects.all()					
					for tax_type in all_tax_types:
						if tax_type in obj.tax_types.all():
							tax_type.tick = True
						else:
							tax_type.tick = False
					obj.all_tax_types = all_tax_types
					permissions.append(obj)
				user.all_permissions = permissions
				
				return render_to_response('admin/auth_user_list.html', {'form':form, 'user':user,'search_user_form':search_user_form,'provinces':provinces,'actions':actions,'tax_types':tax_types,'action':'edit',},
							context_instance=RequestContext(request))
		
	elif action == 'deactivate':
		if obj_id != None:
			user_id = int(obj_id)
			user=PMUser.getUserById(user_id)
			LogMapper.createLog(request,object=user,old_data=model_to_dict(user),action="deactivate")
			user.i_status = 'inactive'
			user.save()
			return redirect("/admin/auth/user/")
	elif action == 'activate':
		if obj_id != None:
			user_id = int(obj_id)
			user=PMUser.getUserById(user_id)
			LogMapper.createLog(request,object=user,old_data=model_to_dict(user),action="activate")
			user.i_status = 'active'
			user.save()
			return redirect("/admin/auth/user/")
	elif action == "view":
		return construction(request)

def group_default(request, action, obj_id):
	"""
	This funcion adds, changes or deletes group according to the passed parameter "action" 
	"""
	
	#content_type = PMContentType.getContentTypeByName('auth','group')
	#print content_type	
	if not action:
		# show group default page
		if request.method != 'POST':
			search_group_form = GroupFilterForm()
			all_groups = GroupMapper.getActiveGroups()
			return render_to_response('admin/auth_group_list.html', {\
								'groups':all_groups, 'search_group_form':search_group_form, 'action':'search',},
								context_instance=RequestContext(request))
		else:
			search_group_form = GroupFilterForm(request.POST)
			kwargs = {}
			if search_group_form.is_valid():
				conditions = search_group_form.cleaned_data
				for key,value in conditions.iteritems():
					if value != None and str(value).strip() != '':
						if key == 'name':
							kwargs[key + '__icontains'] = value.strip()
						else:
							kwargs[key + '__iexact'] = value.strip()
			groups = PMGroup.objects.filter(**kwargs)
			return render_to_response('admin/auth_group_list.html', {'groups':groups, 'search_group_form':search_group_form,},
							context_instance=RequestContext(request))
	elif action == 'add':
		# add group+++
		if not request.session['user'].has_action_by_name('auth','group','add_group'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
		
		if request.method == 'POST':
			POST=request.POST
			group_name = POST['group_name']
			group = PMGroup()
			group.name = group_name
			group.save()
			permission_ids = []
			for key, value in POST.iteritems():
				if key[:9] == 'province_':
					id = key.replace('province_','')
					permission_ids.append(id)
			if len(permission_ids) > 0:
				for id in permission_ids:
					province = POST['province_'+id]
					district = POST['district_'+id]
					sector = POST['sector_'+id]
					
					actions = POST.getlist("selected_actions_"+id)
					tax_types = POST.getlist("tax_types_"+id+"[]")
					
					permission = PMPermission()
					if province and province !="":
						province = Province.objects.get(pk = int(province))
						permission.province = province
					if district and district !="":
						district = District.objects.get(pk = int(district))
						permission.district = district
					if sector and sector !="":
						sector = Sector.objects.get(pk = int(sector))
						permission.sector = sector
					permission.save()
					
					if tax_types and len(tax_types) > 0:
						for tax_type in tax_types:
							permission.tax_types.add(int(tax_type))
					if actions and len(actions) > 0:
						for action in actions:
							permission.actions.add(int(action))
					permission.save()
					group.permissions.add(permission)
			return redirect("/admin/auth/group/")
		else:            
			search_group_form = GroupFilterForm()
			provinces = Province.objects.all()
			actions = Action.objects.all()
			from common.models import TaxType
			tax_types = TaxType.objects.all()
			return render_to_response('admin/auth_group_list.html', {'provinces':provinces,'actions':actions,'tax_types':tax_types,'search_group_form':search_group_form,'action':'add'},
								context_instance=RequestContext(request))
	elif action == 'change':
		if not request.session['user'].has_action_by_name('auth','group','change_group'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
		
		if obj_id != None:
			group = get_object_or_404(PMGroup,pk=obj_id)
			LogMapper.createLog(request,object=group,action="view")
			search_group_form = GroupFilterForm()
			
			provinces = Province.objects.all()
			actions = Action.objects.all()
			from common.models import TaxType
			tax_types = TaxType.objects.all()
			
			if request.method == 'POST':
				POST=request.POST
				permission_ids_to_delete = group.permissions.all().values('id')
				permission_ids_to_delete = Common.get_value_list(permission_ids_to_delete,'id')
				
				group.name = POST['group_name']
				group.save()
				#group.permissions.all().delete()
				
				permission_ids = []
						
				for key, value in POST.iteritems():
					if key[:9] == 'province_':
						id = key.replace('province_','')
						permission_ids.append(id)
				if len(permission_ids) > 0:
					for id in permission_ids:
						province = POST['province_'+id]
						district = POST['district_'+id]
						sector = POST['sector_'+id]
						
						actions = POST.getlist("selected_actions_"+id)
						tax_types = POST.getlist("tax_types_"+id+"[]")
						
						permission = PMPermission()
						if province:
							province = Province.objects.get(pk = int(province))
							permission.province = province
						if district:
							district = District.objects.get(pk = int(district))
							permission.district = district
						if sector:
							sector = Sector.objects.get(pk = int(sector))
							permission.sector = sector
						permission.save()
						
						if tax_types and len(tax_types) > 0:
							for tax_type in tax_types:
								permission.tax_types.add(int(tax_type))
						if actions and len(actions) > 0:
							for action in actions:
								permission.actions.add(int(action))
						permission.save()
						group.permissions.add(permission)
				if permission_ids_to_delete:
					for id in permission_ids_to_delete:
						group.permissions.remove(id)
						permission = PMPermission.objects.get(pk = id)
						if permission.actions.all():
							for action in permission.actions.all():
								permission.actions.remove(action.id)
						if permission.tax_types.all():
							for tax_type in permission.tax_types.all():
								permission.tax_types.remove(tax_type.id)
						PMPermission.objects.get(pk = id).delete()
				return redirect("/admin/auth/group/")
			else:
				objects = group.permissions.all()
				permissions = []
				for obj in objects:
					province_list = Province.objects.all()
					obj.province_list = province_list
					if obj.province:
						obj.district_list = District.objects.filter(province = obj.province)
					if obj.district:
						obj.sector_list = Sector.objects.filter(district = obj.district)
					
					all_actions = Action.objects.all()
					non_selected_actons = []
					for action in all_actions:
						if action not in obj.actions.all():
							non_selected_actons.append(action)
					obj.non_selected_actions = non_selected_actons
					obj.selected_actions = obj.actions.all()
					
					from common.models import TaxType
					all_tax_types = TaxType.objects.all()					
					for tax_type in all_tax_types:
						if tax_type in obj.tax_types.all():
							tax_type.tick = True
						else:
							tax_type.tick = False
					obj.all_tax_types = all_tax_types
					permissions.append(obj)
				group.all_permissions = permissions
				
				return render_to_response('admin/auth_group_list.html', {'group':group,'search_group_form':search_group_form,'provinces':provinces,'actions':actions,'tax_types':tax_types,'action':'edit',},
							context_instance=RequestContext(request))
		return redirect("/admin/auth/group/")


	elif action == 'delete':
		# delete group
		if not request.session['user'].has_action_by_name('auth','group','delete_group'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
		
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
	elif action == 'deactivate':
		if obj_id != None:
			group_id = int(obj_id)
			group=GroupMapper.getGroupById(group_id)
			LogMapper.createLog(request,object=group,action="deactivate")
			group.i_status = 'inactive'
			group.save()
			return redirect("/admin/auth/group/")
	elif action == 'activate':
		if obj_id != None:
			group_id = int(obj_id)
			group=GroupMapper.getGroupById(group_id)
			LogMapper.createLog(request,object=group,action="activate")
			group.i_status = 'active'
			group.save()
			return redirect("/admin/auth/group/")
	else:
		return redirect("/admin/auth/group/")


					
def access_content_type(request, content_type_name, action = None, content_type_name1 = None, obj_id = None):
	"""
	This function direct request to the correspodding {module}_{contenttype}_default page
	"""	
	
	if not request.session.get('user'):
		return login(request);
	if content_type_name == 'group':
		if not request.session['user'].has_content_type_by_name('auth','group'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
		return group_default(request, action,obj_id)
	if content_type_name == 'user':
		if not request.session['user'].has_content_type_by_name('auth','user'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
		return user_default(request, action,obj_id)
	
def construction(request):
	#return HttpResponse('Unauthorized', status=401)
	raise Http404
	#return render_to_response('admin/construction.html', {}, context_instance=RequestContext(request))
	
	