from partstore.settings import *

STATIC_ROOT = '/home/part/static/'

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'OPTIONS': {
            'read_default_file': '/home/parts/partstore/partstore/my.cnf',
        },
    }
}
