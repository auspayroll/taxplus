from django.db import models, connection, transaction
from django.forms import model_to_dict
from datetime import datetime
from django.utils import timezone
import ast
import pytz

class LogManager(models.Manager):
    @classmethod
    def getTransactionId(cls):
        count = Log.objects.all().count()
        if count == 0:
            return 1
        else:
            log = Log.objects.all().order_by("-transactionid")[0]
            return log.transactionid + 1
        
    # action could be: 1)view 2)add 3)change 4)delete 5)login 6)logout 
    def createLog(self,user,obj=None,old_data=None,new_data=None,action=None):
        log = Log()
        log.transactionid = self.getTransactionId()
        log.setUser(user)
        message = ""
        if action == "login":
            message = "login"
            log.setTable(user._meta.db_table)
        elif action == "logout":
            message = "logout"
            log.setTable(user._meta.db_table)
        else:
            message = self.getLogMessage(obj,old_data, new_data, action)
        if new_data is not None:
            for key, value in new_data.iteritems():
                if type(value) is datetime:
                    new_data[key]=value.astimezone(pytz.utc)  
        log.setOldObj(old_data)
        log.setNewObj(new_data)
        log.setMessage("User["+user.firstname+" "+user.lastname+"] "+message)
        if not log.table:
            log.setTable(obj._meta.db_table)
        log.save()
        
    def objToStr(self, dict):
        if dict is None:
            return str("")
        for key, value in dict.iteritems():
            if type(value) is datetime:
                dict[key] = value.strftime('%Y-%m-%d %H:%M:%S')
        dict = str(dict)
        return dict
    
    def getLogMessage(self, obj,olddata=None,newdata=None,action=None):
        old_data = None
        new_data = None
        if olddata is not None:
            old_data=ast.literal_eval(self.objToStr(olddata))
        if newdata is not None:
            new_data=ast.literal_eval(self.objToStr(newdata))
        return obj.getLogMessage(old_data,new_data,action)
        
class Log(models.Model):
    transactionid = models.IntegerField()
    userid = models.IntegerField()
    plotid = models.IntegerField(null = True, blank = True)
    tids = models.CharField(max_length = 200, null=True, blank = True)
    username = models.CharField(max_length=100)
    table = models.CharField(blank=True, null=True, max_length=100)
    datetime = models.DateTimeField(default=timezone.now)
    olddata = models.CharField(blank=True, null=True, max_length=1000)
    newdata = models.CharField(blank=True, null=True, max_length=1000)
    message = models.CharField(blank=True, null=True, max_length=1000)
    
    def elements_to_add(self, old_list,new_list):
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
