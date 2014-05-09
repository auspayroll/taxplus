from django.forms import ModelForm
from django import forms
from citizen.models import Status
from log.models import Log
from django.forms import model_to_dict
from log.mappers.LogMapper import LogMapper
from dev1.variables import gender_types, HorizontalRadioRenderer
from contact.models import *

class ContactCreationForm(ModelForm):
	"""
	Used for citizen registry
	Override the save method to integrate with log capability
	"""
	class Meta:
		model = Contact
		exclude = ('status','date_time')

	def save(self, request, commit=True):
		contact = forms.ModelForm.save(self, False)
		if commit:
			contact.save()
			LogMapper.createLog(request,object=contact,action="add")			
		return contact

