from django.conf.urls import patterns, url

import views

urlpatterns = patterns('',
    url(r'^get_info$', views.get_info, name='get_info'),
    url(r'^get_privacy$', views.get_privacy, name='get_privacy'),
)
