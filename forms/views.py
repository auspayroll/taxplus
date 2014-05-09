from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse 
from django.contrib import messages
from django.conf import settings
from dev1 import variables
from forms.models import *
from forms.modelforms import *
from log.mappers.LogMapper import LogMapper
import os
from pmauth.models import PMUser

from admin.views import login

def index(request, content_type_name, action = None):

	form = FormUploadForm()
	staff = request.session.get('user')
	#get user group permission - only allow super user to modify forms for now until we fix up the permission system
	have_permission = False
	if staff.superuser:
		have_permission = True

	if request.method == 'POST':
		form = FormUploadForm(request.POST)
		if form.is_valid():
			#start upload file & create media record
			if request.FILES != None and request.FILES.has_key('url'):
				file = request.FILES['url']
				file_valid = True
				file_info = os.path.splitext(file.name)

				#validate file
				if file.size > variables.MAX_UPLOAD_SIZE:
					messages.error(request, 'File upload exceeded the maximum limit of ' + str(int(variables.MAX_UPLOAD_SIZE / 1048576.0)) + 'Mb')
					file_valid = False
				if file_info[1].lower() not in variables.FORM_UPLOAD_FILE_TYPES:
					messages.error(request, 'File upload must be in the following format: ' + ", ".join(variables.FORM_UPLOAD_FILE_TYPES))
					file_valid = False

				if file_valid:

					#determine the location to upload file to, use the priority:  tax > citizen > property > business
					# (if file associated with citizen then put inside citizen folder, etc)
					folder = 'forms/'

					if os.path.exists(settings.MEDIA_ROOT + folder) == False:
						os.mkdir(settings.MEDIA_ROOT + folder)

					now = str(datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))

					#strip all "." out of file name if exists
					file_name = file_info[0].replace('.','_') + '_' + now + file_info[1]
					file_path = folder + file_name

					with open(settings.MEDIA_ROOT + file_path, 'wb+') as destination:
						for chunk in file.chunks():
							destination.write(chunk)

					#manually set required by excluded fields
					uploadForm = form.save(commit=False)
					uploadForm.path = file_path
					uploadForm.user_id = staff.id
					uploadForm.save()

					#log
					LogMapper.createLog(request,object=uploadForm,action="add",user=staff)   
					
					messages.success(request, 'Form uploaded successfully.')    
					#KLUDGE - hardcode the urls here, need to change later
					if request.POST.get('redirect',None) != None:
						redirect_var =request.POST.get('redirect') + "_url"
						if redirect_var in request.session:
							url = request.session[redirect_var] 
							return HttpResponseRedirect(url)
						else:
							return HttpResponseRedirect('/admin/forms/forms/')
					else:
						return HttpResponseRedirect('/admin/forms/forms/')

			else:
				messages.error(request, "Please select a file to upload")

	redirect = None
	if request.GET.get('redirect',None) != None:
		redirect = request.GET.get('redirect')

	uploaded_forms = Form.objects.filter(i_status__exact='active').order_by('language','title')
	#seperate search result to different language tables
	list = {}
	if uploaded_forms:
		for i in uploaded_forms:
			if i.language == '' or i.language == None:
				i.language = 'English'
			if list.has_key(i.language):
				temp = list[i.language]
				temp.append(i)
				list[i.language] = temp
			else:
				list[i.language] = [i]

	return render_to_response('forms/index.html', {'form':form,'redirect':redirect,'list':list,'have_permission':have_permission},
						context_instance=RequestContext(request))

def delete(request, content_type_name, id):
	form = get_object_or_404(Form, pk=id)
	#remove the file
	if os.path.isfile(settings.MEDIA_ROOT + form.path):
		os.remove(settings.MEDIA_ROOT + form.path)

	form.delete()
	#log
	user = PMUser.objects.get(pk = form.user_id)
	LogMapper.createLog(request,object=form,action="delete",user=user)   

	return HttpResponseRedirect('/admin/forms/forms/')