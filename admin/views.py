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
from django.contrib.auth import authenticate as auth_authenticate, login as auth_login, logout as auth_logout
from django.core.urlresolvers import reverse
from django.contrib.auth.decorators import login_required

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
		username = None
		form = LoginForm(request.POST)
		errorMessage=None
		if form.is_valid():
			username = form.cleaned_data['username']
			password = form.cleaned_data['password']
			try:
				pm_user = login_attempt(username, password)
				user = auth_authenticate(username=username, password=password)

				if user is not None and not user.is_active:
					errorMessage="Your account has been disabled"

				elif (pm_user is not None and user is not None):
					#import pdb
					#pdb.set_trace()
					request.session['user'] = pm_user
					auth_login(request, user)
					content_types = pm_user.getContentTypesWithWeight()
					LogMapper.createLog(request,action="login")
					next = request.POST.get('next')
					if next:
						return HttpResponseRedirect(next)
					else:
						return HttpResponseRedirect(reverse('admin_home'))
				else:
					errorMessage="Incorrect username and password"
			except ValidationError, e:
					errorMessage= e.messages[0]
		else:
			errorMessage=form.errors
		return render_to_response('admin/login.html', {'form':form,'errorMessage':errorMessage, 'username':username}, context_instance=RequestContext(request))

	form = LoginForm()
	return render_to_response('admin/login.html', {'form': form}, context_instance=RequestContext(request))


@login_required
def admin(request):
	user = request.session.get('user')
	content_types = user.getContentTypesWithWeight()
	return render_to_response('admin/admin.html', {\
					 'content_types':content_types,},
					  context_instance=RequestContext(request))


def logout(request):
	# logout and clear session
	auth_logout(request)
	if request.session.has_key("user"):
		user = request.session['user']
		LogMapper.createLog(request,action="logout", user=user)
	for key in request.session.keys():
		del request.session[key]
	auth.logout(request)

	return HttpResponseRedirect(reverse('login'))

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

