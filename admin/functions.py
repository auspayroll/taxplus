from pmauth.models import PMUser,PMGroup,PMPermission,PMContentType,PMModule
    
def initializeAuthData():
        
    """ 
    create testing module data
    """
    module1 = PMModule.getModule('auth')
    module2 = PMModule.getModule('property')
    module3 = PMModule.getModule('log')
    module4 = PMModule.getModule('citizen')
    module5 = PMModule.getModule('tax')
    
    if module1 is None:
        module1 = PMModule.objects.create(name='auth')
    if module2 is None:
        module2 = PMModule.objects.create(name='property')
    if module3 is None:
        module3 = PMModule.objects.create(name='log')
    if module4 is None:
        module4 = PMModule.objects.create(name='citizen')
    if module5 is None:
        module5 = PMModule.objects.create(name='tax')
    
        
    """ 
    create testing content type data
    """
    contenttype1 = PMContentType.getContentType('permission',module1)
    if contenttype1 is None:
          contenttype1 = PMContentType.objects.create(name ='permission',module = module1)
    contenttype2 = PMContentType.getContentType('group', module1)
    if contenttype2 is None:
          contenttype2 = PMContentType.objects.create(name ='group',image= 'icons/group.png', module = module1)
    contenttype3 = PMContentType.getContentType('user',module1)
    if contenttype3 is None:
          contenttype3 = PMContentType.objects.create(name ='user', image= 'icons/user.png',  module = module1)
    
    contenttype4 = PMContentType.getContentType('property',module2)      
    if contenttype4 is None:
          contenttype4 = PMContentType.objects.create(name ='property', image= 'icons/property.png',module = module2)
    contenttype6 = PMContentType.getContentType('log', module3)
    if contenttype6 is None:
          contenttype6 = PMContentType.objects.create(name ='log', image= 'icons/logging.png',module = module3)
    contenttype7 = PMContentType.getContentType('citizen',module4)
    if contenttype7 is None:
          contenttype7 = PMContentType.objects.create(name ='citizen', image= 'icons/citizen.png', module = module4)
    contenttype8 = PMContentType.getContentType('tax',module5)
    if contenttype8 is None:
          contenttype8 = PMContentType.objects.create(name ='tax', image= 'icons/tax.png', module = module5)
    
    
    
    """
    create testig permission data
    """
    contentTypes = PMContentType.objects.all()
    for obj in contentTypes:
        permission1 = PMPermission.getPermission('Can view '+obj.name, obj)
        if permission1 is None:
            PMPermission.objects.create(name='Can view '+obj.name,codename='view_'+obj.name,contenttype=obj)
        permission2 = PMPermission.getPermission('Can add '+obj.name, obj)
        if permission1 is None:
            PMPermission.objects.create(name='Can add '+obj.name,codename='add_'+obj.name,contenttype=obj)
        permission3 = PMPermission.getPermission('Can change '+obj.name, obj)
        if permission1 is None:
            PMPermission.objects.create(name='Can change '+obj.name,codename='change_'+obj.name,contenttype=obj)
        permission4 = PMPermission.getPermission('Can delete '+obj.name, obj)
        if permission1 is None:
            PMPermission.objects.create(name='Can delete '+obj.name,codename='delete_'+obj.name,contenttype=obj)    


    """
    create testig group data
    """
    group1 = PMGroup.getGroup('testgroup')
    if group1 is None:
        group1 = PMGroup.objects.create(name='testgroup', i_status='active')
    
    group2 = PMGroup.getGroup('dev')
    if group2 is None:
        group2 = PMGroup.objects.create(name='dev', i_status='active')
    
    
    """
    create testig user data
    """
    user1 = PMUser.getUser('linkongluan@gmail.com','ilyjun')
    user2 = PMUser.getUser('test@test.com','test')
    user3 = PMUser.getUser('shane@propertymode.com.au','shane100')
    user4 = PMUser.getUser('sandra@propertymode.com.au','sandra100')
    user5 = PMUser.getUser('justin@propertymode.com.au','justin100')
    
    if user1 is None:
        user1 = PMUser.objects.create(username='Kongluan Lin', firstname='Kongluan', lastname='Lin', password='ilyjun', email='linkongluan@gmail.com', i_status='active', active=True,superuser=True)
    if user2 is None:
        user2 = PMUser.objects.create(username='Peter Wang', firstname='Peter', lastname='Wang', password='test', email='test@test.com', i_status='active', active=True,superuser=False)
    if user3 is None:
        user3 = PMUser.objects.create(username='Shane Dale', firstname='Shane', lastname='Dale', password='shane100', email='shane@propertymode.com.au', i_status='active', active=True,superuser=True)
    if user4 is None:
        user4 = PMUser.objects.create(username='Sandra Macnaughton', firstname='Sandra', lastname='Macnaughton', password='sandra100', email='sandra@propertymode.com.au', i_status='active', active=True,superuser=True)
    if user5 is None:
        user5 = PMUser.objects.create(username='Justin Hopley', firstname='justin', lastname='Hopley', password='justin100', email='justin@propertymode.com.au', i_status='active', active=True,superuser=True)
    
    
    """
    create testing group permission data
    """
    permission1 = PMPermission.getPermissionByCodeName('view_property')
    if not group1.has_permission(permission1):
        group1.permissions.add(permission1)
    permission2 = PMPermission.getPermissionByCodeName('view_citizen')
    if not group1.has_permission(permission2):
        group1.permissions.add(permission2)
    group1.save()
    
    
    permissions = PMPermission.objects.all()
    for per in permissions:
        if not group2.has_permission(per):
            group2.permissions.add(per)
    group2.save()
      
   
    """
    create a group for test user
    """
    if not user2.has_group(group1):
        user2.groups.add(group1)
        user2.save()
    
    """
    create testing user permission data
    """
    permission1 = PMPermission.getPermissionByCodeName(codename = 'change_property')
    if not user2.has_permission(permission1):
        user2.permissions.add(permission1)
    permission2 = PMPermission.getPermissionByCodeName(codename = 'delete_property')
    if not user2.has_permission(permission2):
        user2.permissions.add(permission2)
    user2.save()
    
            