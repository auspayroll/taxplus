from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^merge_business/(?P<pk1>\d+)/(?P<pk2>\d+)/$','asset.views.merge_business', name='merge_business'),	
    url(r'^close_business/(?P<pk>\d+)/$','asset.views.close_business', name='close_business'),
    url(r'^business/change_business/(?P<obj_id>\d+)/$','asset.views.access_content_type', { 'content_type_name':'business','action':'change', 'content_type_name1':'business'}, name='update_business'),
    url(r'^(?P<content_type_name>\w+)/$','asset.views.access_content_type'),
    url(r'^(?P<content_type_name>\w+)/(?P<action>\w+)_(?P<content_type_name1>\w+)/$','asset.views.access_content_type'),
    url(r'^(?P<content_type_name>\w+)/(?P<action>\w+)_(?P<content_type_name1>\w+)/(?P<obj_id>\d+)/$','asset.views.access_content_type'),

)
