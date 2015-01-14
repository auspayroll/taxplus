from datetime import date, datetime
from django.utils import timezone
from django.db.models import Sum

def kicukiro_ll_fees():
	return Fee.objects.filter(category__code='land_lease', status__code='active', prop__village__cell__sector__district__name__iexact='Kicukiro')



def adjust_payments(payments, date_from=None):
	fees = {}
	receipts = {}

	payments = payments.filter(status__code='active').order_by('paid_date').order_by('id')

	balance = 0
	for payment in payments:

		if not payment.receipt or not payment.paid_date:
			continue

		if date_from and date_from < payment.paid_date:
			balance = payment.bf
			continue

		payment.bf = balance

		fee = fees.get(payment.fee.pk)
		if not fee: # new fee payment
			fee = payment.fee
			fee.penalty = 0
			fee.penalty_paid = 0
			fee.interest_paid = 0
			fee.principle_paid = 0
			fee.residual_interest = 0
			fee.remaining_amount = fee.amount
			fees[fee.pk] = fee

		receipt = receipts.get(payment.pk)
		if not receipt:
			receipt = payment.receipt
			receipts[payment.pk] = receipt
			balance = balance + int(receipt.amount)

		payment.interest = 0
		payment.penalty = 0
		payment.principle = 0

		#calculate amounts owed before payment
		calc_penalty, calc_interest = fee.calc_penalty(payment.paid_date, fee.remaining_amount)
		if not fee.penalty:
			fee.penalty = calc_penalty

		payment.interest_due = calc_interest + fee.residual_interest
		fee.penalty = fee.penalty - fee.penalty_paid
		payment.penalty_due = fee.penalty
		payment.principle_due = fee.remaining_amount

		if balance <= fee.remaining_amount:
			calc_penalty, calc_interest = fee.calc_penalty(payment.paid_date, balance)
			fee.residual_interest = fee.residual_interest + calc_interest
			fee.remaining_amount = fee.remaining_amount - balance
			payment.interest = 0
			payment.principle = balance
			balance = 0

		else: # balance > remaining amount
			balance = balance - fee.remaining_amount
			payment.principle = fee.remaining_amount

			# pay off residual interest
			if fee.residual_interest > 0:
				if balance > fee.residual_interest:
					balance = balance - fee.residual_interest
					payment.interest = fee.residual_interest
					fee.residual_interest = 0
				else:
					fee.residual_interest = fee.residual_interest - balance
					payment.interest = balance
					balance = 0

			# pay off remaining interest
			calc_penalty, calc_interest = fee.calc_penalty(payment.paid_date, fee.remaining_amount)
			if balance > calc_interest:
				balance = balance - calc_interest
				payment.interest = payment.interest + calc_interest
			else:
				fee.residual_interest = fee.residual_interest + calc_interest
				balance = 0

			fee.remaining_amount = 0

		#pay off penalty
		if fee.penalty > 0 and balance > 0:
			if balance >= fee.penalty:
				balance = balance - fee.penalty
				payment.penalty = fee.penalty

			elif balance > 0:
				payment.penalty = balance
				balance = 0


		payment.credit = balance
		payment.amount = payment.penalty + payment.interest + payment.principle
		payment.save()

		fee.penalty_paid += payment.penalty
		fee.interest_paid += payment.interest
		fee.principle_paid += payment.principle

	outstanding_fees = []
	#bring interest  penalty up to date
	for pk, fee in fees.iteritems():
		calc_penalty, calc_interest = fee.calc_penalty(date.today(), fee.remaining_amount)
		if not fee.penalty:
			fee.penalty = calc_penalty
		fee.penalty = fee.penalty - fee.penalty_paid
		fee.interest = calc_interest + fee.residual_interest

		if fee.total_due <=0 and fee.amount > 0:
			fee.is_paid = True
		else:
			fee.is_paid = False
			outstanding_fees.append(fee)

		fee.submit_date =  timezone.make_aware(datetime.today(), timezone.get_default_timezone())
		fee.save()

	#update balance
	if fee.business_id:
		business = fee.business
		business.credit = balance
		business.save(update_fields=('credit',))

	elif fee.prop:
		prop = fee.prop
		prop.credit = balance
		prop.save(update_fields=('credit',))


	return balance