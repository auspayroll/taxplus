from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from taxplus import views as taxplus_views
from django.views.generic.base import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib import admin
from crud.api_views import *
from rest_framework import routers


router = routers.DefaultRouter()
router.register('accounts', AccountApi)
router.register('property', PropertyApi)
router.register('districts', DistrictApi)
router.register('sectors', SectorApi)
router.register('cells', CellApi)
router.register('villages', VillageApi)

urlpatterns = patterns('',
	url(r'^$','crud.views.login', name='login'),
	url(r'^logout/$','crud.views.logout', name='logout'),
	url(r'^collector/', include('collector.urls')),
	url(r'^staff/', include('crud.urls')),
	#url(r'^api/', PropertyList.as_view()),

)

urlpatterns += [
	url(r'^api/', include(router.urls)),
	url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]

urlpatterns += patterns('',
		url(r'^media/(?P<path>.*)$', 'django.views.static.serve', {
			'document_root': settings.MEDIA_ROOT,
		}),
   )
