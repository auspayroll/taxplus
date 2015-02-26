from django.core.management.base import BaseCommand, CommandError
from taxplus.models import Property, PlotBoundary

class Command(BaseCommand):
	#fixed_asset/rental_income/trading_license/cleaning_fee/market_fee/land_lease_fee
	args = ''
	help = """
	Adds entity relationship to fees
	This will be the entity responsible for fee payment

	"""
	name= 'Convert land use types'

	def handle(self, *args, **options):
		for p in Property.objects.filter(cell__sector__district__name__iexact='Kicukiro').select_related('cell'):
			pb = PlotBoundary.objects.filter(cell_code=p.cell.code.lstrip('0'), parcel_id=p.parcel_id)
			if not pb:
				print('**** No boundary found for %s' %p)
			else:
				p.plot_boundary = pb[0]
				p.save()
				print('Property %s boundary updated' % p)

		print 'completed boundary update'


