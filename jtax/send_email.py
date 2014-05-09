from jtax.models import *
from property.models import *
from asset.models import *
from datetime import date
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from log.mappers.LogMapper import LogMapper
from common.util import CommonUtil
from django.core.mail import EmailMultiAlternatives
from jtax.shared_functions import *
from dev1.settings import domain_name


"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Get email list for a tax item
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def get_email_receivers(tax_item):
	to_list = []
	citizens = get_contact_citizens_for_tax_item(tax_item)
	if citizens:
		to_list = get_contact_emails(citizens)
	return to_list




"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# Functions on reminder email for upcomming taxes or fees
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
Get email content for a tax item

Information needed if applicable:
1.citizen name (including title)
2. P.O.BOX 
3. TIN (if applicable)
4. year of tax item i.e., 2013
5. Current date with format: dd/mm/yyyy
6. Province, district
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def generate_tax_reminder_emails(tax_item):
	
	# get province, district,tin, and contact citizens info from tax_item
	location_and_tin = get_location_and_tin_info(tax_item)
	citizens = get_contact_citizens_for_tax_item(tax_item)
	tax_type = get_tax_type_from_tax_item(tax_item)
	year_of_tax_due = tax_item.due_date.year
	today = date.today().strftime("%d/%m/%Y")
	tax_description = get_tax_item_description(tax_item)	

	emails = []
	if citizens:
		for citizen in citizens:
			if citizen.email:
				email = {}
				citizen.fullname = citizen.getDisplayName() 
				citizen.salutation = 'Ms./Mr.'
				if citizen.gender:
					if citizen.gender == 'Male':
						citizen.salutation = 'Mr.'
					elif citizen.gender == 'Female':
						citizen.salutation = 'Ms.'
				

				html_content = render_to_string('letters/reminder_notice.html', {"location_and_tin":location_and_tin, \
				"domain_name":domain_name,"tax_description":tax_description,"citizen":citizen, "tax_type":tax_type, "year_of_tax_due":year_of_tax_due, "today":today,})
				text_content = strip_tags(html_content)
				
				email['to'] = citizen.email
				email['html_content'] = html_content
				email['text_content'] = text_content
				emails.append(email)
	return emails

"""
["email_sent":2,"email_failure":2]
"""
def send_reminder_emails(tax_item):
	username = "Automate Email/SMS"
	email_subject = 'Upcoming Tax Reminder'
	emails = generate_tax_reminder_emails(tax_item)
	email_sent_result = {}
	email_sent_result['email_sent'] = 0
	email_sent_result['email_failed'] = 0

	for email in emails:
		log_message = ""
		if CommonUtil.sendEmail(email_subject, email['text_content'], email['html_content'], [email['to']]):
			log_message = "sent an upcoming tax reminder email to " + email['to']
			email_sent_result['email_sent'] = email_sent_result['email_sent'] + 1
		else:
			log_message = "failed to send an upcoming tax reminder email to " + email['to']
			email_sent_result['email_failed'] = email_sent_result['email_failed'] + 1
		log_dict = get_log_dict_for_tax_item(tax_item)
		LogMapper.createLogCommand(request=None,uername=username, business=log_dict['business'],property=log_dict['property'],subbusiness=log_dict['subbusiness'],message=log_message)
	return email_sent_result	



"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# Functions on warning email for upcomming taxes or fees
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
def generate_tax_warning_emails(tax_item):
	# get province, district,tin, and contact citizens info from tax_item	
	location_and_tin = get_location_and_tin_info(tax_item)
	citizens = get_contact_citizens_for_tax_item(tax_item)
	tax_type = get_tax_type_from_tax_item(tax_item)
	year_of_tax_due = tax_item.due_date.year
	today = date.today().strftime("%d/%m%y")
	current_month = date.today().strftime("%B")
	late_fee_detail = get_late_fee_details(tax_item)
	tax_description = get_tax_item_description(tax_item)
	
	print tax_item
	print tax_type

	warning_letter_template = "tax_warning_letter.html"
	if isinstance(tax_item, Fee):
		warning_letter_template = "fee_warning_letter.html"
	
	print warning_letter_template

	emails = []
	if citizens:
		for citizen in citizens:
			if citizen.email:
				email = {}
				citizen.fullname = citizen.getDisplayName() 
				citizen.salutation = 'Ms./Mr.'
				if citizen.gender:
					if citizen.gender == 'Male':
						citizen.salutation = 'Mr.'
					elif citizen.gender == 'Female':
						citizen.salutation = 'Ms.'
				
				html_content = render_to_string('letters/'+warning_letter_template, {"location_and_tin":location_and_tin, "late_fee_detail":late_fee_detail, \
					"domain_name":domain_name,"tax_description":tax_description,"citizen":citizen, "tax_type":tax_type, "year_of_tax_due":year_of_tax_due,"current_month":current_month, "today":today,})
				text_content = strip_tags(html_content)
				
				email['to'] = citizen.email
				email['html_content'] = html_content
				email['text_content'] = text_content
				emails.append(email)
	return emails
	
	
"""
["email_sent":2,"email_failure":2]
"""
def send_warning_emails(tax_item):
	email_subject = 'Overdue Tax Reminder'
	emails = generate_tax_warning_emails(tax_item)
	email_sent_result = {'email_sent':0,'email_failed':0}
	username = "Automate Email/SMS"
	for email in emails:		
		log_message = ""
		if CommonUtil.sendEmail(email_subject, email['text_content'], email['html_content'], [email['to']]):
			log_message = "sent an overdue tax reminder email to " + email['to']
			email_sent_result['email_sent'] = email_sent_result['email_sent'] + 1
		else:
			log_message = "failed to send an overdue tax reminder email to " + email['to']
			email_sent_result['email_failed'] = email_sent_result['email_failed'] + 1
		log_dict = get_log_dict_for_tax_item(tax_item)
		LogMapper.createLogCommand(request=None,username = username, business=log_dict['business'],property=log_dict['property'],subbusiness=log_dict['subbusiness'],message=log_message)
	return email_sent_result	




	