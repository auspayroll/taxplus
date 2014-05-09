from pmauth.models import PMPermission,PMContentType,PMModule,PMUser,PMGroup
from django.http import HttpResponse
from django.db.models import Q


def check_group_exist(request):
	if request.method == 'GET':
		GET = request.GET
		if GET.has_key('name'):
			name = GET['name']
			group = PMGroup.objects.filter(name__iexact = name)
			if GET.has_key('group_id'):
				group = group.filter(~Q(id = int(GET['group_id'])))
			if len(group) > 0:
				return HttpResponse("YES")
			else:
				return HttpResponse("NO")
			
def check_user_email_exist(request):
	if request.method == 'GET':
		GET = request.GET
		if GET.has_key('email'):
			email = GET['email']
			user = PMUser.objects.filter(email__iexact = email)
			if GET.has_key('user_id'):
				user = user.filter(~Q(id = int(GET['user_id'])))
			if len(user) > 0:
				return HttpResponse("YES")
			else:
				return HttpResponse("NO")

