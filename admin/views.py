from django.shortcuts import render_to_response, HttpResponse, HttpResponseRedirect
from django.template import RequestContext
from django.http import Http404
from pmauth.forms.forms import LoginForm
from log.mappers.LogMapper import LogMapper
from pmauth.models import *
from dev1 import variables
from django.contrib import auth
from django.utils.translation import ugettext
from django.core.exceptions import ValidationError
from pmauth.login import *

def set_temp_password(request):
	stringok='Generate your password, please check it from your email!\n'\
		+'The temporary password can only work '+str(FLB_BLOCK_INTERVAL)+' minutes.'
	stringerror='generate password error. please contact the web administrator'
	username=request.GET['username']
	if(generate_temp_passwd(username)):

# 		return HttpResponse(stringok) 
		
		return render_to_response('admin/temp_password.html', {'errorMessage':''}, context_instance=RequestContext(request))
	else:
# 		return HttpResponse(stringerror)
		return render_to_response('admin/temp_password.html', {'errorMessage':'generate password error. please contact the web administrator'}, context_instance=RequestContext(request))
def login(request):
	"""
	Show login form if user hasn't yet logged in. Otherwise, go to home page
	"""
	if request.method == 'POST':
		form = LoginForm(request.POST)
		errorMessageType = 0
		errorMessage=None
		if form.is_valid():
			username = form.cleaned_data['username']
			password = form.cleaned_data['password']
			try:
				user = login_attempt(username, password)
				if (user is not None):
					request.session['user'] = user
					content_types = user.getContentTypesWithWeight()
					LogMapper.createLog(request,action="login")
					return render_to_response('admin/admin.html', {\
							 'content_types':content_types,},
							  context_instance=RequestContext(request))
				else:
					errorMessage="Your username and password were incorrect or your username "
			except ValidationError, e:
# 					import pdb
# 					pdb.set_trace()
					errorMessage= e.messages[0]
		else:
			errorMessageType = 0#"Your username and password were incorrect."
			errorMessage=form.errors 
		return render_to_response('admin/login.html', {'form':form,'errorMessage':errorMessage, 'username':username}, context_instance=RequestContext(request))
	elif request.session.get('user') is not None:
		# since user has logged in, go to home page
		user = request.session.get('user')
		if not user or not type(user) is PMUser:
			form = LoginForm()
			return render_to_response('admin/login.html', {'form': form}, context_instance=RequestContext(request))
		content_types = user.getContentTypesWithWeight()
		return render_to_response('admin/admin.html', {\
						 'content_types':content_types,},
						  context_instance=RequestContext(request))
	else:
		form = LoginForm()
	return render_to_response('admin/login.html', {'form': form}, context_instance=RequestContext(request))

def logout(request):
	# logout and clear session
	if request.session.has_key("user"):
		user = request.session['user']
		LogMapper.createLog(request,action="logout", user=user)
	for key in request.session.keys():
		del request.session[key]
	auth.logout(request)

	return login(request)

def construction(request):
    #return HttpResponse('Unauthorized', status=401)
    raise Http404
    #return render_to_response('admin/construction.html', {}, context_instance=RequestContext(request))


#from django.utils.translation import ugettext as _


'''
def my_view(request):
	output = _("Welcome to my site.")

	print request.session.keys()
	if request.session.has_key('language'):
		language = request.session['language']
		return HttpResponse(language)
	return HttpResponse(output)


def set_language(request):

	return render_to_response('admin/languages.html', {},context_instance=RequestContext(request))
'''

