from django.forms import ModelForm
from django import forms
from citizen.models import Citizen, Status
from log.models import Log
from django.forms import model_to_dict
from log.mappers.LogMapper import LogMapper
from dev1.variables import gender_types, HorizontalRadioRenderer
from dev1 import settings
from admin.Common import Common
from datetime import datetime
import md5

class CitizenCreationForm(ModelForm):
	"""
	Used for citizen registry
	Override the save method to integrate with log capability
	"""
	class Meta:
		model = Citizen
		exclude = ('status','deactivate_reason','cp_password')
	#date_of_birth = forms.DateField(widget=forms.DateInput(format = settings.DATE_INPUT_FORMAT), input_formats=settings.DATE_INPUT_FORMATS, required=False)	
	year_of_birth = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:80px'}),required=False, choices=Common.getYearRange())
	day_of_birth = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:70px'}),required=False, choices=Common.getDayRange())
	month_of_birth = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:90px'}),required=False, choices = Common.getMonthRange())
	gender = forms.ChoiceField(widget = forms.RadioSelect(renderer=HorizontalRadioRenderer), choices=gender_types)
	
	
	
	
	def save(self, request, commit=True):
		citizen = forms.ModelForm.save(self, commit)
		if commit:
			citizen.status = Status.objects.get(pk=1)
			if self.cleaned_data['year_of_birth'] and self.cleaned_data['year_of_birth'] != '' and self.cleaned_data['day_of_birth'] and self.cleaned_data['day_of_birth'] != '' and self.cleaned_data['month_of_birth'] and self.cleaned_data['month_of_birth'] != '' :
				citizen.date_of_birth  = datetime.strptime(self.cleaned_data['year_of_birth']  + '-' + self.cleaned_data['month_of_birth']  + '-' + self.cleaned_data['day_of_birth'] ,'%Y-%m-%d')
		
			#set default cp_password 
			citizen.cp_password = md5.new(citizen.first_name.strip() + ' ' + citizen.last_name.strip()).hexdigest()

			citizen.save()
			LogMapper.createLog(request,object=citizen,action="add", citizen =  citizen)			
		return citizen




class CitizenChangeForm(ModelForm):
	"""
	Used to change citizen
	Override the save method to integrate with log capability
	"""
	class Meta:
		model = Citizen
		exclude = ('cp_password')

	obj_id = forms.IntegerField()
	#date_of_birth = forms.DateField(widget=forms.DateInput(format = settings.DATE_INPUT_FORMAT), input_formats=settings.DATE_INPUT_FORMATS, required=False)	
	year_of_birth = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:80px'}),required=False, choices=Common.getYearRange())
	day_of_birth = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:70px'}),required=False, choices=Common.getDayRange())
	month_of_birth = forms.ChoiceField(widget=forms.Select(attrs={'style':'width:90px'}),required=False, choices = Common.getMonthRange())
	contact_details_confirmed = forms.DateField(widget=forms.DateInput(format = settings.DATE_INPUT_FORMAT, attrs={'class' : 'date_picker'}), input_formats=settings.DATE_INPUT_FORMATS, help_text="dd/mm/yyyy", initial=datetime.now)

	def __init__(self, *args, **kwargs):
		model = kwargs['instance']
		if model.date_of_birth and kwargs.has_key('initial'):
			kwargs['initial']['day_of_birth'] = model.date_of_birth.day
			kwargs['initial']['month_of_birth'] = model.date_of_birth.month

		try:
			dynamic_choices = kwargs.pop('statuses')
		except KeyError:
			dynamic_choices = None
		super(CitizenChangeForm, self).__init__(*args, **kwargs)
		if dynamic_choices is not None:
			self.fields['status'] = ModelChoiceField(queryset = dynamic_choices)
	def save(self, request, commit = True):
		obj_id = self.cleaned_data['obj_id']
		old_citizen = Citizen.objects.get(pk = obj_id)
		old_data = model_to_dict(old_citizen)
		citizen = forms.ModelForm.save(self, False)

		if self.cleaned_data['year_of_birth'] and self.cleaned_data['year_of_birth'] != '' and self.cleaned_data['day_of_birth'] and self.cleaned_data['day_of_birth'] != '' and self.cleaned_data['month_of_birth'] and self.cleaned_data['month_of_birth'] != '' :
			citizen.date_of_birth = datetime.strptime(self.cleaned_data['year_of_birth']  + '-' + self.cleaned_data['month_of_birth']  + '-' + self.cleaned_data['day_of_birth'] ,'%Y-%m-%d')

		#do not allow modify of citizen status fields if user is not admin
		if not request.session.get('user').isAdmin():
			citizen.status = old_citizen.status
			citizen.deactivate_reason = old_citizen.deactivate_reason
			citizen.note = old_citizen.note

		citizen.save()
		LogMapper.createLog(request,object=citizen, citizen = citizen, old_data= old_data, new_data=model_to_dict(citizen), action="change")

		