from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^admin/', include('admin.urls')),    
    url(r'^$','admin.views.login'),
)
