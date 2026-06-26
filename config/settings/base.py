import os
from pathlib import Path
from environ import Env

BASE_DIR = Path(__file__).resolve().parent.parent.parent
env = Env()
if os.path.exists(BASE_DIR / '.env'):
    env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('DJANGO_SECRET_KEY', default='django-insecure-change-me-in-production')
DEBUG = env.bool('DEBUG', default=True)

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'django.contrib.humanize',
    'axes',
    'honeypot',
    'csp',
    'apps.core',
    'apps.booking',
    'apps.portfolio',
    'apps.reviews',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'axes.middleware.AxesMiddleware',
    'csp.middleware.CSPMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'apps.core.context_processors.site_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

DATABASES = {
    # Без абсолютного пути sqlite-файл резолвится относительно текущей
    # рабочей директории процесса, а не BASE_DIR — на PythonAnywhere у
    # WSGI-воркера и Bash-консоли разный CWD, из-за чего они читали/писали
    # разные файлы db.sqlite3.
    'default': env.db('DATABASE_URL', default=f'sqlite:///{BASE_DIR / "db.sqlite3"}'),
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ru'
TIME_ZONE = 'Asia/Almaty'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'
STORAGES = {
    'default': { 'BACKEND': 'django.core.files.storage.FileSystemStorage' },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('EMAIL_HOST_USER', default='')
ADMIN_EMAIL = env('ADMIN_EMAIL', default='')

AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 0.5
AXES_LOCK_OUT_BY_COMBINATION_USER_AND_IP = True
HONEYPOT_FIELD_NAME = 'honeypot'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'loggers': {
        'apps': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
    },
}

CONTENT_SECURITY_POLICY = {
    'DIRECTIVES': {
        'default-src': ("'self'",),
        'script-src': ("'self'", "https://cdnjs.cloudflare.com", "https://cdn.jsdelivr.net"),
        'style-src': ("'self'", "'unsafe-inline'", "https://cdnjs.cloudflare.com", "https://cdn.jsdelivr.net", "https://fonts.googleapis.com"),
        'font-src': ("'self'", "https://fonts.gstatic.com"),
        'img-src': ("'self'", "data:", "https:"),
        'connect-src': ("'self'",),
        'form-action': ("'self'",),
    }
}
