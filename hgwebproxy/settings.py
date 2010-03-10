import os
from django.conf import settings

STATIC_URL   = getattr(settings, 'HGWEBPROXY_STATIC_URL', os.path.join(settings.MEDIA_URL, 'hg/'))
STYLES_PATH  = getattr(settings, 'HGWEBPROXY_STYLE_PATH', None)
