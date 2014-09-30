"""
Django settings for mana project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '9fp*i*gp!lxi1k5c5zo4&^2&hie5+_guoyzze0q#0**(gb^3#%'

# SECURITY WARNING: don't run with debug turned on in production!

import socket

if socket.gethostname()=="devstack":
    DEBUG = True
    TEMPLATE_DEBUG = True
else:
    DEBUG = True
    TEMPLATE_DEBUG = True

ALLOWED_HOSTS = ["*"]


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'api',
    'minions',
    'runner',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    #'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'mana.urls'

WSGI_APPLICATION = 'mana.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

import conf

DATABASES =conf.DATABASES

"""
     Config for mana project
"""
REGIONS=conf.REGIONS

BACK_UP_AZ="BACKUP"

SYS_C2=conf.SYS_C2


# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'zh-cn'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATICFILES_DIRS=(
	os.path.join(BASE_DIR,"static"),
	'/opt/projects/mana/static',
)


STATIC_URL = '/static/'

#STATIC_ROOT = os.path.join(BASE_DIR, "static/")

#C2 CONF START

C2_AUTH_TOKEN=conf.C2_AUTH_TOKEN

C2_LIMIT_NETWORK_FLOW_SCRIPT="sh /opt/minion/extmods/modules/bandwith_limit.sh"

C2_CHANGE_VIR_PWD_SCRIPT="python /opt/minion/extmods/modules/chg_pwd"

C2_STATIC=conf.STATIC


#C2 CONF END
