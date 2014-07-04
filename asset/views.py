from django.shortcuts import render_to_response, redirect, get_object_or_404
from django.template import RequestContext
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import Http404, HttpResponseRedirect
from django.forms import model_to_dict

from asset.modelforms.modelforms import *
from asset.forms.forms import *
from asset.models import *
from django.template.response import TemplateResponse

from citizen.mappers.CitizenMapper import CitizenMapper
from pmauth.mappers.ModuleMapper import ModuleMapper
from pmauth.mappers.ContentTypeMapper import ContentTypeMapper
from pmauth.mappers.PermissionMapper import PermissionMapper
from pmauth.mappers.GroupMapper import GroupMapper
from admin.views import login
from pmauth.models import PMContentType

from django.contrib import messages
from media.mappers.MediaMapper import MediaMapper
from datetime import date, datetime
from media.models import Media
import os
from property.models import *
import hashlib
from pmauth.models import Action

def merge_business(request, pk1, pk2):
	if not request.session.get('user'):
		return login(request)
	business1 = get_object_or_404(Business, pk=pk1)
	business2 = get_object_or_404(Business, pk=pk2)

	if request.method == 'POST':
		post = request.POST.copy()
		if post.get('date_started'):
			post['date_started'] = datetime.strptime(post.get('date_started'),'%Y-%m-%d').date()

		if post.get('closed_date'):
			post['closed_date'] = datetime.strptime(post.get('closed_date'),'%Y-%m-%d').date()

		form = BusinessForm(post)
		if form.is_valid():
			business = form.save(request)
			message_log = ["Business %s created" % business]
			merge_messages = business.merge(business1, business2)
			message_log.extend(merge_messages)
			for merge_message in merge_messages:
				LogMapper.createLog(request,object=business, action="merge", business = business, user=request.session.get('user'), message=merge_message)	
			LogMapper.createLog(request,object=business,action="merge", business = business, user=request.session.get('user'), message="merging of %s and %s" % (business1.name, business2.name))	  
			success_message = 'Business merged successfully. %s + %s -> %s ' % (business1, business2, business)
			dup = Duplicate.objects.get(business1=business1, business2=business2)
			dup.status = 0
			dup.save()
			messages.success(request, success_message) 
			return TemplateResponse(request, 'asset/business/merge_business_message.html', { 'message_log':message_log, 'business':business })
		else:
			raise Exception(form.errors)

	fields = [(k,k.replace('business_category', 'cleaning fee category').replace('business_subcategory','business category').replace('_',' ')) for k in \
	('name', 'tin', 'address', 'email', 'po_box', 'phone1', 'phone2', 'vat_register', 'sector', 'cell', 'village', 'accountant_name',
	'accountant_phone', 'accountant_email', 'date_started', 'closed_date', 'business_category', 'business_subcategory')]

	return TemplateResponse(request, 'asset/business/merge_business.html', { 'business1':business1, 'business2':business2, 'fields':fields })




