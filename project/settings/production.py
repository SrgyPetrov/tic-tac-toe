from .common import *

PUBLIC_ROOT = os.path.join(os.sep, 'var', 'www', 'project', 'public')
STATIC_ROOT = os.path.join(PUBLIC_ROOT, 'static')

PREPEND_WWW = False

ALLOWED_HOSTS = ['188.226.193.98']

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'project',
    }
}

REDIS_HOST = '127.0.0.1'
