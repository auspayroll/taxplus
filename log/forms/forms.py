from django import forms

class LogSearchForm(forms.Form):
    """
    Search log by userid, plotid or transactionid
    """
    username = forms.CharField(max_length=50,required = True)
    plotid = forms.IntegerField(required = False)
    transactionid = forms.IntegerField(required = False)

class LogRefineSearchForm(forms.Form):
    """
    Search log by userid, plotid or transactionid
    """
    username = forms.CharField(max_length=50,required = True)
    plotid = forms.IntegerField(required = False)
    transactionid = forms.IntegerField(required = False)
    
    new_plotid = forms.IntegerField(required = False)
    new_transactionid = forms.IntegerField(required = False)
    new_citizenid = forms.IntegerField(required = False)
    