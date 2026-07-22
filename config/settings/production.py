import os

from .base import *

DEBUG = False

# Render injects RENDER_EXTERNAL_HOSTNAME automatically for the service's
# *.onrender.com domain, so a Render deploy works with zero extra config.
# Any other host (custom domain, different PaaS) must set ALLOWED_HOSTS explicitly.
_render_host = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if _render_host:
    ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[_render_host])
else:
    ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')

CSRF_TRUSTED_ORIGINS = []
for host in ALLOWED_HOSTS:
    CSRF_TRUSTED_ORIGINS.append(f'https://{host}')
    CSRF_TRUSTED_ORIGINS.append(f'http://{host}')

# Render (and most PaaS) terminate TLS at a proxy and forward plain HTTP,
# so Django must trust X-Forwarded-Proto to know the original request was HTTPS.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# HTTPS-принуждение можно временно выключить через .env (SECURE_SSL_REDIRECT=False),
# чтобы открыть сайт по http на голом IP-адресе, пока не подключён домен и SSL.
# По умолчанию включено (боевой режим с доменом).
_force_https = env.bool('SECURE_SSL_REDIRECT', default=True)
SECURE_SSL_REDIRECT = _force_https
SESSION_COOKIE_SECURE = _force_https
CSRF_COOKIE_SECURE = _force_https
if _force_https:
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
