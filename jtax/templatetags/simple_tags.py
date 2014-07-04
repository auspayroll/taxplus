from django import template
from decimal import Decimal
register = template.Library()
from django.forms import Form
import re

def lookup(object, property, property2=None):
	attribute = None
	try:
		attribute = object[property]
	except:
		try:
			attribute = getattr(object, property)
		except:
			pass


	if property2 and attribute:
		try:
			attribute = attribute[property2]
		except:
			try:
				attribute = getattr(attribute, property2)
			except:
				pass

	return attribute

def lookup_filter(value, arg):
	return lookup(value, arg)

def chunks(value):
	return '-'.join(re.findall('...?', value))

def currency(value):
	if value:
		try:
			return '{:,}'.format(Decimal(value))
		except:
			return value
	else:
		return value

register.filter('currency', currency)
register.filter('chunks', chunks)
register.filter('lookup', lookup_filter)
register.simple_tag(lookup)