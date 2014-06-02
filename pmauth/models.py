from django.db import models
from django.db.models import Q
from django.utils import timezone
from admin.ListCompare import ListCompare
from datetime import datetime
from dev1 import variables
from property.models import Province, District, Sector, Council
from admin.Common import Common
from dev1 import ThreadLocal
from common.validator import *
from common.util import *
import hashlib
from datetime import datetime, timedelta
from django.conf import settings
from django.core.exceptions import ValidationError
FLB_MAX_FAILURES = int( getattr( settings, 'FLB_MAX_FAILURES', 3 ) )
FLB_BLOCK_INTERVAL = int( getattr( settings, 'FLB_BLOCK_INTERVAL', 30 ) )
USER_STATUS='active'
##############################################################################################	
# Module
############################################################################################## 

class PMModule(models.Model):
	name = models.CharField(max_length = 50, help_text = 'Module name')
	image = models.ImageField(upload_to='module_images')
	icon_weight = models.IntegerField()
	description = models.CharField(max_length = 200, blank=True, help_text = 'Module description')

	class Meta:
		app_label  = 'pmauth'
		db_table = 'auth_pmmodule'

	def getDisplayName(self):
		return self.name

	def __unicode__(self):
		return self.name
	
	@staticmethod
	def get_module_by_name(self, name):
		module = PMModule.objects.filter(name__iexact = name)
		if not module:
			return None
		else:
			return module[0]
		
	def get_access_link(self):
		if self.name=='report':
			return settings.REPORTS_LINK
		else:
			return '/admin/' + self.name + '/'
	
##############################################################################################	
# ContentType
##############################################################################################		
class PMContentType(models.Model):
	name = models.CharField(max_length = 50, help_text = 'Content type name')
	image = models.ImageField(upload_to='content_type_images')
	model_name = models.CharField(max_length = 50, help_text = 'Model name')
	module = models.ForeignKey(PMModule)

	class Meta:
		app_label  = 'pmauth'
		db_table = 'auth_pmcontenttype'
		ordering = ['name']
	def __unicode__(self):
		return self.name

	def getDisplayName(self):
		return self.name

	def getModuel(self):
		return self.module

	def get_access_link(self):
		if self.name=='report':
			return settings.REPORTS_LINK
		else:
			return '/admin/' + self.module.name + '/' + self.name + '/'
 
	@staticmethod
	def getContentTypeByName(module_name,content_type_name):
		content_types = PMContentType.objects.filter(name__iexact = content_type_name, module__name__iexact = module_name)
		if not content_types:
			return None
		else:
			return content_types[0]
	
	@staticmethod
	def getContentTypeById(id):
		return Common.get_object_or_none(PMContentType, id = id)
		

class ActionManager(models.Manager):
	def get_query_set(self):
		user = ThreadLocal.get_current_user()
		if not user:
			return super(ActionManager,self).get_query_set().none()
		if user.superuser:
			return super(ActionManager,self).get_query_set().all().order_by('contenttype__id')
		else:
			return super(ActionManager,self).get_query_set().filter(permission__in = user.getPermissions())

class Action(models.Model):
	name = models.CharField(max_length = 50, help_text = 'The name of the permission shown to users')
	codename = models.CharField(max_length = 50, help_text = 'The name of the permission used in code')
	contenttype = models.ForeignKey(PMContentType)
	objects = ActionManager()
	find = models.Manager()
	
	class Meta:
		app_label  = 'pmauth'
		db_table = 'auth_action'
	def __unicode__(self):
		return self.name
	def get_access_link(self):
		if self.name=='report':
			return settings.REPORTS_LINK
		else:
			return '/admin/' + self.contenttype.module.name + '/' + self.contenttype.name + '/' + self.codename + '/'
	def getDisplayName(self):
		if self.name[:4]=='Can ':
			return str(self.name[4:]).capitalize()
		else:
			return str(self.name).capitalize()
	
##############################################################################################	
# old permission
##############################################################################################  
"""
class PMPermission(models.Model):
	name = models.CharField(max_length = 50, help_text = 'The name of the permission shown to users')
	codename = models.CharField(max_length = 50, help_text = 'The name of the permission used in code')
	contenttype = models.ForeignKey(PMContentType)
	class Meta:
		app_label  = 'pmauth'
		db_table = 'auth_pmpermission'
	def __unicode__(self):
		return self.name
	def get_access_link(self):
		return '/admin/' + self.contenttype.module.name + '/' + self.contenttype.name + '/' + self.codename + '/'
"""
	
