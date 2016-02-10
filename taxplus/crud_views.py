#from property.models import District, Sector, Cell
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
from jtax.models import PayFee, Fee
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from taxplus.forms import PaymentForm, PayFeesForm, TitleForm, LogSearchForm, LogSearchFormExtended
from taxplus.forms import SearchForm, DebtorsForm, MergeBusinessForm, BusinessForm, BusinessFormRegion, \
	MessageBatchForm, PaymentSearchForm, CitizenUpdate, CitizenContact
from taxplus.management.commands.generate_invoices import generate_invoice
from taxplus.models import *
import csv
import json

@login_required
def index(request):
	return TemplateResponse(request, 'crud/home.html')