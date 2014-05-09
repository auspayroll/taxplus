from django import forms
from dev1.variables import *
from property.models import Sector, Cell, District
from django.forms.widgets import CheckboxSelectMultiple

from dev1 import settings
from dev1 import variables

class BulkMessagingForm(forms.Form):
	CHOICES = [
        ('sms', 'SMS'),
		('email','Email')
    ]
	subject =  forms.CharField(required = True, max_length = 250)
	message =  forms.CharField(required = True, max_length = 2000, widget=forms.Textarea)
	method = forms.MultipleChoiceField(required = True, widget=forms.CheckboxSelectMultiple, choices = CHOICES)
	#def __init__(self, *args, **kw):
	#	super(BulkMessagingForm, self).__init__(*args, **kw)

	
	
	



	