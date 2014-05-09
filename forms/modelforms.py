from django.forms import ModelForm
from django import forms
from forms.models import *
from datetime import date, datetime, time
from dev1 import variables

class FormUploadForm(ModelForm):

	class Meta:
		model = Form
		exclude = ('i_status','date_created','user_id','path')
