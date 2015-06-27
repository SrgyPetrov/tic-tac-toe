from .common import *

PUBLIC_ROOT = os.path.join(os.sep, 'var', 'www', 'project', 'public')
STATIC_ROOT = os.path.join(PUBLIC_ROOT, 'static')

PREPEND_WWW = False

ALLOWED_HOSTS = ['*']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'project',
    }
}

REDIS_HOST = '127.0.0.1'
