from django.utils import simplejson
from media.models import *
from django.forms.models import model_to_dict
from citizen.models import Citizen
from property.models import Property
from asset.models import Business

class MediaMapper:    
          
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get Media by Associated Type
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""    
	@staticmethod
	def getMedia(type,obj):
		kwargs = {}
		kwargs[type + '__exact'] = obj
		kwargs['i_status__exact'] = 'active'
		mediaList = Media.objects.filter(**kwargs).order_by("-date_created")
		result = []
		if mediaList:
			for i in mediaList:
				temp = model_to_dict(i)
				if i.tags:
					temp['tags'] = temp['tags'].replace("|"," | ")
				temp['associations'] = MediaMapper.getMediaAssociations(i)
				temp['date'] = i.date_created

				result.append(temp)
		return result

	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get Media by tags
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""    
	@staticmethod
	def getMediaByTags(tags):
		kwargs = {}
		if tags:
			for tag in tags:
				kwargs['tags__icontains'] = tag
				kwargs['i_status__exact'] = 'active'

		media = Media.objects.filter(**kwargs)
		return media

	@staticmethod
	def getMediaAssociations(media):
		links = ""
		if media.citizen != None:
			citizen = media.citizen
			links += "<b>C:</b> " + '<a href="/admin/citizen/citizen/view_citizen/' + str(citizen.id) + '/" >' + citizen.getDisplayName() + " (CID: " + citizen.citizen_id + ")</a><br/>"
		if media.business != None:
			business = media.business
			links += "<b>B:</b> " + '<a href="/admin/asset/business/change_business/' + str(business.id) + '/" >' + business.name + " (TIN: " + business.tin + ")</a><br/>"
		if media.property != None:
			property = media.property
			links += "<b>P:</b> " + '<a href="/admin/property/property/view_property/' + str(property.id) + '/" >' + property.getDisplayName() + " (UPI: " + property.getUPI() + ")</a><br/>"
		if media.billboard != None:
			billboard = media.billboard
			links += "<b>Billboard:</b> " + '<a href="/admin/asset/billboard/change_billboard/' + str(billboard.id) + '/" >' + billboard.name + " (UPI: " + billboard.property.getUPI() + ")</a><br/>"

		return links