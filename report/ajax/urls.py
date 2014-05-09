from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^properties_with_unpaid_tax_for_printing/$','report.ajax.views.properties_with_unpaid_tax_for_printing'),
)
