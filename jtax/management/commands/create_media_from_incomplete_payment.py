"""
This script generate tax items for all citizens & businesses in the system for current year.
SHOULD BE USED WITH CAUTION AS LOT OF LEGACY DATA IS MISSING ATM.
"""

from django.core.management.base import BaseCommand, CommandError 
from jtax.models import IncompletePayment
import os
from dev1.settings import PROJECT_DIR
from media.models import Media
import magic, mimetypes, urllib

class Command(BaseCommand):
	def handle(self, *args, **options):
		incomplete_payment_path =  os.path.dirname(os.path.join(PROJECT_DIR, 'uploads/incomplete_payment/'))
		for obj in IncompletePayment.objects.all():
			if obj.saved_files and obj.user_id:
				files = str(obj.saved_files).split(';')
				for file in files:
					if file:
						file_full_path = os.path.join(incomplete_payment_path,str(obj.id)+'/'+file)
						if os.path.exists(file_full_path):
							media = Media()
							media.tags = 'incomplete payment'
							media.file_name = file
							media.path = 'incomplete_payment/'+str(obj.id)+'/'+file
							mime = mimetypes.MimeTypes()
							url = urllib.pathname2url(file_full_path)
							mime_type = mime.guess_type(url)[0]
							media.file_type = mime_type
							fileinfo = os.stat(file_full_path)
							media.file_size = fileinfo.st_size
							media.incomplete_payment = obj
							media.user_id = obj.user.id
							media.save()
							
							
							
		