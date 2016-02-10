from django import forms

class NewUtilityForm(forms.Form):
	identifier = forms.CharField(max_length=30)
	sector = forms.ModelChoiceField(queryset=None)
	lat = forms.DecimalField(required=False, min_value=-90, max_value=90)
	lon = forms.DecimalField(required=False, min_value=-180, max_value=180)
	fee_auto = forms.ChoiceField(choices=fee_auto_choices, required=False)
	fee_auto = forms.TypedChoiceField(choices=fee_auto_choices, widget = forms.HiddenInput(), coerce=bool)
	fee_type = forms.ModelChoiceField( widget = forms.HiddenInput(),
		queryset=ContentType.objects.filter(pk__in=[ct.pk for ct in get_fee_types()]))
	start_date = forms.DateField(widget=html5_widgets.DateInput)

	def __init__(self, *args, **kwargs):
		auto = district = None
		if 'auto' in kwargs:
			auto = kwargs.pop('auto')
		if 'district' in kwargs:
			district = kwargs.pop('district')
		super(NewUtilityForm, self).__init__(*args, **kwargs)

		if not auto:
			self.fields['amount'] = forms.FloatField(label='Fee Amount', min_value=0)

		if district:
			self.fields['sector'].queryset = Sector.objects.filter(district=district).order_by('name')


class CleaningFeeForm(forms.ModelForm, NewUtilityForm):
	class Meta:
		model = CleaningFee
		fields = ('identifier', 'sector', 'lat', 'lon', 'fee_auto', 'fee_cycle', 'start_date')