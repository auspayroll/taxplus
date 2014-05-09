from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^(?P<content_type_name>\w+)/$','log.views.access_content_type'),
    url(r'^(?P<content_type_name>\w+)/(?P<action>\w+)_(?P<content_type_name1>\w+)/$','log.views.access_content_type'),
    url(r'^$','admin.views.login'),
)
