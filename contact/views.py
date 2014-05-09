from django.shortcuts import render_to_response, HttpResponse, redirect
from django.template import RequestContext
from contact.modelforms.modelforms import *
from admin.views import login
from django.core.mail import send_mail

def enquiry(request):
	if request.method != 'POST':
		form = ContactCreationForm()
		return render_to_response('contact/contact_contact_add.html', {'form':form,},
							  context_instance=RequestContext(request))
	else:
		form = ContactCreationForm(request.POST)
		if form.is_valid():
			form.save(request)
			name = form.cleaned_data['name']
			query_type = form.cleaned_data['query_type']
			phone = form.cleaned_data['phone']
			message = form.cleaned_data['message']
			message = message + '\r\n\r\nregards,\r\n\r\n' + name
			if phone and str(phone).strip()!='':
				message = message + ' ('+phone+')'



			email = form.cleaned_data['email']

			email_subject = query_type
			email_message = message


			email_from = email
			email_to = []
			if query_type == 'payment dispute' or 'complaints on council':
				email_to.append('stanley@propertymode.com.au')
			elif query_type == 'technical issue':
				email_to.append('justin@propertymode.com.au')
			elif query_type == 'general feedback':
				email_to.append('vincent@propertymode.com.au')
			elif query_type == 'customer support':
				email_to.append('vincent@propertymode.com.au')
			send_mail(email_subject, email_message, email_from, email_to, fail_silently=False)
			return redirect("/admin/")
		else: 
			return render_to_response('contact/contact_contact_add.html', {'form':form,},
								context_instance=RequestContext(request))
	