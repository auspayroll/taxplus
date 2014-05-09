# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'AccessAttempt'
        db.create_table('auth_accessattempt', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('loginname', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('failures', self.gf('django.db.models.fields.PositiveIntegerField')(default=0)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
            ('temppasswd', self.gf('django.db.models.fields.CharField')(default=None, max_length=255, null=True, blank=True)),
        ))
        db.send_create_signal(u'pmauth', ['AccessAttempt'])

        # Adding model 'UserHistory'
        db.create_table(u'pmauth_userhistory', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('email', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=225)),
            ('timestamp', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, null=True, blank=True)),
        ))
        db.send_create_signal(u'pmauth', ['UserHistory'])


    def backwards(self, orm):
        # Deleting model 'AccessAttempt'
        db.delete_table('auth_accessattempt')

        # Deleting model 'UserHistory'
        db.delete_table(u'pmauth_userhistory')


    models = {
        u'common.taxtype': {
            'Meta': {'object_name': 'TaxType'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'displayname': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'i_status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'pmauth.accessattempt': {
            'Meta': {'ordering': "['-timestamp']", 'object_name': 'AccessAttempt', 'db_table': "'auth_accessattempt'"},
            'failures': ('django.db.models.fields.PositiveIntegerField', [], {'default': '0'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'loginname': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'temppasswd': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '255', 'null': 'True', 'blank': 'True'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'})
        },
        'pmauth.action': {
            'Meta': {'object_name': 'Action', 'db_table': "'auth_action'"},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'contenttype': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pmauth.PMContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'pmauth.pmcontenttype': {
            'Meta': {'ordering': "['name']", 'object_name': 'PMContentType', 'db_table': "'auth_pmcontenttype'"},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'model_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'module': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pmauth.PMModule']"}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'pmauth.pmgroup': {
            'Meta': {'ordering': "['name']", 'object_name': 'PMGroup', 'db_table': "'auth_pmgroup'"},
            'i_status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'group'", 'blank': 'True', 'to': "orm['pmauth.PMPermission']"})
        },
        'pmauth.pmmodule': {
            'Meta': {'object_name': 'PMModule', 'db_table': "'auth_pmmodule'"},
            'description': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'icon_weight': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'image': ('django.db.models.fields.files.ImageField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        'pmauth.pmpermission': {
            'Meta': {'object_name': 'PMPermission', 'db_table': "'auth_pmpermission'"},
            'actions': ('django.db.models.fields.related.ManyToManyField', [], {'blank': 'True', 'related_name': "'permission'", 'null': 'True', 'symmetrical': 'False', 'to': "orm['pmauth.Action']"}),
            'district': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'permission'", 'null': 'True', 'to': u"orm['property.District']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '80', 'unique': 'True', 'null': 'True'}),
            'province': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'permission'", 'null': 'True', 'to': u"orm['property.Province']"}),
            'sector': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'permission'", 'null': 'True', 'to': u"orm['property.Sector']"}),
            'tax_types': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'permission'", 'blank': 'True', 'to': u"orm['common.TaxType']"})
        },
        u'pmauth.pmuser': {
            'Meta': {'object_name': 'PMUser', 'db_table': "'auth_pmuser'"},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'contactnumber': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'council': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['property.Council']", 'null': 'True', 'blank': 'True'}),
            'datejoined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'firstname': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'user'", 'blank': 'True', 'to': "orm['pmauth.PMGroup']"}),
            'i_status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '10', 'blank': 'True'}),
            'id': ('django.db.models.fields.AutoField', [], {'unique': 'True', 'primary_key': 'True'}),
            'lastlogin': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'lastname': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'user'", 'blank': 'True', 'to': "orm['pmauth.PMPermission']"}),
            'superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'username': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'pmauth.userhistory': {
            'Meta': {'object_name': 'UserHistory'},
            'email': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '225'}),
            'timestamp': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'null': 'True', 'blank': 'True'})
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
        }
    }

    complete_apps = ['pmauth']