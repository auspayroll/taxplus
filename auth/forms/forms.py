from django import forms
from auth.models import Group, User

class LoginForm(forms.Form):
    """
    In order to login, user needs to enter username and password
    Both of these two are required
    """
    username = forms.CharField(min_length=1, max_length=50, help_text='The username should not be empty', widget=forms.TextInput(attrs={'autocomplete':'off'}))
    password = forms.CharField(min_length=1, widget=forms.PasswordInput(attrs={'autocomplete':'off'}), help_text='The password should not be empty')

class select_group_form(forms.Form):
    """
    select group to change or delete
    """
    group_id = forms.ChoiceField()
    def __init__(self, *args, **kwargs):
        super(select_group_form, self).__init__(*args, **kwargs)
        self.fields['group_id'] = forms.ChoiceField(widget=forms.RadioSelect, choices=[ (o.id, o.name) for o in Group.objects.all() ])

class select_user_form(forms.Form):
    """
    select user by userid
    """
    user_id = forms.IntegerField()
                