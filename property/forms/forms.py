from django import forms

class select_property_form(forms.Form):
    plotid = forms.IntegerField(required = False)
    streetno = forms.IntegerField(required = False)
    streetname = forms.CharField(required = False)
    suburb = forms.CharField(required = False)
    

class select_district_form(forms.Form):
    name = forms.CharField(required = True)
    superuser = forms.BooleanField(required = False)
    
class select_council_form(forms.Form):
    name = forms.CharField(required = True)
    superuser = forms.BooleanField(required = False)

class select_sector_form(forms.Form):
    id = forms.IntegerField(required = True)
    name = forms.CharField(required = False)
    