"""
Django settings for eSharing project.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.6/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os,socket
SETTINGS_DIR = os.path.dirname(__file__)
PROJECT_PATH = os.path.join(SETTINGS_DIR, os.pardir)
PROJECT_PATH = os.path.abspath(PROJECT_PATH)
TEMPLATE_PATH = os.path.join(PROJECT_PATH, 'templates')
TEMPLATE_DIRS = ( TEMPLATE_PATH, )
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(PROJECT_PATH, 'media')

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.6/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'i1!f03pmc9%(r9yy*ifzrx+l+(#0+a#3@hpzy3px2^#oul0jnp'


# SECURITY WARNING: don't run with debug turned on in production!
if socket.gethostname()=='ansh-HP-430-Notebook-PC':
    DEBUG = True
    TEMPLATE_DEBUG = True
else:
    DEBUG = False
    TEMPLATE_DEBUG = False
    
ALLOWED_HOSTS = ['localhost','127.0.0.1']
#ALLOWED_HOSTS = ['*']
ADMINS = (
    ('anshul singh bisht', 'anshul.bisht06@gmail.com'),

)

# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'workNshare',
   'emoticons',
  # 'mod_wsgi.server',

)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'eSharing.urls'

WSGI_APPLICATION = 'eSharing.wsgi.application'


AUTH_PROFILE_MODULE = 'workNshare.UserProfile'

# Database
# https://docs.djangoproject.com/en/1.6/ref/settings/#databases

DATABASES = {
     'default':  {    
        'ENGINE': 'django.db.backends.mysql', 
        'NAME': 'workNshare',
        'USER': 'root',
        'PASSWORD': 'ANSHULbisht007',
	'HOST': '127.0.0.1',
        #'HOST': '52.26.69.232',   
        'PORT': '3306',
    }
}

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
        #'LOCATION': '127.0.0.1:11211',
		'LOCATION': '52.26.69.232:11211',
    }
}
# Internationalization
# https://docs.djangoproject.com/en/1.6/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

LOGIN_URL='/'
LOGIN_REDIRECT_URL = '/'
SESSION_EXPIRE_AT_BROWSER_CLOSE=True
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.6/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(PROJECT_PATH,'static')
