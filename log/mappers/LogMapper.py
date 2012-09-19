from django.forms import model_to_dict
from datetime import datetime
from django.utils import timezone
from admin.Common import Common
import ast, pytz
from log.models import Log


class LogMapper:
    
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
    Get logs by conditions
    """""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""    
    @staticmethod
    def getLogsByConditions(conditions):
        logs = None
        count = 0
        for key, value in conditions.iteritems():
            if key == 'plotid' and value:
                logs = Log.objects.filter(plotid = value)
                count = count + 1
            if key == 'transactionid' and value:
                if count > 0:
                    logs = logs.filter(transactionid = value)
                else:
                    logs = Log.objects.filter(transactionid = value)
                count = count + 1
            if key == 'username' and value:
                if count > 0:
                    logs = logs.filter(username__icontains = value)
                else:
                    logs = Log.objects.filter(username__icontains = value)
                count = count + 1
        return logs
    
    
    @staticmethod
    def raw(sql):
        return Log.objects.raw(sql)
    
    
    
    @staticmethod
    def getTransactionId():
        """
        Generate a new transactionid by using max transactionid + 1 
        """
        count = Log.objects.all().count()
        if count == 0:
            return None
        else:
            return None
            #log = Log.objects.all().order_by("-transactionid")[0]
            #return log.transactionid + 1

        
    # action could be: 1)view 2)add 3)change 4)delete 5)login 6)logout 
    @staticmethod
    def createLog(request,**kwargs):
        """
        Given the action taken on the object, create a log for this action
        Make a copy of the old data and new data as strings in databse
        """
        
        plotid = None
        citizenid = None
        object = None
        old_data = None
        new_data = None
        action = None
        search_message_all = None
        search_message_action =None
        search_message_purpose =None
        search_object_class_name = None
        search_conditions = {}
        
        user = request.session.get('user')
        message = ""
        
        log = Log()
        log.transactionid = LogMapper.getTransactionId()
        log.setUser(user)
        
        # get parameters from arguments
        for key, value in kwargs.iteritems():
            if key == "action":
                action = kwargs["action"]
            if key == "object":
                object = kwargs["object"]
            if key == "old_data":
                old_data = kwargs["old_data"]
            if key == "new_data":
                new_data = kwargs["new_data"]
            if key == "plotid":
                plotid = kwargs["plotid"]
            if key == "citizenid":
                citizenid = kwargs["citizenid"]
            if key == "search_message_all":
                search_message_all = kwargs["search_message_all"]
            if key == "search_message_action":
                search_message_action = kwargs["search_message_action"]
            if key == "search_message_purpose":
                search_message_purpose = kwargs["search_message_purpose"]
            if key == "search_object_class_name":
                search_object_class_name = kwargs["search_object_class_name"]
            if key == "search_conditions":
                search_conditions = kwargs["search_conditions"]
            
        if action == "login" or action == "logout":
            message = action
            log.setTable(user._meta.db_table)     
        elif action == "search":
            # we can provide customized message for a search
            if search_message_all:
                message = search_message_all
            # normal search: we need search object class name and conditions
            else:
                if search_message_action:
                    message = search_message_action
                else:
                    message = "search " + search_object_class_name
                if search_message_purpose:
                    message  = message + " for " + search_message_purpose + " purpose"
                if search_conditions:
                    message = message + " with conditions("
                    count = 0
                    for key, value in search_conditions.iteritems():
                        if value:
                            if count > 0:
                                message = message + ", "
                            message = message + key + "=" + str(value)
                            count = count + 1
                    message = message + ")"
        else:
            message = LogMapper.getLogMessage(object,old_data, new_data, action)
            if new_data is not None:
                for key, value in new_data.iteritems():
                    if type(value) is datetime:
                        new_data[key]=value.astimezone(pytz.utc)  
            log.setOldObj(old_data)
            log.setNewObj(new_data)
            if not log.table and object:
                log.setTable(object._meta.db_table)
            if plotid:
                log.plotid = plotid
            if citizenid:
                log.citizenid = citizenid
        log.setMessage("User ["+user.firstname+" "+user.lastname+"] "+message)
        log.save()
        
    
    @staticmethod
    def getLogMessage(obj,olddata=None,newdata=None,action=None):
        """
        Call getLogMessage function from each object
        """
        old_data = None
        new_data = None
        if olddata is not None:
            old_data=ast.literal_eval(Common.objToStr(olddata))
        if newdata is not None:
            new_data=ast.literal_eval(Common.objToStr(newdata))
        return obj.getLogMessage(old_data,new_data,action)
    