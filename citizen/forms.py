from django import forms

class select_citizen_form(forms.Form):
    citizen_id = forms.IntegerField()