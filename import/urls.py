from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$','import.views.index'),
) 


