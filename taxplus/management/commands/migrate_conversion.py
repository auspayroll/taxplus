from django.core.management.base import BaseCommand, CommandError 
from datetime import date, datetime, time, timedelta
#from pmeval.models import PaymentReceipt, PayFee, MultipayReceiptPaymentRelation, CategoryChoice, Property, Fee, Entity
from taxplus.models import Entity, CategoryChoice, PaymentReceipt, Property
import dateutil.parser
from datetime import date
from django.utils import timezone
from django.db import models
from dateutil.relativedelta import relativedelta
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


fields  = (

	('jtax_fee', 'category', models.ForeignKey(CategoryChoice, limit_choices_to={'category__code':'fee_type'}, related_name='fee_type', null=True)), 
	('jtax_fee', 'status', models.ForeignKey(CategoryChoice, limit_choices_to={'category__code':'status'}, related_name='fee_status', null=True)), 
	('jtax_fee', 'entity', models.ForeignKey(Entity, null=True)), 

	('jtax_payfee', 'status', models.ForeignKey(CategoryChoice, limit_choices_to={'category__code':'status'}, null=True)), 
	('jtax_payfee', 'receipt', models.ForeignKey(PaymentReceipt, related_name="fee_receipts", null=True)),

	#('property_property', 'landuse_types', models.ManyToManyField(CategoryChoice, related_name='property_types', limit_choices_to={'category__code':'land_use'})),
	('property_property', 'bedrooms', models.IntegerField(blank = True, null = True)),
	('property_property', 'bathrooms', models.IntegerField(blank = True, null = True)),
	('property_property', 'ensuites', models.IntegerField(blank=True, null=True)),
	('property_property', 'garages', models.IntegerField(blank = True, null = True)),
	('property_property', 'car_ports', models.IntegerField(blank = True, null = True)),
	('property_property', 'car_spaces', models.IntegerField(blank=True, null=True)),
	('property_property', 'building_type', models.ForeignKey(CategoryChoice, related_name='building_types', null=True, blank=True,  limit_choices_to={'category__code':'property_type'})),
	('property_property', 'market_status', models.ForeignKey(CategoryChoice, related_name='market_status_properties', null=True, blank=True,  limit_choices_to={'category__code':'market_status'})),
	('property_property', 'occupancy_status', models.ForeignKey(CategoryChoice, related_name='occupancy_status', null=True, blank=True, limit_choices_to={'category__code':'occupancy_status'})),
	('property_property', 'taxexempt_reason', models.ForeignKey(CategoryChoice, blank = True, null = True, limit_choices_to={'category__code':'tax_exempt_reason'})),
	('property_property', 'landlease_type', models.ForeignKey(CategoryChoice, blank = True, null = True, limit_choices_to={'category__code':'land_lease'})),
	('property_property', 'lot_number', models.CharField(max_length=5, null=True, blank=True)),
	('property_property', 'street_number', models.IntegerField(null=True, blank=True)),
	('property_property', 'street', models.CharField(max_length=50, blank=True, null=True)),

	('jtax_multipayreceipt', 'sector_receipt', models.CharField(max_length=50, blank=True, null=True)),
	('jtax_multipayreceipt', 'bank_receipt', models.CharField(max_length=50, blank=True, null=True)),
	('jtax_multipayreceipt', 'paid_date', models.CharField(max_length=50, blank=True, null=True)),
	('jtax_multipayreceipt', 'citizen_id', models.IntegerField(blank=True, null=True)),
	('jtax_multipayreceipt', 'business_id', models.IntegerField(blank=True, null=True)),
	('jtax_multipayreceipt', 'bank', models.CharField(max_length=100, blank=True, null=True)),
	('jtax_multipayreceipt', 'note', models.TextField(blank=True, null=True)),
	('jtax_multipayreceipt', 'payer_name', models.CharField(max_length=100, blank=True, null=True)),
	('jtax_multipayreceipt', 'status', models.ForeignKey(CategoryChoice, limit_choices_to={'category__code':'status'}, null=True)), 
	('jtax_multipayreceipt', 'payer', models.ForeignKey(Entity, null=True)), 

)

def forwards():
	db.start_transaction()
	for (table, field_name, field) in fields:
		db.add_column(table, field_name, field, keep_default=False)

	db.create_table('property_property_landuse_types', (
		('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
		('property', models.ForeignKey(Property, null=False)),
		('categorychoice', models.ForeignKey(CategoryChoice, null=False))
	))
	db.create_unique('property_property_landuse_types', ['property_id', 'categorychoice_id'])
	db.commit_transaction()
	

def backwards():
	db.start_transaction()
	
	db.delete_column('jtax_fee', 'category_id')
	db.delete_column('jtax_fee', 'entity_id')
	db.delete_column('jtax_fee', 'status_id')

	db.delete_column('jtax_payfee', 'receipt_id')
	db.delete_column('jtax_payfee', 'status_id')

	db.delete_table('property_property_landuse_types')

	db.delete_column('property_property', 'bedrooms')
	db.delete_column('property_property', 'landlease_type_id')
	db.delete_column('property_property', 'bathrooms')
	db.delete_column('property_property', 'ensuites')
	db.delete_column('property_property', 'garages')
	db.delete_column('property_property', 'car_ports')
	db.delete_column('property_property', 'car_spaces')
	db.delete_column('property_property', 'building_type_id')
	db.delete_column('property_property', 'market_status_id')
	db.delete_column('property_property', 'occupancy_status_id')
	db.delete_column('property_property', 'taxexempt_reason_id')
	db.delete_column('property_property', 'lot_number')
	db.delete_column('property_property', 'street_number')
	db.delete_column('property_property', 'street')

	db.delete_column('jtax_multipayreceipt', 'sector_receipt')
	db.delete_column('jtax_multipayreceipt', 'bank_receipt')
	db.delete_column('jtax_multipayreceipt', 'paid_date')
	db.delete_column('jtax_multipayreceipt', 'citizen_id')
	db.delete_column('jtax_multipayreceipt', 'business_id')
	db.delete_column('jtax_multipayreceipt', 'bank')
	db.delete_column('jtax_multipayreceipt', 'note')
	db.delete_column('jtax_multipayreceipt', 'payer_name')
	db.delete_column('jtax_multipayreceipt', 'payer_id')	
	db.delete_column('jtax_multipayreceipt', 'status_id')

	db.commit_transaction()


class Command(BaseCommand):
	#fixed_asset/rental_income/trading_license/cleaning_fee/market_fee/land_lease_fee
	args = ''
	help = """


	"""
	name= 'Convert tax dates'
	
	def handle(self, *args, **options):
		if args and args[0] == 'b':
			self.stdout.write('rollback migrations..')
			backwards()
		else:
			self.stdout.write('migrating..')
			forwards()







