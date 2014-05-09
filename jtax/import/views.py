from django.shortcuts import render_to_response
from django.template import RequestContext
from django.shortcuts import render_to_response, get_object_or_404
from django.http import Http404, HttpResponseRedirect
from django.core.urlresolvers import reverse 
from django.contrib import messages
from django.conf import settings
from dev1 import variables
from log.mappers.LogMapper import LogMapper
from property.models import Boundary
from django.conf import settings
from django.contrib.gis.geos import Point, GEOSGeometry, Polygon


def index(request):
	"""
	Import boundary UPI data & populate the existing boundary table
	"""   
	#get list of boundary data from data file
	print 'fetching boundary data from file...'
	data = []
	FILE = settings.MEDIA_ROOT + "data.txt"
	#count = 1
	f = open( FILE, 'r')
	for line in f:
		row = line.split('|')
		data.append(row)
		"""
		if count > 6:
			break
		count = count + 1
		"""
	f.close()
	print '... fetched ' + str(len(data)) + ' rows'
	print 'start matching boundary...'
	boundaries = Boundary.objects.filter(type__exact='official',polygon_imported__isnull=False).order_by('id')
	#do a compare between earch boundaries and the data to get the boundary UPI info
	#Each data row is a list with the following item index:
	row_index = {0:'ogc_fid',
				1:'wkb_geometry',
				2:'objectid',
				3:'parcel_id',
				4:'province',
				5:'district',
				6:'sector',
				7:'cell',
				8:'village',
				9:'cell_code',
				10:'shape_leng',
				11:'shape_area'}

	count = 0
	failList = []
	for b in boundaries:
		"""
		if count > 5:
			break
		"""
		count = count +1

		print '-------------------'
		print str(count) + ' - processing boundary ' + str(b.id)
		#get row that match this boundary data
		for l in data:
			try:
				if b.polygon_imported.hexewkb == l[1]:
					#populate boundary
					b.location_type = 'property'
					b.parcel_id = l[3]
					b.province = l[4].upper()
					b.district = l[5].upper()
					b.sector = l[6].upper()
					b.cell = l[7].upper()
					b.village = l[8].upper()
					b.cell_code = l[9]
					b.shape_leng = l[10]
					b.shape_area = l[11]
					b.save()
					print 'Populated with ogc_fid ' + l[0]
					break;					
			except Exception as e:
				print 'Failure to match ' + str(b.id) + ' - ' + e.message + ' [' + str(type(e)) + ']'
				failList.append(b.id)
				continue

		print 'DONE'

	print 'FINISHED - Failed matches: '	+ str(len(failList)) + ':'
	print failList.join(',')

