"""
Django settings for bioconvertserver project.

Generated by 'django-admin startproject' using Django 1.11.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.11/ref/settings/
"""

import os

from django.utils.translation import ugettext_lazy
from kombu import Exchange, Queue
import configparser

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

locals_ini = [
    os.path.join(BASE_DIR, 'resources', 'default.ini'),
    os.path.join('etc', 'composeexample', 'default.ini'),
    os.path.join(BASE_DIR, 'resources', 'local.ini'),
    os.path.join('etc', 'composeexample', 'local.ini'),
]
config = configparser.ConfigParser()
config.add_section('global')
config.optionxform = str
for local_ini in locals_ini:
    if os.path.isfile(local_ini):
        config.read(local_ini)

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.11/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config['global'].get('SECRET_KEY', 'q5s+!b&w@o75t@d)y99dc11j=m#i&ue^k!^#&imao*5*h3&&sx')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config['global'].get('DEBUG', 'true').lower() == 'true'

ALLOWED_HOSTS = []

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_crontab',
    'bootstrap4',
    'bioconvertapi',
    'webui',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'bioconvertserver.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'bioconvertserver.wsgi.application'

# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases


if "POSTGRES_PASSWORD" in os.environ:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'postgres',
            'USER': 'postgres',
            'PASSWORD': config['global']['POSTGRES_PASSWORD'],
            'HOST': 'db',
            'PORT': 5432,
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

# Password validation
# https://docs.djangoproject.com/en/1.11/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/1.11/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True
LANGUAGES = [
    ('en', ugettext_lazy('English')),
    # ('fr', ugettext_lazy('French')),
]

USE_L10N = True

USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.11/howto/static-files/
# STATICFILES_DIRS = [
#     os.path.join(BASE_DIR, "webui", "static"),
# ]
STATIC_ROOT = os.path.join(BASE_DIR, '.static')
STATIC_URL = config['global'].get('STATIC_URL', '/static') + '/'
MEDIA_ROOT = os.path.join(BASE_DIR, '.media')
MEDIA_URL = config['global'].get('MEDIA_URL', '/media') + '/'

# django-crontab
CRONJOBS = [
    ('0 4 * * *', 'django.core.management.call_command', ['clearsessions']),
]
CRONTAB_LOCK_JOBS = True
CRONTAB_COMMAND_SUFFIX = '>> /var/log/apache2/django-crontab.log'

SESSION_COOKIE_AGE = 14 * 24 * 60 * 60 if DEBUG else 12 * 60 * 60
SESSION_COOKIE_SECURE = False if DEBUG else True

################################################################################
# Redis
################################################################################

REDIS_PORT = 6379
REDIS_DB = 0
REDIS_HOST = os.environ.get('REDIS_PORT_6379_TCP_ADDR', 'redis')

RABBIT_HOSTNAME = os.environ.get('RABBIT_PORT_5672_TCP', 'rabbit')

if RABBIT_HOSTNAME.startswith('tcp://'):
    RABBIT_HOSTNAME = RABBIT_HOSTNAME.split('//')[1]

BROKER_URL = os.environ.get('BROKER_URL', '')
if not BROKER_URL:
    BROKER_URL = 'amqp://{user}:{password}@{hostname}/{vhost}/'.format(
        user=os.environ.get('RABBITMQ_DEFAULT_USER', 'admin'),
        password=os.environ.get('RABBITMQ_DEFAULT_PASS', 'mypass'),
        hostname=RABBIT_HOSTNAME,
        vhost=os.environ.get('RABBIT_ENV_VHOST', ''))

# We don't want to have dead connections stored on rabbitmq, so we have to negotiate using heartbeats
BROKER_HEARTBEAT = '?heartbeat=30'
if not BROKER_URL.endswith(BROKER_HEARTBEAT):
    BROKER_URL += BROKER_HEARTBEAT

BROKER_POOL_LIMIT = 1
BROKER_CONNECTION_TIMEOUT = 10

################################################################################
# Celery configuration
################################################################################

CELERY_ENABLE_UTC = True
CELERY_TIMEZONE = "UTC"

# configure queues, currently we have only one
CELERY_DEFAULT_QUEUE = 'default'
CELERY_QUEUES = (
    Queue('default', Exchange('default'), routing_key='default'),
)

# Sensible settings for celery
CELERY_ALWAYS_EAGER = False
CELERY_ACKS_LATE = True
CELERY_TASK_PUBLISH_RETRY = True
CELERY_DISABLE_RATE_LIMITS = False

# By default we will ignore result
# If you want to see results and try out tasks interactively, change it to False
# Or change this setting on tasks level
CELERY_IGNORE_RESULT = True
CELERY_SEND_TASK_ERROR_EMAILS = False
CELERY_TASK_RESULT_EXPIRES = 600

# Set redis as celery result backend
CELERY_RESULT_BACKEND = 'redis://%s:%d/%d' % (REDIS_HOST, REDIS_PORT, REDIS_DB)
CELERY_REDIS_MAX_CONNECTIONS = 1

# Don't use pickle as serializer, json is much safer
CELERY_TASK_SERIALIZER = "json"
CELERY_ACCEPT_CONTENT = ['application/json']

CELERYD_HIJACK_ROOT_LOGGER = False
CELERYD_PREFETCH_MULTIPLIER = 1
CELERYD_MAX_TASKS_PER_CHILD = 1000

CELERY_ENABLED = os.environ.get('RABBITMQ_DEFAULT_USER', '') != ''

################################################################################
# Local settings
################################################################################
try:
    from .local_settings import *
except ImportError as e:
    print(e)
    pass


################################################################################
#
################################################################################