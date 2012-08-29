from django import forms
from auth.models import Group, User

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




    
    
    
    
    


