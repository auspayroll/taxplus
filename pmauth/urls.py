from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
	url(r'^ajax/', include('pmauth.ajax.urls')),				
    url(r'^(?P<content_type_name>\w+)/$','pmauth.views.access_content_type'),
    url(r'^(?P<content_type_name>\w+)/(?P<action>\w+)_(?P<content_type_name1>\w+)/$','pmauth.views.access_content_type'),
    url(r'^(?P<content_type_name>\w+)/(?P<action>\w+)_(?P<content_type_name1>\w+)/(?P<obj_id>\d+)/$','pmauth.views.access_content_type'),
    url(r'^$','admin.views.login'),
)
