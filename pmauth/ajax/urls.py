from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^check_group_exist/$','pmauth.ajax.views.check_group_exist'),
    url(r'^check_user_email_exist/$','pmauth.ajax.views.check_user_email_exist'),
)
