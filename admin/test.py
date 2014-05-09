from django.http import HttpResponse
from django.utils import simplejson

def post(request):
    if request.method == 'POST' and request.GET.has_key("username") and request.GET.has_key("password"):
        to_json = {}
        to_json['username']=request.POST["username"]
        to_json['password']=request.POST["password"]
        return HttpResponse(simplejson.dumps(to_json), mimetype='application/json')

