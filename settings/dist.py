# -*- coding: utf-8 -*-

import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__),
    os.path.pardir))

def rel(x):
    return os.path.join(PROJECT_ROOT, x)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:', #rel('local.db'),
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    },
    'assist': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'assist',
        'USER': 'root',
        'PASSWORD': '123',
        'HOST': 'localhost',
        'PORT': '',
    },
}

if 'test' in sys.argv:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:', #rel('default.db'),
        },
        'assist': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': ':memory:', #rel('assist.db'),
        },
    }



DATABASE_ROUTERS = ['db_routers.AssistRouter',]

TIME_ZONE = 'Europe/Moscow'

LANGUAGE_CODE = 'ru-ru'

SITE_ID = 1

USE_I18N = True

USE_L10N = True

LOCALE_PATHS = (
    rel('templates/locale'),
)

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = rel('media/')

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/media/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/admin-media/'

LOGIN_URL = '/login/'

# Make this unique, and don't share it with anybody.
if not hasattr(globals(), 'SECRET_KEY'):
    SECRET_FILE = os.path.join(PROJECT_ROOT, 'settings/secret.txt')
    try:
        SECRET_KEY = open(SECRET_FILE).read().strip()
    except IOError:
        try:
            from random import choice
            CHAR_SET = 'abcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*(-_=+)'
            SECRET_KEY = ''.join([choice(CHAR_SET) for i in range(50)])
            secret = file(SECRET_FILE, 'w')
            secret.write(SECRET_KEY)
            secret.close()
        except IOError:
            raise Exception('Please create a %s file with random characters to '
                'generate your secret key!' % SECRET_FILE)


# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.core.context_processors.auth',
    'django.core.context_processors.debug',
    'django.core.context_processors.i18n',
    'django.core.context_processors.media',
    'django.core.context_processors.request',
    'django.contrib.messages.context_processors.messages',
    'apps.social.context_processors.site_domain',

)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.http.ConditionalGetMiddleware',
)

ROOT_URLCONF = 'urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates"
    # Don't forget to use absolute paths, not relative paths.
    rel('templates/')
)

INSTALLED_APPS = (
    #'django.contrib.auth',
    #'django.contrib.contenttypes',
    'django.contrib.sessions',
    #'django.contrib.sites',
    'django.contrib.messages',
    #'django.contrib.admin',
    #'mongoengine.django.auth',
    'djcelery',
    'apps.social',
    'apps.media',
    'apps.cam',
    'apps.notes',
    'apps.user_messages',
    'apps.billing',
    'apps.groups',
    'assist',
)

CELERY_RESULT_BACKEND = "mongodb"

CELERY_MONGODB_BACKEND_SETTINGS = {
    "host": "127.0.0.1",
    "port": 27017,
    "database": "celery",
    "taskmeta_collection": "taskmeta",
}

TASKS_ENABLED = dict(
    AVATAR_RESIZE = 1,
    MESSAGE_STORE_READED = 1,
    MESSAGE_DELETE = 1,
)


AUTHENTICATION_BACKENDS = (
    'apps.social.auth.MongoEngineBackend',
)

SESSION_ENGINE = 'mongoengine.django.sessions'

FORCE_SCRIPT_NAME = ''

SEND_EMAILS = True

SITE_DOMAIN = 'modnoemesto.ru' # no slashes here, please

ROBOT_EMAIL_ADDRESS = 'noreply@modnoemesto.ru'

AVATAR_SIZES = (
    (100, 100),
    (60, 60),
    (47, 47),
)

MAX_USER_MESSAGES_COUNT = 500


ASSIST_SHOP_IDP = '123456789'
ASSIST_LOGIN = 'test'
ASSIST_PASSWORD = 'test'
ASSIST_TEST_MODE = True
