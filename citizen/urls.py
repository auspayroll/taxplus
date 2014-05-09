from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^ajax/', include('citizen.ajax.urls')),
    url(r'^(?P<content_type_name>\w+)/$','citizen.views.access_content_type'),
    url(r'^(?P<content_type_name>\w+)/(?P<action>\w+)_(?P<content_type_name1>\w+)/$','citizen.views.access_content_type'),
	url(r'^(?P<content_type_name>\w+)/(?P<action>\w+)_(?P<content_type_name1>\w+)/(?P<obj_id>\d+)/$','citizen.views.access_content_type'),
	url(r'^(?P<content_type_name>\w+)/(?P<action>\w+)_(?P<content_type_name1>\w+)/(?P<obj_id>\d+)/(?P<part>\w+)/$','citizen.views.access_content_type'),
    url(r'^$','admin.views.login'),
)