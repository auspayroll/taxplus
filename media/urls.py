from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^(?P<content_type_name>\w+)/$','media.views.index'),
    url(r'^(?P<content_type_name>\w+)/update/$','media.views.update'),
    url(r'^(?P<content_type_name>\w+)/upload_ajax/$','media.views.upload_ajax'),
    url(r'^(?P<content_type_name>\w+)/preview/(?P<id>\d+)/$','media.views.preview'),
    url(r'^$','admin.views.login'),
) 


