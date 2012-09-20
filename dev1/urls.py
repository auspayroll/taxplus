from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = patterns('',
    url(r'^admin/property/', include('property.urls')),
    url(r'^admin/auth/', include('auth.urls')),
    url(r'^admin/log/', include('log.urls')),
    url(r'^admin/tax/', include('jtax.urls')), 
    url(r'^admin/citizen/', include('citizen.urls')),
    url(r'^admin/', include('admin.urls')),
    url(r'^$','admin.views.login'),
)


urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )
