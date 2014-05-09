from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404, HttpResponseRedirect,HttpResponse
from django.core.urlresolvers import reverse 
from django.contrib import messages
from django.conf import settings
from common.util import CommonUtil
from dev1 import variables
from bulk_messaging.forms import BulkMessagingForm
from log.mappers.LogMapper import LogMapper
from asset.models import Business
from property.models import Property
from citizen.models	import	Citizen

def send(request):
	if not request.is_ajax() or request.GET.get('list',None) == None:
		raise Http404

	list = request.GET.get('list')
	if not request.session.has_key(list + '_sms') or not request.session.has_key(list + '_email'):
		raise Http404
	form = BulkMessagingForm()
	result = {}
	if request.method == 'POST':
		form = BulkMessagingForm(request.POST)
		if form.is_valid():
			subject = form.cleaned_data['subject']
			mesg = form.cleaned_data['message']
			methods = form.cleaned_data['method']
			smsError = []
			emailError = []

			#get the list of email/sms from the session using the provided list name
			if 'sms' in methods:
				smsList = request.session[list + '_sms']
				if smsList:
					sendList = smsList.keys()

					#message content need to be urlencoded
					content = mesg

					response = CommonUtil.sendSms(content, sendList)

					if response.find('ERROR') >= 0:
						lines = response.split("\n")

						count = 0
						for i in lines:
							if i.find('ERROR') >= 0:
								smsError.append(sendList[count])
							count = count + 1

					result['sms_success'] = len(sendList) - len(smsError)
					result['sms_error'] = smsError
							
					#start logging this event
					for k,v in smsList.iteritems():
						business = None
						property = None
						citizen = None
						if v.has_key('bid'):
							businesses = Business.objects.filter(pk=v['bid'])
							if businesses:
								business = businesses[0]
						if v.has_key('cid'):
							citizens = Citizen.objects.filter(pk=v['cid'])
							if citizens:
								citizen = citizens[0]
						if v.has_key('pid'):
							properties = Property.objects.filter(pk=v['pid'])
							if properties:
								property = properties[0]

						if k in smsError:
							message = " failed to send SMS to " + k 
						else:
							message = " sent a SMS to " + k

						#only include first 50 characters of the sms content into the log
						message = message + ". Content:\n [" + content[:50] + "]"
						if len(content) > 50:
							message = message + "..."
						LogMapper.createLog(request,business=business,property=property,citizen=citizen,message=message)

			if 'email' in methods:
				from_email = variables.SUPPORT_EMAIL
				emailList = request.session[list + '_email']
				if emailList:
					sendList = emailList.keys()
					#try:
					content =  mesg
					html_content = '<p>' + mesg + '</p>'

					CommonUtil.sendEmail(subject,content,html_content,sendList)

					#except (ValueError, IndexError) as e:
						#emailError.append(email)

					result['email_success'] = len(emailList) - len(emailError)
					result['email_error'] = emailError

					#start logging this event
					for k,v in emailList.iteritems():
						business = None
						property = None
						citizen = None
						if v.has_key('bid'):
							businesses = Business.objects.filter(pk=v['bid'])
							if businesses:
								business = businesses[0]
						if v.has_key('cid'):
							citizens = Citizen.objects.filter(pk=v['cid'])
							if citizens:
								citizen = citizens[0]
						if v.has_key('pid'):
							properties = Property.objects.filter(pk=v['pid'])
							if properties:
								property = properties[0]

						if k in emailError:
							message = " failed to send Email to " + k 
						else:
							message = " sent an Email to " + k

						#only include first 50 characters of the sms content into the log
						message = message + ". Subject:\n [" + subject + "]"
						LogMapper.createLog(request,business=business,property=property,citizen=citizen,message=message)

	return render_to_response('bulk_messaging/_bulk_messaging_box.html', {'form':form,'list':list,'result':result},
						context_instance=RequestContext(request))

