from django.forms import ModelForm
from django import forms
from citizen.models import Citizen
from log.models import Log
from django.forms import model_to_dict
from log.mappers.LogMapper import LogMapper

class CitizenCreationForm(ModelForm):
    """
    Used for citizen registry
    Override the save method to integrate with log capability
    """
    class Meta:
        model = Citizen   
    def save(self, request, commit=True):
        citizen = forms.ModelForm.save(self, False)
        if commit:
            citizen.save()
            LogMapper.createLog(request,object=citizen,action="add", citizenid =  citizen.citizenid)            
        return citizen
     
class CitizenChangeForm(ModelForm):
    """
    Used to change citizen
    Override the save method to integrate with log capability
    """
    citizen_id = forms.IntegerField(required = False)
    citizenid = forms.IntegerField(required = True)
    class Meta:
        model = Citizen
        fields =("firstname","lastname")
    def save(self, request, commit=True):
        citizen_id = self.cleaned_data["citizen_id"]
        citizenid = self.cleaned_data["citizenid"]
        citizen = Citizen.objects.get(id = citizen_id)
        old_data = model_to_dict(citizen)
        citizen.citizenid = citizenid
        citizen.firstname = self.cleaned_data["firstname"]
        citizen.lastname = self.cleaned_data["lastname"]
        citizen.save()
        new_data = model_to_dict(citizen)
        Log.objects.createLog(request,object=citizen, old_data=old_data, new_data=new_data, action="change", citizenid = citizenid)            
        return citizen
        
 