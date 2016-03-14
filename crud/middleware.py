from django.db.models import signals
from django.utils.functional import curry
import json
from django.contrib.contenttypes.models import ContentType
from .models import Log

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

class LogMiddleware(object):
    def process_request(self, request):
        if not request.method in ('GET', 'HEAD', 'OPTIONS', 'TRACE'):
            if hasattr(request, 'user') and request.user.is_authenticated():
                user = request.user
            else:
                user = None
            request_ip = get_client_ip(request)
            mark_whodid = curry(self.mark_whodid, user, request.path, request_ip)
            signals.pre_save.connect(mark_whodid,  dispatch_uid = (self.__class__, request,), weak = False)

    def process_response(self, request, response):
        signals.pre_save.disconnect(dispatch_uid =  (self.__class__, request,))
        return response

    def mark_whodid(self, user, request_path, request_ip, sender, instance, **kwargs):
        if hasattr(instance, 'pk') and instance.pk is not None:
            ct = ContentType.objects.get_for_model(instance)
            if ct.app_label == 'crud':
                db_object = instance.__class__.objects.get(pk=instance.pk)
                fields = set([f.name for f in instance._meta.fields]).union(set([f.name for f in db_object._meta.fields]))
                fields = list(fields)
                changes = {}
                for f in fields:
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
                    account = None
                    if hasattr(instance, 'account'):
                        account = instance.account
                    Log.objects.create(changes=change_string, instance=instance, account= account, user=user, request_path=request_path, request_ip=request_ip)
