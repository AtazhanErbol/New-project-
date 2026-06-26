import os

from .base import *

DEBUG = False

# На бесплатном тарифе PythonAnywhere нет UI для переменных окружения —
# проще всего задать ALLOWED_HOSTS прямо в WSGI-файле (см. инструкцию в README),
# поэтому здесь разумный дефолт + возможность переопределить через env.
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['*.pythonanywhere.com'])

CSRF_TRUSTED_ORIGINS = ['https://*.pythonanywhere.com']

# PythonAnywhere сам терминирует HTTPS на своём proxy и уже отдаёт сайт
# только по https для *.pythonanywhere.com — принудительный SECURE_SSL_REDIRECT
# здесь не нужен и может уйти в редирект-петлю.
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
