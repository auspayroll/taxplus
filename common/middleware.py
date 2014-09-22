from datetime import datetime, timedelta
from django.conf import settings
from django.contrib import auth
from pmauth.models import *

"""
class AutoLogout:
    def process_request(self, request):
        user=None
        if 'user' in request.session:
            user=request.session['user']
            if not PMUser.validateUser(user):
                request.session.flush()
                return

            else:            
                try:
                    if datetime.now() - request.session['last_touch'] > timedelta( 0, settings.AUTO_LOGOUT_DELAY * 60, 0):
    #                 logout(request)
                        request.user=None
                        del request.session['user']
                        del request.session['last_touch']
                        return
                except KeyError:
                    pass
                request.session['last_touch'] = datetime.now()
        else:
            pass
"""  
    
#     def login(self,request, user):
# 
#         if user is None:
#             user = request.user
#         # TODO: It would be nice to support different login methods, like signed cookies.
#         if user in request.session:
#             if PMUser.getUserByEmailAndPassword(user.email, user.password)==None
#                 request.session.flush()
#         else:
#             request.session.cycle_key()
#         request.session[SESSION_KEY] = user.pk
#         request.session[BACKEND_SESSION_KEY] = user.backend
#         if hasattr(request, 'user'):
#             request.user = user
#         rotate_token(request)
#         user_logged_in.send(sender=user.__class__, request=request, user=user)

