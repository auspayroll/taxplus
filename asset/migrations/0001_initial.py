# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Business'
        db.create_table(u'asset_business', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('pm_tin', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('tin', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('date_started', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('foreign_record_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=255, null=True, blank=True)),
            ('phone1', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('phone2', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('po_box', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('vat_register', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('area_type', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('business_type', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('sector', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['property.Sector'], null=True, blank=True)),
            ('cell', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['property.Cell'], null=True, blank=True)),
            ('credit', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('accountant_name', self.gf('django.db.models.fields.CharField')(max_length=150, null=True, blank=True)),
            ('accountant_phone', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('accountant_email', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('cp_password', self.gf('django.db.models.fields.CharField')(max_length=128, null=True, blank=True)),
            ('market_fee_applicable', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('i_status', self.gf('django.db.models.fields.CharField')(default='active', max_length=10, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'asset', ['Business'])

        # Adding model 'SubBusiness'
        db.create_table(u'asset_subbusiness', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('branch', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('sector', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['property.Sector'], null=True, blank=True)),
            ('cell', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['property.Cell'], null=True, blank=True)),
            ('village', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['property.Village'], null=True, blank=True)),
            ('parcel_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('credit', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('i_status', self.gf('django.db.models.fields.CharField')(default='active', max_length=10, blank=True)),
            ('business', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['asset.Business'])),
        ))
        db.send_create_signal(u'asset', ['SubBusiness'])

        # Adding model 'Billboard'
        db.create_table(u'asset_billboard', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('property', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['property.Property'], null=True, blank=True)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('longitude', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('latitude', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('i_status', self.gf('django.db.models.fields.CharField')(default='active', max_length=10, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'asset', ['Billboard'])

        # Adding model 'Vehicle'
        db.create_table(u'asset_vehicle', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('vehicle_type', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('plate_number', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50)),
            ('use_since', self.gf('django.db.models.fields.DateTimeField')()),
            ('brand', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('model', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('i_status', self.gf('django.db.models.fields.CharField')(default='active', max_length=10, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'asset', ['Vehicle'])

        # Adding model 'Shop'
        db.create_table(u'asset_shop', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('phone1', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('phone2', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('i_status', self.gf('django.db.models.fields.CharField')(default='active', max_length=10, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'asset', ['Shop'])

        # Adding model 'Stall'
        db.create_table(u'asset_stall', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('phone1', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('phone2', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('i_status', self.gf('django.db.models.fields.CharField')(default='active', max_length=10, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'asset', ['Stall'])

        # Adding model 'Office'
        db.create_table(u'asset_office', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('phone1', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('phone2', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=50, blank=True)),
            ('i_status', self.gf('django.db.models.fields.CharField')(default='active', max_length=10, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'asset', ['Office'])

        # Adding model 'Ownership'
        db.create_table(u'asset_ownership', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('owner_citizen', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='assets', null=True, to=orm['citizen.Citizen'])),
            ('owner_business', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='assets', null=True, to=orm['asset.Business'])),
            ('owner_subbusiness', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='assets', null=True, to=orm['asset.SubBusiness'])),
            ('asset_business', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='owners', null=True, to=orm['asset.Business'])),
            ('asset_subbusiness', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='owners', null=True, to=orm['asset.SubBusiness'])),
            ('asset_property', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='owners', null=True, to=orm['property.Property'])),
            ('asset_billboard', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='owners', null=True, to=orm['asset.Billboard'])),
            ('asset_vehicle', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='owners', null=True, to=orm['asset.Vehicle'])),
            ('share', self.gf('django.db.models.fields.FloatField')()),
            ('date_started', self.gf('django.db.models.fields.DateField')()),
            ('date_ended', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('i_status', self.gf('django.db.models.fields.CharField')(default='active', max_length=10, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'asset', ['Ownership'])


    def backwards(self, orm):
        # Deleting model 'Business'
        db.delete_table(u'asset_business')

        # Deleting model 'SubBusiness'
        db.delete_table(u'asset_subbusiness')

        # Deleting model 'Billboard'
        db.delete_table(u'asset_billboard')

        # Deleting model 'Vehicle'
        db.delete_table(u'asset_vehicle')

        # Deleting model 'Shop'
        db.delete_table(u'asset_shop')

        # Deleting model 'Stall'
        db.delete_table(u'asset_stall')

        # Deleting model 'Office'
        db.delete_table(u'asset_office')

        # Deleting model 'Ownership'
        db.delete_table(u'asset_ownership')


    models = {
        u'asset.billboard': {
            'Meta': {'object_name': 'Billboard'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'i_status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'latitude': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'longitude': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'property': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['property.Property']", 'null': 'True', 'blank': 'True'})
        },
        u'asset.business': {
            'Meta': {'object_name': 'Business'},
            'accountant_email': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'accountant_name': ('django.db.models.fields.CharField', [], {'max_length': '150', 'null': 'True', 'blank': 'True'}),
            'accountant_phone': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'area_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'business_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'cell': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['property.Cell']", 'null': 'True', 'blank': 'True'}),
            'cp_password': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'credit': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_started': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'foreign_record_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'i_status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'market_fee_applicable': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'phone1': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'phone2': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'pm_tin': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'po_box': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'sector': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['property.Sector']", 'null': 'True', 'blank': 'True'}),
            'tin': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'vat_register': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'asset.office': {
            'Meta': {'object_name': 'Office'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'i_status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'phone1': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'phone2': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'})
        },
        u'asset.ownership': {
            'Meta': {'object_name': 'Ownership'},
            'asset_billboard': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'owners'", 'null': 'True', 'to': u"orm['asset.Billboard']"}),
            'asset_business': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'owners'", 'null': 'True', 'to': u"orm['asset.Business']"}),
            'asset_property': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'owners'", 'null': 'True', 'to': u"orm['property.Property']"}),
            'asset_subbusiness': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'owners'", 'null': 'True', 'to': u"orm['asset.SubBusiness']"}),
            'asset_vehicle': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'owners'", 'null': 'True', 'to': u"orm['asset.Vehicle']"}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_ended': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'date_started': ('django.db.models.fields.DateField', [], {}),
            'i_status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'owner_business': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assets'", 'null': 'True', 'to': u"orm['asset.Business']"}),
            'owner_citizen': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assets'", 'null': 'True', 'to': u"orm['citizen.Citizen']"}),
            'owner_subbusiness': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'assets'", 'null': 'True', 'to': u"orm['asset.SubBusiness']"}),
            'share': ('django.db.models.fields.FloatField', [], {})
        },
        u'asset.shop': {
            'Meta': {'object_name': 'Shop'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'i_status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'phone1': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'phone2': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'})
        },
        u'asset.stall': {
            'Meta': {'object_name': 'Stall'},
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'}),
            'i_status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'phone1': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'phone2': ('django.db.models.fields.CharField', [], {'max_length': '50', 'blank': 'True'})
        },
        u'asset.subbusiness': {
            'Meta': {'object_name': 'SubBusiness'},
            'branch': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'business': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['asset.Business']"}),
            'cell': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['property.Cell']", 'null': 'True', 'blank': 'True'}),
            'credit': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'i_status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parcel_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'sector': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['property.Sector']", 'null': 'True', 'blank': 'True'}),
            'village': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['property.Village']", 'null': 'True', 'blank': 'True'})
        },
        u'asset.vehicle': {
            'Meta': {'object_name': 'Vehicle'},
            'brand': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'i_status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'plate_number': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'use_since': ('django.db.models.fields.DateTimeField', [], {}),
            'vehicle_type': ('django.db.models.fields.CharField', [], {'max_length': '25'})
        },
        u'citizen.citizen': {
            'Meta': {'object_name': 'Citizen'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'citizen_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50'}),
            'cp_password': ('django.db.models.fields.CharField', [], {'max_length': '128', 'null': 'True', 'blank': 'True'}),
            'date_of_birth': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'deactivate_reason': ('django.db.models.fields.CharField', [], {'default': '1', 'max_length': '50', 'null': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'foreign_identity_number': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'foreign_identity_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'foreign_record_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'gender': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'middle_name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'phone_1': ('django.db.models.fields.CharField', [], {'max_length': '30', 'null': 'True', 'blank': 'True'}),
            'phone_2': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'photo': ('django.db.models.fields.files.ImageField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'po_box': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'default': '1', 'to': u"orm['common.Status']"}),
            'year_of_birth': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'})
        },
        u'common.status': {
            'Meta': {'object_name': 'Status'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'property.boundary': {
            'Meta': {'object_name': 'Boundary'},
            'cell': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'cell_code': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'central_point': ('django.contrib.gis.db.models.fields.PointField', [], {'null': 'True', 'blank': 'True'}),
            'district': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'i_status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '10'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'location_type': ('django.db.models.fields.CharField', [], {'default': "'property'", 'max_length': '20'}),
            'parcel_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'polygon': ('django.contrib.gis.db.models.fields.PolygonField', [], {'null': 'True', 'blank': 'True'}),
            'polygon_imported': ('django.contrib.gis.db.models.fields.PolygonField', [], {'srid': '3857', 'null': 'True', 'blank': 'True'}),
            'province': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'sector': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'shape_area': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '11', 'blank': 'True'}),
            'shape_leng': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '11', 'blank': 'True'}),
            'type': ('django.db.models.fields.CharField', [], {'default': "'official'", 'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'village': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'})
        },
        u'property.cell': {
            'Meta': {'ordering': "['name']", 'object_name': 'Cell'},
            'boundary': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['property.Boundary']"}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '8'}),
            'i_status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'sector': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['property.Sector']", 'null': 'True', 'blank': 'True'})
        },
        u'property.council': {
            'Meta': {'object_name': 'Council'},
            'address': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'boundary': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['property.Boundary']", 'null': 'True', 'blank': 'True'}),
            'i_status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'property.district': {
            'Meta': {'object_name': 'District'},
            'boundary': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'district_boundary'", 'null': 'True', 'to': u"orm['property.Boundary']"}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '4', 'null': 'True', 'blank': 'True'}),
            'i_status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'province': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['property.Province']", 'null': 'True', 'blank': 'True'})
        },
        u'property.property': {
            'Meta': {'object_name': 'Property'},
            'boundary': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['property.Boundary']", 'null': 'True'}),
            'cell': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['property.Cell']", 'null': 'True', 'blank': 'True'}),
            'date_created': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'date_modified': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'floor_count': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'floor_total_square_meters': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'foreign_plot_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_land_lease': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_leasing': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_tax_exempt': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'land_lease_approval_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'land_lease_type': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'land_use_type': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'parcel_id': ('django.db.models.fields.IntegerField', [], {}),
            'plot_id': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '50', 'blank': 'True'}),
            'region_type': ('django.db.models.fields.CharField', [], {'max_length': '20', 'null': 'True', 'blank': 'True'}),
            'sector': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['property.Sector']", 'null': 'True', 'blank': 'True'}),
            'shape_area': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '11', 'blank': 'True'}),
            'shape_leng': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '19', 'decimal_places': '11', 'blank': 'True'}),
            'size_hectare': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'size_sqm': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'status': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['common.Status']", 'null': 'True', 'blank': 'True'}),
            'tax_exempt_note': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'tax_exempt_reason': ('django.db.models.fields.CharField', [], {'max_length': '40', 'null': 'True', 'blank': 'True'}),
            'village': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['property.Village']", 'null': 'True', 'blank': 'True'}),
            'year_built': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'})
        },
        u'property.province': {
            'Meta': {'object_name': 'Province'},
            'boundary': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'province_boundary'", 'null': 'True', 'to': u"orm['property.Boundary']"}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '2', 'null': 'True', 'blank': 'True'}),
            'i_status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'property.sector': {
            'Meta': {'ordering': "['name', 'district__name']", 'object_name': 'Sector'},
            'boundary': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'sector_boundary'", 'null': 'True', 'to': u"orm['property.Boundary']"}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '6'}),
            'council': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['property.Council']", 'null': 'True', 'blank': 'True'}),
            'district': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['property.District']"}),
            'i_status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'province': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['property.Province']"})
        },
        u'property.village': {
            'Meta': {'ordering': "['name']", 'object_name': 'Village'},
            'boundary': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'+'", 'null': 'True', 'to': u"orm['property.Boundary']"}),
            'cell': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['property.Cell']", 'null': 'True', 'blank': 'True'}),
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10'}),
            'i_status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        }
    }

    complete_apps = ['asset']