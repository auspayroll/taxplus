from django import forms

class select_property_form(forms.Form):
    plotid = forms.IntegerField(required = False)
    streetno = forms.IntegerField(required = False)
    streetname = forms.CharField(required = False)
    suburb = forms.CharField(required = False)