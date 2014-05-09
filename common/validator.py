from django.core.exceptions import ValidationError
import string


# validators

def validate_passwd(value):
	number=False
	letter=False
	return True
# 	print '----------------'
	if(len(value)<4):
		msg="The password must be a minimun 6 characters"
		raise ValidationError(msg)
	for i in string.digits:
		if i in value:
			number =True
			break
	for i in string.letters:
		if i in value:
			letter=True
			break
# 	if(not number):
# 		msg="The password at least contain a number character"
# 		raise ValidationError(msg)
# 	if(not letter):
# 		msg="The password at least contain an alpha character"
# 		raise ValidationError(msg)
	
# def validate_user(user):
	