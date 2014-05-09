from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^searchSingleProperty/$','citizen.ajax.views.searchSingleProperty'),
    url(r'^addPropertyToCitizen/$','citizen.ajax.views.addPropertyToCitizen'),
)
