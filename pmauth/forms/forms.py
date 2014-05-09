from django import forms
from pmauth.models import *
from property.models import Council, District, Sector, Province
from dev1 import variables
from common.validator import *


class LoginForm(forms.Form):
	"""
	In order to login, user needs to enter username and password
	Both of these two are required
	"""
	username = forms.CharField(min_length=1, max_length=50, help_text='The username should not be empty', widget=forms.TextInput(attrs={'autocomplete':'off'}))
	password = forms.CharField(min_length=1, widget=forms.PasswordInput(attrs={'autocomplete':'off'}), help_text='The password should not be empty')

	def __init__(self, *args, **kwargs):
		super(LoginForm, self).__init__(*args, **kwargs)
# 		self.fields["username"].validators.append(validate_user)
		self.fields["password"].validators.append(validate_passwd)

class GroupCreationForm(forms.Form):
	provinces = forms.CharField(max_length="500", required = False)
	districts = forms.CharField(max_length="500", required = False)
	sectors = forms.CharField(max_length="500", required = False)
	action_choices = [('','----------')]
	
	actions = forms.SelectMultiple( choices = action_choices, attrs = {'class':'group_creation_form'})

	def __init__(self, *args, **kwargs):
		super(GroupCreationForm, self).__init__(*args, **kwargs)
		action_choices_more = Action.objects.all()
		if action_choices_more:
			action_choices.extend((o.id, o.name) for o in action_choices_more)

class LocationForm(forms.Form):
	"""
	The location where the permissions are restricted within.
	"""
	province = forms.ChoiceField(required = False)
	
	district_choices = [('','----------')]
	district = forms.ChoiceField(required = False, choices = district_choices)

	sector_choices = [('','----------')]
	sector = forms.ChoiceField(required = False, choices = sector_choices)

	def __init__(self, *args, **kwargs):
		super(LocationForm,self).__init__(*args, **kwargs)
		province_choices = [('','----------')]
		province_choices_more = Province.objects.all()
		if province_choices_more:
			province_choices.extend((o.id, o.name) for o in Province.objects.all())
		self.fields['province'] = province_choices

	def clean(self):
		super(LocationForm,self).clean()
		if 'province' in self._errors:
			del self.errors['province']
			self.cleaned_data['province'] = self.data['province']
		if 'district' in self._errors:
			del self.errors['district']
			self.cleaned_data['district'] = self.data['district']
		if 'sector' in self._errors:
			del self.errors['sector']
			self.cleaned_data['sector'] = self.data['sector']
		return self.cleaned_data


# class LoginForm(forms.Form):
# 	"""
# 	In order to login, user needs to enter username and password
# 	Both of these two are required
# 	"""
# 	username = forms.CharField(min_length=1, max_length=50, help_text='The username should not be empty', widget=forms.TextInput(attrs={'autocomplete':'off'}))
# 	password = forms.CharField(min_length=1, widget=forms.PasswordInput(attrs={'autocomplete':'off'}), help_text='The password should not be empty')

class select_group_form(forms.Form):
	"""
	select group to change or delete
	"""
	group_id = forms.ChoiceField()
	def __init__(self, *args, **kwargs):
		super(select_group_form, self).__init__(*args, **kwargs)
		self.fields['group_id'] = forms.ChoiceField(widget=forms.RadioSelect, choices=[ (o.id, o.name) for o in PMGroup.objects.all() ])

class select_user_form(forms.Form):
	"""
	select user by userid
	"""
	user_id = forms.IntegerField()
				
class UserFilterForm(forms.Form):

	filter_username = forms.CharField(min_length=1, max_length=50, required = False)
	filter_firstname = forms.CharField(min_length=1, max_length=50, required = False)
	filter_lastname = forms.CharField(min_length=1, max_length=50, required = False)
	filter_email = forms.CharField(min_length=1, max_length=50, required = False)
	filter_council_id = forms.ModelChoiceField(queryset=None, empty_label="----------", required = False)
	status_choices = [('','----------'), ('active','Active'),('inactive','Inactive')]
	filter_i_status = forms.CharField(required = False, widget=forms.Select(choices=status_choices))

	def __init__(self, *args, **kwargs):
		super(UserFilterForm, self).__init__(*args, **kwargs)
		self.fields['filter_council_id'].queryset = Council.objects.all()
	
	
class GroupFilterForm(forms.Form): 
	name = forms.CharField(max_length=50, required = False)
	i_status = forms.CharField(required = False, widget=forms.Select(choices=variables.status_choices))
