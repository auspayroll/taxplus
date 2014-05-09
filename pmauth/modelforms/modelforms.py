from django.forms import ModelForm
from django import forms
from pmauth.models import PMUser, PMGroup, PMPermission, UserHistory
from log.mappers.LogMapper import LogMapper
from django.forms import model_to_dict
from django.conf import settings
import hashlib, ast, pytz, string, random
from datetime import datetime
from django.utils import timezone
from property.mappers.CouncilMapper import CouncilMapper
from django.forms import PasswordInput
from common.util import *
from django.contrib.auth.hashers import check_password, make_password
from django.core.exceptions import FieldError

def save_userhistory(email, password):
	userhistory=UserHistory.objects.filter(email=email)
	if userhistory:
		for uh in userhistory:
			if check_password(password, uh.password):
				raise FieldError('This password has already been used. Please select another one.')

	newrecord=UserHistory(email=email, password=make_password(password), timestamp=CommonUtil.pg_utcnow())
	newrecord.save()


class GroupCreationForm(ModelForm):
	"""
	The form is used for Group registry
	"""
	permissions_all = forms.ModelMultipleChoiceField(queryset = PMPermission.objects.all(), required=False, widget = forms.SelectMultiple(attrs = {'class':'group_creation_form_permission'}))
	permissions_selected = forms.ModelMultipleChoiceField(queryset = PMPermission.objects.all(), required=False, widget = forms.SelectMultiple(attrs = {'class':'group_creation_form_permission'}))
	class Meta:
		model = PMGroup
		fields = ("name","permissions",)

	def save(self, request, commit=True):
		"""
		The save method is override because the default one does not save the referencing permissions
		"""
		group = forms.ModelForm.save(self, False)
		if commit:
			group.save()
			group.permissions.clear()
			if self.cleaned_data['permissions_selected']:
				for per in self.cleaned_data['permissions_selected']:
					group.permissions.add(per)
			group.save()
			new_data = model_to_dict(group)
			LogMapper.createLog(request,object=group, new_data=model_to_dict(group), action="add")			
		return group
	
	
class GroupChangeForm(ModelForm):
	"""
	The form is used to chagne Group
	"""
	permissions_all = forms.ModelMultipleChoiceField(queryset = PMPermission.objects.all(), required=False, widget = forms.SelectMultiple(attrs = {'class':'group_creation_form_permission'}))
	permissions_selected = forms.ModelMultipleChoiceField(queryset = PMPermission.objects.all(), required=False, widget = forms.SelectMultiple(attrs = {'class':'group_creation_form_permission'}))
	group_id = forms.IntegerField()
	name = forms.CharField(required = False, max_length = 30)

	class Meta:
		model = PMGroup
		fields = ("permissions",)

	def save(self, request, commit=True):
		"""
		The save method is override because the default one does not save the referencing permissions
		"""
		group_id = self.cleaned_data["group_id"]
		group = PMGroup.objects.get(id = group_id)
		old_data = model_to_dict(group)
		group.name = self.cleaned_data["name"]
		if commit:
			group.save()
			group.permissions.clear()
			if self.cleaned_data['permissions_selected']: 
				for per in self.cleaned_data['permissions_selected']:
					group.permissions.add(per)
			group.save()
		new_data = model_to_dict(group)
		LogMapper.createLog(request,object=group, old_data=old_data, new_data=new_data, action="change")			
		return group


