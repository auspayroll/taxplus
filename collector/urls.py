from django.conf.urls import patterns, include, url
from .views import *

urlpatterns = patterns('',
	url(r'^$',collector_roster, name='collector_index'),
	url(r'^account/(?P<pk>\d+)/$',account, name='collector_account'),
	url(r'^recent_collections/$',recent_collections, name='collector_recent_collections'),

	#contacts
	url(r'^account/(?P<pk>\d+)/contact/new/$',new_contact, name='collector_new_contact'),
	url(r'^account/(?P<pk>\d+)/contacts/$',account_contacts, name='collector_account_contacts'),


	#media
	url(r'^account/(?P<pk>\d+)/media/new/$',new_media, name='collector_new_media'),
	url(r'^account/(?P<pk>\d+)/media/$',account_media, name='collector_account_media'),
	url(r'^collection/(?P<pk>\d+)/update/$',edit_collection, name='collector_edit_collection'),

	url(r'^account/(?P<pk>\d+)/fee_collection/new/$',new_fee_collection, name='collector_new_fee_collection'),
	url(r'^account/(?P<pk>\d+)/collections/$',fee_collections, name='collector_fee_collections'),
	url(r'^account/(?P<pk>\d+)/holders/$',account_holders, name='collector_account_holders'),
	url(r'^account/(?P<pk>\d+)/note/new/$',new_account_note, name='collector_new_account_note'),
	url(r'^account/(?P<pk>\d+)/notes/$',account_notes, name='collector_account_notes'),


	url(r'^districts/$',districts, name='collector_districts'),
	url(r'^district/(?P<pk>\d+)/$',district, name='collector_district'),
	url(r'^sector/(?P<pk>\d+)/$',sector, name='collector_sector'),
	url(r'^cell/(?P<pk>\d+)/$',cell, name='collector_cell'),
	url(r'^village/(?P<pk>\d+)/$',village, name='collector_village'),

	url(r'^roster/(?P<blocks>-?\d+)/$',collector_roster, name='collector_roster_block'),
	url(r'^roster/$',collector_roster, name='collector_roster'),


)