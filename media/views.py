from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404, HttpResponseRedirect,HttpResponse
from django.core.urlresolvers import reverse 
from django.contrib import messages
from django.conf import settings
from dev1 import variables
from media.models import *
#from media.modelforms import MediaUploadForm
from jtax.models import *
from log.mappers.LogMapper import LogMapper
from property.models import Property
from citizen.models import Citizen
import os
from asset.models import Business
from property.models import Property
from citizen.models import Citizen
from admin.views import login
from django.utils import simplejson
from media.mappers.MediaMapper import MediaMapper
from django.contrib.auth.decorators import login_required

@login_required
def index(request, content_type_name, action = None):
	"""
	Search logs by 1)username, 2)plot id or 3)transaction id
	"""   
	form = MediaUploadForm(request.GET)
	business = None
	citizen = None
	property = None
	billboard = None
	redirect = None

	if request.GET.get('redirect',None) != None:
		redirect = request.GET.get('redirect')
	if request.GET.get('business_id',None) != None:
		result = Business.objects.filter(pk__exact=request.GET.get('business_id'))
		if result:
			business = result[0]
		redirect = '/admin/asset/business/change_business/' + str(business.id) + '/'
	if request.GET.get('citizen_id',None) != None:
		result = Citizen.objects.filter(pk__exact=request.GET.get('citizen_id'))
		if result:
			citizen = result[0]
		redirect = '/admin/citizen/citizen/view_citizen/' + str(citizen.id) + '/media/'

	if request.GET.get('property_id',None) != None:
		result = Property.objects.filter(pk__exact=request.GET.get('property_id'))
		if result:
			property = result[0]
		redirect = '/admin/property/property/view_property/' + str(property.id) + '/media/'

	if request.GET.get('billboard_id',None) != None:
		result = Billboard.objects.filter(pk__exact=request.GET.get('billboard_id'))
		if result:
			billboard = result[0]
		redirect = '/admin/asset/billboard/change_billboard/' + str(billboard.id) + '/'

	return render_to_response('media/media_upload.html', {'form':form,'default_tags':variables.media_tags,'redirect':redirect,'business':business,'citizen':citizen,'property':property,'billboard':billboard},
						context_instance=RequestContext(request))


def update(request, content_type_name):
	if request.method == 'GET' and request.GET.get('id',None) != None:
		media = get_object_or_404(Media,pk=request.GET['id'])
		if request.GET.get('description',None) != None and request.GET['description'] != None:
			media.description = request.GET['description']
		if request.GET.get('title',None) != None  and request.GET['title'] != None:
			media.title = request.GET['title']

		media.save()
		return HttpResponse("")
	else:
		raise Http404


