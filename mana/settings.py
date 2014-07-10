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
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'api'
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

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    },
    'mana': {
         'ENGINE': 'django.db.backends.mysql',
         'NAME': 'nova',
         'USER': 'huming',
         'PASSWORD': 'huming1',
         'HOST': '192.168.39.112',
         'PORT': '',
    },

    'KEYSTONE': {
         'ENGINE': 'django.db.backends.mysql',
         'NAME': 'keystone',
         'USER': 'huming',
         'PASSWORD': 'huming1',
         'HOST': '192.168.39.112',
         'PORT': '',
    },

    'RegionOne_nova': {
         'ENGINE': 'django.db.backends.mysql',
         'NAME': 'nova',
         'USER': 'huming',
         'PASSWORD': 'huming1',
         'HOST': '192.168.39.112',
         'PORT': '',
    },
    'test_nova': {
         'ENGINE': 'django.db.backends.mysql',
         'NAME': 'nova',
         'USER': 'root',
         'PASSWORD': 'ztgame111',
         'HOST': '192.168.39.111',
         'PORT': '',
    },

    'RegionOne_neutron': {
         'ENGINE': 'django.db.backends.mysql',
         'NAME': 'neutron_linux_bridge',
         'USER': 'huming',
         'PASSWORD': 'huming1',
         'HOST': '192.168.39.112',
         'PORT': '',
    },
    'test_neutron': {
         'ENGINE': 'django.db.backends.mysql',
         'NAME': 'ovs_neutron',
         'USER': 'root',
         'PASSWORD': 'ztgame111',
         'HOST': '192.168.39.111',
         'PORT': '',
    },


}

"""
     Config for mana project
"""
REGIONS=(
	"test",
	"RegionOne",
)


#KS_AUTH="192.168.39.111:5000"
#KS_COMPUTE="192.168.39.110:8774"

#KS_USER="admin"
#KS_PWD="NanHui_Cloud@PWXadmin"
#KS_TENANT="admin"
#ADMIN_DEF_TID="7bd2a8b1b0374a42bc1b6cb9871b3fc1"


BACK_UP_AZ="BACKUP"

SYS_C2={
	"KS_USER":"admin",
	"KS_PWD":"NanHui_Cloud@PWXadmin",
	"tenant_id":"7bd2a8b1b0374a42bc1b6cb9871b3fc1",
	"KS_AUTH":"http://192.168.39.111:5000/v2.0",
	"KS_TENANT":"admin"
}



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

#C2 CONF START







#C2 CONF END