def access_content_type(request, content_type_name, action = None, content_type_name1 = None, obj_id = None):
	"""
	This function direct request to the correspodding {module}_{contenttype}_default page
	"""	
	if not request.session.get('user'):
		return login(request);
	
	#clear all the old messages
	storage = messages.get_messages(request)
	storage.used = True

	if content_type_name == 'business':
		if not request.session['user'].has_content_type_by_name('asset','business'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
		return business_default(request, action, content_type_name1, obj_id)
	if content_type_name == 'shop':
		if not request.session['user'].has_content_type_by_name('asset','shop'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
		return shop_default(request, action, content_type_name1, obj_id)
	if content_type_name == 'office':
		if not request.session['user'].has_content_type_by_name('asset','office'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
		return office_default(request, action, content_type_name1, obj_id)
	if content_type_name == 'stall':
		if not request.session['user'].has_content_type_by_name('asset','stall'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
		return stall_default(request, action, content_type_name1, obj_id)
	if content_type_name == 'billboard':
		if not request.session['user'].has_content_type_by_name('asset','billboard'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
		return billboard_default(request, action, content_type_name1, obj_id)
	if content_type_name == 'vehicle':
		if not request.session['user'].has_content_type_by_name('asset','vehicle'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
		return vehicle_default(request, action, content_type_name1, obj_id)

	raise Http404

def business_default(request, action, content_type_name1, obj_id = None):
	content_type = PMContentType.getContentTypeByName('asset','business')
	actions = Action.objects.filter(contenttype = content_type)
	search_business_form = BusinessFilterForm()
	if not actions:
		return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
	if not action:
		return render_to_response('asset/business/business_list.html', {\
								 'search_business_form':search_business_form, 'action':'search',},
								context_instance=RequestContext(request))
	elif action == 'search':

		if request.method !='POST' and not request.GET.has_key('page'):
			return render_to_response('asset/business/business_list.html', {'search_business_form':search_business_form,'action':'search',},
						context_instance=RequestContext(request))
		else:
			page = 1
			records_in_page = 20
			conditions = {}
			if request.method == 'POST':
				search_business_form = BusinessFilterForm(request.POST)
				business_name = request.POST['filter_business_name']
				tin = request.POST['filter_tin']
				conditions['business_name'] = business_name
				conditions['tin'] = tin
				request.session['conditions'] = conditions
			elif request.method == 'GET' and request.GET.has_key('page'):
				page = int(request.GET["page"])
				conditions = request.session['conditions']

			kwargs = {}
			if conditions.has_key('business_name') and conditions['business_name']:
				kwargs['name__icontains'] = conditions['business_name'].strip()
			if conditions.has_key('tin') and conditions['tin']:
				kwargs['tin__icontains'] = conditions['tin'].strip()
			businesses = Business.objects.filter(**kwargs)
			
			paginator = {}
			paginator['count'] = len(businesses)
			paginator['number'] = page
			paginator['num_pages'] = 0
			paginator['has_next'] = False
			paginator['has_previous'] = False
			paginator['next_page_number'] = 0
			paginator['previous_page_number'] = 0

			if paginator['count']%records_in_page == 0:
				paginator['num_pages'] =  paginator['count']/records_in_page
			else:
				paginator['num_pages'] = int( paginator['count']/records_in_page) + 1

			if page == 1:
				paginator['has_previous'] = False
			else:
				 paginator['has_previous'] = True
				 paginator['previous_page_number'] = page - 1

			if page == paginator['num_pages']:
				  paginator['has_next'] = False
			else:
				 paginator['has_next'] = True
				 paginator['next_page_number'] = page + 1

			businesses = businesses[(page-1)*records_in_page:page*records_in_page]

			return render_to_response('asset/business/business_list.html', {'businesses':businesses, 'search_business_form':search_business_form,'paginator':paginator,},
						context_instance=RequestContext(request))

	elif action == 'add':
		search_business_form = BusinessFilterForm(request.POST)
		if not request.session['user'].has_action_by_name('asset','business','add_business'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
		
		if request.method != 'POST':
			#if is redirected from citizen view page, preload default owner with citizen details
			if request.GET.has_key("redirect") and "admin/tax/tax/citizen/" in request.GET['redirect']:
				citizen_id = request.GET['redirect'].replace("admin/tax/tax/citizen/","").replace("/","")
				citizens = Citizen.objects.filter(pk=citizen_id)
				if citizens:
					citizen = citizens[0]
					owners = '{"id": "' + str(citizen.id) + '", "share": "100", "type": "citizen"},'
					owner_select_options = '<option value="' + str(citizen.id) + '" opt_share="100" opt_type="citizen" >' + citizen.getDisplayName() + "(CID: " + citizen.citizen_id + ") [100% Share]"  + '</option>'
					total_share = 100
					owner_ids = "," + str(citizen.id)
					form =  BusinessForm(initial={'i_status':'active','owners':owners,'owner_select_options':owner_select_options,'total_share':total_share,'owner_ids':owner_ids})
				else:
					form =  BusinessForm(initial={'i_status':'active',})
			else:
				form =  BusinessForm(initial={'i_status':'active',})

			return render_to_response('asset/business/business_list.html', {'form':form,'action':'add','search_business_form':search_business_form,},
							context_instance=RequestContext(request))
		else:
			form = BusinessForm(request.POST, request.FILES)
			POST = request.POST
			if form.is_valid():
				branch_ids = []
				for key, value in POST.iteritems():
					if key[:11] == 'branchname_':
						id = key.replace('branchname_','')
						branch_ids.append(id)
				obj = form.save(request)

				#set default cp_password if is creating new business
				obj.cp_password = hashlib.md5(obj.name.strip()).hexdigest()
				obj.save()
				if len(branch_ids) > 0:
					for id in branch_ids:
						sub_business = SubBusiness()
						sub_business.business = obj
						sub_business.branch = POST['branchname_'+id]

						if POST.has_key('sector_'+id) and POST['sector_'+id] != '':
							sub_business.sector =  Sector.objects.get(pk= int(POST['sector_'+id]))
						if POST.has_key('cell_'+id) and POST['cell_'+id] != '':
							sub_business.cell = Cell.objects.get(pk=int(POST['cell_'+id]))
						if POST.has_key('parcel_id_'+id) and POST['parcel_id_'+id] != '':
							sub_business.parcel_id = int(POST['parcel_id_'+id])
						sub_business.save()
				messages.success(request, 'Business added successfully.') 
				LogMapper.createLog(request,object=obj,action="add", business = obj)
				
				if request.POST.get('redirect_tax',None) != None:
					return HttpResponseRedirect('/admin/tax/tax/business/' + str(obj.id) + '/taxes/')

				if request.GET.has_key("redirect"):
					redirect_url = '/'+request.GET['redirect']
					return HttpResponseRedirect(redirect_url)
				else:
					return HttpResponseRedirect('/admin/asset/business/add_business/')
			else:
				POST= request.POST
				sub_businesses_arr = []
				for key, value in POST.iteritems():
					if key[:11] == 'branchname_':
						id = key.replace('branchname_','')
						sub_business_dict = {}
						sub_business_dict['branch'] = POST['branchname_'+str(id)]
						sub_business_dict['parcel_id'] = POST['parcel_id_'+str(id)]

						if POST.has_key('sector_'+str(id)) and POST['sector_'+str(id)] != '':
							sector = Sector.objects.get(id = int(POST['sector_'+str(id)]))
							sub_business_dict['sector'] = sector
							sub_business_dict['cell_list'] = Cell.objects.filter(sector = sector)
						sub_business_dict['sector_list'] = Sector.objects.all()
						if POST.has_key('cell_'+str(id)) and POST['cell_'+str(id)] != '':
							sub_business_dict['cell'] = Cell.objects.get(pk=int(POST['cell_'+str(id)]))

						sub_businesses_arr.append(sub_business_dict)				
				cell_value = ''
				if request.POST['cell_value']!="":
					cell_value = int(request.POST['cell_value'])
				search_business_form = BusinessFilterForm(request.POST)
				return render_to_response('asset/business/business_list.html', {'form':form,'cell_value':cell_value,'branches':sub_businesses_arr,'search_business_form':search_business_form,'action':'add',},
							context_instance=RequestContext(request))

	elif action == 'change':
		if not request.session['user'].has_action_by_name('asset','business','change_business'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))

		if obj_id != None:
			obj = get_object_or_404(Business, pk=obj_id)
			if request.method == 'POST' and request.POST.get('submit_update'):
				old_data = model_to_dict(obj)
				POST = request.POST
				form = BusinessForm(request.POST, instance = obj)
				form.id = obj_id
				
				if form.is_valid():
					obj = form.save(request)
					new_data = model_to_dict(obj)
					# save subBusiness if applicable
					branch_ids = []
					branch_to_change_ids = []
					for key, value in POST.iteritems():
						if key[:11] == 'branchname_':
							id = key.replace('branchname_','')
							branch_ids.append(int(id))
						if key[:9] == 'branchid_':
							id = key.replace('branchid_','')
							branch_to_change_ids.append(int(POST['branchid_'+id]))
					
					# Delete sub business if needed ...
					existing_branches = SubBusiness.objects.filter(business = obj)

					
					for existing_branch in existing_branches:
						if existing_branch.id not in branch_to_change_ids:
							SubBusiness.objects.filter(pk = existing_branch.id).delete()

					if len(branch_ids) > 0:
						for row_id in branch_ids:
							sub_business = None
							if POST.has_key('branchid_'+str(row_id)):
								sub_business = SubBusiness.objects.get(pk = int(POST['branchid_'+str(row_id)]))
							else:
								sub_business = SubBusiness()
							sub_business.business = obj
							sub_business.branch = POST['branchname_'+str(row_id)]
							sector_key = 'sector_' + str(row_id)
							cell_key = 'cell_'+ str(row_id)
							sector = request.POST.get(sector_key)
							cell = request.POST.get(cell_key)
							parcel_key = 'parcel_id_' + str(row_id)
							if sector and sector != '':
								sector = int(POST[sector_key])
								if sector != 0:
									sub_business.sector =  Sector.objects.get(pk= sector)
								else:
									sub_business.sector = None
							if POST.has_key(cell_key) and cell != '':
								cell = int(POST[cell_key])
								if cell != 0:
									sub_business.cell =  Cell.objects.get(pk= cell)
							if POST.has_key(parcel_key):
								parcel_id = POST[parcel_key]
								if parcel_id:
									sub_business.parcel_id =  POST[parcel_key]
							sub_business.save()

					LogMapper.createLog(request,object=obj,action="change", business = obj)	  
					
					success_message = 'Business updated successfully.'
					messages.success(request, success_message) 
					#redirect back to whatever url set in session at the moment
					if request.GET.has_key('redirect'):
						redirect = request.GET['redirect']

						if request.session.has_key(redirect + '_url'):
							
							return HttpResponseRedirect(request.session[redirect + '_url'])
			else:
				form = BusinessForm(instance=obj)

			#get media
			media = MediaMapper.getMedia('business',obj)
			#store current business URL into session to use in media upload redirect later
			request.session['business_url'] = request.get_full_path()


			sub_businesses = SubBusiness.objects.filter(business = obj)
			sub_businesses_arr = []
			if len(sub_businesses) > 0:
				for sub_business in sub_businesses:
					sub_business_dict = {}
					sub_business_dict['name'] = sub_business.branch
					sub_business_dict['id'] = sub_business.id
					sub_business_dict['branch'] = sub_business.branch
					if sub_business.sector:
						sub_business_dict['sector'] = sub_business.sector
					sub_business_dict['sector_list'] = Sector.objects.all()
					if sub_business.cell:
						sub_business_dict['cell'] = sub_business.cell
						sub_business_dict['cell_list'] = Cell.objects.filter(sector = sub_business.sector)
					if	sub_business.parcel_id:
						sub_business_dict['parcel_id'] = sub_business.parcel_id
					sub_businesses_arr.append(sub_business_dict)

			search_business_form = BusinessFilterForm(request.POST)
			LogMapper.createLog(request,object=obj,action="view", business = obj)
			return render_to_response('asset/business/business_list.html', {'form':form, 'obj_id': obj_id,'media':media, 'branches':sub_businesses_arr,'search_business_form':search_business_form,'action':'edit'},
							context_instance=RequestContext(request))
		elif request.method == 'POST':
			messages.error(request, 'Invalid business selected. Please try again.')
		return HttpResponseRedirect('/admin/asset/business/')

	elif action == 'delete':
		if not request.session['user'].has_action_by_name('asset','business','delete_business'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
		if obj_id != None:
			obj = get_object_or_404(Business, pk=obj_id)
			LogMapper.createLog(request,object=obj,old_data=model_to_dict(obj), action="delete",business = obj)
			obj.delete()
			messages.success(request, 'Business deleted successfully.')
			return HttpResponseRedirect('/admin/asset/business/')
		return HttpResponseRedirect('/admin/asset/business/')


def close_business(request, pk):
	business = get_object_or_404(Business, pk=pk)
	if request.POST:
		form = closeBusinessForm(request.POST, request.FILES)
		if form.is_valid():
			business.i_status = 'inactive'
			file = request.FILES['file']
			business.close(close_date=form.cleaned_data.get('close_date'))

			file_info = os.path.splitext(file.name)
			#strip all "." out of file name if exists
			file_name = file_info[0].replace('.','_') + '_' + datetime.now().strftime('%Y_%m_%d_%H_%M_%S') + file_info[1]
			file_path = 'business/' + file_name
			with open(settings.MEDIA_ROOT + file_path, 'wb+') as destination:
				for chunk in file.chunks():
					destination.write(chunk)
			media = Media(title='business closed', description="business closed on %s" % (form.cleaned_data.get('close_date').strftime('%Y-%m-%d')), file_name=file_name, 
				 path=file_path, file_type=file.content_type, file_size=file.size, business=business, user_id=request.session.get('user').pk)
			media.save()
			messages.success(request, '%s has been closed' % business)
			return HttpResponseRedirect('/admin/asset/business/change_business/%s/' % business.pk)
	else:
		form = closeBusinessForm()
	return TemplateResponse(request, 'asset/business/business_close.html', {'form':form, 'business':business  })


def shop_default(request, action, content_type_name1, obj_id = None):
	if not action:
		user = request.session.get('user')
		module = ModuleMapper.getModuleByName("asset")
		content_type = ContentTypeMapper.getContentTypeByModuleAndName('shop', module)
		actions = user.getActionsByContentTypeWithLink(content_type)
		return render_to_response('asset/shop/asset_shop_default.html', {\
							 'permissions':actions},
							  context_instance=RequestContext(request))
	elif action == 'add':
		if not request.session['user'].has_action_by_name('asset','shop','add_shop'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
		
		if request.method != 'POST':
			form =  ShopForm(initial={'i_status':'active',})
			return render_to_response('asset/shop/asset_shop_add.html', {'form':form,},
							context_instance=RequestContext(request))
		else:
			form = ShopForm(request.POST, request.FILES)
			if form.is_valid():
				form.save(request)
				messages.success(request, 'Shop added successfully.') 
				return HttpResponseRedirect('/admin/asset/shop/add_shop/')
			else:
				return render_to_response('asset/shop/asset_shop_add.html', {'form':form,},
							context_instance=RequestContext(request))

	elif action == 'change':
		if not request.session['user'].has_action_by_name('asset','shop','change_shop'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
		
		if obj_id != None:
			obj = get_object_or_404(Shop, pk=obj_id)
			form = ShopForm(initial= model_to_dict(obj))
			if request.method == 'POST' and request.POST.get('submit_update',None) != None:
				form = ShopForm(request.POST, instance = obj)
				form.id = obj_id
				if form.is_valid():
					form.save(request)
					messages.success(request, 'Shop updated successfully.') 
					LogMapper.createLog(request,object=obj,action="change")		  

			return render_to_response('asset/shop/asset_shop_change.html', {'form':form, 'obj_id': obj_id},
							context_instance=RequestContext(request))
		elif request.method == 'POST':
			messages.error(request, 'Invalid shop selected. Please try again.') 

		return render_to_response('asset/shop/asset_shop_change.html', {},
								context_instance=RequestContext(request))

	elif action == 'delete':
		if not request.session['user'].has_action_by_name('asset','shop','delete_shop'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
		if obj_id != None:
			obj = get_object_or_404(Shop, pk=obj_id)
			LogMapper.createLog(request,object=obj,old_data=model_to_dict(obj), action="delete")
			obj.delete()
			messages.success(request, 'Shop deleted successfully.') 
			return HttpResponseRedirect('/admin/asset/shop/')
		elif request.method == 'POST':
			messages.error(request, 'Invalid shop selected. Please try again.') 

		return render_to_response('asset/shop/asset_shop_delete.html', {},
								context_instance=RequestContext(request))


def office_default(request, action, content_type_name1, obj_id = None):
	if not action:
		user = request.session.get('user')
		module = ModuleMapper.getModuleByName("asset")
		content_type = ContentTypeMapper.getContentTypeByModuleAndName('office', module)
		actions = user.getActionsByContentTypeWithLink(content_type)
		return render_to_response('asset/office/asset_office_default.html', {\
							 'permissions':actions},
							  context_instance=RequestContext(request))
	elif action == 'add':
		if not request.session['user'].has_action_by_name('asset','office','add_office'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
		
		if request.method != 'POST':
			form =  OfficeForm(initial={'i_status':'active',})
			return render_to_response('asset/office/asset_office_add.html', {'form':form,},
							context_instance=RequestContext(request))
		else:
			form = OfficeForm(request.POST, request.FILES)
			if form.is_valid():
				form.save(request)
				messages.success(request, 'Office added successfully.') 
				return HttpResponseRedirect('/admin/asset/office/add_office/')
			else:
				return render_to_response('asset/office/asset_office_add.html', {'form':form,},
							context_instance=RequestContext(request))

	elif action == 'change':
		if not request.session['user'].has_action_by_name('asset','shop','change_shop'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
		
		if obj_id != None:
			obj = get_object_or_404(Office, pk=obj_id)
			form = OfficeForm(initial= model_to_dict(obj))
			if request.method == 'POST' and request.POST.get('submit_update',None) != None:
				form = OfficeForm(request.POST, instance = obj)
				form.id = obj_id
				if form.is_valid():
					form.save(request)
					messages.success(request, 'Office updated successfully.') 
					LogMapper.createLog(request,object=obj,action="change")		  

			return render_to_response('asset/office/asset_office_change.html', {'form':form, 'obj_id': obj_id},
							context_instance=RequestContext(request))
		elif request.method == 'POST':
			messages.error(request, 'Invalid office selected. Please try again.') 

		return render_to_response('asset/office/asset_office_change.html', {},
								context_instance=RequestContext(request))

	elif action == 'delete':
		if not request.session['user'].has_action_by_name('asset','shop','delete_shop'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
		
		if obj_id != None:
			obj = get_object_or_404(Office, pk=obj_id)
			LogMapper.createLog(request,object=obj,old_data=model_to_dict(obj), action="delete")
			obj.delete()
			messages.success(request, 'Office deleted successfully.') 
			return HttpResponseRedirect('/admin/asset/office/')
		elif request.method == 'POST':
			messages.error(request, 'Invalid office selected. Please try again.') 

		return render_to_response('asset/office/asset_office_delete.html', {},
								context_instance=RequestContext(request))


def stall_default(request, action, content_type_name1, obj_id = None):
	if not action:
		user = request.session.get('user')
		module = ModuleMapper.getModuleByName("asset")
		content_type = ContentTypeMapper.getContentTypeByModuleAndName('business', module)
		actions = user.getActionsByContentTypeWithLink(content_type)
		return render_to_response('asset/stall/asset_stall_default.html', {\
							 'permissions':actions},
							  context_instance=RequestContext(request))
	elif action == 'add':
		if not request.session['user'].has_action_by_name('asset','stall','add_stall'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
		
		if request.method != 'POST':
			form =  StallForm(initial={'i_status':'active',})
			return render_to_response('asset/stall/asset_stall_add.html', {'form':form,},
							context_instance=RequestContext(request))
		else:
			form = StallForm(request.POST, request.FILES)
			if form.is_valid():
				form.save(request)
				messages.success(request, 'Stall added successfully.') 
				return HttpResponseRedirect('/admin/asset/stall/add_stall/')
			else:
				return render_to_response('asset/stall/asset_stall_add.html', {'form':form,},
							context_instance=RequestContext(request))

	elif action == 'change':
		if not request.session['user'].has_action_by_name('asset','stall','change_stall'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
		if obj_id != None:
			obj = get_object_or_404(Stall, pk=obj_id)
			form = StallForm(initial= model_to_dict(obj))
			if request.method == 'POST' and request.POST.get('submit_update',None) != None:
				form = StallForm(request.POST, instance = obj)
				form.id = obj_id
				if form.is_valid():
					form.save(request)
					messages.success(request, 'Stall updated successfully.') 
					LogMapper.createLog(request,object=obj,action="change")		  

			return render_to_response('asset/stall/asset_stall_change.html', {'form':form, 'obj_id': obj_id},
							context_instance=RequestContext(request))
		elif request.method == 'POST':
			messages.error(request, 'Invalid stall selected. Please try again.') 

		return render_to_response('asset/stall/asset_stall_change.html', {},
								context_instance=RequestContext(request))

	elif action == 'delete':
		if not request.session['user'].has_action_by_name('asset','stall','delete_stall'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
		if obj_id != None:
			obj = get_object_or_404(Stall, pk=obj_id)
			LogMapper.createLog(request,object=obj,old_data=model_to_dict(obj), action="delete")
			obj.delete()
			messages.success(request, 'Stall deleted successfully.') 
			return HttpResponseRedirect('/admin/asset/stall/')
		elif request.method == 'POST':
			messages.error(request, 'Invalid stall selected. Please try again.') 

		return render_to_response('asset/stall/asset_stall_delete.html', {},
								context_instance=RequestContext(request))


def vehicle_default(request, action, content_type_name1, obj_id = None):
	if not action:
		user = request.session.get('user')
		module = ModuleMapper.getModuleByName("asset")
		content_type = ContentTypeMapper.getContentTypeByModuleAndName('vehicle', module)
		actions = user.getActionsByContentTypeWithLink(content_type)
		return render_to_response('asset/vehicle/asset_vehicle_default.html', {\
							 'permissions':actions},
							  context_instance=RequestContext(request))
	elif action == 'add':
		if not request.session['user'].has_action_by_name('asset','vehicle','add_vehicle'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
		if request.method != 'POST':
			form =  VehicleForm(initial={'i_status':'active',})
			return render_to_response('asset/vehicle/asset_vehicle_add.html', {'form':form,},
							context_instance=RequestContext(request))
		else:
			form = VehicleForm(request.POST, request.FILES)
			if form.is_valid():
				form.save(request)
				messages.success(request, 'Vehicle added successfully.') 
				return HttpResponseRedirect('/admin/asset/vehicle/add_vehicle/')
			else:
				return render_to_response('asset/vehicle/asset_vehicle_add.html', {'form':form,},
							context_instance=RequestContext(request))

	elif action == 'change':
		if not request.session['user'].has_action_by_name('asset','stall','change_stall'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
		if obj_id != None:
			obj = get_object_or_404(Vehicle, pk=obj_id)
			form = VehicleForm(initial= model_to_dict(obj))
			if request.method == 'POST' and request.POST.get('submit_update',None) != None:
				form = VehicleForm(request.POST, instance = obj)
				form.id = obj_id
				if form.is_valid():
					form.save(request)
					messages.success(request, 'Vehicle updated successfully.') 
					LogMapper.createLog(request,object=obj,action="change")		  

			return render_to_response('asset/vehicle/asset_vehicle_change.html', {'form':form, 'obj_id': obj_id},
							context_instance=RequestContext(request))
		elif request.method == 'POST':
			messages.error(request, 'Invalid vehicle selected. Please try again.') 

		return render_to_response('asset/vehicle/asset_vehicle_change.html', {},
								context_instance=RequestContext(request))

	elif action == 'delete':
		if not request.session['user'].has_action_by_name('asset','stall','delete_stall'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
		if obj_id != None:
			obj = get_object_or_404(Vehicle, pk=obj_id)
			LogMapper.createLog(request,object=obj,old_data=model_to_dict(obj), action="delete")
			obj.delete()
			messages.success(request, 'Vehicle deleted successfully.') 
			return HttpResponseRedirect('/admin/asset/vehicle/')
		elif request.method == 'POST':
			messages.error(request, 'Invalid vehicle selected. Please try again.') 

		return render_to_response('asset/vehicle/asset_vehicle_delete.html', {},
								context_instance=RequestContext(request))


def billboard_default(request, action, content_type_name1, obj_id = None):
	if not action:
		user = request.session.get('user')
		module = ModuleMapper.getModuleByName("asset")
		content_type = ContentTypeMapper.getContentTypeByModuleAndName('billboard', module)
		actions = user.getActionsByContentTypeWithLink(content_type)
		return render_to_response('asset/billboard/asset_billboard_default.html', {\
							 'permissions':actions},
							  context_instance=RequestContext(request))
	elif action == 'add':	
		if not request.session['user'].has_action_by_name('asset','billboard','add_billboard'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))	
		form =  BillboardForm(initial={'i_status':'active',})
		file_list = []
		if request.method == 'POST':
			form = BillboardForm(request.POST, request.FILES)
			if form.is_valid():
				file_valid = True
				if request.FILES != None:
					file_list = zip( request.FILES.getlist('media_urls'), request.POST.getlist('media_titles'), request.POST.getlist('media_descs'))
					#validate file
					for file, title, desc in file_list:
						if file.size > variables.MAX_UPLOAD_SIZE:
							messages.error(request, 'File upload exceeded the maximum limit of ' + str(intploads(variables.MAX_UPLOAD_SIZE / 1048576.0)) + 'Mb')
							file_valid = False

				if file_valid:
					billboard = form.save(request)
					#start upload file & create media record
					if request.FILES != None:
						folder = 'billboard/'
						if os.path.exists(settings.MEDIA_ROOT + folder) == False:
							os.mkdir(settings.MEDIA_ROOT + folder)

						media_folder = folder +  str(billboard.id) + '/'
						if os.path.exists(settings.MEDIA_ROOT + media_folder) == False:
							os.mkdir(settings.MEDIA_ROOT + media_folder)

						now = str(datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))

						staff = request.session.get('user')

						for file, title, desc in file_list:

							file_info = file.name.split('.')
							file_name = file_info[0].replace(" ","_") + '_' + now + '.' + file_info[1]
							file_path = media_folder + file_name
							with open(settings.MEDIA_ROOT + file_path, 'wb+') as destination:
								for chunk in file.chunks():
									destination.write(chunk)

							tags = 'billboard'

							media = Media(tags=tags,title=title,description=desc,file_name=file_name,path=file_path,file_type=file.content_type,
											file_size=file.size,billboard_id=billboard.id,user_id=staff.id)
							media.save()

					messages.success(request, 'Billboard added successfully.') 
					return HttpResponseRedirect('/admin/asset/billboard/add_billboard/')

		return render_to_response('asset/billboard/asset_billboard_add.html', {'form':form,'file_list':file_list},
					context_instance=RequestContext(request))

	elif action == 'change':
		if not request.session['user'].has_action_by_name('asset','billboard','change_billboard'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
		if obj_id != None:
			obj = get_object_or_404(Billboard, pk=obj_id)
			data = model_to_dict(obj)
			data['property'] = PropertyMapper.getUPIByPropertyId(data['property'])
			form = BillboardForm(initial= data)
			if request.method == 'POST' and request.POST.get('submit_update',None) != None:
				form = BillboardForm(request.POST, instance = obj)
				form.id = obj_id
				if form.is_valid():
					file_valid = True
					if request.FILES != None:
						file_list = zip( request.FILES.getlist('media_urls'), request.POST.getlist('media_titles'), request.POST.getlist('media_descs'))
						#validate file
						for file, title, desc in file_list:
							if file.size > variables.MAX_UPLOAD_SIZE:
								messages.error(request, 'File upload exceeded the maximum limit of ' + str(int(variables.MAX_UPLOAD_SIZE / 1048576.0)) + 'Mb')
								file_valid = False

					if file_valid:
						billboard = form.save(request)
						#start upload file & create media record
						if request.FILES != None:
							folder = 'billboard/'
							if os.path.exists(settings.MEDIA_ROOT + folder) == False:
								os.mkdir(settings.MEDIA_ROOT + folder)

							media_folder = folder +  str(billboard.id) + '/'
							if os.path.exists(settings.MEDIA_ROOT + media_folder) == False:
								os.mkdir(settings.MEDIA_ROOT + media_folder)

							now = str(datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))

							staff = request.session.get('user')

							for file, title, desc in file_list:

								file_info = file.name.split('.')
								file_name = file_info[0].replace(" ","_") + '_' + now + '.' + file_info[1]
								file_path = media_folder + file_name
								with open(settings.MEDIA_ROOT + file_path, 'wb+') as destination:
									for chunk in file.chunks():
										destination.write(chunk)

								tags = 'billboard'

								media = Media(tags=tags,title=title,description=desc,file_name=file_name,path=file_path,file_type=file.content_type,
												file_size=file.size,billboard_id=billboard.id,user_id=staff.id)
								media.save()

						messages.success(request, 'Billboard updated successfully.') 
						LogMapper.createLog(request,object=obj,action="change")		  

			#get media
			media = MediaMapper.getMedia('billboard',obj)
			#store current billboard URL into session to use in media upload redirect later
			request.session['billboard_url'] = request.get_full_path()

			return render_to_response('asset/billboard/asset_billboard_change.html', {'form':form, 'obj_id': obj_id,'media':media},
							context_instance=RequestContext(request))
		elif request.method == 'POST':
			messages.error(request, 'Invalid billboard selected. Please try again.') 

		return render_to_response('asset/billboard/asset_billboard_change.html', {},
								context_instance=RequestContext(request))

	elif action == 'delete':
		if not request.session['user'].has_action_by_name('asset','billboard','delete_billboard'):
			return render_to_response('forbidden.html', {},context_instance=RequestContext(request))
		if obj_id != None:
			obj = get_object_or_404(Billboard, pk=obj_id)
			LogMapper.createLog(request,object=obj,old_data=model_to_dict(obj), action="delete")
			obj.delete()
			messages.success(request, 'Billboard deleted successfully.') 
			return HttpResponseRedirect('/admin/asset/billboard/')
		elif request.method == 'POST':
			messages.error(request, 'Invalid billboard selected. Please try again.') 

		return render_to_response('asset/billboard/asset_billboard_delete.html', {},
								context_instance=RequestContext(request))