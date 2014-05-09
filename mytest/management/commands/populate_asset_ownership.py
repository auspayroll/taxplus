from django.core.management.base import BaseCommand, CommandError 
from asset.models import Ownership, Business, SubBusiness
from citizen.models import Citizen
from property.models import Property

class Command(BaseCommand):
	def handle(self, *args, **options):
		for obj in Ownership.objects.all():
			if obj.owner_type == 'citizen':
				owner_citizen = Citizen.objects.filter(id = obj.owner_id)
				if len(owner_citizen) > 0:
					owner_citizen = owner_citizen[0]
					obj.owner_citizen = owner_citizen
			if obj.owner_type == 'business':
				owner_business = Business.objects.filter(id = obj.owner_id)
				if len(owner_business) > 0:
					owner_business = owner_business[0]
					obj.owner_business = owner_business
			if obj.asset_type == 'business':
				asset_business = Business.objects.filter(id = obj.asset_id)
				if len(asset_business) > 0:
					asset_business = asset_business[0]
					obj.asset_business = asset_business
			if obj.asset_type == 'property':
				asset_property = Property.objects.filter(id = obj.asset_id)
				if len(asset_property) > 0:
					asset_property = asset_property[0]
					obj.asset_property = asset_property
			print "populate record: " + str(obj.id)
			obj.save()
		





	
		