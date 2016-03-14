from django.db import models, connection, transaction
from datetime import datetime
from django.utils import timezone
import ast
from property.models import Property
from asset.models import Business, SubBusiness
from citizen.models import Citizen
from pmauth.models import PMUser
from dev1 import variables
from taxplus.management.commands.convert_logging import convert_old_log
from django.db.models.signals import post_save
from django.dispatch import receiver

class Log(models.Model):
	"""
	keep log for each action taken by user.
	"""
	transaction_id = models.IntegerField(null = True, blank = True)
	#user_id = models.IntegerField(null=True, blank=True)
	user = models.ForeignKey(PMUser,null=True,blank=True)
	#citizen_id = models.CharField(max_length = 50, null = True, blank = True)
	citizen = models.ForeignKey(Citizen, null=True, blank=True)
	#plot_id = models.CharField(max_length = 50, null = True, blank = True)
	property = models.ForeignKey(Property, null=True, blank=True)
	#business_id = models.CharField(max_length = 50, null = True, blank = True)
	business = models.ForeignKey(Business, null=True, blank=True)
	subbusiness = models.ForeignKey(SubBusiness, null=True, blank=True)
	tids = models.CharField(max_length = 200, null=True, blank = True)
	tax_type = models.CharField(max_length = 50, null=True, blank = True)
	tax_id = models.CharField(max_length = 50, null=True, blank = True)
	payment_type = models.CharField(max_length = 50, null=True, blank = True)
	payment_id = models.CharField(max_length = 50, null=True, blank = True)
	media_id = models.CharField(max_length = 50, null=True, blank = True)
	username = models.CharField(max_length=100)
	table = models.CharField(blank=True, null=True, max_length=100)
	date_time = models.DateTimeField(default=timezone.now)
	old_data = models.CharField(blank=True, null=True, max_length=1000)
	new_data = models.CharField(blank=True, null=True, max_length=1000)
	message = models.TextField(blank=True, null=True)
	fee_id = models.IntegerField(blank=True, null=True)
	payfee_id = models.IntegerField(blank=True, null=True)

	def setUser(self,user):
		self.user = user
		self.username = user.firstname + ' '+user.lastname
	def setTable(self,table):
		self.table = table
	def setOldObj(self,obj):
		str = Common.objToStr(obj)
		self.old_data = str
	def setNewObj(self, obj):
		str= Common.objToStr(obj)
		self.new_data = str
	def setMessage(self,message):
		self.message = message


	"""
	Rollback the changes recorded in the log
	This function is to be used later.
	"""
	def rollback(self):
		old_data = ast.literal_eval(self.old_data)
		new_data = ast.literal_eval(self.new_data)
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

@receiver(post_save, sender=Log)
def after_business_save(sender, instance, created, **kwargs):
	convert_old_log(log=instance.pk)



"""
The following Models are Related to Cron jobs
"""
class CronLog(models.Model):
	name = models.CharField(max_length=50)
	command = models.CharField(max_length=250)
	description = models.CharField(max_length=2000,null=True, blank=True)
	started = models.DateTimeField()
	finished = models.DateTimeField(null=True, blank=True)
	date_time = models.DateTimeField(help_text="The date when this cronjob record is generated.",auto_now_add=True)
	i_status = models.CharField(max_length = 10, choices = variables.status_choices, default='active', blank = True)

	def __unicode__(self):
		return self.name + " on " + str(self.date_time)
	def getLogMessage(self,old_data=None,new_data=None, action=None):
		return getLogMessage(self,old_data,new_data, action)