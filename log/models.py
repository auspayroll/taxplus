from django.db import models, connection, transaction
from datetime import datetime
from django.utils import timezone
from admin.ListCompare import ListCompare
from admin.Common import Common
import ast

 
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
    
    def setUser(self,user):
        self.userid = user.id
        self.username = user.firstname + ' '+user.lastname
    def setTable(self,table):
        self.table = table
    def setOldObj(self,obj):
        str = Common.objToStr(obj)
        self.olddata = str
    def setNewObj(self, obj):
        str= Common.objToStr(obj)
        self.newdata = str
    def setMessage(self,message):
        self.message = message  
    
    
    
    
    
    """
    Rollback the changes recorded in the log
    This function is to be used later.
    """  
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
                """
                Check if the object has attribute(s) referencing objects in some other table.
                If so, check whether the object has different referencing objects after it was changed.
                If so, then rollback.
                """
                if old_data[key] != new_data[key]:
                    to_delete = ListCompare.getLessItems(old_data[key], new_data[key])
                    to_add = ListCompare.getExtraItems(old_data[key], new_data[key])
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
