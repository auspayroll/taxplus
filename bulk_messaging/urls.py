from django.conf.urls import patterns, include, url

urlpatterns = patterns('',

	url(r'^send/$','bulk_messaging.views.send'),
    url(r'^$','admin.views.login'),
) 
