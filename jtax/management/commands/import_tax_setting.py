from django.core.management.base import BaseCommand, CommandError 
from django.conf import settings
from dev1 import variables
from jtax.models import *
from log.models import CronLog
import dateutil.parser
import os
from property.functions import *
from property.models import *
from asset.models import Ownership
from datetime import datetime, date, time
from jtax.models import Setting
from property.models import District, Sector, Cell, Village
from django.db import IntegrityError, transaction
import csv


sub_types=[]
class Command(BaseCommand):
    args = '<CSV data file (e.g data.csv)>'
    help = 'Import Ownership data from CSV files and .'
    name= 'Import Land Lease Script'
    
    
    def set_line_tax(self, cols, file_path):
#         sub_types=['residential', 'Commercial', 'Industrial','Nonprofit Orginations','Others','Agriculture (>2 hectares)', 'Agriculture (2 hectares to 35 hectares)'\
#                    , 'Agriculture (>35 hectares)','Forestry']
        districtid=District.objectsIgnorePermission.filter(name=cols[0], i_status="active")
        sectorid=Sector.objectsIgnorePermission.filter(name=cols[1].upper(), i_status="active", district__in=districtid)
        cellid=Cell.objects.filter(sector__in=sectorid, name=cols[2].upper(),  i_status="active")
        villageid=Village.objects.filter(cell__in=cellid, name=cols[3].upper(), i_status="active")
#         print sectorid
#         print cellid
#         print cols[3].upper()
#         print villageid
        today = date.today()
        current=datetime.now()
        for i in range(len(sub_types)):
            try:
                try:
                    newset=Setting.objects.get(tax_fee_name='land_lease_fee', sub_type=sub_types[i],sector=sectorid[0],cell=cellid[0],village=villageid[0], district=districtid[0],i_status='active')
                    newset.value=cols[i+4]
                except Setting.DoesNotExist:
                    newset=Setting(tax_fee_name='land_lease_fee', setting_name='area_and_fee_matches', sub_type=sub_types[i], value=cols[i+4], i_status='active'\
                           , valid_from=today, date_time=current, sector=sectorid[0],cell=cellid[0],village=villageid[0], district=districtid[0])
                newset.save()
            except IndexError as e:
                print e
                print cols
                print sub_types
                print sectorid
                print villageid                
                print sectorid
                print cellid
                print cellid[0].pk
                print str(len(sub_types))
                print cols[i+4]
                raise IndexError
                break

    @transaction.commit_on_success
    def handle(self, *args, **options):
        if len(args) == 0:
            file_path = os.sep.join([settings.ROOT_PATH, 'csv', 'LandLeaseFee_Nyanza.csv'])
        else:
            file_path = args[0]
            if not os.path.isfile(file_path) or file_path.find('.csv') < 0:
                print 'Invalid CSV file inputted.'
                exit()

        file = open(file_path, "rb")
        i=0;
        for line in file.readlines():
            i+=1
            cols=line.strip().split(',')
            if '' in cols:
                continue
            elif 'DISTRTRICT' in cols:
                for i in range(4,len(cols)):
                    sub_types.append(cols[i])
                continue
            else:
                print "---run---"+str(i)  
                self.set_line_tax(cols, file_path)

        misc_fees = os.sep.join([settings.ROOT_PATH, 'csv', 'nyanza_fees.csv'])
        nyanza = District.objectsIgnorePermission.filter(name='NYANZA', i_status="active")
        row = csv.reader(misc_fees)