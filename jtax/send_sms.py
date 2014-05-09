from jtax.models import *
from common.util import CommonUtil
from jtax.shared_functions import *

def get_sms_receivers(tax_item):
	phone_list = []
	citizens = get_contact_citizens_for_tax_item(tax_item)
	if citizens:
		phone_list = get_contact_phones(citizens)
	return phone_list

"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# Functions on reminder sms for upcomming taxes or fees
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""

def get_reminder_sms_content(tax_item):
	description = get_tax_item_description(tax_item)
	content = 'You have an upcoming ' + description + ' due on ' + tax_item.due_date.strftime('%d/%m/%Y') + '. Please pay on time or fines will be applied.'	
	return content	
def generate_tax_reminder_sms(tax_item):
	sms_messages = []
	phone_list = get_sms_receivers(tax_item)
	content = get_reminder_sms_content(tax_item)
	for phone in phone_list:
		sms = {}
		sms['phone_number'] = phone
		sms['content'] = content
		sms_messages.append(sms)
	return sms_messages

def send_reminder_sms(tax_item):
	sms_messages = generate_tax_reminder_sms(tax_item)
	print sms_messages
	sms_sent_result = {}
	sms_sent_result['sms_sent'] = 0
	sms_sent_result['sms_failed'] = 0
	username = "Automate Email/SMS"
	for sms in sms_messages:
		log_message = ""		
		response = CommonUtil.sendSms(sms['content'],[sms['phone_number']])
		if response.find('ERROR') >= 0:
			sms_sent_result['sms_failed'] = sms_sent_result['sms_failed'] + 1
			log_message = "failed to send an upcoming tax reminder sms to " + sms['phone_number']
		else:
			sms_sent_result['sms_sent'] = sms_sent_result['sms_sent'] + 1
			log_message = "sent an upcoming tax reminder sms to " + sms['phone_number']
		log_dict = get_log_dict_for_tax_item(tax_item)
		LogMapper.createLogCommand(request=None,username=username, business=log_dict['business'],property=log_dict['property'],subbusiness=log_dict['subbusiness'],message=log_message)	
	return sms_sent_result

	
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""
# Functions on warning sms for due taxes or fees
"""""""""""""""""""""""""""""""""""""""""""""""""""""""""	
def get_warning_sms_content(tax_item):
	description = get_tax_item_description(tax_item)
	content = 'You have an overdue ' + description + ' due on ' + tax_item.due_date.strftime('%d/%m/%Y') + '. Please pay on time or fines will be applied.'	
	return content	
def generate_tax_warning_sms(tax_item):
	sms_messages = []
	phone_list = get_sms_receivers(tax_item)
	content = get_warning_sms_content(tax_item)
	for phone in phone_list:
		sms = {}
		sms['phone_number'] = phone
		sms['content'] = content
		sms_messages.append(sms)
	return sms_messages

def send_warning_sms(tax_item):
	sms_messages = generate_tax_warning_sms(tax_item)
	sms_sent_result = {}
	sms_sent_result['sms_sent'] = 0
	sms_sent_result['sms_failed'] = 0
	username = "Automate Email/SMS"
	for sms in sms_messages:
		log_message = ""
		response = CommonUtil.sendSms(sms['content'],[sms['phone_number']])
		if response.find('ERROR') >= 0:
			sms_sent_result['sms_failed'] = sms_sent_result['sms_failed'] + 1
			log_message = "failed to send an overdue tax reminder sms to " + sms['phone_number']
		else:
			sms_sent_result['sms_sent'] = sms_sent_result['sms_sent'] + 1
			log_message = "sent an overdue tax reminder sms to " + sms['phone_number']
		log_dict = get_log_dict_for_tax_item(tax_item)
		LogMapper.createLogCommand(request=None,username = username,business=log_dict['business'],property=log_dict['property'],subbusiness=log_dict['subbusiness'],message=log_message)	
	return sms_sent_result

	
	
	

	

