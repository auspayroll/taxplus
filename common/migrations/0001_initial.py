# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Status'
        db.create_table(u'common_status', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=30)),
        ))
        db.send_create_signal(u'common', ['Status'])

        # Adding model 'TaxType'
        db.create_table(u'common_taxtype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('displayname', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('codename', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('i_status', self.gf('django.db.models.fields.CharField')(default='active', max_length=10, blank=True)),
        ))
        db.send_create_signal(u'common', ['TaxType'])


    def backwards(self, orm):
        # Deleting model 'Status'
        db.delete_table(u'common_status')

        # Deleting model 'TaxType'
        db.delete_table(u'common_taxtype')


    models = {
        u'common.status': {
            'Meta': {'object_name': 'Status'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '30'})
        },
        u'common.taxtype': {
            'Meta': {'object_name': 'TaxType'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'displayname': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'i_status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        }
    }

    complete_apps = ['common']