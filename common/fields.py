from django import forms
from decimal import Decimal
from django.utils.safestring import mark_safe


class CurrencyInput(forms.TextInput):
	
	def render(self, name, value, attrs=None):
		default_attrs = { 'class':'currency' }
		if attrs:
			attrs.update(default_attrs)
		else:
			attrs = default_attrs
		if value:
			if isinstance(value, basestring):
				value = value.replace(',','')
			value = '{:,}'.format(Decimal(value))
		return super(CurrencyInput, self).render(name, value, attrs)


class CurrencyField(forms.DecimalField):
	
	def clean(self, value):
		if value:
			value = value.replace(',','')
		return super(CurrencyField, self).clean(value)

	def __init__(self, *args, **kwargs):
		if not kwargs.has_key('widget'):
			widget = CurrencyInput()
			return super(CurrencyField, self).__init__(*args, widget=widget, **kwargs)
		else:
			return super(CurrencyField, self).__init__(*args, **kwargs)