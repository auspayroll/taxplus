from django import forms
from dev1 import settings
from datetime import datetime

class BusinessFilterForm(forms.Form):
    filter_business_name = forms.CharField(min_length=1, max_length=50, required = False)
    filter_tin = forms.CharField(min_length=1, max_length=50, required = False)


class closeBusinessForm(forms.Form):
	close_date = forms.DateField(widget=forms.DateInput(format = settings.DATE_INPUT_FORMAT, attrs={'class' : 'date_picker'}), input_formats=settings.DATE_INPUT_FORMATS, help_text="dd/mm/yyyy", initial=datetime.now)
	file = forms.FileField(label="Attach Documentation")

