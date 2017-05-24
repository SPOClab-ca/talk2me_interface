# Django settings for csc2518 project.
import os
PROJECT_DIR = os.path.dirname(__file__)

DEBUG = True
TEMPLATE_DEBUG = DEBUG

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Create a Mongo DB and populate it first
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mydatabase', # Name of your mongo DB
        'USER': 'Chloe', # Username
        'PASSWORD': 'hello', # DB password
        'HOST': '',
        'PORT': '',
    }
}

ALLOWED_HOSTS = []
TIME_ZONE = 'America/Toronto'
LANGUAGE_CODE = 'en-ca'
SITE_ID = 1
USE_I18N = True
USE_L10N = True


MEDIA_ROOT = '~/django_datacollector/media' # Absolute path to media directory

MEDIA_URL = '/media/'

STATIC_ROOT = ''

STATIC_URL = '~/django_datacollector/datacollector/static/' # Absolute path to static directory

ADMIN_MEDIA_PREFIX = '/static/admin/'

STATICFILES_DIRS = (
)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
)

SECRET_KEY = 'blahblah' 

TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
)

ROOT_URLCONF = 'csc2518.urls'

TEMPLATE_DIRS = (
    "templates/",
)

TEMPLATE_CONTEXT_PROCESSORS = (
    'django.contrib.auth.context_processors.auth',
    'django.core.context_processors.request',
    'django.core.context_processors.static',
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'datacollector',
    # Uncomment the next line to enable admin documentation:
    'django.contrib.admindocs',
)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'ERROR',
            'propagate': True,
        },
    }
}

WSGI_APPLICATION = 'csc2518.wsgi.application'


# ---------------------------------------------------------
# CUSTOM VARIABLES ADDED TO SETTINGS

_prefix = "/"
RELATIVE_STATIC_URL = STATIC_URL
STATIC_URL = _prefix + STATIC_URL
ADMIN_MEDIA_PREFIX = _prefix + ADMIN_MEDIA_PREFIX
SUBSITE_ID = "talk2me/"
SYSTEM_CRED = '' 