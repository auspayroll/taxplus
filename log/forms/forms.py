from django import forms
from dev1 import settings

class LogSearchForm(forms.Form):
	"""
	Search log by userid, plotid or transactionid
	"""
	username = forms.CharField(max_length=50,required = False,label="Staff")
	upi = forms.CharField(required = False)
	#plot_id = forms.CharField(required = False)
	citizen_id = forms.CharField(required = False)
	period_from = forms.DateTimeField(required = False,initial='', input_formats=settings.DATE_INPUT_FORMATS)
	period_to = forms.DateTimeField(required = False,initial='', input_formats=settings.DATE_INPUT_FORMATS)
	message = forms.CharField(max_length=350,required = False,widget = forms.TextInput(attrs={'size': 150,}))
	business = forms.CharField(max_length=50,required = False,label="Staff")
	tin = forms.CharField(max_length=50,required = False,label="Staff")
