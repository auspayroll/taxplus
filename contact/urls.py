from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^contact/$','contact.views.enquiry'),
    url(r'^$','admin.views.login'),
)