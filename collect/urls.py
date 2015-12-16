from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
	url(r'^$','collect.views.index', name='index'),
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
