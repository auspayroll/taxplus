from pmauth.models import PMModule



class ModuleMapper:
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Display module name
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @staticmethod
    def getDisplayName(module):
        return module.name
    

    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Get module by ID
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @staticmethod
    def getModuleById(id):
        module = PMModule.objects.filter(id = id)
        if len(module) == 0:
            return None
        else:
            return module[0]
    
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Get module by module name
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @staticmethod
    def getModuleByName(name):
        module = PMModule.objects.filter(name = name)
        if len(module) == 0:
            return None
        else:
            return module[0]
        
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Get all modules
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    @staticmethod
    def getAllModules():
        return PMModule.objects.all()    
    
  

    