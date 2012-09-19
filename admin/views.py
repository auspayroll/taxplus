from django.shortcuts import render_to_response
from django.template import RequestContext
from django.http import Http404
from auth.forms.forms import LoginForm
from log.mappers.LogMapper import LogMapper
from auth.mappers.UserMapper import UserMapper

    
def login(request):
    """
    Show login form if user hasn't yet logged in. Otherwise, go to home page
    """
        
    if request.method == 'POST':
        form = LoginForm(request.POST)
        errorMessageType = 0
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = UserMapper.getUserByEmailAndPassword(email = username, password = password)
            if user is not None:
                if user.active:
                    content_types = UserMapper.getContentTypes(user)
                    request.session['user'] = user
                    LogMapper.createLog(request,action="login")
                    return render_to_response('admin/admin.html', {\
                         'content_types':content_types,},
                          context_instance=RequestContext(request))
                else:
                    errorMessageType = 1 #"Your account has been disabled!"
            else:
                errorMessageType = 2 #"Your username and password were incorrect."  
        else:
            errorMessageType = 2 #"Your username and password were incorrect."  
        return render_to_response('admin/login.html', {'form':form,'errorMessageType':errorMessageType,}, context_instance=RequestContext(request))
    elif request.session.get('user') is not None:
        # since user has logged in, go to home page
        id = request.session.get('user').id
        user = UserMapper.getUserById(id)
        content_types = UserMapper.getContentTypes(user)
        return render_to_response('admin/admin.html', {\
                         'content_types':content_types,},
                          context_instance=RequestContext(request))
    else:
        form = LoginForm()
    return render_to_response('admin/login.html', {'form': form}, context_instance=RequestContext(request))

def logout(request):
    # logout and clear session
    LogMapper.createLog(request,action="logout")
    for key in request.session.keys():
        del request.session[key]
    return login(request)     
