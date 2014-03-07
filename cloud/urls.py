from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'cloud.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    (r'^qrcode/', include('apps.qrcode.urls', namespace='qrcode')),
    (r'^oauth/', include('apps.oauth.urls', namespace='oauth')),
    (r'^user/', include('apps.user_we.urls', namespace='user')),

    url(r'^admin/', include(admin.site.urls)),
)
