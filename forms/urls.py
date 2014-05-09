from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^(?P<content_type_name>\w+)/$','forms.views.index'),
    url(r'^(?P<content_type_name>\w+)/(?P<action>\w+)/$','forms.views.index'),
    url(r'^(?P<content_type_name>\w+)/delete/(?P<id>\d+)/$','forms.views.delete'),
    url(r'^$','admin.views.login'),
) 


