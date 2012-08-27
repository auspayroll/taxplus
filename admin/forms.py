from django import forms

class LoginForm(forms.Form):
    username = forms.CharField(min_length=1, max_length=50, help_text='The username should not be empty', widget=forms.TextInput(attrs={'autocomplete':'off'}))
    password = forms.CharField(min_length=1, widget=forms.PasswordInput(attrs={'autocomplete':'off'}), help_text='The password should not be empty')

class LogSearchForm(forms.Form):
    userid = forms.IntegerField(required = True)
    plotid = forms.IntegerField(required = False)
    transactionid = forms.IntegerField(required = False)                