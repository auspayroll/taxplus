from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^edit_profile/$','admin.views.construction'),
    url(r'^ajax/add_property/$','admin.ajax.add_property'),
    url(r'^ajax/declare_value/$','admin.ajax.declare_value'),
    url(r'^ajax/search_user/$','admin.ajax.search_user'),
    url(r'^ajax/search_citizen/$','admin.ajax.search_citizen'),
    url(r'^ajax/search_property_in_area/$','admin.ajax.search_property_in_area'),
    url(r'^ajax/search_property_field/$','admin.ajax.search_property_field'),
    url(r'^ajax/search_property_by_fields/$','admin.ajax.search_property_by_fields'),
    url(r'^logout/$','admin.views.logout'),
    url(r'^(?P<module_name>\w+)/(?P<content_type_name>\w+)/$','admin.views.access_content_type'),
    url(r'^(?P<module_name>\w+)/(?P<content_type_name>\w+)/(?P<action>\w+)_(?P<content_type_name1>\w+)/$','admin.views.access_content_type'),
    url(r'^$','admin.views.login'),
)
