import os

from django.utils.translation import ugettext_lazy as _


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = '2tay@wc#ci_8l6t!=ond3yx2832pl((gv26g+s1yg%=i7#5v_u'

DEBUG = False

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'game',
    'users',
    'widget_tweaks'
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.locale.LocaleMiddleware',
)

ROOT_URLCONF = 'project.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.i18n',
                'django.core.context_processors.static',
            ],
        },
    },
]


STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'static'),
)

STATIC_ROOT = os.path.join(BASE_DIR, 'public', 'static')

WSGI_APPLICATION = 'project.wsgi.application'

LANGUAGE_CODE = 'ru'

LANGUAGES = (
    ('en', _(u'English')),
    ('ru', _(u'Russian')),
)

LOCALE_PATHS = (
    os.path.join(BASE_DIR, 'locale'),
)

TIME_ZONE = 'Europe/Moscow'

USE_I18N = True

USE_L10N = True

STATIC_URL = '/static/'

LOGIN_URL = 'users_login'

REDIS_HOST = 'localhost'
