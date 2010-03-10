from django.conf.urls.defaults import *
from django.contrib import admin
from django.conf import settings
from hgwebproxy import settings as hgwebproxy_settings

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    (r'^repo/', include('hgwebproxy.urls')),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        (r'^static/(?P<path>.*)$', 'django.views.static.serve', 
            {'document_root': hgwebproxy_settings.STATIC_PATH}),
    )
