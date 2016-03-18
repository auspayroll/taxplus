from django.core.management.base import BaseCommand, CommandError
from taxplus.models import Business, Property, Fee, PaymentReceipt, PropertyTitle, CategoryChoice, PayFee
from crud.models import Account, AccountHolder, BankDeposit, AccountFee
from django.db.models import Q, Sum



class Command(BaseCommand):
	#fixed_asset/rental_income/trading_license/cleaning_fee/market_fee/land_lease_fee
	args = ''
	help = """
	Adds entity relationship to fees
	This will be the entity responsible for fee payment

	"""

	def handle(self, *args, **options):
		log = open('convert2taxplus.log', 'w')
		land_lease = CategoryChoice.objects.get(category__code='fee_type', code='land_lease')
		for pt in PropertyTitle.objects.all().order_by('id'):
			account = Account.objects.create(start_date=pt.date_from, end_date=pt.date_to)
			print 'PT: %s' % pt.pk

			log.write("\n pk: %s account created, " % account.pk)


			af = AccountFee.objects.create(account=account, auto=True, period=1, fee_type=land_lease, prop=pt.prop, from_date=pt.date_from, to_date=pt.date_to)
			log.write("Land Lease created: %s, " % af.pk)


			for o in pt.prop_title_ownerships.all():
				if o.owner_citizen:
					account.name = o.owner_citizen.name
					account.save()
					ah = AccountHolder.objects.create(account=account, holder=o.owner_citizen)
					log.write("Account Holder %s- %s added." % (ah.pk, ah.holder) )
				if o.owner_business:
					account.name = o.owner_business.name
					account.save()
					ah = AccountHolder.objects.create(account=account, holder=o.owner_business)
					log.write("Account Holder %s- %s added, " % (ah.pk, ah.holder) )

				# handle know property title payments
				payfees = PayFee.objects.filter(fee__prop_title=pt, fee__category__code='land_lease')
				for payfee in payfees:
					r = payfee.receipt
					deposit = BankDeposit.objects.create(account=account, bank_receipt_no=r.bank_receipt, bank=r.bank,
						date_banked=r.paid_date, depositor_name=r.payer_name, amount=r.amount,
						note=r.note, created=r.date_time, sector_receipt=r.sector_receipt)
					log.write("Deposit %s created, amount %s, receipt: %s, " % (deposit.pk, deposit.amount, deposit.sector_receipt))

				pay_fees = PayFee.objects.filter(fee__category__code='land_lease', fee__prop_title__isnull=True, fee__prop=pt.prop)
				for payfee in payfees:
					r = payfee.receipt
					deposit = BankDeposit(account=account, bank_receipt_no=r.bank_receipt, bank=r.bank,
						date_banked=r.paid_date, depositor_name=r.payer_name, amount=r.amount,
						note=r.note, created=r.date_time, sector_receipt=r.sector_receipt)

					if r.paid_date < account.start_date or (account.end_date and r.paid_date > account.end_date):
						print '*********************'
						found_accounts = PropertyTitle.objects.filter(date_from__lte=r.paid_date, prop=pt.prop).filter(Q(date_to__isnull=True) | Q(date_to__gte=r.paid_date)).exclude(pk=pt.pk).order_by('-date_from')
						if not found_accounts:
							deposit.save()
							print 'hooorayyy!!!!!!!!!!!!!!!'
					else:
						deposit.save()
						print '#############################'





