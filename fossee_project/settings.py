"""
Django settings for fossee_project project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""
#from local import DBNAME, DBUSER, DBPASS
from os.path import *
PROJDIR = abspath(dirname(__file__))
# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))
from getpass import getpass

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'j_4@2e^e*byl1c2@^=^)bo75r5h$l01aa8*)ladv7+8druq6f*'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = [] #['localhost'] when debug is False

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    join(PROJDIR, '../certificate/templates'),
) 

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #'south',
    'certificate',
    #'csvimport.app.CSVImportConf',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'fossee_project.urls'

WSGI_APPLICATION = 'fossee_project.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {

     'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': 'mydatabase',
    }
    # 'default': {
    #     'ENGINE': 'django.db.backends.mysql',
    #     'NAME' : DBNAME,
    #     #'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    #     'USER' : DBUSER,
    #     'PASSWORD': DBPASS,
    # }

}

# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'

# Set this varable to <True> if smtp-server is not allowing to send email.
EMAIL_USE_TLS = True

EMAIL_HOST = 'smtp-auth.iitb.ac.in'

EMAIL_PORT = 25

EMAIL_HOST_USER = 'dummy@iitb.ac.in'

EMAIL_HOST_PASSWORD = 'dummyme'

# Set EMAIL_BACKEND to 'django.core.mail.backends.smtp.EmailBackend'
# in production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'                    


# SENDER_EMAIL, REPLY_EMAIL, PRODUCTION_URL, IS_DEVELOPMENT are used in email
# verification. Set the variables accordingly to avoid errors in production

# This email id will be used as <from address> for sending emails.
# For example no_reply@<your_organization>.in can be used.
#SENDER_EMAIL = 'your_email'

# Organisation/Indivudual Name.
#SENDER_NAME = ''

# This email id will be used by users to send their queries
# For example queries@<your_organization>.in can be used.
#REPLY_EMAIL = ''

GOOGLE_RECAPTCHA_SECRET_KEY = '6LcDdk0UAAAAAOVRYSFOh07HwXMl0I9fPzTw4_VR'