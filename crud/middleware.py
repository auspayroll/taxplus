from django.db.models import signals
from django.utils.functional import curry
import json
from django.contrib.contenttypes.models import ContentType
from .models import Log, Account
from django.contrib.auth.models import User

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

exclude_fields = ('pk', 'created', 'updated', 'created_on', 'updated_on', 'id', 'user', 'password', 'passwd')

class LogMiddleware(object):
    def process_request(self, request):
        if not request.method in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            if hasattr(request, 'user') and request.user.is_authenticated():
                user = request.user
            else:
                user = None
            request_ip = get_client_ip(request)
            mark_whodid_update = curry(self.mark_whodid_update, user, request.path, request_ip)
            mark_whodid_create = curry(self.mark_whodid_create, user, request.path, request_ip)
            signals.pre_save.connect(mark_whodid_update,  dispatch_uid = (self.__class__, request,), weak = False)
            signals.post_save.connect(mark_whodid_create,  dispatch_uid = (self.__class__, request,), weak = False)

    def process_response(self, request, response):
        signals.pre_save.disconnect(dispatch_uid =  (self.__class__, request,))
        signals.post_save.disconnect(dispatch_uid =  (self.__class__, request,))
        return response

    def mark_whodid_update(self, user, request_path, request_ip, sender, instance, **kwargs):
        account = None
        if hasattr(instance, 'account'):
            account = instance.account
        if hasattr(instance, 'pk') and instance.pk is not None:
            ct = ContentType.objects.get_for_model(instance)
            if ct.app_label == 'crud' or isinstance(instance, User):
                #last logins are set by the system so user will be empty, set it here
                if isinstance(instance, User) and not user:
                    user = instance
                db_object = instance.__class__.objects.get(pk=instance.pk)
                fields = set([f.name for f in instance._meta.fields]).union(set([f.name for f in db_object._meta.fields]))
                fields = list(fields)
                changes = {}
                for f in fields:
                    if f in exclude_fields:
                        continue
                    old_value = ''
                    new_value = ''
                    if hasattr(db_object, f):
                        old_value = str(getattr(db_object, f))
                    if hasattr(instance, f):
                        new_value = str(getattr(instance, f))
                    if old_value != new_value:
                        changes[f] = (old_value, new_value)
                if changes:
                    change_string = json.dumps(changes)
                    Log.objects.create(changes=change_string, instance=instance, account= account, user=user, request_path=request_path, request_ip=request_ip)


    def mark_whodid_create(self, user, request_path, request_ip, sender, instance, created, **kwargs):
        if created and not isinstance(instance, Log):
            account = None
            if hasattr(instance, 'account'):
                account = instance.account
            elif isinstance(instance, Account):
                account = instance
            ct = ContentType.objects.get_for_model(instance)
            if ct.app_label == 'crud' or isinstance(instance, User):
                changes = dict([(f.name,(None, str(getattr(instance, f.name)))) \
                    for f in instance._meta.fields if getattr(instance, f.name) is not None \
                    and f.name not in exclude_fields])
                if changes:
                    change_string = json.dumps(changes)
                    Log.objects.create(changes=change_string, instance=instance, account= account, user=user, request_path=request_path, request_ip=request_ip)