class UserChangeForm(ModelForm):
	"""
	Display user info in this form by default,
	Update user inof by saving this form
	"""
	class Meta:
		model = PMUser
		fields = ("firstname","lastname","password","contactnumber","superuser","groups","permissions","i_status") 
	new_password = forms.CharField(required=False,max_length=100)
	council = forms.ChoiceField(widget = forms.Select(),required = True, choices = [])
	user_id = forms.IntegerField()
	email = forms.CharField(required = True, max_length = 50)
	
	def __init__(self,*args, **kw):
		initial = kw.get('initial', {})
		if 'council' in initial and initial['council']:
			kw['initial']['council'] = initial['council'].id
		super(UserChangeForm, self).__init__(*args, **kw)
		councils = [(c.id, c.name) for c in CouncilMapper.getAllCouncils()]
		self.fields['council'] = forms.ChoiceField(widget = forms.Select(),required = True, choices = councils)
		self.fields['groups'] = forms.ModelMultipleChoiceField(queryset = PMGroup.objects.all(), required=False, widget = forms.SelectMultiple(attrs = {'size':6, 'class':'group_select_box'}))
		
	def save(self, request, commit=True):
		user_id = self.cleaned_data["user_id"]
		user = PMUser.objects.get(id = user_id)   
		old_data = model_to_dict(user)
		user.username = self.cleaned_data["firstname"] + self.cleaned_data["lastname"]
		user.firstname = self.cleaned_data["firstname"]
		user.lastname = self.cleaned_data["lastname"]
		user.email = self.cleaned_data["email"]
		user.password = self.cleaned_data["password"]
		

		user.contactnumber = self.cleaned_data["contactnumber"]
		user.superuser = self.cleaned_data["superuser"]
		user.council = CouncilMapper.getCouncilById(self.cleaned_data['council'])
		user.i_status = self.cleaned_data["i_status"]
		new_password = self.cleaned_data.get("new_password")
		if commit:
			if new_password:
				user.password =new_password.strip()	 
				save_userhistory(user.email, user.password)
			user.save()
			user.groups.clear()
			if self.cleaned_data['groups']:
				print "with group ..." 
				for group in self.cleaned_data['groups']:
					user.groups.add(group)
			else:
				print "no group ..."
			user.save()			
		user.datejoined = user.datejoined.astimezone(pytz.utc)
		new_data = model_to_dict(user)
		LogMapper.createLog(request,object=user, old_data=old_data, new_data=new_data, action="change")
		return user

class UserCreationForm(ModelForm):
	"""
	This form is used for user registry
	"""
	error_messages = {
		'empty': "Required.",
		'empty_username': "Required. Maximum 30 characters.",
		'duplicate_username': "A user with that username already exists.",
		'password_mismatch': "The two password fields didn't match.",
		
	}
	#username = forms.RegexField(label="Username", max_length=30,
	#	required = False,
	#	regex=r'^[\w.@+-]+$',
	#	help_text = "Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.",
	#	error_message = "Required. Maximum 30 characters.")
	#password1 = forms.CharField(label="Password",help_text = "Enter password.",
	#	widget=forms.PasswordInput)
	#password2 = forms.CharField(label="Password confirmation",
	#	widget=forms.PasswordInput,
	#	help_text = "Enter the same password as above, for verification.")
	password = forms.CharField(widget=PasswordInput())
	council = forms.ChoiceField(widget = forms.Select(),required = True, choices = [])
	#groups = forms.ModelMultipleChoiceField(queryset = Group.objects.all())
	#permissions_all = forms.ModelMultipleChoiceField(queryset = Permission.objects.all(), widget = forms.SelectMultiple(attrs = {'class':'user_creation_form_permission'}))
	#permissions_selected = forms.ModelMultipleChoiceField(queryset = Permission.objects.none(), widget = forms.SelectMultiple(attrs = {'class':'user_creation_form_permission'}))
	class Meta:
		model = PMUser
		fields = ("firstname","lastname","password","email","contactnumber")	
			
	def __init__(self, *args, **kwargs):
		super(UserCreationForm,self).__init__(*args,**kwargs)
		councils = [(c.id, c.name) for c in CouncilMapper.getAllCouncils()]
		self.fields['council'] = forms.ChoiceField(widget = forms.Select(),required = True, choices = councils)
		self.fields['groups'] = forms.ModelMultipleChoiceField(queryset = PMGroup.objects.all(), required=False, widget = forms.SelectMultiple(attrs = {'size':6, 'class':'group_select_box'}))

	#def clean_username(self):
	#	username = self.cleaned_data["username"]
	#	username = username.strip()
	#	try:
	#		User.objects.get(username=username)
	#	except User.DoesNotExist:
	#		return username
	#	raise forms.ValidationError(self.error_messages['duplicate_username'])

	def save(self,request, commit=True):
		user = forms.ModelForm.save(self, False)
		user.username = self.cleaned_data["firstname"] + self.cleaned_data["lastname"]
		user.email=self.cleaned_data["email"]
		user.council = CouncilMapper.getCouncilById(self.cleaned_data['council'])

		if self.cleaned_data['password'] and self.cleaned_data['password'] !='':
			user.password = str(self.cleaned_data['password']).strip()
		else:
			password_length = 8
			user.password="".join([random.choice(string.letters+string.digits) for x in range(1, password_length)])

		if commit:
			save_userhistory(user.email, user.password)
			user.save(user.password)
			user.groups.clear()
			if self.cleaned_data['groups']:
				for group in self.cleaned_data['groups']:
					user.groups.add(group)
			#for group in self.cleaned_data['groups']:
			#	user.groups.add(group)
			user.save()
			LogMapper.createLog(request,object=user,new_data=model_to_dict(user), action="add")
		return user
	