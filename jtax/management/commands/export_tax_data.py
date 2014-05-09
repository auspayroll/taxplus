"""
This script export tax data to a specific CSV file.
Currently the available export option are:
- Land Lease
"""
from django.core.management.base import BaseCommand, CommandError 
from django.conf import settings
from dev1 import variables
from jtax.models import *
from log.models import CronLog
import dateutil.parser
import os
from property.functions import *
from property.models import *
from property.mappers.OwnershipMapper import OwnershipMapper
from datetime import datetime, date, time
from django.db.models import Q
from jtax.shared_functions import get_tax_type_from_tax_item

class Command(BaseCommand):

	args = '<tax_type (e.g all_taxes,land_lease,fixed_asset, incomplete)> <year (e.g. 2013)> <paid_unpaid (e.g. paid/unpaid/both)'
	help = 'Export tax data to CSV file'
	name= 'Tax Data Exporter'

	tax_types = ['all_taxes','land_lease','incomplete','fixed_asset','rental_income','land_lease_contact']
	years = ['2013', '2012']

	file_path = 'jtax/management/data/'

	#currently export taxes in Kicukiro (65), Nyarugenge (2), Remera (3)
	sector_ids = [65, 2, 3]

	def handle(self, *args, **options):	
		if len(args) < 2:
			print 'Please input the tax_type and year to export.'
			exit()
		else:
			tax_type = args[0]
			if tax_type not in self.tax_types:
				print 'Invalid tax type inputted.'
				exit()

			year = args[1]
			if year not in self.years:
				print 'Invalid year inputted.'
				exit()

			paid_status = None
			if len(args) > 2:
				if args[2] == 'paid':
					paid_status = True
				elif args[2] == 'unpaid':
					paid_status = False

			#get list of taxes 
			taxes = None
			rows = []
			error_rows = []

			#add heading row
			heading = '"TAX TYPE", "TAX / INCOMPLETE_PAYMENT ID","UPI","ADDRESS","AREA SIZE (BOUNDARY)","AREA SIZE","AREA SIZE TYPE","SECTOR","DISTRICT","SURNAME","GIVEN NAME","ID CARD NUMBER","BUSINESS","TIN","PAID","PAID AMOUNT","PAID ON"'
			rows.append(heading)

			if tax_type == 'land_lease_contact':
				heading = '"UPI","ADDRESS","SECTOR","DISTRICT","SURNAME","GIVEN NAME","ID CARD NUMBER","BUSINESS","TIN","PHONE 1","PHONE 2","EMAIL"'
				rows = [heading]
				properties = Property.objectsIgnorePermission.filter(status_id=1,is_land_lease=True,sector__id__in=self.sector_ids)
				print 'TOTAL PROPERTIES FOUND: ' + str(len(properties))
				print 'Generating CSV...'
				print '------'
				if properties:
					for k,i in  enumerate(properties):
						try:
							row = self.generateLandLeaseContactRow(i)
							rows.append(row)
							#print k
							#if k > 5:
							#	exit()
							#	break
						except Exception as e:    
							print ' - Error at' + str(k) + ' - ID' + str(i.id)
							print '%s (%s)' % (e.message, type(e))
							error_rows.append(str(k) + ' - Fee ID' + i.id)
							continue

			if tax_type == 'all_taxes' or tax_type == 'fixed_asset':

				taxes = PropertyTaxItem.objects.filter(i_status='active', property__isnull=False,period_to__year=int(year),property__sector__id__in=self.sector_ids)
				if paid_status:
					taxes = taxes.filter(is_paid=paid_status)
				taxes = taxes.select_related('property','property__cell','property__sector')
				print 'TOTAL FIXED ASSET TAXES FOUND: ' + str(len(taxes))
				print 'Generating CSV...'
				print '------'
				if taxes:
					for k,i in  enumerate(taxes):
						try:
							row = self.generateRow(i)
							rows.append(row)
							#print k
							#if k > 5:
							#	exit()
							#	break
						except Exception as e:    
							print ' - Error at' + str(k) + ' - ID' + str(i.id)
							print '%s (%s)' % (e.message, type(e))
							error_rows.append(str(k) + ' - Fee ID' + i.id)
							continue

			if tax_type == 'all_taxes' or tax_type == 'rental_income':

				taxes = RentalIncomeTax.objects.filter(i_status='active', property__isnull=False,due_date__year=int(year),property__sector__id__in=self.sector_ids)
				if paid_status:
					taxes = taxes.filter(is_paid=paid_status)
				taxes = taxes.select_related('property','property__cell','property__sector')		
				
				print 'TOTAL RENTAL INCOME TAXES FOUND: ' + str(len(taxes))
				print 'Generating CSV...'
				print '------'
				if taxes:
					for k,i in  enumerate(taxes):
						try:
							row = self.generateRow(i)
							rows.append(row)
							#print k
							#if k > 5:
							#	break
						except Exception as e:    
							print ' - Error at' + str(k) + ' - ID' + str(i.id)
							print '%s (%s)' % (e.message, type(e))
							error_rows.append(str(k) + ' - Fee ID' + i.id)
							continue

			if tax_type == 'all_taxes' or tax_type == 'trading_license':
				taxes = TradingLicenseTax.objects.filter(Q(business__isnull=False)|Q(subbusiness__isnull=False),i_status='active',period_to__year=int(year)).filter(Q(business__sector__id__in=self.sector_ids)|Q(subbusiness__business__sector__id__in=self.sector_ids))
				if paid_status:
					taxes = taxes.filter(is_paid=paid_status)
				taxes = taxes.select_related('business','subbusiness','business__sector','business__sector__district','subbusiness__business__sector','subbusiness__business__sector__district')
				
				print 'TOTAL TRADING LICENSE TAXES FOUND: ' + str(len(taxes))
				print 'Generating CSV...'
				print '------'
				if taxes:
					for k,i in  enumerate(taxes):
						try:
							row = self.generateRow(i)
							rows.append(row)
							#print k
							#if k > 5:
							#	break
						except Exception as e:    
							print ' - Error at' + str(k) + ' - ID' + str(i.id)
							print '%s (%s)' % (e.message, type(e))
							error_rows.append(str(k) + ' - Fee ID' + i.id)
							continue

			if tax_type == 'all_taxes' or tax_type == 'land_lease':
				taxes = Fee.objects.filter(property__isnull=False,fee_type='land_lease',i_status='active',period_to__year=int(year),property__sector__id__in=self.sector_ids)
				if paid_status:
					taxes = taxes.filter(is_paid=paid_status)
				taxes = taxes.select_related('property','property__cell','property__sector')
				
				print 'TOTAL LAND LEASE FEES FOUND: ' + str(len(taxes))
				print 'Generating CSV...'
				print '------'
				if taxes:
					for k,i in  enumerate(taxes):
						try:
							row = self.generateRow(i)
							rows.append(row)
							#print k
							#if k > 5:
							#	break
						except Exception as e:    
							print ' - Error at' + str(k) + ' - Fee ID' + str(i.id)
							print '%s (%s)' % (e.message, type(e))
							error_rows.append(str(k) + ' - Fee ID' + i.id)
							continue

			if tax_type == 'all_taxes' or tax_type == 'incomplete':
				#print Fee.objects.filter(fee_type='land_lease',i_status='active', property__isnull=False,period_to__year=int(year)).query
				#also include incomplete payments
				if not paid_status or paid_status == 'unpaid':
					incomplete_payments = IncompletePayment.objectsIgnorePermission.filter(i_status='active',period_to__year= int(year),sector__id__in=self.sector_ids)
					incomplete_payments = incomplete_payments.select_related('business','subbusiness','sector','sector__district')
					print 'TOTAL INCOMPLETE PAYMENT FOUND: ' + str(len(incomplete_payments))
					print 'Generating CSV...'
					print '------'

					if incomplete_payments:
						for k,i in  enumerate(incomplete_payments):
							try:
								row = self.generateRow(i)
								rows.append(row)
								#print k
								#if k > 5:
								#	break
							except Exception as e:    
								print ' - Error at' + str(k) + ' - IP ID' + str(i.id)
								print '%s (%s)' % (e.message, type(e))
								error_rows.append(str(k) + ' - IP ID' + i.id)
								continue

			#start saving csv file
			#save data into the csv
			if paid_status:
				file_name = tax_type + '_' + args[2] + '_' + year + '_' + datetime.now().strftime("%Y%m%d_%H%M") + '.csv'
				error_file_name = tax_type + '_' + args[2] + '_' + year + '_' + datetime.now().strftime("%Y%m%d_%H%M") + '.csv'
			else:
				file_name = tax_type + '_' + year + '_' + datetime.now().strftime("%Y%m%d_%H%M") + '.csv'
				error_file_name = tax_type + '_' + year + '_' + datetime.now().strftime("%Y%m%d_%H%M") + '.csv'
			handle1=open(self.file_path + file_name ,'w+')
			handle1.write("\n".join(rows).encode('ascii', 'ignore'))
			handle1.close()

			if len(error_rows) > 1:
				#save data into the csv
				handle1=open(self.file_path + error_file_name ,'w+')
				handle1.write("\n".join(error_rows).encode('ascii', 'ignore'))
				handle1.close()

			print 'DONE'


	def generateRow(self,tax):
		#row data is in order: "TAX TYPE","TAX / INCOMPLETE_PAYMENT ID","UPI","ADDRESS","SIZE (BOUNDARY)","SIZE","SIZE TYPE","SECTOR","DISTRICT","SURNAME","GIVEN NAME","ID CARD NUMBER","BUSINESS","TIN","PAID","PAID AMOUNT","PAID ON"
		cols = {
		  'tax_type':get_tax_type_from_tax_item(tax),
		  'id':str(tax.id),
		  'upi': '',
		  'address': '',
		  'size_boundary': '',
		  'size': '',
		  'size_type': '',
		  'sector': '',
		  'district': '',
		  'surname': '',
		  'given_name': '',
		  'citizen_id': '',
		  'business': '',
		  'tin': '',
		  'paid': 'N',
		  'paid_amount': '',
		  'paid_on': '',
		}

		if type(tax) is PropertyTaxItem or type(tax) is RentalIncomeTax or (type(tax) is Fee and tax.fee_type == 'land_lease'):
			property = tax.property
			cols['upi'] = property.getUPI()	
			cols['address'] = property.getDisplayName()
			if property.boundary:
				cols['size_boundary'] = str(property.boundary.shape_area)

			if property.size_sqm:
				cols['size'] = str(property.size_sqm)
				cols['size_type'] = 'sqm'
			else:
				cols['size'] = str(property.size_hectare)
				cols['size_type'] = 'hectare'

			if property.sector:
				cols['sector'] = property.sector.name
				cols['district'] = property.sector.district.name

			ownership_objs = OwnershipMapper.getCurrentOwnershipsByPropertyId(property.id)
			if ownership_objs:
				#only display the first owner
				if ownership_objs[0].owner_citizen:
					owner = ownership_objs[0].owner_citizen
					cols['surname'] = owner.last_name
					cols['given_name'] = owner.first_name
					cols['citizen_id'] = owner.citizen_id
				elif ownership_objs[0].owner_business:
					cols['business'] = ownership_objs[0].owner_business.name
					cols['tin'] = ownership_objs[0].owner_business.tin
			if tax.is_paid:
				cols['paid'] = 'Y'
				payments = tax.payments.all()
				payment = payments[0]
				cols['paid_amount'] = str(payment.amount)
				cols['paid_on'] = payment.date_time.strftime('%d/%m/%Y')
			else:
				if type(tax) is Fee and tax.fee_type == 'land_lease' and cols['size'] != None and cols['size'] != '' and cols['size'] != 'None':
					cols['paid_amount'] = str(round(float(cols['size']) * 70))
		elif type(tax) is TradingLicenseTax or (type(tax) is Fee and tax.fee_type in ('cleaning','market')):
			business = None
			if tax.subbusiness:
				cols['business'] = tax.subbusiness.business.name + ' - ' + tax.subbusiness.branch
				cols['tin'] = tax.subbusiness.business.tin
				business = tax.subbusiness.business
			elif tax.business:
				cols['business'] = tax.business.name
				cols['tin'] = tax.business.tin
				business = tax.business

			cols['address'] = business.address

			if business.sector:
				cols['sector'] = business.sector.name
				cols['district'] = business.sector.district.name

			ownership_objs = business.owners.filter(i_status='active')
			if ownership_objs:
				#only display the first owner
				owner = ownership_objs[0].owner_citizen
				cols['surname'] = owner.last_name
				cols['given_name'] = owner.first_name
				cols['citizen_id'] = owner.citizen_id

			if tax.is_paid:
				cols['paid'] = 'Y'
				payments = tax.payments.all()
				payment = payments[0]
				cols['paid_amount'] = str(payment.amount)
				cols['paid_on'] = payment.date_time.strftime('%d/%m/%Y')
		elif type(tax) is IncompletePayment:
			cols['id'] = 'IP ' + str(tax.id)
			cols['tax_type'] = tax.tax_type
			if tax.sector:
				cols['sector'] = tax.sector.name
				cols['district'] = tax.sector.district.name
			if tax.citizen_id:
				citizens = Citizen.objects.filter(citizen_id=tax.citizen_id,status__name='Active')
				if citizens:
					owner = citizens[0]
					cols['surname'] = owner.last_name
					cols['given_name'] = owner.first_name
					cols['citizen_id'] = owner.citizen_id
			if tax.business:
				cols['business'] = tax.business.name
				cols['tin'] = tax.business.tin
			if tax.subbusiness:
				cols['business'] = cols['business'] + ' - ' + tax.subbusiness.branch

			if tax.paid_amount:
				cols['paid_amount'] = str(tax.paid_amount)
			if tax.paid_date:
				cols['paid_on'] = tax.paid_date.strftime('%d/%m/%Y')
		row_data = [cols['tax_type'],
					cols['id'],
					cols['upi'],
					cols['address'],
					cols['size_boundary'],
					cols['size'],
					cols['size_type'],
					cols['sector'],
					cols['district'],
					cols['surname'],
					cols['given_name'],
					cols['citizen_id'],
					cols['business'],
					cols['tin'],
					cols['paid'],
					cols['paid_amount'],
					cols['paid_on']]

		#replace all None value with ''
		for k,i in enumerate(row_data):
			if i == None:
				row_data[k] = ''

		#print row_data
		row = ''
		try:
			row = '","'.join(row_data)
			row = '"' + row + '"'
		except Exception, e:
			print row_data
			print str(e)
			exit()
		#append "" on both end
		
		#print row
		#print '===='
		return row

	
	def generateLandLeaseContactRow(self,property):
		#row data is in order: "UPI","ADDRESS","SECTOR","DISTRICT","SURNAME","GIVEN NAME","ID CARD NUMBER","BUSINESS","TIN","PHONE 1","PHONE 2","EMAIL"
		cols = {		  
		  'upi': '',
		  'address': '',
		  'sector': '',
		  'district': '',
		  'surname': '',
		  'given_name': '',
		  'citizen_id': '',
		  'business': '',
		  'tin': '',
		  'phone_1': '',
		  'phone_2': '',
		  'email': '',
		}


		cols['upi'] = property.getUPI()	
		cols['address'] = property.getDisplayName()
		
		if property.sector:
			cols['sector'] = property.sector.name
			cols['district'] = property.sector.district.name

		ownership_objs = OwnershipMapper.getCurrentOwnershipsByPropertyId(property.id)
		if ownership_objs:
			#only display the first owner
			if ownership_objs[0].owner_citizen:
				owner = ownership_objs[0].owner_citizen
				cols['surname'] = owner.last_name
				cols['given_name'] = str(owner.id) + '  -  '  + owner.first_name
				cols['citizen_id'] = owner.citizen_id
				cols['phone_1'] = owner.phone_1
				cols['phone_2'] = owner.phone_2
				cols['email'] = owner.email

			elif ownership_objs[0].owner_business:
				cols['business'] = ownership_objs[0].owner_business.name
				cols['tin'] = ownership_objs[0].owner_business.tin
				cols['phone_1'] = ownership_objs[0].owner_business.phone1
				cols['phone_2'] = ownership_objs[0].owner_business.phone2
				cols['email'] = ownership_objs[0].owner_business.email

		row_data = [cols['upi'],
					cols['address'],					
					cols['sector'],
					cols['district'],
					cols['surname'],
					cols['given_name'],
					cols['citizen_id'],
					cols['business'],
					cols['tin'],
					cols['phone_1'],
					cols['phone_2'],
					cols['email']]

		#replace all None value with ''
		for k,i in enumerate(row_data):
			if i == None:
				row_data[k] = ''

		#print row_data
		row = ''
		try:
			row = '","'.join(row_data)
			row = '"' + row + '"'
		except Exception, e:
			print row_data
			print str(e)
			exit()
		#append "" on both end
		
		#print row
		#print '===='
		return row
