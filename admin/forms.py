from django import forms

class LoginForm(forms.Form):
    """
    In order to login, user needs to enter username and password
    Both of these two are required
    """
    username = forms.CharField(min_length=1, max_length=50, help_text='The username should not be empty', widget=forms.TextInput(attrs={'autocomplete':'off'}))
    password = forms.CharField(min_length=1, widget=forms.PasswordInput(attrs={'autocomplete':'off'}), help_text='The password should not be empty')

                