from django.conf.urls import patterns, url

import views

urlpatterns = patterns('',
    url(r'^small$', views.qr, {'size': 2}, name='small'),
    url(r'^middle$', views.qr, {'size': 4}, name='middle'),
    url(r'^large$', views.qr, {'size': 8}, name='large'),
    (r'^(?P<size>\d+)$', views.qr),
)
