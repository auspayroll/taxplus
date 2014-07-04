from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from taxplus import views as taxplus_views


urlpatterns = patterns('',
	url(r'^admin/property/', include('property.urls')),
	url(r'^admin/auth/', include('pmauth.urls')),
	url(r'^admin/log/', include('log.urls')),
	url(r'^admin/tax/', include('jtax.urls')), 
	url(r'^admin/citizen/', include('citizen.urls')),
	url(r'^admin/contact/', include('contact.urls')),
	url(r'^admin/asset/', include('asset.urls')),
	url(r'^admin/media/', include('media.urls')),
	#url(r'^admin/import/', include('import.urls')),
	url(r'^admin/report/', include('report.urls')),
	url(r'^admin/forms/', include('forms.urls')),
	url(r'^admin/cleaning_audit/', taxplus_views.cleaning_audit, name='cleaning_audit'),
	url(r'^admin/cleaning_debtors/', taxplus_views.cleaning_debtors, name='cleaning_debtors'),
	url(r'^admin/duplicates/', taxplus_views.duplicates, name='duplicates'),
	url(r'^admin/bulk_messaging/', include('bulk_messaging.urls')),
	url(r'^admin/', include('admin.urls')),
	#url(r'^api/', include('api.urls')),
	url(r'^$','admin.views.login'),
	url(r'^temppassword/','admin.views.set_temp_password'),
	url(r'^test/',include('mytest.urls')),
)

urlpatterns += patterns('',
		url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
			'document_root': settings.MEDIA_ROOT,
		}),
   )
