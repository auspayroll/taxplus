from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
	url(r'^add_epay/$','collect.views.addEpay', name='add_epay'),

)
