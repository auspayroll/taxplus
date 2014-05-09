# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'upiBreakdown'
        db.create_table('dataimport_upibreakdown', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('province_id', self.gf('django.db.models.fields.IntegerField')()),
            ('district_id', self.gf('django.db.models.fields.IntegerField')()),
            ('sector_id', self.gf('django.db.models.fields.IntegerField')()),
            ('cell_id', self.gf('django.db.models.fields.IntegerField')()),
            ('parcel_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('province', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('district', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('sector', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('cell', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('upicode', self.gf('django.db.models.fields.CharField')(max_length=100)),
        ))
        db.send_create_signal(u'property', ['upiBreakdown'])

        # Adding model 'Boundary'
        db.create_table(u'property_boundary', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('location_type', self.gf('django.db.models.fields.CharField')(default='property', max_length=20)),
            ('parcel_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('province', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('district', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('sector', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('cell', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('village', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('cell_code', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('shape_leng', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=11, blank=True)),
            ('shape_area', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=11, blank=True)),
            ('polygon', self.gf('django.contrib.gis.db.models.fields.PolygonField')(null=True, blank=True)),
            ('polygon_imported', self.gf('django.contrib.gis.db.models.fields.PolygonField')(srid=3857, null=True, blank=True)),
            ('central_point', self.gf('django.contrib.gis.db.models.fields.PointField')(null=True, blank=True)),
            ('type', self.gf('django.db.models.fields.CharField')(default='official', max_length=10, null=True, blank=True)),
            ('i_status', self.gf('django.db.models.fields.CharField')(default='active', max_length=10)),
        ))
        db.send_create_signal(u'property', ['Boundary'])

        # Adding model 'Province'
        db.create_table(u'property_province', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=2, null=True, blank=True)),
            ('boundary', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='province_boundary', null=True, to=orm['property.Boundary'])),
            ('i_status', self.gf('django.db.models.fields.CharField')(default='active', max_length=10, blank=True)),
        ))
        db.send_create_signal(u'property', ['Province'])

        # Adding model 'District'
        db.create_table(u'property_district', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=4, null=True, blank=True)),
            ('boundary', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='district_boundary', null=True, to=orm['property.Boundary'])),
            ('province', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['property.Province'], null=True, blank=True)),
            ('i_status', self.gf('django.db.models.fields.CharField')(default='active', max_length=10, blank=True)),
        ))
        db.send_create_signal(u'property', ['District'])

        # Adding model 'Council'
        db.create_table(u'property_council', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('address', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('boundary', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['property.Boundary'], null=True, blank=True)),
            ('i_status', self.gf('django.db.models.fields.CharField')(default='active', max_length=10, blank=True)),
        ))
        db.send_create_signal(u'property', ['Council'])

        # Adding model 'Sector'
        db.create_table(u'property_sector', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=6)),
            ('district', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['property.District'])),
            ('council', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['property.Council'], null=True, blank=True)),
            ('province', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['property.Province'])),
            ('boundary', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='sector_boundary', null=True, to=orm['property.Boundary'])),
            ('i_status', self.gf('django.db.models.fields.CharField')(default='active', max_length=10, blank=True)),
        ))
        db.send_create_signal(u'property', ['Sector'])

        # Adding model 'Cell'
        db.create_table(u'property_cell', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=8)),
            ('sector', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['property.Sector'], null=True, blank=True)),
            ('boundary', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['property.Boundary'])),
            ('i_status', self.gf('django.db.models.fields.CharField')(default='active', max_length=10, blank=True)),
        ))
        db.send_create_signal(u'property', ['Cell'])

        # Adding model 'Village'
        db.create_table(u'property_village', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=10)),
            ('cell', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['property.Cell'], null=True, blank=True)),
            ('boundary', self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='+', null=True, to=orm['property.Boundary'])),
            ('i_status', self.gf('django.db.models.fields.CharField')(default='active', max_length=10, blank=True)),
        ))
        db.send_create_signal(u'property', ['Village'])

        # Adding model 'Property'
        db.create_table(u'property_property', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('plot_id', self.gf('django.db.models.fields.CharField')(unique=True, max_length=50, blank=True)),
            ('is_leasing', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_land_lease', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('land_lease_type', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('land_lease_approval_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('foreign_plot_id', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('parcel_id', self.gf('django.db.models.fields.IntegerField')()),
            ('cell', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['property.Cell'], null=True, blank=True)),
            ('village', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['property.Village'], null=True, blank=True)),
            ('shape_leng', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=11, blank=True)),
            ('shape_area', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=19, decimal_places=11, blank=True)),
            ('sector', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['property.Sector'], null=True, blank=True)),
            ('boundary', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['property.Boundary'], null=True)),
            ('region_type', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('land_use_type', self.gf('django.db.models.fields.CharField')(max_length=20, null=True, blank=True)),
            ('size_sqm', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('size_hectare', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('floor_count', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('floor_total_square_meters', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('year_built', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('is_tax_exempt', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('tax_exempt_reason', self.gf('django.db.models.fields.CharField')(max_length=40, null=True, blank=True)),
            ('tax_exempt_note', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('date_created', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('date_modified', self.gf('django.db.models.fields.DateTimeField')(auto_now_add=True, blank=True)),
            ('status', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['common.Status'], null=True, blank=True)),
        ))
        db.send_create_signal(u'property', ['Property'])


    def backwards(self, orm):
        # Deleting model 'upiBreakdown'
        db.delete_table('dataimport_upibreakdown')

        # Deleting model 'Boundary'
        db.delete_table(u'property_boundary')

        # Deleting model 'Province'
        db.delete_table(u'property_province')

        # Deleting model 'District'
        db.delete_table(u'property_district')

        # Deleting model 'Council'
        db.delete_table(u'property_council')

        # Deleting model 'Sector'
        db.delete_table(u'property_sector')

        # Deleting model 'Cell'
        db.delete_table(u'property_cell')

        # Deleting model 'Village'
        db.delete_table(u'property_village')

        # Deleting model 'Property'
        db.delete_table(u'property_property')


    models = {
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
        u'property.upibreakdown': {
            'Meta': {'object_name': 'upiBreakdown', 'db_table': "'dataimport_upibreakdown'"},
            'cell': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'cell_id': ('django.db.models.fields.IntegerField', [], {}),
            'district': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'district_id': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'parcel_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'province': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'province_id': ('django.db.models.fields.IntegerField', [], {}),
            'sector': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'sector_id': ('django.db.models.fields.IntegerField', [], {}),
            'upicode': ('django.db.models.fields.CharField', [], {'max_length': '100'})
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

    complete_apps = ['property']