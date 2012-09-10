from django.db import models, connection, transaction
from django.forms import model_to_dict
from datetime import datetime
from django.utils import timezone
from django.db.models.fields.files import ImageFieldFile
import ast
import pytz

class LogManager(models.Manager):
    
    @classmethod
    def getTransactionId(cls):
        """
        Generate a new transactionid by using max transactionid + 1 
        """
        count = Log.objects.all().count()
        if count == 0:
            return None
            #return 1
        else:
            return None
            #log = Log.objects.all().order_by("-transactionid")[0]
            #return log.transactionid + 1
        
    # action could be: 1)view 2)add 3)change 4)delete 5)login 6)logout 
    #def createLog(self,user,obj=None,old_data=None,new_data=None,action=None, plotid = None, search_condition = None):
    def createLog(self,request,**kwargs):
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
        log.transactionid = self.getTransactionId()
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
            message = self.getLogMessage(object,old_data, new_data, action)
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
        
    def objToStr(self, dict):
        """
        convert object to string
        """
        print dict
        if dict is None:
            return str("")
        for key, value in dict.iteritems():
            if type(value) is datetime:
                dict[key] = value.strftime('%Y-%m-%d %H:%M:%S')
            if type(value) is ImageFieldFile:
                dict[key] = value.name
        dict = str(dict)
        return dict
    
    def getLogMessage(self, obj,olddata=None,newdata=None,action=None):
        """
        Call getLogMessage function from each object
        """
        old_data = None
        new_data = None
        if olddata is not None:
            old_data=ast.literal_eval(self.objToStr(olddata))
        if newdata is not None:
            new_data=ast.literal_eval(self.objToStr(newdata))
        return obj.getLogMessage(old_data,new_data,action)
        
class Log(models.Model):
    """
    keep log for each action taken by user.
    """
    transactionid = models.IntegerField(null = True, blank = True)
    userid = models.IntegerField()
    citizenid = models.IntegerField(null = True, blank = True)
    plotid = models.IntegerField(null = True, blank = True)
    tids = models.CharField(max_length = 200, null=True, blank = True)
    username = models.CharField(max_length=100)
    table = models.CharField(blank=True, null=True, max_length=100)
    datetime = models.DateTimeField(default=timezone.now)
    olddata = models.CharField(blank=True, null=True, max_length=1000)
    newdata = models.CharField(blank=True, null=True, max_length=1000)
    message = models.CharField(blank=True, null=True, max_length=1000)
    
      
    def elements_to_add(self, old_list,new_list):
        """
        Compare two list, and get the items in old_list but not in new_list.
        """
        result = []
        if len(old_list) == 0:
            return result
        elif len(new_list) == 0:
            return old_list
        for element in old_list:
            if element not in new_list:
                result.append(element)
        return result    
     
    def elements_to_delete(self, old_list,new_list):
        """
        Compare two list, and get the items not in old_list but in new_list.
        """
        result = []
        if len(old_list) == 0:
            return new_list
        elif len(new_list) == 0:
            return result
        else:
            for element in new_list:
                if element not in old_list:
                    result.append(element)
            return result
    
    def rollback(self):
        """
        Rollback the changes recorded in the log
        """
        old_data = ast.literal_eval(self.olddata)
        new_data = ast.literal_eval(self.newdata)
        sql = "update " + self.table
        count = 0
        for key, value in old_data.iteritems():
            if key != 'id' and type(value) is not list:
                if count != 0:
                    sql = sql + ','
                else:
                    sql = sql + ' set'
                if type(value) is bool:
                    if value:
                        sql = sql + " "+key + " = 1"  
                    else: 
                        sql = sql + " "+key + " = 0"
                elif type(value) is datetime:
                    sql = sql + " "+key + " = '" + value.strftime('%Y-%m-%d %H:%M:%S')+"'"
                elif type(value) is unicode:
                    sql = sql + " "+key + " = '" + value+"'"
                elif type(value) is str:
                    sql = sql + " "+key + " = '" + value+"'"
                elif type(value) is long:
                    sql = sql + " "+key + " = " + value
                count = count + 1
            elif key != 'id' and type(value) is list:
                """
                Check if the object has attribute(s) referencing objects in some other table.
                If so, check whether the object has different referencing objects after it was changed.
                If so, then rollback.
                """
                if old_data[key] != new_data[key]:
                    to_delete = self.elements_to_delete(old_data[key], new_data[key])
                    to_add = self.elements_to_add(old_data[key], new_data[key])
                    foreign_table_name = self.table+'_'+key
                    foreign_field_name = key[:-1]+'_id'
                    parts = str(self.table).split('_')
                    object_field_name = ''+parts[len(parts)-1]+'_id'
                    
                    if len(to_delete) != 0:
                        sql_delete = ""
                        id_array_delete ="("
                        delete_count = 0
                        for id_value in to_delete:
                            if delete_count == 0:
                                id_array_delete = id_array_delete + str(id_value)
                            else:
                                id_array_delete = id_array_delete + ","+str(id_value)
                            delete_count = delete_count + 1
                        id_array_delete = id_array_delete  + ")"
                        sql_delete = "delete from "+foreign_table_name + " where "+foreign_field_name+" in " + id_array_delete
                        cursor_delete = connection.cursor()
                        cursor_delete.execute(sql_delete)
                        transaction.commit_unless_managed()
                    if len(to_add) != 0:
                        sql_add = ""
                        for id_value in to_add:
                            sql_add = sql_add + " insert into "+foreign_table_name + " ("+object_field_name + "," + foreign_field_name +  ") values("+str(old_data['id']) + "," + str(id_value) +  ")"
                        cursor_add = connection.cursor()
                        cursor_add.execute(sql_add)
                        transaction.commit_unless_managed()
        sql=sql+' where id='+str(int(old_data['id']))
        cursor = connection.cursor()
        cursor.execute(sql)
        transaction.commit_unless_managed()
        return True    
    
    def objToStr(self, dict):
        """
        convert object to string type. Especially, datetime type needs to be cast with desired string format
        """
        if dict is None:
            return str('') 
        for key, value in dict.iteritems():
            if type(value) is datetime:
                dict[key] = value.strftime('%Y-%m-%d %H:%M:%S')
        dict = str(dict)
        return dict
    def setUser(self,user):
        self.userid = user.id
        self.username = user.firstname + ' '+user.lastname
    def setTable(self,table):
        self.table = table
    def setOldObj(self,obj):
        str = self.objToStr(obj)
        self.olddata = str
    def setNewObj(self, obj):
        str= self.objToStr(obj)
        self.newdata = str
    def setMessage(self,message):
        self.message = message  
    objects = LogManager()
