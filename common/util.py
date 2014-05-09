#put the common utililities here
from dev1 import variables
from django.core.mail import EmailMultiAlternatives

import urllib2
import psycopg2
import string
import random
from datetime import datetime
from django.core import mail
class CommonUtil:	

	"""
	Function to send email. To attach files put them in a list of dicts in the format: [{'name':'receipt.pdf','content':content,'mime':'application/pdf'},{...},...]
	"""

	@staticmethod
	def sendEmail(subject, content, html_content, to_list, from_list = variables.SUPPORT_EMAIL, attachments=None):
# 		connection = mail.get_connection()
# 		connection.open()
		try:
			#html_content = '<p>This is an <strong>important</strong> message.</p>'
			email = EmailMultiAlternatives(subject, content, from_list, [','.join(to_list)])
			email.attach_alternative(html_content, "text/html")
			if attachments:
				for i in attachments:
					email.attach(i['name'],i['content'],i['mime'])

			#if ','.join(to_list) == 'sandra@surroundpix.com.au' or ','.join(to_list) == 'peterd@surroundpix.com.au':
			#	email.send()
			email.send()
			#print ','.join(to_list) + " ====> " + html_content
			#email = EmailMessage(subject, content, from_email,[','.join(list)])
			#email.attach('receipt.pdf', content, 'application/pdf')
# 			email.send()
			return True
		except (ValueError, IndexError) as e:
			#self.emailErrors.append('Error sending email ' + tax_type + ' to ' + ValueError)
			print e
# 		finally:
# 			connection.close()
		
		return False

	@staticmethod
	def sendSms(content, to_list, from_list = variables.SUPPORT_PHONE):
		content = urllib2.quote(content)
		print content
		response = ''
		#message content need to be urlencoded
		url = "http://www.smsglobal.com/http-api.php?action=sendsms&user=" + variables.SMS_USER + "&password=" + variables.SMS_PW + "&from=" + from_list + "&to=" + ','.join(to_list) + "&text=" + content
		#if ','.join(to_list) == '610433777029' or ','.join(to_list) == '61420364232':
		#	response = urllib2.urlopen(url).read()
		response = urllib2.urlopen(url).read()

		return response
	
	@staticmethod
	def pg_utcnow():
		return datetime.utcnow().replace(
        		tzinfo=psycopg2.tz.FixedOffsetTimezone(offset=0, name=None))
		
	@staticmethod
	def passwd_generator(size=6, chars=string.ascii_lowercase + string.digits):
		re=random.choice(string.ascii_lowercase)
		for i in range(0,size-2):
			re+=random.choice(chars)
		re+=random.choice(string.digits)
		return re