from taxplus.models import Sector, Business
from datetime import date
from dateutil.relativedelta import relativedelta
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.urlresolvers import reverse
from django.db.models import Q, Sum
from django.forms.models import modelformset_factory
from django.http import HttpResponse, Http404
from django.shortcuts import HttpResponseRedirect, render_to_response, get_object_or_404, redirect
from django.template.response import TemplateResponse
from collect.models import Epay, CollectionGroup, Collector, Epay, EpayBatch
from collect.forms import EpayForm, CollectionGroupForm, RegistrationForm, CollectorForm, BusinessForm
import csv
import json
from random import randint
from django.contrib.auth.models import User
from django.core.mail import send_mail
from djqscsv import render_to_csv_response



@login_required
def index(request):
	return TemplateResponse(request, 'crud/readme.html')