##############################################################################################	
# new permission
##############################################################################################  
class PMPermissionManager(models.Manager):
	def get_query_set(self, *args, **kwargs):
		user = ThreadLocal.get_current_user()
		if user:
			if user.superuser:
				return super(PMPermissionManager,self).get_query_set()
			else:
				return super(PMPermissionManager,self).get_query_set().filter(Q(user = user)|Q(group__in = user.groups.all()))
		else:
			return super(PMPermissionManager,self).get_query_set().none()


class PMPermission(models.Model):
	name = models.CharField(max_length=80, unique=True, null=True)
	actions = models.ManyToManyField(Action, verbose_name='actions', related_name = 'permission',  null=True, blank=True, help_text = "The action this permission allows.")
	province = models.ForeignKey(Province,null=True, blank=True,  related_name = 'permission',  help_text = "The province this permission is restricted in.")
	district = models.ForeignKey(District, null=True, blank=True,  related_name = 'permission',  help_text = "The district this permission is restricted in.")
	sector = models.ForeignKey(Sector, null=True, blank=True,  related_name = 'permission',  help_text = "The sector this permission is restricted in.")
	
	from common.models import TaxType
	tax_types = models.ManyToManyField(TaxType, related_name='permission', blank=True)

	objects = PMPermissionManager()
	find = models.Manager()

	def __unicode__(self):
		if self.name: 
			return self.name
		else:
			return "ID:%s unnamed permissons" % self.id

	class Meta:
		app_label  = 'pmauth'
		db_table = 'auth_pmpermission'
	
	# cascade delete to clean up 
	def delete(self):
		self.actions.all().delete()
		self.tax_types.all().delete()
		super(PMPermission, self).delete()
		
##############################################################################################	
# Group
############################################################################################## 
class PMGroupManager(models.Manager):
	def get_query_set(self):
		user = ThreadLocal.get_current_user()
		if user:
			if user.superuser:
				return super(PMGroupManager, self).get_query_set()
			else:
				return super(PMGroupManager, self).get_query_set().filter(user = user)
		else:
			return super(PMGroupManager, self).get_query_set().none()

class PMGroup(models.Model):
	name = models.CharField(max_length=80, unique=True)
	permissions= models.ManyToManyField(PMPermission, verbose_name='permissions', related_name='group',  blank=True)
	i_status = models.CharField(max_length=10, choices=variables.status_choices, default="active", blank = True)
	
	objects = PMGroupManager()
	
	class Meta:
		verbose_name ='group'
		ordering = ['name']
		app_label  = 'pmauth'
		db_table = 'auth_pmgroup'
		verbose_name_plural ='groups'
	
	def __unicode__(self):
		return self.name

	def getContentTypes(self):
		if not self.permissions or len(self.permissions) == 0:
			return None
		else:
			contenttype_id_arr = []
			for permission in self.permissions.all():
				contenttype_ids = permission.actions.all().values('contenttype_id').distinct()
				contenttype_ids = Common.get_value_list(contenttype_ids,'contenttype_id')
				contenttype_id_arr = contenttype_id_arr + list(set(contenttype_ids)-set(contenttype_id_arr))
			if contenttype_id_arr and len(contenttype_id_arr) >0:
				contenttypes = PMContentType.objects.filter(id__in = contenttype_id_arr)
				if not contenttypes or len(contenttypes) == 0 :
					return None
				else:
					return contenttypes
	def getModules(self):
		content_types = self.getContentTypes()
		if content_types:
			modules = []
			for content_type in content_types:
				if content_type.module not in modules:
					modules.append(content_type.module)	
			if len(modules) == 0:
				 return None
			else:
				return modules
	
	def save(self, *args, **kwargs):
		"""
		The status of a group is set to "active" by default
		"""
		if not self.i_status:
			self.i_status = 'active'
		models.Model.save(self)
 
	def getLogMessage(self,old_data=None,new_data=None,action=None):
		"""
		return tailored log message for different actions taken on this group
		"""
		if action == "view":
			return "view Group [" + self.__unicode__() + "]"
		if action == "delete":
			return "delete Group [" + self.__unicode__() + "]"
		if action == "deactivate":
			return "deactivate Group [" + self.__unicode__() + "]"
		if action == "activate":	
			return "activate Group [" + self.__unicode__() + "]"
		if action == "add":
			return "add Group [" + self.__unicode__() + "]"
		if action == "change":
			message=""
			count = 0
			for key, value in old_data.iteritems():
				if old_data[key] != new_data[key]:
					if count != 0:
						message = message + ","
					count = count + 1
					if type(value) is not list:
						message = message + " change "+key + " from '"+ str(value) + "' to '"+str(new_data[key])+"'"
					else:
						extraFields = ListCompare.getExtraItems(old_data[key], new_data[key])
						lessFields = ListCompare.getLessItems(old_data[key], new_data[key])
						if key == "permissions":
							extraFields_display = []
							lessFields_display = []
							for permission_id in extraFields:
								extraFields_display.append(str(PMPermission.objects.get(id=permission_id).name))
							for permission_id in lessFields:
								lessFields_display.append(str(PMPermission.objects.get(id=permission_id).name))
							comma_needed = True
							if len(extraFields_display) > 0:
								message = message + " remove permissions " +  str(extraFields_display)
								comma_needed = True
							if len(lessFields_display) > 0:
								if comma_needed:
									message = message + ','
								message = message + " add permissions " +  str(lessFields_display)
			if message == "":
				message = "No change made"
			message = message + " on Group [" + self.__unicode__() + "]"
			return message
	
