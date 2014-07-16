from django.db import models
from asset.models import Business, SubBusiness

# Create your models here.

class StatusCategory(models.Model):
	code = models.CharField(max_length=20)
	name  = models.CharField(max_length=100)


class Status(models.Model):
	code = models.CharField(max_length=20)
	name = models.CharField(max_length=100)
	category = models.ForeignKey(StatusCategory)


class Entity(models.Model):
	category = models.ForeignKey(Status)


class Tax(models.Model):
	pass
	"""
	tax_type = models.ForeignKey(TaxType)
	amount = models.DecimalField(max_digits = 20, decimal_places = 2)
	remaining = models.DecimalField(max_digits = 20, decimal_places = 2, default=0)
	due_date = models.DateField(help_text="The date this tax item is due.")
	is_paid = models.BooleanField(help_text="Whether tax is payed.")
	property = models.ForeignKey(Property, null=True, blank=True)
	entity = models.ForeignKey(Entity, null=True, blank=True)
	branch = models.ForeignKey(Branch, null=True, blank=True)
	submit_date = models.DateTimeField(help_text="The date this fee item is submited.", null=True, blank=True)
	submit_details = models.CharField(max_length=500, null=True, blank=True)
	is_reviewed = models.BooleanField(help_text ="whether this tax item is reviewed.")
	is_accepted = models.BooleanField(help_text="whether this tax item is accepted.")
	staff_id = models.IntegerField(help_text="The staff who generates this property tax item.", null=True, blank=True)
	status = models.CharField(max_length = 10, choices = variables.status_choices, default='active', blank = True)

	created = models.DateTimeField(help_text="The date this tax item is generated.")
	"""


class DebtorsReport(models.Model):
	as_at = models.DateField(auto_now_add=True)
	fee_type = models.CharField(max_length=30)


class DebtorsReportLine(models.Model):
	report = models.ForeignKey(DebtorsReport)
	business = models.ForeignKey(Business)
	subbusiness = models.ForeignKey(SubBusiness, null=True)
	rate = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	month = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	month_1 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	month_3 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	month_6 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	month_12 = models.DecimalField(max_digits=10, decimal_places=2, default=0)
	total = models.DecimalField(max_digits=10, decimal_places=2, default=0)



