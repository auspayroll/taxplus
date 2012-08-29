from django.forms import ModelForm
from django import forms
from auth.models import User, Group, Permission
from log.models import Log
import string
import random
from django.forms import model_to_dict
import pytz
from django.conf import settings
import md5

class GroupCreationForm(ModelForm):
    """
    The form is used for Group registry
    """
    permissions_all = forms.ModelMultipleChoiceField(queryset = Permission.objects.all(), required=False, widget = forms.SelectMultiple(attrs = {'class':'group_creation_form_permission'}))
    permissions_selected = forms.ModelMultipleChoiceField(queryset = Permission.objects.all(), required=False, widget = forms.SelectMultiple(attrs = {'class':'group_creation_form_permission'}))
    class Meta:
        model = Group
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
            Log.objects.createLog(request.session.get('user'),group, None, None,"add")            
        return group
    
    
class GroupChangeForm(ModelForm):
    """
    The form is used to chagne Group
    """
    permissions_all = forms.ModelMultipleChoiceField(queryset = Permission.objects.all(), required=False, widget = forms.SelectMultiple(attrs = {'class':'group_creation_form_permission'}))
    permissions_selected = forms.ModelMultipleChoiceField(queryset = Permission.objects.all(), required=False, widget = forms.SelectMultiple(attrs = {'class':'group_creation_form_permission'}))
    group_id = forms.IntegerField()
    name = forms.CharField(required = False, max_length = 30)
    class Meta:
        model = Group
        fields = ("permissions",)
    def save(self, request, commit=True):
        """
        The save method is override because the default one does not save the referencing permissions
        """
        group_id = self.cleaned_data["group_id"]
        group = Group.objects.get(id = group_id)
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
        Log.objects.createLog(request.session.get('user'),group, old_data, new_data, "change")            
        return group


class UserChangeForm(ModelForm):
    """
    Display user info in this form by default,
    Update user inof by saving this form
    """
    class Meta:
        model = User
        fields = ("firstname","lastname","contactnumber","active","superuser","datejoined","groups","permissions",) 
    password = forms.CharField(label="Password",help_text = "Enter password.", widget=forms.PasswordInput)
    permissions_selected = forms.ModelMultipleChoiceField(queryset = Permission.objects.all(), required=False, widget = forms.SelectMultiple(attrs = {'class':'user_change_form_permissions'}))
    groups_selected = forms.ModelMultipleChoiceField(queryset = Group.objects.all(), required=False, widget = forms.SelectMultiple(attrs = {'class':'user_change_form_groups'}))
    user_id = forms.IntegerField()
    email = forms.CharField(required = True, max_length = 50)
    def save(self, request, commit=True):
        user_id = self.cleaned_data["user_id"]
        user = User.objects.get(id = user_id)   
        old_data = model_to_dict(user)
        user.username = self.cleaned_data["firstname"] + self.cleaned_data["lastname"]
        user.firstname = self.cleaned_data["firstname"]
        user.lastname = self.cleaned_data["lastname"]
        user.email = self.cleaned_data["email"]
        user.password = self.cleaned_data["password"]
        password = user.password
        user.contactnumber = self.cleaned_data["contactnumber"]
        user.superuser = self.cleaned_data["superuser"]
        user.active = self.cleaned_data["active"]
        user.datejoined = self.cleaned_data["datejoined"]
        if commit:
            user.save()
            user.permissions.clear()
            if self.cleaned_data['permissions_selected']: 
                for per in self.cleaned_data['permissions_selected']:
                    user.permissions.add(per)
            user.groups.clear()
            if self.cleaned_data['groups_selected']: 
                for group in self.cleaned_data['groups_selected']:
                    user.groups.add(group)
            user.save()            
        new_data = model_to_dict(user)
        Log.objects.createLog(request.session.get('user'),user, old_data, new_data,"change")
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
    #    required = False,
    #    regex=r'^[\w.@+-]+$',
    #    help_text = "Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.",
    #    error_message = "Required. Maximum 30 characters.")
    #password1 = forms.CharField(label="Password",help_text = "Enter password.",
    #    widget=forms.PasswordInput)
    #password2 = forms.CharField(label="Password confirmation",
    #    widget=forms.PasswordInput,
    #    help_text = "Enter the same password as above, for verification.")
    groups = forms.ModelChoiceField(queryset = Group.objects.all(), required = False, empty_label='')
    #groups = forms.ModelMultipleChoiceField(queryset = Group.objects.all())
    #permissions_all = forms.ModelMultipleChoiceField(queryset = Permission.objects.all(), widget = forms.SelectMultiple(attrs = {'class':'user_creation_form_permission'}))
    #permissions_selected = forms.ModelMultipleChoiceField(queryset = Permission.objects.none(), widget = forms.SelectMultiple(attrs = {'class':'user_creation_form_permission'}))
    class Meta:
        model = User
        fields = ("firstname","lastname","email","contactnumber")    
            
    #def clean_username(self):
    #    username = self.cleaned_data["username"]
    #    username = username.strip()
    #    try:
    #        User.objects.get(username=username)
    #    except User.DoesNotExist:
    #        return username
    #    raise forms.ValidationError(self.error_messages['duplicate_username'])

    def save(self,request, commit=True):
        user = forms.ModelForm.save(self, False)
        user.username = self.cleaned_data["firstname"] + self.cleaned_data["lastname"]
        password_length = 8
        user.password="".join([random.choice(string.letters+string.digits) for x in range(1, password_length)])

        if commit:
            user.save(user.password)
            user.groups.clear()
            if self.cleaned_data['groups']:
                user.groups.add(self.cleaned_data['groups'])
            #for group in self.cleaned_data['groups']:
            #    user.groups.add(group)
            user.save()
            Log.objects.createLog(request.session.get('user'),user, None, None,"add")
        return user
    