##############################################################################################	
# User
##############################################################################################					

class PMUserManager(models.Manager):
	def get_query_set(self):
		user = ThreadLocal.get_current_user()
		if user:
			if user.superuser:
				return super(PMUserManager, self).get_query_set().all()
			else:
				groups = PMGroup.objects.all()
				return super(PMUserManager, self).get_query_set().filter(groups__in = groups)
		else:
			return super(PMUserManager, self).get_query_set().none()
		
class PMUser(models.Model):
	id=models.AutoField(unique=True, primary_key=True)
	username = models.CharField(max_length=30, help_text='Required. Maximum 30 characters.')
	firstname = models.CharField(max_length=30, help_text='Enter first name.')
	lastname = models.CharField(max_length=30, help_text='Enter last name.')
	contactnumber = models.CharField(max_length=30, blank=True, help_text='Telephone number or mobile number.')
	email = models.EmailField(unique=True,help_text='Enter email address.')
	password = models.CharField(max_length=128, help_text='Enter password.', validators=[validate_passwd])
	superuser = models.BooleanField(default=False,help_text='Designates that this user has all permissions without explicitly assigning them.')
	lastlogin = models.DateTimeField(default=timezone.now, help_text='last login')
	council = models.ForeignKey(Council, null=True, blank=True, help_text="Council the sector belongs to.")
	datejoined = models.DateTimeField(default=timezone.now, help_text='date joined')
	groups = models.ManyToManyField(PMGroup, related_name='user', verbose_name='groups', \
	blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.')
	permissions = models.ManyToManyField(PMPermission, verbose_name='user permissions', related_name = 'user', blank=True,help_text='Specific permissions for this user.')
	active = models.BooleanField(default="active", blank = True)
	i_status = models.CharField(max_length= 10, choices=variables.status_choices, default="active", blank = True, help_text='Designates whether this user should be treated as active.') 
# 	USERNAME_FIELD = 'username'
	
	objects = PMUserManager()
	find = models.Manager()
	objects1 = find
 	USERNAME_FIELD='email'
 	REQUIRED_FIELDS = []
	
	class Meta:
# 		app_label  = 'pmauth'
		verbose_name = 'user'
		verbose_name_plural = 'users'
		db_table = 'auth_pmuser'

	def __unicode__(self):
		return self.username

	@staticmethod
	def getUserById(id):
		user = PMUser.objects.filter(id = id)
		if len(user) == 0:
			return None
		else:
			return user[0]
	
	@staticmethod
	def getUserByUserName(username):
		user = PMUser.objects.filter(username__iexact = username)
		if len(user) == 0:
			user = None
		else:
			user = user[0]
		return user
	
	@staticmethod
	def getActiveUsers():
		return PMUser.objects.filter(i_status = 'active')
	
	@staticmethod
	def getInactiveUsers():
		return PMUser.objects.filter(i_status = 'inactive')
	
	@staticmethod
	def getUserByEmailAndPassword(email, password):
		user = PMUser.objects1.filter(email  = email, password = hashlib.md5(password).hexdigest(), i_status = USER_STATUS)
		if len(user) == 0:
			return None
		else:
			return user[0]
	
	@staticmethod
	def getUserByEmail(email):
		user = PMUser.objects1.filter(email  = email,i_status = USER_STATUS)
		if len(user) == 0:
			return None
		else:
			return user[0]
		
	@classmethod
	def validateUser(cls, user):
		if user is not None:
			user=cls.objects.filter(email  = user.email, password = user.password)
			if len(user)==0:
				return False
			else:
				return True
		else:
			return False

	def getFullName(self):
		return self.firstname.capitalize() + " " + self.lastname.capitalize()
	
	def getDisplayName(self):
		return self.username
	
	def getGroupPermissions(self):
		return PMPermission.objects.filter(group__in = self.groups.all())
	
	def getCustomPermissions(self):
		return PMPermission.objects.filter(user = self)
	
	def getPermissions(self):
		if self.superuser:
			return PMPermission.objects.all()
		else:
			return PMPermission.objects.filter(Q(user = self)|Q(group__in = self.groups.all()))

	def getTaxTypes(self):
		from common.models import TaxType
		if self.superuser:
			return TaxType.objects.all()
		else:
			return TaxType.objects.filter(permission__in = self.getPermissions()).distinct()
	
	def has_tax_type(self, tax_type):
		if self.superuser:
			return True
		else:
			tax_types = self.getTaxTypes()
			if tax_types:
				return tax_type in tax_types
	
	def has_tax_type_by_name(self,name):
		from common.models import TaxType
		tax_type = TaxType.objects.filter(codename__iexact = name)
		if not tax_type:
			return False
		else:
			return self.has_tax_type(tax_type[0])
	
	def getActions(self):
		if self.superuser:
			return Action.objects.select_related('contenttype','contenttype__module').all()
		else:
			return Action.objects.select_related('contenttype','contenttype__module').filter(permission__in = self.getPermissions())
	
	def getActionsByContentType(self, content_type):
		if self.superuser:
			return Action.objects.select_related('contenttype','contenttype__module').filter(contenttype = content_type)
		else:
			return Action.objects.select_related('contenttype','contenttype__module').filter(permission__in = self.getPermissions(),contenttype = content_type).distinct()
		

	def getActionsByContentTypeWithLink(self, content_type):
		actions = self.getActionsByContentType(content_type)
		if not actions:
			return None
		else:
			for action in actions:
				action.access_link = action.get_access_link()
				action.display_name = action.getDisplayName()
			return actions
	
	def has_action_by_name(self, module_name, content_type_name, action_name):
		module = Action.objects.filter(codename__iexact = action_name, contenttype__name__iexact = content_type_name, contenttype__module__name__iexact = module_name)
		if not module:
			return False
		else:
			return True
	
	def has_action(self, action):
		actions = Action.objects.filter(permission__in = self.getPermissions())
		if not actions:
			return None
		else:
			return (action in actions)
		
	def getGroups(self):
		return self.groups.filter(i_status = 'active')
	
	def has_group(self, group):
		if not self.groups:
			return False
		else:
			return (group in self.getGroups())
	
	def getProvinces(self):
		return Province.objects.all()
	
	def getDistricts(self):
		return District.objects.all()
	
	def getSectors(self):
		return Sector.objects.all()
		
	def getContentTypes(self):
		if self.superuser:
			return PMContentType.objects.select_related('module').all().distinct()
		else:
			return PMContentType.objects.filter(action__permission__user=self).select_related('module').distinct()
	
	def getContentTypesWithLink(self):
		content_types=self.getContentTypes()
		ct=[]
		if content_types:
			for content_type in content_types:
				content_type.access_link=content_type.get_access_link()
				ct.append(content_type)
			ct.sort(key=lambda x:x.name, reverse=False)
		return ct
	
				
	def has_content_type(self, content_type):
		content_types = self.getContentTypes()
		if not content_types:
			return False
		else:
			return (content_type in content_types)
		
	def has_content_type_by_name(self, module_name, content_type_name):
		content_type = PMContentType.getContentTypeByName(module_name, content_type_name)
		if not content_type:
			return False
		else:
			return True
	
	def getContentTypesWithWeight(self):
		content_types=self.getContentTypesWithLink()
		dict = {}
		weights = []
		for content_type in content_types:
			weight = content_type.module.icon_weight
			if weight not in weights:
				weights.append(weight)
		
		for weight in weights:
			temp_list = []
			for content_type in content_types:
				if weight == content_type.module.icon_weight:
					temp_list.append(content_type)
			dict[str(weight)]=temp_list
		
		return sorted(dict.iteritems(),key=lambda (k,v): (k,v))
				
	def getModules(self):
		content_types = self.getContentTypes()
		if content_types:
			modules = []
			for content_type in content_types:
				if content_type.module not in modules:
					modules.append(content_type.module)
			if len(modules) == 0:
				 return None
			else:
				return modules
	def has_module(self,module):
		modules = self.getModules()
		if not modules:
			return None
		else:
			return (module in modules)
	
	def has_module_by_name(self, module_name):
		module = PMModule.get_module_by_name(module_name)
		if module:
			return True
		else:
			return False
			
	def getAllowedContentTypesByModule(self,module):
		contenttypes = self.getContentTypes()
		if contenttypes:
			contenttypes = contenttypes.filter(module = module)
			return contenttypes
		else:
			return None

	def save(self, *args, **kwargs):
		"""
		user status is set active by default
		check whether password is encrypted,
		if not, encrypt the password
		"""
		if not self.i_status:
			self.i_status = 'active'
		if self.password and len(self.password) < 32:
			self.password = hashlib.md5(self.password).hexdigest()	
		user = super(PMUser,self).save(*args, **kwargs)
		return user

	def isAdmin(self):
		if self.groups.filter(name__exact='Propertymode Admin') or self.superuser:
			return True
		else:
			return False

	def getLogMessage(self,old_data=None,new_data=None, action = None):
		"""
		return tailored log message for different actions taken on this user
		"""
		if action == "view":
			return "view User [" + self.__unicode__() + "]"
		if action == "delete":
			return "delete User [" + self.__unicode__() + "]"
		if action == "deactivate":
			return "deactivate User [" + self.__unicode__() + "]"
		if action == "activate":
			return "activate User [" + self.__unicode__() + "]"
		if action == "add":
			return "add User [" + self.__unicode__() + "]"
		if action == "change":
			message=""
			count = 0
			for key, value in old_data.iteritems():
				if old_data[key] != new_data[key]:
					if count != 0:
						message = message + ","
					count = count + 1
					if type(value) is not list:
						message = message + " change "+key + " from '"+ str(value) + "' to '"+str(new_data[key])+"'"
					else:
						extraFields = ListCompare.getExtraItems(old_data[key], new_data[key])
						lessFields = ListCompare.getLessItems(old_data[key], new_data[key])
						if key == "permissions":
							extraFields_display = []
							lessFields_display = []
							for permission_id in extraFields:
								extraFields_display.append(str(PMPermission.objects.get(id=permission_id).name))
							for permission_id in lessFields:
								lessFields_display.append(str(PMPermission.objects.get(id=permission_id).name))
							comma_needed = True
							if len(extraFields_display) > 0:
								message = message + " remove permissions " +  str(extraFields_display)
								comma_needed = True
							if len(lessFields_display) > 0:
								if comma_needed:
									message = message + ','
								message = message + " add permissions " +  str(lessFields_display)
						if key == "groups":
							extraFields_display = []
							lessFields_display = []
							for group_id in extraFields:
								extraFields_display.append(str(PMGroup.objects.get(id=group_id).name))
							for group_id in lessFields:
								lessFields_display.append(str(PMGroup.objects.get(id=group_id).name))
							comma_needed = False
							if len(extraFields_display) > 0:
								message = message + " detatch from groups " +  str(extraFields_display)
								comma_needed = True
							if len(lessFields_display) > 0:
								if comma_needed:
									message = message + ','
								message = message + " associate with groups " +  str(lessFields_display)	   
			if message == "":
				message = "No change made"
			message = message + " on User [" + self.__unicode__() + "]" 
			return message
		
		
class AccessAttempt( models.Model ):
    	loginname = models.CharField('loginname', max_length=255)
#     	user=models.ForeignKey(PMUser, null=True, unique=True)
#     	user=models.AutoField(unique=True, primary_key=True)
    	failures = models.PositiveIntegerField( 'Failures', default=0 )
    	timestamp = models.DateTimeField( 'Last failed attempt', null=True,auto_now=True )
      	temppasswd=models.CharField('temp_password', max_length=255,default=None,  null=True, blank=True)
   	class Meta:
		db_table = 'auth_accessattempt'
		ordering = [ '-timestamp' ]
		
	def too_many_failures( self ):
		return self.failures >= FLB_MAX_FAILURES
      	
   	def recent_failure( self ):
		return CommonUtil.pg_utcnow() -self.timestamp < timedelta(minutes=FLB_BLOCK_INTERVAL )
	
	def hastemppassword(self):
		if(self.temppasswd==None or self.temppasswd==''):
			return False
		else:
			return True
   
	def blocked( self ):
		return self.too_many_failures( ) and self.recent_failure( )
	blocked.boolean = True
   
	def __unicode__(self):
		return u'%s (%d failures until %s): ' % \
			   ( self.username,self.failures, self.timestamp )
			   
	def save(self, *args, **kwargs):
		models.Model.save(self)	

class UserHistory(models.Model):   		
	email=models.CharField('email', max_length=255)
	password=models.CharField('password', max_length=225)
	timestamp = models.DateTimeField( 'Last failed attempt', null=True,auto_now=True )
	
	