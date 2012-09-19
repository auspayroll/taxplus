from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^admin/property/', include('property.urls')),
    url(r'^admin/auth/', include('auth.urls')),
    url(r'^admin/log/', include('log.urls')),
    url(r'^admin/tax/', include('jtax.urls')), 
    url(r'^admin/citizen/', include('citizen.urls')),
    url(r'^admin/', include('admin.urls')),
    url(r'^$','admin.views.login'),
)
