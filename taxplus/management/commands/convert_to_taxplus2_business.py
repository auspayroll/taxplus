from django.core.management.base import BaseCommand, CommandError
from taxplus.models import Property, Fee, PaymentReceipt, PropertyTitle, CategoryChoice, PayFee, Media as tpMedia, PMUser, Ownership
from crud.models import Account, AccountHolder, BankDeposit, AccountFee, Media, Business
from django.db.models import Q, Sum
from django.contrib.auth.models import User


def get_user(pm_user):
	if not pm_user:
		return None
	try:
		user = User.objects.get(username=pm_user.username)
	except User.DoesNotExist:
		try:
			user = User.objects.get(username=pm_user.email)
		except User.DoesNotExist:
			try:
				user = User.objects.get(email=pm_user.email)
			except User.DoesNotExist:
				user = None
	return user


class Command(BaseCommand):
	#fixed_asset/rental_income/trading_license/cleaning_fee/market_fee/land_lease_fee
	args = ''
	help = """
	Adds entity relationship to fees
	This will be the entity responsible for fee payment

	"""


	def handle(self, *args, **options):
		#log = open('convert2taxplus.log', 'w')
		cleaning = CategoryChoice.objects.get(category__code='fee_type', code='cleaning')
		for b in Business.objects.all().order_by('id'):
			account = Account.objects.create(name=b.name, start_date=b.date_started, end_date=b.closed_date, phone=b.phone1 or b.phone2, email=b.email, business_id=b.pk)
			print 'Business: %s, Account %s' % (b.pk, account.pk)

			if b.business_category_id:
				sub_category = CategoryChoice.objects.get(code="cat%s" % b.business_category_id, category__code='cleaning_rate')
			else:
				sub_category = CategoryChoice.objects.get(code="cat1", category__code='cleaning_rate')

			af = AccountFee.objects.create(account=account, auto=True, period=12, fee_type=cleaning, fee_subtype=sub_category,
				from_date=account.start_date, to_date=account.end_date, village=b.village, cell=b.cell, sector=b.sector)

			print 'Account Fee created: %s' % af.pk


			medias = [m for m in tpMedia.objects.filter(business__pk=b.pk)]
			new_media  = []
			for m in medias:
				title = m.title or m.description
				user = get_user(m.user)
				nm = Media.objects.create(created_on=m.date_created, item=m.path, title=title, account=account, user=user, old_media_id=m.pk)
				print 'media %s created' % nm.pk
				nm.payfee_id = m.payfee_id
				nm.fee_id = m.fee_id
				nm.receipt_id = m.receipt_id
				new_media.append(nm)
			receipts = []

			AccountHolder.objects.create(account=account, holder=b)
			for o in Ownership.objects.filter(asset_business__pk=b.pk):
				if o.owner_citizen:
					AccountHolder.objects.create(account=account, holder=o.owner_citizen)
				elif o.owner_business:
					AccountHolder.objects.create(account=account, holder=o.owner_business)

			# handle know property title payments
			payfees = PayFee.objects.filter(fee__business__pk=b.pk, fee__category__code='cleaning')
			for payfee in payfees:
				r = payfee.receipt
				if r.pk not in receipts:
					receipts.append(r.pk)
					user = get_user(r.user)
					deposit = BankDeposit.objects.create(account=account, bank_receipt_no=r.bank_receipt, bank=r.bank,
						date_banked=r.paid_date, depositor_name=r.payer_name, amount=r.amount, status_id=r.status_id,
						note=r.note, created=r.date_time, sector_receipt=r.sector_receipt, old_receipt_id=r.pk, user=user)
					print 'deposit %s' % deposit.pk

				for nm in new_media:
					if payfee.pk == nm.payfee_id or payfee.fee_id == nm.fee_id or nm.receipt_id  == r.pk:
						if nm.receipt_id == r.pk:
							nm.record = deposit
						nm.save()
						print '1111111. media pk %s saved' % nm.pk

			account.transactions(update=True)


