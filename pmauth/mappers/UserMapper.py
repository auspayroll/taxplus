from pmauth.models import PMUser, PMModule,PMPermission,PMContentType
from pmauth.mappers.ContentTypeMapper import ContentTypeMapper
import md5

class UserMapper:
	
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Display username only
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def getDisplayName(user):
		return user.username
	
	
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Display user fullname
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def getFullName(user):
		return user.firstname.capitalize() + " " + user.lastname.capitalize()
	
	
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get user by user ID
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def getUserById(id):
		user = PMUser.objects.filter(id = id)
		if len(user) == 0:
			return None
		else:
			return user[0]
	
	
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get user by username
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def getUserByUserName(username):
		user = PMUser.objects.filter(username = username)
		if len(user) == 0:
			return None
		else:
			return user[0]
	
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get all users
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def getAllUsers():
		return PMUser.objects.all()

	
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get all active users
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def getActiveUsers():
		return PMUser.objects.filter(i_status = 'active')


	
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get all inactive users
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def getInactiveUsers():
		return PMUser.objects.filter(i_status = 'inactive')



	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get user by Email and Password
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def getUserByEmailAndPassword(email, password):
		user = PMUser.objects.filter(email  = email, password = md5.new(password).hexdigest())
		if len(user) == 0:
			return None
		else:
			return user[0]
	
	
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get all the modules that user is able to get access to.
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def getModules(user):
		if user.superuser:
			return PMModule.objects.all()
		else:
			modules = []
			sql1 = "select distinct m.* from auth_pmmodule m \
				inner join auth_pmcontenttype ct on m.id = ct.module_id \
				inner join auth_pmpermission ap on ct.id = ap.contenttype_id \
				inner join auth_pmuser_permissions aup on aup.pmpermission_id = ap.id \
				inner join auth_pmuser au on au.id = aup.user_id \
				where au.username = '%s' " % user.username
			sql2 = " union select distinct m.* from auth_pmmodule m \
				inner join auth_pmcontenttype ct on m.id = ct.module_id \
				inner join auth_pmpermission ap on ct.id = ap.contenttype_id \
				inner join auth_pmgroup_permissions agp on agp.pmpermission_id = ap.id \
				inner join auth_pmgroup ag  on agp.pmgroup_id = ag.id \
				inner join auth_pmuser_groups ug on ag.id = ug.pmgroup_id \
				inner join auth_pmuser au on au.id = ug.user_id \
				where au.username = '%s' " % user.username
	
			sql = sql1 + sql2
			for module in PMModule.objects.raw(sql):
				if module not in modules:
					modules.append(module)			
			return modules
	
	
	
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get all the contentTypes within a given module that the user has permission to access
	if module is None, then get all the contenttypes that the user has permission to access 
	Both user specific permissions and group permissions are considered
	The returned contenttypes are sorted
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def getContentTypes(user, module=None):
		content_types=UserMapper.getContentTypes1(user,module)
		ct=[]
		for content_type in content_types:
			content_type.access_link=content_type.get_access_link()
			ct.append(content_type)
		ct.sort(key=lambda x:x.name, reverse=False)
		return ct
	
	
	
	@staticmethod
	def getContentTypesWithWeight(user):
		if not user:
			return None
		content_types=UserMapper.getContentTypes1(user,None)
		ct=[]
		for content_type in content_types:
			content_type.access_link=content_type.get_access_link()
			ct.append(content_type)
		ct.sort(key=lambda x:x.name, reverse=False)
		content_types = ct
		
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
		
		
		
		
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get all the contentTypes within a given module that the user has permission to access
	if module is None, then get all the contenttypes that the user has permission to access 
	Both user specific permissions and group permissions are considered
	The returned contenttypes are not sorted
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def getContentTypes1(user,module=None):
		if not user:
			return None
		if user.superuser:
			if module is None:
				return PMContentType.objects.all()
			else:
				return PMContentType.objects.filter(module = module)
		else:
			contentTypes = []
			sql1 = "select distinct ct.* from auth_pmcontenttype ct \
				inner join auth_pmpermission ap on ct.id = ap.contenttype_id \
				inner join auth_pmuser_permissions aup on aup.pmpermission_id = ap.id \
				inner join auth_pmuser au on au.id = aup.pmuser_id \
				where au.username = '%s' " % user.username
			sql2 = " union select distinct ct.* from auth_pmcontenttype ct \
				inner join auth_pmpermission ap on ct.id = ap.contenttype_id \
				inner join auth_pmgroup_permissions agp on agp.pmpermission_id = ap.id \
				inner join auth_pmgroup ag  on agp.pmgroup_id = ag.id \
				inner join auth_pmuser_groups ug on ag.id = ug.pmgroup_id \
				inner join auth_pmuser au on au.id = ug.pmuser_id \
				where au.username = '%s' " % user.username
			sql = sql1 + sql2	
			for contentType in PMContentType.objects.raw(sql):
				if contentType not in contentTypes:
					contentTypes.append(contentType)
			if module is None:
				return contentTypes
			else:
				allowed_content_types = PMContentType.objects.filter(module = module)
				final_content_types = []
				for content_type in contentTypes:
					if content_type in allowed_content_types:
						final_content_types.append(content_type)
				return final_content_types
	
	
	
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get groups that user belongs to
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def getGroups(user):
		sql = "select distinct ag.* from auth_pmgroup ag \
			inner join auth_pmuser_groups ug on ag.id = ug.pmgroup_id \
			inner join auth_pmuser au on au.id = ug.pmuser_id \
			where au.username = '%s' " % user.username
		groups = []
		for group in Group.objects.raw(sql):
			groups.append(group)
		return groups
	

	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get all the group permissions that user has.
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def getGroupPermissions(user):
		final_permissions = []
		if user.superuser:
			final_permissions = PMPermission.objects.all()
		else:
			sql = "select distinct ap.* from auth_pmpermission ap \
				inner join auth_pmgroup_permissions agp on agp.pmpermission_id = ap.id \
				inner join auth_pmgroup ag on agp.pmgroup_id = ag.id \
				inner join auth_pmuser_groups ug on ag.id = ug.pmgroup_id \
				inner join auth_pmuser au on au.id = ug.pmuser_id \
				where au.username = '%s' " % user.username
			for permission in PMPermission.objects.raw(sql):
				final_permissions.append(permission)
		return final_permissions
	
	
	
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get all the additional permissions that user has.
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def getAdditionalPermissions(user):
		final_permissions = []
		if user.superuser:
			return None
		else:
			sql = "select distinct ap.* from auth_pmpermission ap \
				inner join auth_pmuser_permissions aup on aup.pmpermission_id = ap.id \
				inner join auth_pmuser au on au.id = aup.pmuser_id \
				where au.username = '%s' " % user.username	
			for permission in PMPermission.objects.raw(sql):
				final_permissions.append(permission)   
		return final_permissions
	
	
	
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get all the permissions that user has.
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def getAllPermissions(user):
		all_permissions =  []	
		permissions = UserMapper.getAdditionalPermissions(user)
		if permissions is not None:
			for per in permissions:
				all_permissions.append(per)		
		grouppermissions=UserMapper.getGroupPermissions(user)
		if grouppermissions is not None:
			for per in grouppermissions:
				if per not in all_permissions:
					all_permissions.append(per)			
		return all_permissions
	
	
	
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Get all the permissions within a content type that user has.
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def getAllPermissionsByContentType(user,content_type):
		all_permissions=UserMapper.getAllPermissions(user)
		final_permissions=[]
		for per in all_permissions:
			if per.contenttype == content_type:
				final_permissions.append(per)	
		return final_permissions
	
	
	
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Return permissions the user has asssociated with the given contenttype,
	Return additional info regarding permissions like, permission name and permission access link info
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def getUserPermissionsByContentType(request, module_name, content_type_name):
		username = request.session.get('user').username
		user = PMUser.objects.get(username = username)
		module = PMUser.getModule(module_name)
		content_type = ContentTypeMapper.getContentType(content_type_name, module)
		permissions_new=user.getAllPermissionsByContentType(content_type)
		permissions_new=wrap_permissions(permissions_new)
		return permissions_new
	
	
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Check whether user has Permission
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def has_permission(user,permission):
		permissions = UserMapper.getAllPermissions(user)
		if permission in permissions:
			return True
		else:
			return False
		
	
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Check whether user can access to module
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def has_module(user, module):
		modules = UserMapper.getModules(user,module)
		if module in modules:
			return True
		else:
			return False

	
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	Check whether user can access to group
	"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
	@staticmethod
	def has_group(user, group):
		groups = UserMapper.getGroups(user)
		if group in groups:
			return True
		else:
			return False
	
	
	
	
	
	