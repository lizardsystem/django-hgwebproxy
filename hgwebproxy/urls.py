from django.conf.urls.defaults import *

urlpatterns = patterns('hgwebproxy.views',
    url('^$', 'repo_index', name='repo_index'),
    url('^(?P<username>[\w-]+)/(?P<pattern>[\w-]+)', 'repo_detail', name='repo_detail'),
)
