# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'LandUse'
        db.create_table(u'property_landuse', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(default=None, max_length=10, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('fixed_asset', self.gf('django.db.models.fields.BooleanField')(default=False)),
        ))
        db.send_create_signal(u'property', ['LandUse'])

        # Adding field 'Property.lease_type'
        db.add_column(u'property_property', 'lease_type',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, related_name='leased_property', null=True, blank=True, to=orm['property.LandUse']),
                      keep_default=False)

        # Adding M2M table for field land_use_types on 'Property'
        db.create_table(u'property_property_land_use_types', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('property', models.ForeignKey(orm[u'property.property'], null=False)),
            ('landuse', models.ForeignKey(orm[u'property.landuse'], null=False))
        ))
        db.create_unique(u'property_property_land_use_types', ['property_id', 'landuse_id'])


    def backwards(self, orm):
        # Deleting model 'LandUse'
        db.delete_table(u'property_landuse')

        # Deleting field 'Property.lease_type'
        db.delete_column(u'property_property', 'lease_type_id')

        # Removing M2M table for field land_use_types on 'Property'
        db.delete_table('property_property_land_use_types')


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
        u'property.landuse': {
            'Meta': {'object_name': 'LandUse'},
            'code': ('django.db.models.fields.CharField', [], {'default': 'None', 'max_length': '10', 'null': 'True', 'blank': 'True'}),
            'fixed_asset': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
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
            'land_use_types': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['property.LandUse']", 'symmetrical': 'False'}),
            'lease_type': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'related_name': "'leased_property'", 'null': 'True', 'blank': 'True', 'to': u"orm['property.LandUse']"}),
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