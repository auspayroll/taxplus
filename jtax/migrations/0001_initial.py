# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'IncompletePayment'
        db.create_table(u'jtax_incompletepayment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tax_type', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('tin', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('business', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['asset.Business'], null=True, blank=True)),
            ('subbusiness', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['asset.SubBusiness'], null=True, blank=True)),
            ('paid_amount', self.gf('django.db.models.fields.FloatField')(default=0, null=True, blank=True)),
            ('paid_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('period_from', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('period_to', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('bank', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('bank_receipt', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('sector_receipt', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('district', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['property.District'], null=True, blank=True)),
            ('sector', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['property.Sector'], null=True, blank=True)),
            ('cell', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['property.Cell'], null=True, blank=True)),
            ('village', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['property.Village'], null=True, blank=True)),
            ('parcel_id', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('tax_payer', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('citizen_id', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('date_of_birth', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
            ('phone', self.gf('django.db.models.fields.CharField')(max_length=100, null=True, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=100, null=True, blank=True)),
            ('note', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pmauth.PMUser'], null=True, blank=True)),
            ('date_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('i_status', self.gf('django.db.models.fields.CharField')(default='active', max_length=10, blank=True)),
        ))
        db.send_create_signal(u'jtax', ['IncompletePayment'])

        # Adding model 'Historical'
        db.create_table(u'jtax_historical', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('citizen', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['citizen.Citizen'], null=True, blank=True)),
            ('business', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['asset.Business'], null=True, blank=True)),
            ('fee_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('fee_type', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('period_from', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('period_to', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('due_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('amount_due', self.gf('django.db.models.fields.FloatField')(null=True, blank=True)),
            ('late_paymemt_penalty', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('late_payment_interest', self.gf('django.db.models.fields.FloatField')(default=0)),
            ('is_paid', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('invoince_no', self.gf('django.db.models.fields.CharField')(max_length=50, null=True, blank=True)),
        ))
        db.send_create_signal(u'jtax', ['Historical'])

        # Adding model 'DeclaredValue'
        db.create_table(u'jtax_declaredvalue', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('citizen', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['citizen.Citizen'], null=True, blank=True)),
            ('amount', self.gf('django.db.models.fields.BigIntegerField')()),
            ('currency', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('date_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pmauth.PMUser'], null=True, blank=True)),
            ('accepted', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('property', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['property.Property'], null=True, blank=True)),
        ))
        db.send_create_signal(u'jtax', ['DeclaredValue'])

        # Adding model 'DeclaredValueNotes'
        db.create_table(u'jtax_declaredvaluenotes', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('declared_value', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['jtax.DeclaredValue'])),
            ('citizen', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['citizen.Citizen'], null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pmauth.PMUser'], null=True, blank=True)),
            ('note', self.gf('django.db.models.fields.TextField')()),
            ('date_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'jtax', ['DeclaredValueNotes'])

        # Adding model 'DeclaredValueMedia'
        db.create_table(u'jtax_declaredvaluemedia', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('declared_value', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['jtax.DeclaredValue'])),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('file_name', self.gf('django.db.models.fields.CharField')(max_length=150)),
            ('path', self.gf('django.db.models.fields.CharField')(max_length=255)),
            ('file_type', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('file_size', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pmauth.PMUser'], null=True, blank=True)),
            ('date_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'jtax', ['DeclaredValueMedia'])

        # Adding model 'AssignedValue'
        db.create_table(u'jtax_assignedvalue', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('plot_id', self.gf('django.db.models.fields.IntegerField')()),
            ('amount', self.gf('django.db.models.fields.BigIntegerField')()),
            ('date_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('currency', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('staff_id', self.gf('django.db.models.fields.IntegerField')()),
            ('citizen_id', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('valid_until', self.gf('django.db.models.fields.DateTimeField')()),
            ('on_hold', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('property', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['property.Property'], null=True, blank=True)),
        ))
        db.send_create_signal(u'jtax', ['AssignedValue'])

        # Adding model 'LandRentalTax'
        db.create_table(u'jtax_landrentaltax', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('plot_id', self.gf('django.db.models.fields.IntegerField')()),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('currency', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('period_from', self.gf('django.db.models.fields.DateTimeField')()),
            ('period_to', self.gf('django.db.models.fields.DateTimeField')()),
            ('due_date', self.gf('django.db.models.fields.DateField')()),
            ('is_paid', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('date_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('property', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['property.Property'], null=True, blank=True)),
        ))
        db.send_create_signal(u'jtax', ['LandRentalTax'])

        # Adding model 'LandRentalTaxNotes'
        db.create_table(u'jtax_landrentaltaxnotes', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('land_rental_tax', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['jtax.LandRentalTax'])),
            ('staff_id', self.gf('django.db.models.fields.IntegerField')()),
            ('note', self.gf('django.db.models.fields.TextField')()),
            ('date_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'jtax', ['LandRentalTaxNotes'])

        # Adding model 'LandRentalTaxMedia'
        db.create_table(u'jtax_landrentaltaxmedia', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('land_rental_tax', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['jtax.LandRentalTax'])),
        ))
        db.send_create_signal(u'jtax', ['LandRentalTaxMedia'])

        # Adding model 'PropertyTaxItem'
        db.create_table(u'jtax_propertytaxitem', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('plot_id', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=20, decimal_places=2, blank=True)),
            ('remaining_amount', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=20, decimal_places=2, blank=True)),
            ('currency', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('period_from', self.gf('django.db.models.fields.DateTimeField')()),
            ('period_to', self.gf('django.db.models.fields.DateTimeField')()),
            ('due_date', self.gf('django.db.models.fields.DateField')()),
            ('date_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('is_paid', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_chanllenged', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_reviewed', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_accepted', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('submit_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('submit_details', self.gf('django.db.models.fields.CharField')(max_length=500, null=True, blank=True)),
            ('staff_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('i_status', self.gf('django.db.models.fields.CharField')(default='active', max_length=10, blank=True)),
            ('property', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['property.Property'], null=True, blank=True)),
        ))
        db.send_create_signal(u'jtax', ['PropertyTaxItem'])

        # Adding model 'ChallengePropertyTaxItem'
        db.create_table(u'jtax_challengepropertytaxitem', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('property_tax_item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['jtax.PropertyTaxItem'])),
            ('citizen_id', self.gf('django.db.models.fields.IntegerField')()),
            ('staff_id', self.gf('django.db.models.fields.IntegerField')()),
            ('period_from', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('period_to', self.gf('django.db.models.fields.DateTimeField')()),
        ))
        db.send_create_signal(u'jtax', ['ChallengePropertyTaxItem'])

        # Adding model 'ChallengePropertyTaxItemNote'
        db.create_table(u'jtax_challengepropertytaxitemnote', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('challenge_property_tax_item', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['jtax.ChallengePropertyTaxItem'])),
            ('staff_id', self.gf('django.db.models.fields.IntegerField')()),
            ('note', self.gf('django.db.models.fields.TextField')()),
        ))
        db.send_create_signal(u'jtax', ['ChallengePropertyTaxItemNote'])

        # Adding model 'ChallengePropertyTaxItemMedia'
        db.create_table(u'jtax_challengepropertytaxitemmedia', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('challengepropertytaxitemid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['jtax.ChallengePropertyTaxItem'])),
            ('mediatype', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('mediafile', self.gf('django.db.models.fields.files.FileField')(max_length=100)),
            ('staffid', self.gf('django.db.models.fields.IntegerField')()),
            ('mediadatetime', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'jtax', ['ChallengePropertyTaxItemMedia'])

        # Adding model 'ReviewPropertyTaxItem'
        db.create_table(u'jtax_reviewpropertytaxitem', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('challengepropertytaxitemid', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['jtax.ChallengePropertyTaxItem'])),
            ('staffid', self.gf('django.db.models.fields.IntegerField')()),
            ('reviewdate', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('note', self.gf('django.db.models.fields.CharField')(max_length=255)),
        ))
        db.send_create_signal(u'jtax', ['ReviewPropertyTaxItem'])

        # Adding model 'RentalIncomeTax'
        db.create_table(u'jtax_rentalincometax', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('plot_id', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=20, decimal_places=2, blank=True)),
            ('remaining_amount', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=20, decimal_places=2, blank=True)),
            ('currency', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('period_from', self.gf('django.db.models.fields.DateTimeField')()),
            ('period_to', self.gf('django.db.models.fields.DateTimeField')()),
            ('due_date', self.gf('django.db.models.fields.DateField')()),
            ('is_paid', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('submit_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('submit_details', self.gf('django.db.models.fields.CharField')(max_length=500, null=True, blank=True)),
            ('date_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('i_status', self.gf('django.db.models.fields.CharField')(default='active', max_length=10, blank=True)),
            ('property', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['property.Property'], null=True, blank=True)),
            ('staff_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'jtax', ['RentalIncomeTax'])

        # Adding model 'RentalIncomeTaxNotes'
        db.create_table(u'jtax_rentalincometaxnotes', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('rental_income_tax', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['jtax.RentalIncomeTax'])),
            ('staff_id', self.gf('django.db.models.fields.IntegerField')()),
            ('note', self.gf('django.db.models.fields.TextField')()),
            ('date_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'jtax', ['RentalIncomeTaxNotes'])

        # Adding model 'TradingLicenseTax'
        db.create_table(u'jtax_tradinglicensetax', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('business', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['asset.Business'], null=True, blank=True)),
            ('subbusiness', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['asset.SubBusiness'], null=True, blank=True)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=20, decimal_places=2, blank=True)),
            ('remaining_amount', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=20, decimal_places=2, blank=True)),
            ('currency', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('period_from', self.gf('django.db.models.fields.DateTimeField')()),
            ('period_to', self.gf('django.db.models.fields.DateTimeField')()),
            ('due_date', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('is_paid', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('submit_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('submit_details', self.gf('django.db.models.fields.CharField')(max_length=500, null=True, blank=True)),
            ('staff_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('date_time', self.gf('django.db.models.fields.DateTimeField')()),
            ('i_status', self.gf('django.db.models.fields.CharField')(default='active', max_length=10, blank=True)),
        ))
        db.send_create_signal(u'jtax', ['TradingLicenseTax'])

        # Adding model 'Fee'
        db.create_table(u'jtax_fee', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('fee_type', self.gf('django.db.models.fields.CharField')(max_length=25)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('remaining_amount', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=20, decimal_places=2, blank=True)),
            ('currency', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('period_from', self.gf('django.db.models.fields.DateTimeField')()),
            ('period_to', self.gf('django.db.models.fields.DateTimeField')()),
            ('due_date', self.gf('django.db.models.fields.DateField')()),
            ('is_paid', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('submit_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('submit_details', self.gf('django.db.models.fields.CharField')(max_length=500, null=True, blank=True)),
            ('staff_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('date_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('i_status', self.gf('django.db.models.fields.CharField')(default='active', max_length=10, blank=True)),
            ('business', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['asset.Business'], null=True, blank=True)),
            ('subbusiness', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['asset.SubBusiness'], null=True, blank=True)),
            ('property', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['property.Property'], null=True, blank=True)),
            ('citizen', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['citizen.Citizen'], null=True, blank=True)),
        ))
        db.send_create_signal(u'jtax', ['Fee'])

        # Adding model 'MiscellaneousFee'
        db.create_table(u'jtax_miscellaneousfee', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('fee_type', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('fee_sub_type', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('remaining_amount', self.gf('django.db.models.fields.DecimalField')(null=True, max_digits=20, decimal_places=2, blank=True)),
            ('currency', self.gf('django.db.models.fields.CharField')(max_length=4)),
            ('is_paid', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('submit_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('submit_details', self.gf('django.db.models.fields.CharField')(max_length=500, null=True, blank=True)),
            ('staff_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('date_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('i_status', self.gf('django.db.models.fields.CharField')(default='active', max_length=10, blank=True)),
            ('business', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['asset.Business'], null=True, blank=True)),
            ('subbusiness', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['asset.SubBusiness'], null=True, blank=True)),
            ('property', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['property.Property'], null=True, blank=True)),
            ('citizen', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['citizen.Citizen'], null=True, blank=True)),
        ))
        db.send_create_signal(u'jtax', ['MiscellaneousFee'])

        # Adding model 'PayRentalIncomeTax'
        db.create_table(u'jtax_payrentalincometax', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('rental_income_tax', self.gf('django.db.models.fields.related.ForeignKey')(related_name='payments', to=orm['jtax.RentalIncomeTax'])),
            ('business_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('citizen_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('staff', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pmauth.PMUser'], null=True, blank=True)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('receipt_no', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('bank', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('paid_date', self.gf('django.db.models.fields.DateField')(default=datetime.datetime.now)),
            ('fine_amount', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=20, decimal_places=2)),
            ('fine_description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('manual_receipt', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('date_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('note', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('i_status', self.gf('django.db.models.fields.CharField')(default='active', max_length=10, blank=True)),
        ))
        db.send_create_signal(u'jtax', ['PayRentalIncomeTax'])

        # Adding model 'PayTradingLicenseTax'
        db.create_table(u'jtax_paytradinglicensetax', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('citizen_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('business_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('staff', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pmauth.PMUser'], null=True, blank=True)),
            ('trading_license_tax', self.gf('django.db.models.fields.related.ForeignKey')(related_name='payments', to=orm['jtax.TradingLicenseTax'])),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('receipt_no', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('bank', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('paid_date', self.gf('django.db.models.fields.DateField')(default=datetime.datetime.now)),
            ('fine_amount', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=20, decimal_places=2)),
            ('fine_description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('manual_receipt', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('date_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('note', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('i_status', self.gf('django.db.models.fields.CharField')(default='active', max_length=10, blank=True)),
        ))
        db.send_create_signal(u'jtax', ['PayTradingLicenseTax'])

        # Adding model 'PayFee'
        db.create_table(u'jtax_payfee', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('citizen_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('business_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('staff', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pmauth.PMUser'], null=True, blank=True)),
            ('fee', self.gf('django.db.models.fields.related.ForeignKey')(related_name='payments', to=orm['jtax.Fee'])),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('receipt_no', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('bank', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('paid_date', self.gf('django.db.models.fields.DateField')(default=datetime.datetime.now)),
            ('fine_amount', self.gf('django.db.models.fields.DecimalField')(default=0, null=True, max_digits=20, decimal_places=2, blank=True)),
            ('fine_description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('manual_receipt', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('date_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('note', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('i_status', self.gf('django.db.models.fields.CharField')(default='active', max_length=10, blank=True)),
        ))
        db.send_create_signal(u'jtax', ['PayFee'])

        # Adding model 'PayFixedAssetTax'
        db.create_table(u'jtax_payfixedassettax', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('property_tax_item', self.gf('django.db.models.fields.related.ForeignKey')(related_name='payments', to=orm['jtax.PropertyTaxItem'])),
            ('business_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('citizen_id', self.gf('django.db.models.fields.IntegerField')(null=True, blank=True)),
            ('staff', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pmauth.PMUser'], null=True, blank=True)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('receipt_no', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('bank', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('paid_date', self.gf('django.db.models.fields.DateField')(default=datetime.datetime.now)),
            ('fine_amount', self.gf('django.db.models.fields.DecimalField')(default=0, max_digits=20, decimal_places=2)),
            ('fine_description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('manual_receipt', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('date_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('note', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('i_status', self.gf('django.db.models.fields.CharField')(default='active', max_length=10, blank=True)),
        ))
        db.send_create_signal(u'jtax', ['PayFixedAssetTax'])

        # Adding model 'PayMiscellaneousFee'
        db.create_table(u'jtax_paymiscellaneousfee', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('business', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['asset.Business'], null=True, blank=True)),
            ('citizen', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['citizen.Citizen'], null=True, blank=True)),
            ('staff', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pmauth.PMUser'], null=True, blank=True)),
            ('fee', self.gf('django.db.models.fields.related.ForeignKey')(related_name='payments', to=orm['jtax.MiscellaneousFee'])),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('receipt_no', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('bank', self.gf('django.db.models.fields.CharField')(max_length=100)),
            ('paid_date', self.gf('django.db.models.fields.DateField')(default=datetime.datetime.now)),
            ('fine_amount', self.gf('django.db.models.fields.DecimalField')(default=0, null=True, max_digits=20, decimal_places=2, blank=True)),
            ('fine_description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('manual_receipt', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('date_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('note', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('i_status', self.gf('django.db.models.fields.CharField')(default='active', max_length=10, blank=True)),
        ))
        db.send_create_signal(u'jtax', ['PayMiscellaneousFee'])

        # Adding model 'PendingPayment'
        db.create_table(u'jtax_pendingpayment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('payment_id', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('tax_type', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('tax_id', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('reason', self.gf('django.db.models.fields.CharField')(max_length=250)),
            ('note', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pmauth.PMUser'], null=True, blank=True)),
            ('date_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('i_status', self.gf('django.db.models.fields.CharField')(default='active', max_length=10, blank=True)),
        ))
        db.send_create_signal(u'jtax', ['PendingPayment'])

        # Adding model 'Setting'
        db.create_table(u'jtax_setting', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tax_fee_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('setting_name', self.gf('django.db.models.fields.CharField')(max_length=50)),
            ('sub_type', self.gf('django.db.models.fields.CharField')(max_length=250, blank=True)),
            ('value', self.gf('django.db.models.fields.CharField')(default='', max_length=50)),
            ('description', self.gf('django.db.models.fields.TextField')(null=True, blank=True)),
            ('valid_from', self.gf('django.db.models.fields.DateField')()),
            ('valid_to', self.gf('django.db.models.fields.DateField')(null=True, blank=True)),
            ('council', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['property.Council'], null=True, blank=True)),
            ('district', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['property.District'], null=True, blank=True)),
            ('sector', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['property.Sector'], null=True, blank=True)),
            ('i_status', self.gf('django.db.models.fields.CharField')(default='active', max_length=10, blank=True)),
            ('date_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
        ))
        db.send_create_signal(u'jtax', ['Setting'])

        # Adding model 'MultipayReceipt'
        db.create_table(u'jtax_multipayreceipt', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['pmauth.PMUser'], null=True, blank=True)),
            ('date_time', self.gf('django.db.models.fields.DateTimeField')(auto_now=True, auto_now_add=True, blank=True)),
            ('i_status', self.gf('django.db.models.fields.CharField')(default='active', max_length=10, blank=True)),
        ))
        db.send_create_signal(u'jtax', ['MultipayReceipt'])

        # Adding model 'MultipayReceiptPaymentRelation'
        db.create_table(u'jtax_multipayreceiptpaymentrelation', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('payfee', self.gf('django.db.models.fields.related.ForeignKey')(related_name='receipt_relations', to=orm['jtax.PayFee'])),
            ('receipt', self.gf('django.db.models.fields.related.ForeignKey')(related_name='payment_relations', to=orm['jtax.MultipayReceipt'])),
            ('i_status', self.gf('django.db.models.fields.CharField')(default='active', max_length=10, blank=True)),
        ))
        db.send_create_signal(u'jtax', ['MultipayReceiptPaymentRelation'])

        # Adding model 'Installment'
        db.create_table(u'jtax_installment', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('fee', self.gf('django.db.models.fields.related.ForeignKey')(related_name='installments', to=orm['jtax.Fee'])),
            ('amount', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=2)),
            ('payed', self.gf('django.db.models.fields.DecimalField')(default=0.0, max_digits=20, decimal_places=2)),
            ('due', self.gf('django.db.models.fields.DateField')()),
        ))
        db.send_create_signal(u'jtax', ['Installment'])


    def backwards(self, orm):
        # Deleting model 'IncompletePayment'
        db.delete_table(u'jtax_incompletepayment')

        # Deleting model 'Historical'
        db.delete_table(u'jtax_historical')

        # Deleting model 'DeclaredValue'
        db.delete_table(u'jtax_declaredvalue')

        # Deleting model 'DeclaredValueNotes'
        db.delete_table(u'jtax_declaredvaluenotes')

        # Deleting model 'DeclaredValueMedia'
        db.delete_table(u'jtax_declaredvaluemedia')

        # Deleting model 'AssignedValue'
        db.delete_table(u'jtax_assignedvalue')

        # Deleting model 'LandRentalTax'
        db.delete_table(u'jtax_landrentaltax')

        # Deleting model 'LandRentalTaxNotes'
        db.delete_table(u'jtax_landrentaltaxnotes')

        # Deleting model 'LandRentalTaxMedia'
        db.delete_table(u'jtax_landrentaltaxmedia')

        # Deleting model 'PropertyTaxItem'
        db.delete_table(u'jtax_propertytaxitem')

        # Deleting model 'ChallengePropertyTaxItem'
        db.delete_table(u'jtax_challengepropertytaxitem')

        # Deleting model 'ChallengePropertyTaxItemNote'
        db.delete_table(u'jtax_challengepropertytaxitemnote')

        # Deleting model 'ChallengePropertyTaxItemMedia'
        db.delete_table(u'jtax_challengepropertytaxitemmedia')

        # Deleting model 'ReviewPropertyTaxItem'
        db.delete_table(u'jtax_reviewpropertytaxitem')

        # Deleting model 'RentalIncomeTax'
        db.delete_table(u'jtax_rentalincometax')

        # Deleting model 'RentalIncomeTaxNotes'
        db.delete_table(u'jtax_rentalincometaxnotes')

        # Deleting model 'TradingLicenseTax'
        db.delete_table(u'jtax_tradinglicensetax')

        # Deleting model 'Fee'
        db.delete_table(u'jtax_fee')

        # Deleting model 'MiscellaneousFee'
        db.delete_table(u'jtax_miscellaneousfee')

        # Deleting model 'PayRentalIncomeTax'
        db.delete_table(u'jtax_payrentalincometax')

        # Deleting model 'PayTradingLicenseTax'
        db.delete_table(u'jtax_paytradinglicensetax')

        # Deleting model 'PayFee'
        db.delete_table(u'jtax_payfee')

        # Deleting model 'PayFixedAssetTax'
        db.delete_table(u'jtax_payfixedassettax')

        # Deleting model 'PayMiscellaneousFee'
        db.delete_table(u'jtax_paymiscellaneousfee')

        # Deleting model 'PendingPayment'
        db.delete_table(u'jtax_pendingpayment')

        # Deleting model 'Setting'
        db.delete_table(u'jtax_setting')

        # Deleting model 'MultipayReceipt'
        db.delete_table(u'jtax_multipayreceipt')

        # Deleting model 'MultipayReceiptPaymentRelation'
        db.delete_table(u'jtax_multipayreceiptpaymentrelation')

        # Deleting model 'Installment'
        db.delete_table(u'jtax_installment')


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
        u'jtax.declaredvalue': {
            'Meta': {'object_name': 'DeclaredValue'},
            'accepted': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'amount': ('django.db.models.fields.BigIntegerField', [], {}),
            'citizen': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['citizen.Citizen']", 'null': 'True', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'date_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'property': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['property.Property']", 'null': 'True', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pmauth.PMUser']", 'null': 'True', 'blank': 'True'})
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
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pmauth.PMUser']", 'null': 'True', 'blank': 'True'})
        },
        u'jtax.declaredvaluenotes': {
            'Meta': {'object_name': 'DeclaredValueNotes'},
            'citizen': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['citizen.Citizen']", 'null': 'True', 'blank': 'True'}),
            'date_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'declared_value': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['jtax.DeclaredValue']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'note': ('django.db.models.fields.TextField', [], {}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pmauth.PMUser']", 'null': 'True', 'blank': 'True'})
        },
        u'jtax.fee': {
            'Meta': {'object_name': 'Fee'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'business': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['asset.Business']", 'null': 'True', 'blank': 'True'}),
            'citizen': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['citizen.Citizen']", 'null': 'True', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'date_time': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'auto_now_add': 'True', 'blank': 'True'}),
            'due_date': ('django.db.models.fields.DateField', [], {}),
            'fee_type': ('django.db.models.fields.CharField', [], {'max_length': '25'}),
            'i_status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_paid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'period_from': ('django.db.models.fields.DateTimeField', [], {}),
            'period_to': ('django.db.models.fields.DateTimeField', [], {}),
            'property': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['property.Property']", 'null': 'True', 'blank': 'True'}),
            'remaining_amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '20', 'decimal_places': '2', 'blank': 'True'}),
            'staff_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'subbusiness': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['asset.SubBusiness']", 'null': 'True', 'blank': 'True'}),
            'submit_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'submit_details': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'})
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
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pmauth.PMUser']", 'null': 'True', 'blank': 'True'}),
            'village': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['property.Village']", 'null': 'True', 'blank': 'True'})
        },
        u'jtax.installment': {
            'Meta': {'object_name': 'Installment'},
            'amount': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '2'}),
            'due': ('django.db.models.fields.DateField', [], {}),
            'fee': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'installments'", 'to': u"orm['jtax.Fee']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'payed': ('django.db.models.fields.DecimalField', [], {'default': '0.0', 'max_digits': '20', 'decimal_places': '2'})
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
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pmauth.PMUser']", 'null': 'True', 'blank': 'True'})
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
            'staff': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pmauth.PMUser']", 'null': 'True', 'blank': 'True'})
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
            'staff': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pmauth.PMUser']", 'null': 'True', 'blank': 'True'})
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
            'staff': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pmauth.PMUser']", 'null': 'True', 'blank': 'True'})
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
            'staff': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pmauth.PMUser']", 'null': 'True', 'blank': 'True'})
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
            'staff': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pmauth.PMUser']", 'null': 'True', 'blank': 'True'}),
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
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': "orm['pmauth.PMUser']", 'null': 'True', 'blank': 'True'})
        },
        u'jtax.propertytaxitem': {
            'Meta': {'object_name': 'PropertyTaxItem'},
            'amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '20', 'decimal_places': '2', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'date_time': ('django.db.models.fields.DateTimeField', [], {}),
            'due_date': ('django.db.models.fields.DateField', [], {}),
            'i_status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_accepted': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_chanllenged': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_paid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_reviewed': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'period_from': ('django.db.models.fields.DateTimeField', [], {}),
            'period_to': ('django.db.models.fields.DateTimeField', [], {}),
            'plot_id': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'property': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['property.Property']", 'null': 'True', 'blank': 'True'}),
            'remaining_amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '20', 'decimal_places': '2', 'blank': 'True'}),
            'staff_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'submit_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'submit_details': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'})
        },
        u'jtax.rentalincometax': {
            'Meta': {'object_name': 'RentalIncomeTax'},
            'amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '20', 'decimal_places': '2', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'date_time': ('django.db.models.fields.DateTimeField', [], {}),
            'due_date': ('django.db.models.fields.DateField', [], {}),
            'i_status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_paid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'period_from': ('django.db.models.fields.DateTimeField', [], {}),
            'period_to': ('django.db.models.fields.DateTimeField', [], {}),
            'plot_id': ('django.db.models.fields.CharField', [], {'max_length': '50'}),
            'property': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['property.Property']", 'null': 'True', 'blank': 'True'}),
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
            'value': ('django.db.models.fields.CharField', [], {'default': "''", 'max_length': '50'})
        },
        u'jtax.tradinglicensetax': {
            'Meta': {'object_name': 'TradingLicenseTax'},
            'amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '20', 'decimal_places': '2', 'blank': 'True'}),
            'business': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['asset.Business']", 'null': 'True', 'blank': 'True'}),
            'currency': ('django.db.models.fields.CharField', [], {'max_length': '4'}),
            'date_time': ('django.db.models.fields.DateTimeField', [], {}),
            'due_date': ('django.db.models.fields.DateField', [], {'null': 'True', 'blank': 'True'}),
            'i_status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_paid': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'period_from': ('django.db.models.fields.DateTimeField', [], {}),
            'period_to': ('django.db.models.fields.DateTimeField', [], {}),
            'remaining_amount': ('django.db.models.fields.DecimalField', [], {'null': 'True', 'max_digits': '20', 'decimal_places': '2', 'blank': 'True'}),
            'staff_id': ('django.db.models.fields.IntegerField', [], {'null': 'True', 'blank': 'True'}),
            'subbusiness': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['asset.SubBusiness']", 'null': 'True', 'blank': 'True'}),
            'submit_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'submit_details': ('django.db.models.fields.CharField', [], {'max_length': '500', 'null': 'True', 'blank': 'True'})
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
        'pmauth.pmuser': {
            'Meta': {'object_name': 'PMUser', 'db_table': "'auth_pmuser'"},
            'active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'contactnumber': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'council': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['property.Council']", 'null': 'True', 'blank': 'True'}),
            'datejoined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'unique': 'True', 'max_length': '75'}),
            'firstname': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'related_name': "'user'", 'blank': 'True', 'to': "orm['pmauth.PMGroup']"}),
            'i_status': ('django.db.models.fields.CharField', [], {'default': "'active'", 'max_length': '10', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
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

    complete_apps = ['jtax']