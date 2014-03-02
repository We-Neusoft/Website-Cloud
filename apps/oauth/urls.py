from django.conf.urls import patterns, url

import views

urlpatterns = patterns('',
    url(r'^authorize$', views.authorize, name='authorize'),
    url(r'^token$', views.token, name='token'),
)
