from django.core.management.base import BaseCommand, CommandError
from taxplus.models import Business, Property, Fee, PaymentReceipt, PropertyTitle, CategoryChoice, PayFee, Media as tpMedia, PMUser
from crud.models import Account, AccountHolder, BankDeposit, AccountFee, Media
from django.db.models import Q, Sum
from django.contrib.auth.models import User



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
			account = Account.objects.create(start_date=pt.date_from, end_date=pt.date_to, prop_title_id=pt.pk)
			print 'PT: %s' % pt.pk

			log.write("\n pk: %s account created, " % account.pk)


			af = AccountFee.objects.create(account=account, auto=True, period=1, fee_type=land_lease, prop=pt.prop,
				from_date=pt.date_from, to_date=pt.date_to)
			log.write("Land Lease created: %s, " % af.pk)
			medias = [m for m in tpMedia.objects.filter(prop=pt.prop)]
			new_media  = []
			for m in medias:
				title = m.title or m.description
				try:
					user = User.objects.get(username=m.user.username)
				except User.DoesNotExist:
					try:
						user = User.objects.get(username=m.user.email)
					except User.DoesNotExist:
						try:
							user = User.objects.get(email=m.user.email)
						except User.DoesNotExist:
							user = None

				nm = Media.objects.create(created_on=m.date_created, item=m.path, title=title, prop=pt.prop, user=user, old_media_id=m.pk)
				nm.payfee_id = m.payfee_id
				nm.fee_id = m.fee_id
				nm.receipt_id = m.receipt_id
				new_media.append(nm)


			for o in pt.prop_title_ownerships.all():
				if o.owner_citizen:
					account.name = o.owner_citizen.name
					account.save()
					ah = AccountHolder.objects.create(account=account, holder=o.owner_citizen)
					log.write("Account Holder %s- %s added." % (ah.pk, ah.holder) )
				elif o.owner_business:
					account.name = o.owner_business.name
					account.save()
					ah = AccountHolder.objects.create(account=account, holder=o.owner_business)
					log.write("Account Holder %s- %s added, " % (ah.pk, ah.holder) )
				else:
					account.name = str(pt.prop)

				# handle know property title payments
				payfees = PayFee.objects.filter(fee__prop_title=pt, fee__category__code='land_lease')
				for payfee in payfees:
					r = payfee.receipt
					deposit = BankDeposit.objects.create(account=account, bank_receipt_no=r.bank_receipt, bank=r.bank,
						date_banked=r.paid_date, depositor_name=r.payer_name, amount=r.amount,
						note=r.note, created=r.date_time, sector_receipt=r.sector_receipt)
					for nm in new_media:
						if payfee.pk == nm.payfee_id or payfee.fee_id == nm.fee_id or nm.receipt_id  == r.pk:
							nm.account = account
							if nm.receipt_id == r.pk:
								nm.record = deposit
							nm.save()
							print '1111111. media pk %s saved' % nm.pk
					log.write("Deposit %s created, amount %s, receipt: %s, " % (deposit.pk, deposit.amount, deposit.sector_receipt))

				#payments without property title
				pay_fees = PayFee.objects.filter(fee__category__code='land_lease', fee__prop_title__isnull=True, fee__prop=pt.prop)
				for payfee in payfees:
					r = payfee.receipt
					deposit = BankDeposit(account=account, bank_receipt_no=r.bank_receipt, bank=r.bank,
						date_banked=r.paid_date, depositor_name=r.payer_name, amount=r.amount,
						note=r.note, created=r.date_time, sector_receipt=r.sector_receipt)

					if r.paid_date < account.start_date or (account.end_date and r.paid_date > account.end_date):
						found_accounts = PropertyTitle.objects.filter(date_from__lte=r.paid_date, prop=pt.prop).filter(Q(date_to__isnull=True) | Q(date_to__gte=r.paid_date)).exclude(pk=pt.pk).order_by('-date_from')
						if not found_accounts:
							deposit.save()
					else:
						deposit.save()
						for nm in new_media:
							if payfee.pk == nm.payfee_id or payfee.fee_id == nm.fee_id or nm.receipt_id  == r.pk:
								nm.account = account
								if nm.receipt_id == r.pk:
									nm.record = deposit
								nm.save()
								print '222222222. media pk %s saved' % nm.pk





