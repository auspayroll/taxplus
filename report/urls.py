from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^ajax/',include('report.ajax.urls')),
    url(r'^(?P<content_type_name>\w+)/$','report.views.access_content_type'),
    url(r'^(?P<content_type_name>\w+)/(?P<action>\w+)/$','report.views.access_content_type'),
    url(r'^$','admin.views.login'),
)