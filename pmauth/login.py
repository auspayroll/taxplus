from models import *
from datetime import datetime, timedelta
from common.util import *
from django.core.mail import send_mail

def login_attempt(email, passwd):
    """ Wrapper for Django authentication function """
#     email = kwargs.get( 'email', '' )
#     if not email:
#         raise ValueError( 'email must be supplied by the authentication function for FailedLoginBlocker to operate' )         
    user=None
    try:
        fa = AccessAttempt.objects.get( loginname=email )
        if fa.recent_failure():
            if False: #fa.too_many_failures( ):
                # block the authentication attempt because
                # of too many recent failures
                fa.failures += 1
                fa.timestamp=CommonUtil.pg_utcnow() 
                fa.save()
                raise ValidationError("locked user for more than "+ str(FLB_MAX_FAILURES) +" times uncorrect attempt in "+ str(FLB_BLOCK_INTERVAL)+ " minutes")       
            elif(passwd==fa.temppasswd):
                user= PMUser.getUserByEmail(email=email)   
        else:
            # the block interval is over, reset the count
            fa.failures = 0
            fa.timestamp==CommonUtil.pg_utcnow() 
            fa.save()
    except AccessAttempt.DoesNotExist:
        fa = None
    if user is None:
        user = PMUser.getUserByEmailAndPassword(email = email, password = passwd)
    if user:
        # the authentication was successful
        return user
    # authentication failed
    fa = fa or AccessAttempt( loginname=email, failures=0,timestamp=CommonUtil.pg_utcnow() )
    fa.failures += 1
    fa.save()
    # return with unsuccessful auth
    return None

def generate_temp_passwd(email):
    try:
        fa = AccessAttempt.objects.get( loginname=email )
        fa.temppasswd=CommonUtil.passwd_generator()
        fa.save()
        content='Dear sir:\n'+ 'Your template password is:\n'+fa.temppasswd
       
#         send_mail('Your template password for Tax Plus', content, 'from@example.com', [email])
        output=CommonUtil.sendEmail('Your template password for Tax Plus', content, content, [email])
    except Exception as e:
        print e
        return False
#         import pdb
#         pdb.set_trace()
    finally:
        return output