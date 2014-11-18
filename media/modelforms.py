from django.forms import ModelForm
from django import forms
from datetime import date, datetime, time
from dev1 import variables
from media.models import Media

class MediaUploadForm(ModelForm):

	class Meta:
		model = Media
		exclude = ('i_status','date_created','user_id','file_name','file_type','file_size','path')
		widgets = {'tags': forms.HiddenInput,'citizen_id': forms.HiddenInput,'business_id': forms.HiddenInput,'property_id': forms.HiddenInput,'billboard_id': forms.HiddenInput,
			 'tax_type': forms.HiddenInput,'tax_id': forms.HiddenInput,'payment_type': forms.HiddenInput,'payment_id': forms.HiddenInput}