def upload_ajax(request, content_type_name, action = None):

	if request.method == 'POST' and request.FILES != None:
		file = request.FILES['file']
		file_valid = True

		#validate file
		if file.size > variables.MAX_UPLOAD_SIZE:
			messages.error(request, 'File upload exceeded the maximum limit of ' + str(int(variables.MAX_UPLOAD_SIZE / 1048576.0)) + 'Mb')
			file_valid = False

		if file_valid:
			staff = request.session.get('user')
			log_citizen_id = None;
			log_plot_id = None;
			citizen = None
			property = None
			business = None
			billboard = None
			incomplete_payment = None
			tax_type = None
			tax_id = None
			payment_type = None
			payment_id = None
			incomplete_payment_id = None
			title = ''
			description = ''
			tags = ''
			staff = request.session.get('user')

			if request.POST.get('citizen_id',None) != None and request.POST.get('citizen_id') != '' and request.POST.get('citizen_id') != 'None':
				citizen = Citizen.objects.get(pk=int(request.POST.get('citizen_id')))
			if request.POST.get('incomplete_payment_id',None) != None and request.POST.get('incomplete_payment_id') != '' and request.POST.get('incomplete_payment_id') != 'None':
				incomplete_payment= IncompletePayment.objects.get(pk=int(request.POST.get('incomplete_payment_id')))
			if request.POST.get('property_id',None) != None and request.POST.get('property_id') != '' and request.POST.get('property_id') != 'None':
				property = Property.objects.get(pk=int(request.POST.get('property_id')))
			if request.POST.get('business_id',None) != None and request.POST.get('business_id') != '' and request.POST.get('business_id') != 'None':
				business = Business.objects.get(pk=int(request.POST.get('business_id')))
			if request.POST.get('billboard_id',None) != None and request.POST.get('billboard_id') != '' and request.POST.get('billboard_id') != 'None':
				billboard = Billboard.objects.get(pk=int(request.POST.get('billboard_id')))
			if request.POST.get('title',None)  and request.POST.get('title') != '':
				title = request.POST.get('title');
			if request.POST.get('description',None)  and request.POST.get('description') != '' :
				description = request.POST.get('description');
			if request.POST.get('tags',None)  and request.POST.get('tags') != '':
				tags = request.POST.get('tags');

			if request.POST.get('tax_type'):
				#upload from Invoice Generate page
				tax_type = request.POST.get('tax_type')
				tax_id = request.POST.get('tax_id')
				payment_id = request.POST.get('payment_id',None)
				payment_type = 'pay_'+tax_type

				if tax_type == 'fee':
					tax = Fee.objects.get(pk=tax_id)
					business = tax.business
					subbusiness = tax.subbusiness
					property = tax.property
				elif tax_type == 'fixed_asset':
					tax = PropertyTaxItem.objects.get(pk=tax_id)
					property = tax.property
				elif tax_type == 'trading_license':
					tax = TradingLicenseTax.objects.get(pk=tax_id)
					business = tax.business
					subbusiness = tax.subbusiness
				elif tax_type == 'rental_income':
					tax = RentalIncomeTax.objects.get(pk=tax_id)
					property = tax.property

				#determine the location to upload file to, use the priority:  tax > citizen > property > business
				# (if file associated with citizen then put inside citizen folder, etc)
				tax_folder = 'tax/' + tax_type.strip() + '/'
				if os.path.exists(settings.MEDIA_ROOT + tax_folder) == False:
					os.mkdir(settings.MEDIA_ROOT + tax_folder)

				folder = tax_folder +  str(tax_id) + '/'
				tags = 'tax|payment'
			else:
				#determine the location to upload file to, use the priority:  tax > citizen > property > business
				# (if file associated with citizen then put inside citizen folder, etc)
				folder = ''
				if citizen:
					folder = 'citizen/' + str(citizen.id) + '/'
				elif property:
					folder = 'property/' + str(property.id) + '/'
				elif business:
					folder = 'business/' + str(business.id) + '/'
				elif billboard:
					folder = 'billboard/' + str(billboard.id) + '/'
				elif incomplete_payment:
					folder = 'incomplete_payment/' + str(incomplete_payment.id) + '/'
					tags = 'tax|incomplete_payment'

			if os.path.exists(settings.MEDIA_ROOT + folder) == False:
				os.mkdir(settings.MEDIA_ROOT + folder)

			now = str(datetime.now().strftime('%Y_%m_%d_%H_%M_%S'))

			file_info = os.path.splitext(file.name)
			#strip all "." out of file name if exists
			file_name = file_info[0].replace('.','_') + '_' + now + file_info[1]
			file_path = folder + file_name

			with open(settings.MEDIA_ROOT + file_path, 'wb+') as destination:
				for chunk in file.chunks():
					destination.write(chunk)

			media = Media(title=title,description=description,tags=tags,file_name=file_name,path=file_path,file_type=file.content_type,
							file_size=file.size,citizen=citizen,business=business,property=property,billboard=billboard,incomplete_payment=incomplete_payment,
							tax_type=tax_type,tax_id=tax_id,payment_type=payment_type,payment_id=payment_id,user_id=staff.id)
			media.save()

			#log
			LogMapper.createLog(request,object=media,action="add",citizen=citizen,property=property,business=business,user=staff,media_id=media.id,tax_type=tax_type,tax_id=tax_id,payment_type=payment_type,payment_id=payment_id)

			uploaded_files = {'id':media.id,'name':file.name, 'type':file.content_type.split('/')[0] + 'Kb', 'size':file.size,'title':title,'description':description,'tags':tags,'associations':MediaMapper.getMediaAssociations(media)}
			return HttpResponse(simplejson.dumps(uploaded_files), mimetype='application/json')

	else:
		raise Http404


def preview(request,content_type_name,id):
	if not request.is_ajax():
		raise Http404
	media = get_object_or_404(Media,pk=id)

	return render_to_response('media/_media_preview.html', {'media':media,},
						context_instance=RequestContext(request))
