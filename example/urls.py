from django.conf.urls import include, patterns, url 
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
# from django.conf import settings

# from hgwebproxy import settings as hgwebproxy_settings

admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^repo/', include('hgwebproxy.urls')),
)

urlpatterns += staticfiles_urlpatterns('/static/')

