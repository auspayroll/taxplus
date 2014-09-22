from django.contrib.auth.models import User, check_password
from pmauth.models import PMUser

class CustomLoginBackend(object):
	def authenticate(self, username=None, password=None):
		try:
			user = User.objects.get(username=username)

		except User.DoesNotExist:
			try:
				pm_user = PMUser.find.get(email=username)

			except PMUser.DoesNotExist:
				try:
					pm_user = PMUser.find.get(username=username)
				except PMUser.DoesNotExist:
					return None
			else:
				user = User(username = pm_user.email)
				user.is_staff = True
				user.is_superuser = pm_user.superuser
				user.first_name  = pm_user.firstname
				user.last_name = pm_user.lastname
				user.is_active = True if pm_user.i_status == 'active' else False
				user.last_login = pm_user.lastlogin
				user.email = pm_user.email
				user.password = pm_user.password
				user.save()

		if user.check_password(password):
			return user

		else:
			return None


	def get_user(self, user_id):
		try:
			return User.objects.get(pk=user_id)

		except User.DoesNotExist:
			return None