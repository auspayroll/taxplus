from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
	url(r'^$','crud.views.index', name='index'),
	url(r'^select_fees/$','crud.views.select_fees', name='select_fees'),
	url(r'^new_citizen_account/$','crud.views.new_citizen_account', name='new_citizen_account'),
	url(r'^new_business_account/$','crud.views.new_business_account', name='new_business_account'),
	url(r'^account/(?P<pk>\d+)/$','crud.views.account', name='account'),

	url(r'^recent_accounts/$','crud.views.recent_accounts', name='recent_accounts'),
	url(r'^new_account_utility/(?P<pk>\d+)/$','crud.views.new_account_utility', name='new_account_utility'),

	#contacts
	url(r'^account/(?P<pk>\d+)/contact/new/$','crud.views.new_contact', name='new_contact'),
	url(r'^account/(?P<pk>\d+)/contacts/$','crud.views.account_contacts', name='account_contacts'),

	#payments
	url(r'^account/(?P<pk>\d+)/payment/new/$','crud.views.new_payment', name='new_payment'),
	url(r'^account/(?P<pk>\d+)/payments/$','crud.views.account_payments', name='account_payments'),

	#media
	url(r'^account/(?P<pk>\d+)/media/new/$','crud.views.new_media', name='new_media'),
	url(r'^account/(?P<pk>\d+)/media/$','crud.views.account_media', name='account_media'),

	#utilities
		url(r'^utilities/$','crud.views.utilities', name='utilities'),
	url(r'^utilities/(?P<utility_type>\w+)/$','crud.views.utilities', name='utilities_type'),

	#fees
	url(r'^new_account_fee/(?P<pk>\d+)/$','crud.views.new_account_fee', name='new_account_fee'),
	url(r'^account/(?P<pk>\d+)/fees/$','crud.views.account_fees', name='account_fees'),

	url(r'^account/(?P<pk>\d+)/fee_collection/new/$','crud.views.new_fee_collection', name='new_fee_collection'),
	url(r'^account/(?P<pk>\d+)/collections/$','crud.views.fee_collections', name='fee_collections'),

	#url(r'^account/(?P<pk>\d+)/fee_collection/new/$','crud.views.new_fee_collection', name='new_fee_collection'),
	url(r'^account/(?P<pk>\d+)/holders/$','crud.views.account_holders', name='account_holders'),

	url(r'^account/(?P<pk>\d+)/note/new/$','crud.views.new_account_note', name='new_account_note'),
	url(r'^account/(?P<pk>\d+)/notes/$','crud.views.account_notes', name='account_notes'),

	url(r'^account/(?P<pk>\d+)/utility/add/$','crud.views.add_account_utility', name='add_account_utility'),


	url(r'^add_epay/$','collect.views.addEpay', name='add_epay'),
	url(r'^add_collection_group/$','collect.views.addCollectionGroup', name='add_collection_group'),
	url(r'^register/$','collect.views.register', name='register'),
	url(r'^groups/$','collect.views.groups', name='groups'),
	url(r'^edit_group/(?P<pk>\d+)/$','collect.views.editGroup', name='edit_group'),
	url(r'^collectors/(?P<pk>\d+)/$','collect.views.collectors', name='collectors'),
	url(r'^collector/(?P<pk>\d+)/$','collect.views.collector', name='collector'),
	url(r'^group_epays/(?P<pk>\d+)/(?P<status>\d+)/$','collect.views.group_epays', name='group_epays'),
	url(r'^logs/$','collect.views.logs', name='logs'),
	url(r'^epay_batch_csv/(?P<pk>\d+)/$','collect.views.epay_batch_csv', name='epay_batch_csv'),
	url(r'^epay_batch/(?P<pk>\d+)/$','collect.views.epay_batch', name='epay_batch'),
	url(r'^businessSchedule/$','collect.views.businessSchedule', name='business_schedule'),
)