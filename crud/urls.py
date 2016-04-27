from django.conf.urls import patterns, include, url
from .views import *

urlpatterns = patterns('',
	url(r'^$',general_roster, name='index'),
	url(r'^select_fees/$',select_fees, name='select_fees'),
	url(r'^new_citizen_account/$',new_citizen_account, name='new_citizen_account'),
	url(r'^new_business_account/$',new_business_account, name='new_business_account'),
	url(r'^account/(?P<pk>\d+)/$',account_transactions, name='account'),

	url(r'^recent_accounts/$',recent_accounts, name='recent_accounts'),
	url(r'^recent_collections/$',recent_collections, name='recent_collections'),
	url(r'^recent_utilities/(?P<utility_type>\w+)/$',recent_utilities, name='recent_utilities'),
	url(r'^new_account_utility/(?P<pk>\d+)/$',new_account_utility, name='new_account_utility'),

	#contacts
	url(r'^account/(?P<pk>\d+)/contact/new/$',new_contact, name='new_contact'),
	url(r'^account/(?P<pk>\d+)/contacts/$',account_contacts, name='account_contacts'),

	#payments
	url(r'^account/(?P<pk>\d+)/payment/new/$',new_payment, name='new_payment'),
	url(r'^account/(?P<pk>\d+)/payments/$',account_payments, name='account_payments'),

	#media
	url(r'^account/(?P<pk>\d+)/media/new/$',new_media, name='new_media'),
	url(r'^account/(?P<pk>\d+)/media/$',account_media, name='account_media'),

	url(r'^sector/(?P<pk>\d+)/collection/new/$',sector_collection, name='sector_collection'),

	url(r'^collection/(?P<pk>\d+)/update/$',edit_collection, name='edit_collection'),

	url(r'^account/select/$',account_select, name='account_select'),

	url(r'^location/new/$',new_location, name='new_location'),
	url(r'^location/(?P<pk>\d+)/$',edit_location, name='edit_location'),
	url(r'^location/new/post/$',new_location_post, name='new_location_post'),
	url(r'^locations/recent/$',recent_locations, name='recent_locations'),

	#utilities
	url(r'^utilities/$',utilities, name='utilities'),
	url(r'^utilities/(?P<utility_type>\w+)/$',utilities, name='utilities_type'),

	#fees
	url(r'^new_account_fee/(?P<pk>\d+)/$',new_account_fee, name='new_account_fee'),
	url(r'^account/(?P<pk>\d+)/fees/$',account_fees, name='account_fees'),
	url(r'^account/(?P<pk>\d+)/edit/$',edit_account, name='edit_account'),

	url(r'^village/(?P<pk>\d+)/utility/new/$',add_village_utility, name='add_village_utility'),

	url(r'^account/(?P<pk>\d+)/fee_collection/new/$',new_fee_collection, name='new_fee_collection'),
	url(r'^account/(?P<pk>\d+)/collections/$',fee_collections, name='fee_collections'),

	url(r'^account/(?P<pk>\d+)/holders/$',account_holders, name='account_holders'),

	url(r'^account/(?P<pk>\d+)/note/new/$',new_account_note, name='new_account_note'),
	url(r'^account/(?P<pk>\d+)/notes/$',account_notes, name='account_notes'),
	url(r'^add_account_dates/(?P<pk>\d+)/$',add_account_dates, name='add_account_dates'),

	url(r'^account/(?P<pk>\d+)/utility/add/$',add_account_utility, name='add_account_utility'),
	url(r'^account/(?P<pk>\d+)/transactions/$',account_transactions, name='account_transactions'),
	url(r'^account/(?P<pk>\d+)/transactions/archive/$',account_archive_transactions, name='account_archive_transactions'),

	url(r'^districts/$',districts, name='districts'),

	url(r'^users/$',users, name='users'),
	url(r'^user/register/$',register_user, name='register_user'),
	url(r'^user/(?P<pk>\d+)/$',edit_user, name='edit_user'),

	url(r'^district/(?P<pk>\d+)/$',district, name='district'),
	url(r'^district/(?P<pk>\d+)/update/$',district_update, name='district_update'),
	url(r'^district/(?P<pk>\d+)/roster/(?P<blocks>-?\d+)/$',district_roster, name='district_roster_block'),
	url(r'^district/(?P<pk>\d+)/roster/$',district_roster, name='district_roster'),

	url(r'^roster/(?P<blocks>-?\d+)/$',general_roster, name='general_roster_block'),
	url(r'^roster/$',general_roster, name='general_roster'),

	url(r'^sector/(?P<pk>\d+)/$',sector, name='sector'),
	url(r'^cell/(?P<pk>\d+)/$',cell, name='cell'),
	url(r'^village/(?P<pk>\d+)/$',village, name='village'),


	url(r'^sector/(?P<pk>\d+)/update/$',sector_update, name='sector_update'),
	url(r'^cell/(?P<pk>\d+)/update/$',cell_update, name='cell_update'),
	url(r'^village/(?P<pk>\d+)/update/$',village_update, name='village_update'),

	url(r'^rate/(?P<pk>\d+)/update/$',rate_update, name='rate_update'),

	url(r'^village/(?P<pk>\d+)/rates/$',village_rates, name='village_rates'),
	url(r'^sector/(?P<pk>\d+)/rates/$',sector_rates, name='sector_rates'),


	url(r'^utility/(?P<pk>\d+)/update/$',update_utility, name='update_utility'),

	url(r'^recent_logs/$',recent_logs, name='recent_logs'),
	url(r'^account/(?P<pk>\d+)/logs/$',account_logs, name='account_logs'),
	url(r'^user/(?P<pk>\d+)/logs/$',user_logs, name='user_logs'),


	url(r'^report/region/$',region_report, name='region_report'),

	url(r'^report/district/(?P<district_pk>\d+)/sector/(?P<sector_pk>\d+)/cell/(?P<cell_pk>\d+)/village/(?P<village_pk>\d+)/fee_type/(?P<fee_type_pk>\d+)/$',fee_items_report, name='fee_items_report'),
	url(r'^report/district/(?P<district_pk>\d+)/sector/(?P<sector_pk>\d+)/cell/(?P<cell_pk>\d+)/village/(?P<village_pk>\d+)/fee_type/(?P<fee_type_pk>\d+)/web/$',fee_items_report, {'web':True}, name='fee_items_report_web'),

	url(r'^search/$',search, name='search'),



)