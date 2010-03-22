from os.path import join, dirname, abspath
from django.conf import settings
from django.utils.translation import ugettext as _

AUTH_REALM  = getattr(settings, 'HGPROXY_AUTH_RELAM', _('Basic Auth'))
STYLES_PATH = getattr(settings, 'HGWEBPROXY_STYLES_PATH',
                        join(dirname(abspath(__file__)), 'templates/hgstyles'))
                        
DEFAULT_STYLE = getattr(settings, 'HGPROXY_DEFAULT_STYLE', 'django_style')
ALLOW_CUSTOM_STYLE = getattr(settings, 'HGPROXY_ALLOW_CUSTOM_STYLE', True)

STATIC_URL  = getattr(settings, 'HGWEBPROXY_STATIC_URL', settings.MEDIA_URL)
STATIC_PATH = getattr(settings, 'HGWEBPROXY_STATIC_PATH', join(settings.MEDIA_ROOT, '../static/'))

REPO_PERMANENT_DELETE = getattr(settings, 'HGPROXY_REPO_PERMANENT_DELETE', False)

