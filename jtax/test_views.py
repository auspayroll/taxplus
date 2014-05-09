from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext

from django import forms
from dev1.variables import *
from property.models import Sector, Cell, District
from django.forms.widgets import RadioSelect
from dev1 import settings
from dev1 import variables
from asset.models import *
from admin.Common import Common
from jtax.models import *
from jtax.mappers.TaxMapper import TaxMapper
from jtax.mappers.DeclaredValueMapper import DeclaredValueMapper
from dev1 import ThreadLocal
from jtax.forms.forms import * 
from jtax.modelforms.modelforms import *
from property.forms.forms import *
from property.modelforms.modelforms import *
from pmauth.forms.forms import *
from pmauth.modelforms.modelforms import *
from property.forms.forms import *
from property.modelforms.modelforms import *
from citizen.forms.forms import *
from citizen.modelforms.modelforms import *
from asset.forms.forms import *
from asset.modelforms.modelforms import *
from contact.forms.forms import *
from contact.modelforms.modelforms import *
from report.forms.forms import *

def test1(request):
	form = ReportSearchForm(request)
	return render_to_response('blank.html', {'form':form })