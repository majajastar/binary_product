"""
Django settings for binary_product project.

Generated by 'django-admin startproject' using Django 4.2.17.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""
import os
import logging
import pymysql
from pathlib import Path
from django.utils.translation import gettext_lazy as _
from celery.schedules import crontab
from datetime import timedelta

pymysql.install_as_MySQLdb()
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-$0a8l#!=$c&^_d47#%zlzso!ehlxkjpx=$jepaq(q23rikr5b='

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_celery_beat',
    'django_celery_results',
    'myapps.website',
    'myapps.orders',
    'myapps.prices',
    'myapps.users',
    'channels',
    
    # Allauth apps
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
]

ROOT_URLCONF = 'binary_product.urls'

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

WSGI_APPLICATION = 'binary_product.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

# Check if DEBUG is enabled to choose the database
if os.getenv('DJANGO_DEBUG', 'False') == 'True':  # You can also use DEBUG directly if set
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': os.getenv("RDS_DB_NAME"),
            'USER': os.getenv("RDS_USERNAME"),
            'PASSWORD': os.getenv("RDS_PASSWORD"),
            'HOST': os.getenv("RDS_HOSTNAME"),
            'PORT': os.getenv("RDS_PORT"),
        }
    }
    
# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/4.2/topics/i18n/

# Set the language code to Simplified Chinese
LANGUAGE_CODE = 'zh-hans'

TIME_ZONE = 'Asia/Taipei'

USE_I18N = True

USE_TZ = True

# Ensure that the language is available in the `LANGUAGES` setting
LANGUAGES = [
    ('zh-hans', _('Simplified Chinese')),
    # Add other languages you may need
    ('en', _('English')),
]

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.1/howto/static-files/

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'myapps/website/static'),
    os.path.join(BASE_DIR, 'myapps/users/static'),
]
# Whitenoise can serve compressed files, which improves performance
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

ASGI_APPLICATION = 'binary_product.asgi.application'

AUTH_USER_MODEL = 'users.User'  # Add this line in settings.py


# Celery settings
# Celery configuration
CELERY_BROKER_URL = 'sqs://'
CELERY_RESULT_BACKEND = 'django-db'  # Or use Redis, etc., based on your configuration.

# AWS SQS Configuration
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')  # or from environment variables
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
AWS_REGION = 'us-east-1'  # Update to your AWS region
CELERY_TASK_DEFAULT_QUEUE = 'default'
CELERY_TASK_DEFAULT_EXCHANGE = 'default'
CELERY_TASK_DEFAULT_ROUTING_KEY = 'default'

# You can configure your queues if needed:
CELERY_QUEUES = {
    'default': {
        'exchange': 'default',
        'routing_key': 'default',
    },
}
CELERY_LOGGER = logging.getLogger('celery')
CELERY_LOGGER.setLevel(logging.INFO)
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'

CELERY_BEAT_SCHEDULE = {
    'check_and_settle_orders_every_5_minutes': {
        'task': 'myapps.orders.tasks.check_and_settle_orders',  # Path to your Celery task
        'schedule': crontab(minute='0,5,10,15,20,25,30,35,40,45,50,55'),  # Run at 00, 05, 10, 15, ..., 55
    },
    # New periodic task: Generate prices every 4 hours
    'generate_prices_every_4_hours': {
        'task': 'myapps.prices.tasks.generate_prices_task',  # Path to the Celery task
        'schedule': crontab(hour='*/4', minute=2),  # Every 4 hours, at the 2th minute
    },
}