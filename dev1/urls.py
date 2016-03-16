from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from taxplus import views as taxplus_views
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib import admin

urlpatterns = patterns('',
	url(r'^$','crud.views.login', name='login'),
	url(r'^collector/', include('collector.urls')),
	url(r'^staff/', include('crud.urls')),

)

urlpatterns += patterns('',
		url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
			'document_root': settings.MEDIA_ROOT,
		}),
   )
