import os
from django.conf import settings

STATIC_URL   = getattr(settings, 'HGWEBPROXY_STATIC_URL', settings.MEDIA_URL)
STATIC_PATH   = getattr(settings, 'HGWEBPROXY_STATIC_PATH', os.path.join(settings.MEDIA_ROOT, '../static/'))
STYLES_PATH  = getattr(settings, 'HGWEBPROXY_STYLE_PATH', None)
