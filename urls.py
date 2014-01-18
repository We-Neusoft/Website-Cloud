from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    (r'^qrcode/', include('apis.qrcode.urls', namespace='qrcode')),
    (r'^oauth/', include('apis.oauth.urls', namespace='oauth')),
)
