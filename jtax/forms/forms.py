from django import forms

class tax_search_property_form(forms.Form):
    citizenid = forms.IntegerField(required = False)
    plotid = forms.IntegerField(required = False)
    streetno = forms.IntegerField(required = False)
    streetname = forms.CharField(required = False)
    suburb = forms.CharField(required = False)