from django.conf.urls import patterns, include, url

urlpatterns = patterns('',

	url(r'^get_districts/$','jtax.views.getDistricts', name='get_districts'),
	url(r'^get_misc_fees/$','jtax.views.getMiscFees', name='get_misc_fees'),
	url(r'^get_misc_fee_categories/$','jtax.views.getMiscFeeCategories', name='get_misc_fee_categories'),
	url(r'^add_fee/$','jtax.views.addFee', name='add_fee'),
	url(r'^get_fee_cart/$','jtax.views.getFeeCart', name='get_fee_cart'),
	url(r'^clear_misc_fees/$','jtax.views.clearMiscFees', name='clear_misc_fees'),

	url(r'^citizen_fees/(?P<obj_id>\d+)/$','jtax.views.tax_citizen', { 'part':'fees'}, name='citizen_fees'),
	#url(r'^property_fees/(?P<obj_id>\d+)/$','jtax.views.tax_property', { 'part':'fees'}, name='property_fees'),
	#url(r'^business_fees/(?P<obj_id>\d+)/$','jtax.views.tax_business', { 'part':'fees'}, name='business_fees'),

	url(r'^submit_misc_fee/$','jtax.views.submitMiscFee', name='submit_misc_fee'),

	#def submitMiscFee(request, setting_pk, citizen_pk=None, business_pk=None):
	url(r'^misc_fee_citizen/(?P<citizen_pk>\d+)/$','jtax.views.miscFee', name='misc_fee_citizen'),
	url(r'^misc_fee_business/(?P<business_pk>\d+)/$','jtax.views.miscFee', name='misc_fee_business'),
	# url(r'^installments/(?P<tax_type>\w+)/(?P<tax_id>\d+)/$','jtax.views.installments', name='installments'),

	url(r'^submit_misc_fees/$','jtax.views.submitMiscFee', name='submit_misc_fees'),

	url(r'^process_payment/$','jtax.views.processPayment', name='process_payment'),


	url(r'^submit_land_lease/(?P<id>\d+)/$','jtax.views.submitLandLease', name='submit_land_lease'),
	url(r'^submit_fixed_asset/(?P<id>\d+)/$','jtax.views.submitFixedAssetTax', name='submit_fixed_asset'),
	url(r'^submit_trading_license/(?P<id>\d+)/$','jtax.views.submitTradingLicense', name='submit_trading_license'),
	url(r'^submit_rental_income/(?P<id>\d+)/$','jtax.views.submitRentalIncome', name='submit_rental_income'),


	url(r'^tax/submit_tax/','jtax.views.payFee', name='submit_tax_patch'),
	url(r'^tax/submit_fee/','jtax.views.payFee', name='submit_fee'),
	url(r'^tax/pay_taxes/','jtax.views.payFee', name='pay_fee_patch'),

	url(r'^tax/update_installment_date/$','jtax.views.update_installment_date', name='update_installment_date'),
	url(r'^pay_fee/(?P<fee_type>\w+)/(?P<id>\d+)/$','jtax.views.payFee', name='pay_fee'),
	url(r'^pay_fees/$','jtax.views.payFees', name='pay_fees'),
	url(r'^pay_land_lease/(?P<id>\d+)/$','jtax.views.payFee', { 'fee_type':'land_lease'}, name='pay_land_lease'),
	url(r'^pay_fixed_asset/(?P<id>\d+)/$','jtax.views.payFee', { 'fee_type':'fixed_asset'}, name='pay_fixed_asset'),
	url(r'^pay_trading_license/(?P<id>\d+)/$','jtax.views.payFee', { 'fee_type':'trading_license'}, name='pay_trading_license'),
	url(r'^pay_rental_income/(?P<id>\d+)/$','jtax.views.payFee', { 'fee_type':'rental_income'}, name='pay_rental_income'),

	url(r'^multi_invoice/(?P<id>\d+)/$','jtax.views.displayGenerateMultipayInvoicePage', name='multi_invoice'),

	url(r'^incomplete_payment/$','jtax.views.incomplete_payment_default'),
	url(r'^incomplete_payment/(?P<action>\w+)_(?P<content_type_name1>\w+)/$','jtax.views.incomplete_payment_default'),
	url(r'^incomplete_payment/(?P<action>\w+)_(?P<content_type_name1>\w+)/(?P<obj_id>\d+)/$','jtax.views.incomplete_payment_default'),

	url(r'^pending_payment/$','jtax.views.pending_payment_default'),
	url(r'^pending_payment/(?P<action>\w+)/$','jtax.views.pending_payment_default'),
	url(r'^pending_payment/(?P<action>\w+)/(?P<obj_id>\d+)/$','jtax.views.pending_payment_default'),

	url(r'^(?P<content_type_name>\w+)/$','jtax.views.access_content_type'),
	url(r'^(?P<content_type_name>\w+)/(?P<obj_name>\w+)/(?P<obj_id>\d+)/$','jtax.views.access_content_type'),
	url(r'^(?P<content_type_name>\w+)/(?P<obj_name>\w+)/(?P<obj_id>\d+)/(?P<part>\w+)/$','jtax.views.access_content_type'),
	url(r'^(?P<content_type_name>\w+)/(?P<action>\w+)_(?P<content_type_name1>\w+)/$','jtax.views.access_content_type'),


    url(r'^$','admin.views.login'),
)
