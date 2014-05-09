"""
This script generate tax items for all citizens & businesses in the system for current year.
SHOULD BE USED WITH CAUTION AS LOT OF LEGACY DATA IS MISSING ATM.
"""

from django.core.management.base import BaseCommand
from jtax.models import *
from jtax.models import Setting

class Command(BaseCommand):
    def handle(self, *args, **options):
        Setting.objects.create(tax_fee_name='Public Cemetary Fee', setting_name = 'other payment', valid_from = '2012-01-01')
        Setting.objects.create(tax_fee_name='Parking Fees', setting_name = 'other payment', valid_from = '2012-01-01')
        Setting.objects.create(tax_fee_name='Public Parking Fees', setting_name = 'other payment', valid_from = '2012-01-01')
        Setting.objects.create(tax_fee_name='Parking Fees on Boats', setting_name = 'other payment', valid_from = '2012-01-01')
        Setting.objects.create(tax_fee_name='Civil Marriage Fee', setting_name = 'other payment', value='10000', valid_from = '2012-01-01')

        Setting.objects.create(tax_fee_name='Immovable Property Fees', setting_name = 'other payment', valid_from = '2012-01-01')
        Setting.objects.create(tax_fee_name='Immovable Property Fees', setting_name = 'other payment', sub_type = 'change of ownership', value='20000', valid_from = '2012-01-01')
        Setting.objects.create(tax_fee_name='Immovable Property Fees', setting_name = 'other payment', sub_type = 'Registration of Debt Mortgage', value='1200', valid_from = '2012-01-01')
        Setting.objects.create(tax_fee_name='Immovable Property Fees', setting_name = 'other payment', sub_type = 'Cancellation of Debt Mortgage', value='1200', valid_from = '2012-01-01')
        Setting.objects.create(tax_fee_name='Immovable Property Fees', setting_name = 'other payment', sub_type = 'Review Assignment of Debt Mortgage', value='1200', valid_from = '2012-01-01')
        Setting.objects.create(tax_fee_name='Immovable Property Fees', setting_name = 'other payment', sub_type = 'Auth for Repair or Rehabilitation of House', valid_from = '2012-01-01')
        Setting.objects.create(tax_fee_name='Immovable Property Fees', setting_name = 'other payment', sub_type = 'Auth for Erection of Fence', valid_from = '2012-01-01')
        Setting.objects.create(tax_fee_name='Immovable Property Fees', setting_name = 'other payment', sub_type = 'Building Permit', valid_from = '2012-01-01')
        Setting.objects.create(tax_fee_name='Immovable Property Fees', setting_name = 'other payment', sub_type = 'Create Land Lease Title', value='5000', valid_from = '2012-01-01')
        Setting.objects.create(tax_fee_name='Immovable Property Fees', setting_name = 'other payment', sub_type = 'Change Land Lease Title', value='5000', valid_from = '2012-01-01')
        Setting.objects.create(tax_fee_name='Immovable Property Fees', setting_name = 'other payment', sub_type = 'Map Boundaries', value='10000', valid_from = '2012-01-01')
        Setting.objects.create(tax_fee_name='Immovable Property Fees', setting_name = 'other payment', sub_type = 'Shares Certificates or Changing Names', value='20000', valid_from = '2012-01-01')

        Setting.objects.create(tax_fee_name='Official Certificates and Documents', setting_name = 'other payment', valid_from = '2012-01-01')
        Setting.objects.create(tax_fee_name='Official Certificates and Documents', setting_name = 'other payment', sub_type='Civil Status Certificate', value='3000', valid_from = '2012-01-01')
        Setting.objects.create(tax_fee_name='Official Certificates and Documents', setting_name = 'other payment', sub_type='Copy of Civil Status Certificate', value='2400', valid_from = '2012-01-01')
        Setting.objects.create(tax_fee_name='Official Certificates and Documents', setting_name = 'other payment', sub_type='Short Civil Status Certificate', value='1200', valid_from = '2012-01-01')
        Setting.objects.create(tax_fee_name='Official Certificates and Documents', setting_name = 'other payment', sub_type='Living or Death Certificate', value='1200', valid_from = '2012-01-01')
        Setting.objects.create(tax_fee_name='Official Certificates and Documents', setting_name = 'other payment', sub_type='Identity Certificate', value='500', valid_from = '2012-01-01')
        Setting.objects.create(tax_fee_name='Official Certificates and Documents', setting_name = 'other payment', sub_type='Birth Certificate', value='500', valid_from = '2012-01-01')
        Setting.objects.create(tax_fee_name='Official Certificates and Documents', setting_name = 'other payment', sub_type='Marriage Certificate', value='500', valid_from = '2012-01-01')
        Setting.objects.create(tax_fee_name='Official Certificates and Documents', setting_name = 'other payment', sub_type='Celibacy Certificate', value='500', valid_from = '2012-01-01')
        Setting.objects.create(tax_fee_name='Official Certificates and Documents', setting_name = 'other payment', sub_type='Authentification of Documents', value='1500', valid_from = '2012-01-01')
        Setting.objects.create(tax_fee_name='Official Certificates and Documents', setting_name = 'other payment', sub_type='Notarization of By-Laws', value='5000', valid_from = '2012-01-01')
        Setting.objects.create(tax_fee_name='Official Certificates and Documents', setting_name = 'other payment', sub_type='Notarization of Agreements', value='2000', valid_from = '2012-01-01')
        Setting.objects.create(tax_fee_name='Official Certificates and Documents', setting_name = 'other payment', sub_type='Authorisation of Signature', value='1200', valid_from = '2012-01-01')
        Setting.objects.create(tax_fee_name='Official Certificates and Documents', setting_name = 'other payment', sub_type='Public Auction of Private Immovable Property', value='5000', valid_from = '2012-01-01')
        Setting.objects.create(tax_fee_name='Official Certificates and Documents', setting_name = 'other payment', sub_type='Marriage Booklet', value='1500', valid_from = '2012-01-01')
        Setting.objects.create(tax_fee_name='Official Certificates and Documents', setting_name = 'other payment', sub_type='Other Certificate', value='1500', valid_from = '2012-01-01')

        Setting.objects.create(tax_fee_name='Authorisation to Make Bricks or Roof Tiles', setting_name = 'other payment', value='10000', valid_from = '2012-01-01')
        Setting.objects.create(tax_fee_name='Billboards', setting_name = 'other payment', valid_from = '2012-01-01')