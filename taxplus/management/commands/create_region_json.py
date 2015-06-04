from django.core.management.base import BaseCommand, CommandError
from taxplus.models import District, Sector, Cell, Village
import json as js
import os
from django.conf import settings



class Command(BaseCommand):
	#fixed_asset/rental_income/trading_license/cleaning_fee/market_fee/land_lease_fee
	args = ''
	help = """
	Adds entity relationship to fees
	This will be the entity responsible for fee payment

	"""
	name= 'Convert land use types'

	def handle(self, *args, **options):
		json = {}
		for d in District.objects.all():
			json[d.pk] = { 'n': d.name, 's':{} }
			for s in d.sector_set.all():
				json[d.pk]['s'][s.pk] = { 'n': s.name, 'c':{} }
				for c in s.cell_set.all():
					json[d.pk]['s'][s.pk]['c'][c.pk] = { 'n':c.name, 'v':[]}
					for v in c.village_set.all():
						json[d.pk]['s'][s.pk]['c'][c.pk]['v'].append((v.pk, v.name))

		data = js.dumps(json, separators=[',',':'])
		file_path = os.path.join(settings.PROJECT_DIR, 'static', 'region.json')
		f = open(file_path, 'w')
		f.write(data)
		f.close()





