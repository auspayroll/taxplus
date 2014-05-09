# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'Currency'
        db.create_table(u'jtax_currency', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'jtax', ['Currency'])

        # Adding model 'TaxType'
        db.create_table(u'jtax_taxtype', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'jtax', ['TaxType'])

        # Adding model 'FormulaData'
        db.create_table(u'jtax_formuladata', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('data', self.gf('django.db.models.fields.TextField')()),
            ('fee', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['jtax.Fee'], unique=True, null=True)),
            ('property_item', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['jtax.PropertyTaxItem'], unique=True, null=True)),
            ('trading_license', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['jtax.TradingLicenseTax'], unique=True, null=True)),
            ('rental_income', self.gf('django.db.models.fields.related.OneToOneField')(to=orm['jtax.RentalIncomeTax'], unique=True, null=True)),
        ))
        db.send_create_signal(u'jtax', ['FormulaData'])

        # Adding model 'Bank'
        db.create_table(u'jtax_bank', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('code', self.gf('django.db.models.fields.CharField')(max_length=10, null=True, blank=True)),
            ('name', self.gf('django.db.models.fields.CharField')(max_length=50)),
        ))
        db.send_create_signal(u'jtax', ['Bank'])

        # Adding field 'PropertyTaxItem.date_from'
        db.add_column(u'jtax_propertytaxitem', 'date_from',
                      self.gf('django.db.models.fields.DateField')(null=True),
                      keep_default=False)

        # Adding field 'PropertyTaxItem.date_to'
        db.add_column(u'jtax_propertytaxitem', 'date_to',
                      self.gf('django.db.models.fields.DateField')(null=True),
                      keep_default=False)

        # Adding field 'PropertyTaxItem.exempt'
        db.add_column(u'jtax_propertytaxitem', 'exempt',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'PropertyTaxItem.months_deferred'
        db.add_column(u'jtax_propertytaxitem', 'months_deferred',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'PropertyTaxItem.declared_value'
        db.add_column(u'jtax_propertytaxitem', 'declared_value',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['jtax.DeclaredValue'], null=True, blank=True),
                      keep_default=False)

        # Adding M2M table for field land_use_types on 'PropertyTaxItem'
        db.create_table(u'jtax_propertytaxitem_land_use_types', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('propertytaxitem', models.ForeignKey(orm[u'jtax.propertytaxitem'], null=False)),
            ('landuse', models.ForeignKey(orm[u'property.landuse'], null=False))
        ))
        db.create_unique(u'jtax_propertytaxitem_land_use_types', ['propertytaxitem_id', 'landuse_id'])


        # Changing field 'PropertyTaxItem.due_date'
        db.alter_column(u'jtax_propertytaxitem', 'due_date', self.gf('django.db.models.fields.DateField')(null=True))
        # Adding field 'Fee.name'
        db.add_column(u'jtax_fee', 'name',
                      self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Fee.quantity'
        db.add_column(u'jtax_fee', 'quantity',
                      self.gf('django.db.models.fields.IntegerField')(default=1, null=True, blank=True),
                      keep_default=False)

        # Adding field 'Fee.date_from'
        db.add_column(u'jtax_fee', 'date_from',
                      self.gf('django.db.models.fields.DateField')(null=True),
                      keep_default=False)

        # Adding field 'Fee.date_to'
        db.add_column(u'jtax_fee', 'date_to',
                      self.gf('django.db.models.fields.DateField')(null=True),
                      keep_default=False)

        # Adding field 'Fee.exempt'
        db.add_column(u'jtax_fee', 'exempt',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'Fee.land_lease_type'
        db.add_column(u'jtax_fee', 'land_lease_type',
                      self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['property.LandUse'], null=True, blank=True),
                      keep_default=False)


        # Changing field 'Fee.due_date'
        db.alter_column(u'jtax_fee', 'due_date', self.gf('django.db.models.fields.DateField')(null=True))
        # Adding field 'Setting.cell'
        db.add_column(u'jtax_setting', 'cell',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['property.Cell'], null=True, blank=True),
                      keep_default=False)

        # Adding field 'Setting.village'
        db.add_column(u'jtax_setting', 'village',
                      self.gf('django.db.models.fields.related.ForeignKey')(to=orm['property.Village'], null=True, blank=True),
                      keep_default=False)

        # Deleting field 'Installment.payed'
        db.delete_column(u'jtax_installment', 'payed')

        # Adding field 'Installment.paid'
        db.add_column(u'jtax_installment', 'paid',
                      self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=20, decimal_places=2),
                      keep_default=False)

        # Adding field 'Installment.paid_on'
        db.add_column(u'jtax_installment', 'paid_on',
                      self.gf('django.db.models.fields.DateField')(null=True, blank=True),
                      keep_default=False)

        # Adding field 'Installment.propertyTaxItem'
        db.add_column(u'jtax_installment', 'propertyTaxItem',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='installments', null=True, to=orm['jtax.PropertyTaxItem']),
                      keep_default=False)

        # Adding field 'Installment.rentalIncomeTax'
        db.add_column(u'jtax_installment', 'rentalIncomeTax',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='installments', null=True, to=orm['jtax.RentalIncomeTax']),
                      keep_default=False)

        # Adding field 'Installment.tradingLicenseTax'
        db.add_column(u'jtax_installment', 'tradingLicenseTax',
                      self.gf('django.db.models.fields.related.ForeignKey')(blank=True, related_name='installments', null=True, to=orm['jtax.TradingLicenseTax']),
                      keep_default=False)


        # Changing field 'Installment.fee'
        db.alter_column(u'jtax_installment', 'fee_id', self.gf('django.db.models.fields.related.ForeignKey')(null=True, to=orm['jtax.Fee']))
        # Adding field 'DeclaredValue.commercial_amount'
        db.add_column(u'jtax_declaredvalue', 'commercial_amount',
                      self.gf('django.db.models.fields.BigIntegerField')(default=0, null=True, blank=True),
                      keep_default=False)

        # Adding field 'DeclaredValue.residential_amount'
        db.add_column(u'jtax_declaredvalue', 'residential_amount',
                      self.gf('django.db.models.fields.BigIntegerField')(default=0, null=True, blank=True),
                      keep_default=False)

        # Adding field 'DeclaredValue.agriculture_amount'
        db.add_column(u'jtax_declaredvalue', 'agriculture_amount',
                      self.gf('django.db.models.fields.BigIntegerField')(default=0, null=True, blank=True),
                      keep_default=False)

        # Adding field 'DeclaredValue.declared_on'
        db.add_column(u'jtax_declaredvalue', 'declared_on',
                      self.gf('django.db.models.fields.DateField')(null=True),
                      keep_default=False)

        # Adding field 'TradingLicenseTax.date_from'
        db.add_column(u'jtax_tradinglicensetax', 'date_from',
                      self.gf('django.db.models.fields.DateField')(null=True),
                      keep_default=False)

        # Adding field 'TradingLicenseTax.date_to'
        db.add_column(u'jtax_tradinglicensetax', 'date_to',
                      self.gf('django.db.models.fields.DateField')(null=True),
                      keep_default=False)

        # Adding field 'TradingLicenseTax.exempt'
        db.add_column(u'jtax_tradinglicensetax', 'exempt',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'TradingLicenseTax.turnover'
        db.add_column(u'jtax_tradinglicensetax', 'turnover',
                      self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=20, decimal_places=2),
                      keep_default=False)

        # Adding field 'TradingLicenseTax.months_deferred'
        db.add_column(u'jtax_tradinglicensetax', 'months_deferred',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'TradingLicenseTax.activity_data'
        db.add_column(u'jtax_tradinglicensetax', 'activity_data',
                      self.gf('django.db.models.fields.TextField')(null=True),
                      keep_default=False)

        # Adding field 'RentalIncomeTax.date_from'
        db.add_column(u'jtax_rentalincometax', 'date_from',
                      self.gf('django.db.models.fields.DateField')(null=True),
                      keep_default=False)

        # Adding field 'RentalIncomeTax.date_to'
        db.add_column(u'jtax_rentalincometax', 'date_to',
                      self.gf('django.db.models.fields.DateField')(null=True),
                      keep_default=False)

        # Adding field 'RentalIncomeTax.exempt'
        db.add_column(u'jtax_rentalincometax', 'exempt',
                      self.gf('django.db.models.fields.BooleanField')(default=False),
                      keep_default=False)

        # Adding field 'RentalIncomeTax.months_deferred'
        db.add_column(u'jtax_rentalincometax', 'months_deferred',
                      self.gf('django.db.models.fields.IntegerField')(default=0),
                      keep_default=False)

        # Adding field 'RentalIncomeTax.declared_rental_income'
        db.add_column(u'jtax_rentalincometax', 'declared_rental_income',
                      self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=20, decimal_places=2, blank=True),
                      keep_default=False)

        # Adding field 'RentalIncomeTax.declared_bank_interest'
        db.add_column(u'jtax_rentalincometax', 'declared_bank_interest',
                      self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=20, decimal_places=2, blank=True),
                      keep_default=False)


        # Changing field 'RentalIncomeTax.due_date'
        db.alter_column(u'jtax_rentalincometax', 'due_date', self.gf('django.db.models.fields.DateField')(null=True))

    def backwards(self, orm):
        # Deleting model 'Currency'
        db.delete_table(u'jtax_currency')

        # Deleting model 'TaxType'
        db.delete_table(u'jtax_taxtype')

        # Deleting model 'FormulaData'
        db.delete_table(u'jtax_formuladata')

        # Deleting model 'Bank'
        db.delete_table(u'jtax_bank')

        # Deleting field 'PropertyTaxItem.date_from'
        db.delete_column(u'jtax_propertytaxitem', 'date_from')

        # Deleting field 'PropertyTaxItem.date_to'
        db.delete_column(u'jtax_propertytaxitem', 'date_to')

        # Deleting field 'PropertyTaxItem.exempt'
        db.delete_column(u'jtax_propertytaxitem', 'exempt')

        # Deleting field 'PropertyTaxItem.months_deferred'
        db.delete_column(u'jtax_propertytaxitem', 'months_deferred')

        # Deleting field 'PropertyTaxItem.declared_value'
        db.delete_column(u'jtax_propertytaxitem', 'declared_value_id')

        # Removing M2M table for field land_use_types on 'PropertyTaxItem'
        db.delete_table('jtax_propertytaxitem_land_use_types')


        # Changing field 'PropertyTaxItem.due_date'
        db.alter_column(u'jtax_propertytaxitem', 'due_date', self.gf('django.db.models.fields.DateField')(default=None))
        # Deleting field 'Fee.name'
        db.delete_column(u'jtax_fee', 'name')

        # Deleting field 'Fee.quantity'
        db.delete_column(u'jtax_fee', 'quantity')

        # Deleting field 'Fee.date_from'
        db.delete_column(u'jtax_fee', 'date_from')

        # Deleting field 'Fee.date_to'
        db.delete_column(u'jtax_fee', 'date_to')

        # Deleting field 'Fee.exempt'
        db.delete_column(u'jtax_fee', 'exempt')

        # Deleting field 'Fee.land_lease_type'
        db.delete_column(u'jtax_fee', 'land_lease_type_id')


        # Changing field 'Fee.due_date'
        db.alter_column(u'jtax_fee', 'due_date', self.gf('django.db.models.fields.DateField')(default=None))
        # Deleting field 'Setting.cell'
        db.delete_column(u'jtax_setting', 'cell_id')

        # Deleting field 'Setting.village'
        db.delete_column(u'jtax_setting', 'village_id')

        # Adding field 'Installment.payed'
        db.add_column(u'jtax_installment', 'payed',
                      self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=20, decimal_places=2),
                      keep_default=False)

        # Deleting field 'Installment.paid'
        db.delete_column(u'jtax_installment', 'paid')

        # Deleting field 'Installment.paid_on'
        db.delete_column(u'jtax_installment', 'paid_on')

        # Deleting field 'Installment.propertyTaxItem'
        db.delete_column(u'jtax_installment', 'propertyTaxItem_id')

        # Deleting field 'Installment.rentalIncomeTax'
        db.delete_column(u'jtax_installment', 'rentalIncomeTax_id')

        # Deleting field 'Installment.tradingLicenseTax'
        db.delete_column(u'jtax_installment', 'tradingLicenseTax_id')


        # Changing field 'Installment.fee'
        db.alter_column(u'jtax_installment', 'fee_id', self.gf('django.db.models.fields.related.ForeignKey')(default=None, to=orm['jtax.Fee']))
        # Deleting field 'DeclaredValue.commercial_amount'
        db.delete_column(u'jtax_declaredvalue', 'commercial_amount')

        # Deleting field 'DeclaredValue.residential_amount'
        db.delete_column(u'jtax_declaredvalue', 'residential_amount')

        # Deleting field 'DeclaredValue.agriculture_amount'
        db.delete_column(u'jtax_declaredvalue', 'agriculture_amount')

        # Deleting field 'DeclaredValue.declared_on'
        db.delete_column(u'jtax_declaredvalue', 'declared_on')

        # Deleting field 'TradingLicenseTax.date_from'
        db.delete_column(u'jtax_tradinglicensetax', 'date_from')

        # Deleting field 'TradingLicenseTax.date_to'
        db.delete_column(u'jtax_tradinglicensetax', 'date_to')

        # Deleting field 'TradingLicenseTax.exempt'
        db.delete_column(u'jtax_tradinglicensetax', 'exempt')

        # Deleting field 'TradingLicenseTax.turnover'
        db.delete_column(u'jtax_tradinglicensetax', 'turnover')

        # Deleting field 'TradingLicenseTax.months_deferred'
        db.delete_column(u'jtax_tradinglicensetax', 'months_deferred')

        # Deleting field 'TradingLicenseTax.activity_data'
        db.delete_column(u'jtax_tradinglicensetax', 'activity_data')

        # Deleting field 'RentalIncomeTax.date_from'
        db.delete_column(u'jtax_rentalincometax', 'date_from')

        # Deleting field 'RentalIncomeTax.date_to'
        db.delete_column(u'jtax_rentalincometax', 'date_to')

        # Deleting field 'RentalIncomeTax.exempt'
        db.delete_column(u'jtax_rentalincometax', 'exempt')

        # Deleting field 'RentalIncomeTax.months_deferred'
        db.delete_column(u'jtax_rentalincometax', 'months_deferred')

        # Deleting field 'RentalIncomeTax.declared_rental_income'
        db.delete_column(u'jtax_rentalincometax', 'declared_rental_income')

        # Deleting field 'RentalIncomeTax.declared_bank_interest'
        db.delete_column(u'jtax_rentalincometax', 'declared_bank_interest')


        # Changing field 'RentalIncomeTax.due_date'
        db.alter_column(u'jtax_rentalincometax', 'due_date', self.gf('django.db.models.fields.DateField')(default=None))

    models = {
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
        u'common.taxtype': {
            'Meta': {'object_name': 'TaxType'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'displayname': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'i_status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'})
        },
        u'jtax.assignedvalue': {
            'Meta': {'object_name': 'AssignedValue'},
            'amount': ('django.db.models.fields.BigIntegerField', [], {}),
            'citizen_id': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'date_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'on_hold': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'plot_id': ('django.db.models.fields.IntegerField', [], {}),
            'property': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['property.Property']", 'null': 'True', 'blank': 'True'}),
            'staff_id': ('django.db.models.fields.IntegerField', [], {}),
            'valid_until': ('django.db.models.fields.DateTimeField', [], {})
        },
        u'jtax.bank': {
            'Meta': {'object_name': 'Bank'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'jtax.challengepropertytaxitem': {
            'Meta': {'object_name': 'ChallengePropertyTaxItem'},
            'citizen_id': ('django.db.models.fields.IntegerField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'period_from': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'period_to': ('django.db.models.fields.DateTimeField', [], {}),
            'property_tax_item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['jtax.PropertyTaxItem']"}),
            'staff_id': ('django.db.models.fields.IntegerField', [], {})
        },
        u'jtax.challengepropertytaxitemmedia': {
            'Meta': {'object_name': 'ChallengePropertyTaxItemMedia'},
            'challengepropertytaxitemid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['jtax.ChallengePropertyTaxItem']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'mediadatetime': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'mediafile': ('django.db.models.fields.files.FileField', [], {'max_length': '100'}),
            'mediatype': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'staffid': ('django.db.models.fields.IntegerField', [], {})
        },
        u'jtax.challengepropertytaxitemnote': {
            'Meta': {'object_name': 'ChallengePropertyTaxItemNote'},
            'challenge_property_tax_item': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['jtax.ChallengePropertyTaxItem']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {}),
            'staff_id': ('django.db.models.fields.IntegerField', [], {})
        },
        u'jtax.currency': {
            'Meta': {'object_name': 'Currency'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '10', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'jtax.declaredvalue': {
            'Meta': {'object_name': 'DeclaredValue'},
            'accepted': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'agriculture_amount': ('django.db.models.fields.BigIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'amount': ('django.db.models.fields.BigIntegerField', [], {}),
            'citizen': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['citizen.Citizen']", 'null': 'True', 'blank': 'True'}),
            'commercial_amount': ('django.db.models.fields.BigIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'date_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'declared_on': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'property': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['property.Property']", 'null': 'True', 'blank': 'True'}),
            'residential_amount': ('django.db.models.fields.BigIntegerField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pmauth.PMUser']", 'null': 'True', 'blank': 'True'})
        },
        u'jtax.declaredvaluemedia': {
            'Meta': {'object_name': 'DeclaredValueMedia'},
            'date_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'declared_value': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['jtax.DeclaredValue']"}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'file_name': ('django.db.models.fields.CharField', [], {'max_length': '150'}),
            'file_size': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'file_type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'path': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pmauth.PMUser']", 'null': 'True', 'blank': 'True'})
        },
        u'jtax.declaredvaluenotes': {
            'Meta': {'object_name': 'DeclaredValueNotes'},
            'citizen': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['citizen.Citizen']", 'null': 'True', 'blank': 'True'}),
            'date_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'declared_value': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['jtax.DeclaredValue']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pmauth.PMUser']", 'null': 'True', 'blank': 'True'})
        },
        u'jtax.fee': {
            'Meta': {'object_name': 'Fee'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'business': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['asset.Business']", 'null': 'True', 'blank': 'True'}),
            'citizen': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['citizen.Citizen']", 'null': 'True', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'date_from': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'date_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'date_to': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'due_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'exempt': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'fee_type': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'i_status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_paid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'land_lease_type': ('django.db.models.fields.related.ForeignKey', [], {'default': 'None', 'to': u"orm['property.LandUse']", 'null': 'True', 'blank': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'period_from': ('django.db.models.fields.DateTimeField', [], {}),
            'period_to': ('django.db.models.fields.DateTimeField', [], {}),
            'property': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'property_fees'", 'null': 'True', 'to': u"orm['property.Property']"}),
            'quantity': ('django.db.models.fields.IntegerField', [], {'default': '1', 'null': 'True', 'blank': 'True'}),
            'remaining_amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '20', 'decimal_places': '2', 'blank': 'True'}),
            'staff_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'subbusiness': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['asset.SubBusiness']", 'null': 'True', 'blank': 'True'}),
            'submit_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'submit_details': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'})
        },
        u'jtax.formuladata': {
            'Meta': {'object_name': 'FormulaData'},
            'data': ('django.db.models.fields.TextField', [], {}),
            'fee': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['jtax.Fee']", 'unique': 'True', 'null': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'property_item': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['jtax.PropertyTaxItem']", 'unique': 'True', 'null': 'True'}),
            'rental_income': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['jtax.RentalIncomeTax']", 'unique': 'True', 'null': 'True'}),
            'trading_license': ('django.db.models.fields.related.OneToOneField', [], {'to': u"orm['jtax.TradingLicenseTax']", 'unique': 'True', 'null': 'True'})
        },
        u'jtax.historical': {
            'Meta': {'object_name': 'Historical'},
            'amount_due': ('django.db.models.fields.FloatField', [], {'null': 'True', 'blank': 'True'}),
            'business': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['asset.Business']", 'null': 'True', 'blank': 'True'}),
            'citizen': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['citizen.Citizen']", 'null': 'True', 'blank': 'True'}),
            'due_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'fee_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'fee_type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'invoince_no': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'is_paid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'late_paymemt_penalty': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'late_payment_interest': ('django.db.models.fields.FloatField', [], {'default': '0'}),
            'period_from': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'period_to': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'})
        },
        u'jtax.incompletepayment': {
            'Meta': {'object_name': 'IncompletePayment'},
            'bank': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'bank_receipt': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'business': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['asset.Business']", 'null': 'True', 'blank': 'True'}),
            'cell': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['property.Cell']", 'null': 'True', 'blank': 'True'}),
            'citizen_id': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'date_of_birth': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            'date_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'district': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['property.District']", 'null': 'True', 'blank': 'True'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'i_status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'paid_amount': ('django.db.models.fields.FloatField', [], {'default': '0', 'null': 'True', 'blank': 'True'}),
            'paid_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'parcel_id': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'period_from': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'period_to': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'phone': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'sector': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['property.Sector']", 'null': 'True', 'blank': 'True'}),
            'sector_receipt': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'subbusiness': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['asset.SubBusiness']", 'null': 'True', 'blank': 'True'}),
            'tax_payer': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'tax_type': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'tin': ('django.db.models.fields.CharField', [], {'max_length': '100', 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pmauth.PMUser']", 'null': 'True', 'blank': 'True'}),
            'village': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['property.Village']", 'null': 'True', 'blank': 'True'})
        },
        u'jtax.installment': {
            'Meta': {'object_name': 'Installment'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'due': ('django.db.models.fields.DateField', [], {}),
            'fee': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'installments'", 'null': 'True', 'to': u"orm['jtax.Fee']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'paid': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '20', 'decimal_places': '2'}),
            'paid_on': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'propertyTaxItem': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'installments'", 'null': 'True', 'to': u"orm['jtax.PropertyTaxItem']"}),
            'rentalIncomeTax': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'installments'", 'null': 'True', 'to': u"orm['jtax.RentalIncomeTax']"}),
            'tradingLicenseTax': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'installments'", 'null': 'True', 'to': u"orm['jtax.TradingLicenseTax']"})
        },
        u'jtax.landrentaltax': {
            'Meta': {'object_name': 'LandRentalTax'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'date_time': ('django.db.models.fields.DateTimeField', [], {}),
            'due_date': ('django.db.models.fields.DateField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_paid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'period_from': ('django.db.models.fields.DateTimeField', [], {}),
            'period_to': ('django.db.models.fields.DateTimeField', [], {}),
            'plot_id': ('django.db.models.fields.IntegerField', [], {}),
            'property': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['property.Property']", 'null': 'True', 'blank': 'True'})
        },
        u'jtax.landrentaltaxmedia': {
            'Meta': {'object_name': 'LandRentalTaxMedia'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'land_rental_tax': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['jtax.LandRentalTax']"})
        },
        u'jtax.landrentaltaxnotes': {
            'Meta': {'object_name': 'LandRentalTaxNotes'},
            'date_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'land_rental_tax': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['jtax.LandRentalTax']"}),
            'note': ('django.db.models.fields.TextField', [], {}),
            'staff_id': ('django.db.models.fields.IntegerField', [], {})
        },
        u'jtax.miscellaneousfee': {
            'Meta': {'object_name': 'MiscellaneousFee'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'business': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['asset.Business']", 'null': 'True', 'blank': 'True'}),
            'citizen': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['citizen.Citizen']", 'null': 'True', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'date_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'fee_sub_type': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'fee_type': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'i_status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_paid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'property': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['property.Property']", 'null': 'True', 'blank': 'True'}),
            'remaining_amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '20', 'decimal_places': '2', 'blank': 'True'}),
            'staff_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'subbusiness': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['asset.SubBusiness']", 'null': 'True', 'blank': 'True'}),
            'submit_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'submit_details': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'})
        },
        u'jtax.multipayreceipt': {
            'Meta': {'object_name': 'MultipayReceipt'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'date_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'i_status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pmauth.PMUser']", 'null': 'True', 'blank': 'True'})
        },
        u'jtax.multipayreceiptpaymentrelation': {
            'Meta': {'object_name': 'MultipayReceiptPaymentRelation'},
            'i_status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payfee': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'receipt_relations'", 'to': u"orm['jtax.PayFee']"}),
            'receipt': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'payment_relations'", 'to': u"orm['jtax.MultipayReceipt']"})
        },
        u'jtax.payfee': {
            'Meta': {'object_name': 'PayFee'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'bank': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'business_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'citizen_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'date_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'fee': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'payments'", 'to': u"orm['jtax.Fee']"}),
            'fine_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '20', 'decimal_places': '2', 'blank': 'True'}),
            'fine_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'i_status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manual_receipt': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'note': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'paid_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            'receipt_no': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'staff': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pmauth.PMUser']", 'null': 'True', 'blank': 'True'})
        },
        u'jtax.payfixedassettax': {
            'Meta': {'object_name': 'PayFixedAssetTax'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'bank': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'business_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'citizen_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'date_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'fine_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '2'}),
            'fine_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'i_status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manual_receipt': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'note': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'paid_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            'property_tax_item': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'payments'", 'to': u"orm['jtax.PropertyTaxItem']"}),
            'receipt_no': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'staff': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pmauth.PMUser']", 'null': 'True', 'blank': 'True'})
        },
        u'jtax.paymiscellaneousfee': {
            'Meta': {'object_name': 'PayMiscellaneousFee'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'bank': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'business': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['asset.Business']", 'null': 'True', 'blank': 'True'}),
            'citizen': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['citizen.Citizen']", 'null': 'True', 'blank': 'True'}),
            'date_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'fee': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'payments'", 'to': u"orm['jtax.MiscellaneousFee']"}),
            'fine_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'null': 'True', 'max_digits': '20', 'decimal_places': '2', 'blank': 'True'}),
            'fine_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'i_status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manual_receipt': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'note': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'paid_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            'receipt_no': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'staff': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pmauth.PMUser']", 'null': 'True', 'blank': 'True'})
        },
        u'jtax.payrentalincometax': {
            'Meta': {'object_name': 'PayRentalIncomeTax'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'bank': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'business_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'citizen_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'date_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'fine_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '2'}),
            'fine_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'i_status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manual_receipt': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'note': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'paid_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            'receipt_no': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'rental_income_tax': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'payments'", 'to': u"orm['jtax.RentalIncomeTax']"}),
            'staff': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pmauth.PMUser']", 'null': 'True', 'blank': 'True'})
        },
        u'jtax.paytradinglicensetax': {
            'Meta': {'object_name': 'PayTradingLicenseTax'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'bank': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'business_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'citizen_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'date_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'fine_amount': ('django.db.models.fields.DecimalField', [], {'default': '0', 'max_digits': '20', 'decimal_places': '2'}),
            'fine_description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'i_status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'manual_receipt': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'note': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'paid_date': ('django.db.models.fields.DateField', [], {'default': 'datetime.datetime.now'}),
            'receipt_no': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'staff': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pmauth.PMUser']", 'null': 'True', 'blank': 'True'}),
            'trading_license_tax': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'payments'", 'to': u"orm['jtax.TradingLicenseTax']"})
        },
        u'jtax.pendingpayment': {
            'Meta': {'object_name': 'PendingPayment'},
            'date_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'i_status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'payment_id': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'reason': ('django.db.models.fields.CharField', [], {'max_length': '250'}),
            'tax_id': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'tax_type': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['pmauth.PMUser']", 'null': 'True', 'blank': 'True'})
        },
        u'jtax.propertytaxitem': {
            'Meta': {'object_name': 'PropertyTaxItem'},
            'amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '20', 'decimal_places': '2', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'date_from': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'date_time': ('django.db.models.fields.DateTimeField', [], {'default': 'None', 'blank': 'True'}),
            'date_to': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'declared_value': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['jtax.DeclaredValue']", 'null': 'True', 'blank': 'True'}),
            'due_date': ('django.db.models.fields.DateField', [], {'default': 'None', 'null': 'True', 'blank': 'True'}),
            'exempt': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'i_status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_accepted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_chanllenged': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_paid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_reviewed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'land_use_types': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['property.LandUse']", 'symmetrical': 'False'}),
            'months_deferred': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'period_from': ('django.db.models.fields.DateTimeField', [], {}),
            'period_to': ('django.db.models.fields.DateTimeField', [], {}),
            'plot_id': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'property': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'fixed_asset_taxes'", 'null': 'True', 'to': u"orm['property.Property']"}),
            'remaining_amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '20', 'decimal_places': '2', 'blank': 'True'}),
            'staff_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'submit_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'submit_details': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'})
        },
        u'jtax.rentalincometax': {
            'Meta': {'object_name': 'RentalIncomeTax'},
            'amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '20', 'decimal_places': '2', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'date_from': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'date_time': ('django.db.models.fields.DateTimeField', [], {}),
            'date_to': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'declared_bank_interest': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '20', 'decimal_places': '2', 'blank': 'True'}),
            'declared_rental_income': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '20', 'decimal_places': '2', 'blank': 'True'}),
            'due_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'exempt': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'i_status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_paid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'months_deferred': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'period_from': ('django.db.models.fields.DateTimeField', [], {}),
            'period_to': ('django.db.models.fields.DateTimeField', [], {}),
            'plot_id': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'property': ('django.db.models.fields.related.ForeignKey', [], {'blank': 'True', 'related_name': "'rental_income_taxes'", 'null': 'True', 'to': u"orm['property.Property']"}),
            'remaining_amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '20', 'decimal_places': '2', 'blank': 'True'}),
            'staff_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'submit_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'submit_details': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'})
        },
        u'jtax.rentalincometaxnotes': {
            'Meta': {'object_name': 'RentalIncomeTaxNotes'},
            'date_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {}),
            'rental_income_tax': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['jtax.RentalIncomeTax']"}),
            'staff_id': ('django.db.models.fields.IntegerField', [], {})
        },
        u'jtax.reviewpropertytaxitem': {
            'Meta': {'object_name': 'ReviewPropertyTaxItem'},
            'challengepropertytaxitemid': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['jtax.ChallengePropertyTaxItem']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'reviewdate': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'staffid': ('django.db.models.fields.IntegerField', [], {})
        },
        u'jtax.setting': {
            'Meta': {'object_name': 'Setting'},
            'cell': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['property.Cell']", 'null': 'True', 'blank': 'True'}),
            'council': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['property.Council']", 'null': 'True', 'blank': 'True'}),
            'date_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'description': ('django.db.models.fields.TextField', [], {'null': 'True', 'blank': 'True'}),
            'district': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['property.District']", 'null': 'True', 'blank': 'True'}),
            'i_status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'sector': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['property.Sector']", 'null': 'True', 'blank': 'True'}),
            'setting_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'sub_type': ('django.db.models.fields.CharField', [], {'max_length': '250', 'blank': 'True'}),
            'tax_fee_name': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'valid_from': ('django.db.models.fields.DateField', [], {}),
            'valid_to': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'value': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50'}),
            'village': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['property.Village']", 'null': 'True', 'blank': 'True'})
        },
        u'jtax.taxtype': {
            'Meta': {'object_name': 'TaxType'},
            'code': ('django.db.models.fields.CharField', [], {'max_length': '50', 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'jtax.tradinglicensetax': {
            'Meta': {'object_name': 'TradingLicenseTax'},
            'activity_data': ('django.db.models.fields.TextField', [], {'null': 'True'}),
            'amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '20', 'decimal_places': '2', 'blank': 'True'}),
            'business': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['asset.Business']", 'null': 'True', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'date_from': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'date_time': ('django.db.models.fields.DateTimeField', [], {}),
            'date_to': ('django.db.models.fields.DateField', [], {'null': 'True'}),
            'due_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'exempt': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'i_status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_paid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'months_deferred': ('django.db.models.fields.IntegerField', [], {'default': '0'}),
            'period_from': ('django.db.models.fields.DateTimeField', [], {}),
            'period_to': ('django.db.models.fields.DateTimeField', [], {}),
            'remaining_amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '20', 'decimal_places': '2', 'blank': 'True'}),
            'staff_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'subbusiness': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['asset.SubBusiness']", 'null': 'True', 'blank': 'True'}),
            'submit_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'submit_details': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'}),
            'turnover': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '20', 'decimal_places': '2'})
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

    complete_apps = ['jtax']