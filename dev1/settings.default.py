# Django settings for dev1 project.
import os
import sys
ROOT_PATH_SETTINGS = os.path.dirname(os.path.abspath(__file__))
ROOT_PATH = os.path.join(ROOT_PATH_SETTINGS,"..")
PROJECT_DIR = os.path.abspath(os.path.join(ROOT_PATH_SETTINGS, '..'))
DEBUG = True 
TEMPLATE_DEBUG = DEBUG
CHARTIT_DIR = os.path.split(os.path.dirname(__file__))[0]
sys.path = [CHARTIT_DIR] + sys.path
PROJECT_ROOT = os.path.dirname(__file__)

ADMINS = (
    # ('Your Name', 'your_email@example.com'),
)

MANAGERS = ADMINS


DATABASES = {
    'default': {
        'ENGINE':  'postgresql_psycopg2' , #'django.contrib.gis.db.backends.postgis', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'kct',                      # Or path to database file if using sqlite3.
        'USER': 'postgres',                      # Not used with sqlite3.
        'PASSWORD': 'postgres',                  # Not used with sqlite3.
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '5433',
        'OPTIONS': {
        }
    }
	
	#'data': {
    #    'ENGINE': 'django.contrib.gis.db.backends.postgis', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
    #    'NAME': 'test',                      # Or path to database file if using sqlite3.
    #    'USER': 'postgres',                      # Not used with sqlite3.
    #    'PASSWORD': 'propertymode',                  # Not used with sqlite3.
    #    'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
    #    'PORT': '5433',
    #}
	
    #'data': {
    #    'NAME': 'FinDist_NYARUGENGE_NYARUGENGE',
    #    'ENGINE': 'sqlserver_ado',
    #    'HOST': 'JHMBP-PC\SQLEXPRESS',
    #    'USER': 'pmrw',
    #    'PASSWORD': 'pmrw123',
	#	'OPTIONS': {
	#		'autocommit': True,
	#	}
    #}
}


#DATABASE_ROUTERS = ['admin.defaultrouter.DefaultRouter', 'test.testrouter.TestRouter']

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# In a Windows environment this must be set to your system time zone.
TIME_ZONE = 'Australia/Sydney'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"


# - JUSTIN - MEDIA_ROOT = '/var/www/dev1/uploads/'
MEDIA_ROOT = os.path.join(PROJECT_DIR, 'uploads/')
#MEDIA_ROOT = 'C:/wamp/www/dev1/dev1/uploads'
# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = os.path.join(PROJECT_ROOT, 'static')

# URL prefix for static files.
# Example: "http://example.com/static/", "http://static.example.com/"
STATIC_URL = '/static/'

# Additional locations of static files
STATICFILES_DIRS = (
    # '/var/www/dev1/static',
	#'C:/wamp/www/dev1/dev1/static',
    os.path.join(PROJECT_DIR,'static'),
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)

# Make this unique, and don't share it with anybody.
SECRET_KEY = '7uxnb4znw7*7nuzxv!yyd3ziu(erg$%$%sdafghjkldvy!+=r2zpet**7lm3-q^5kn'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
#     'django.template.loaders.eggs.Loader',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    # Uncomment the next line for simple clickjacking protection:
    # 'django.middleware.clickjacking.XFrameOptionsMiddleware',
)

ROOT_URLCONF = 'dev1.urls'

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = 'dev1.wsgi.application'

TEMPLATE_DIRS = (
    # '/var/www/dev1/template',
	#'C:/wamp/www/dev1/dev1/template',
    os.path.join(ROOT_PATH,'template'),    
# Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
)

INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
	'django.contrib.humanize',
	'django.contrib.markup',
    #'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    #'django.contrib.gis',
    'property',
    'auth',
    'admin',
    'log',
	'contact',
    'citizen',
    'jtax',
    'businesslogic',
	'common',
	'asset',
	'forms',
	'media',
	'report',
	#'test',
	'import', 
    #'mytest',
    #'piston',
    #'api',
)


TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.media",
    "django.core.context_processors.request",
    "django.core.context_processors.i18n",
	"django.core.context_processors.static",
    "django.contrib.messages.context_processors.messages"
    )


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'filters': {
        'require_debug_false': {
            '()': 'django.utils.log.RequireDebugFalse'
        }
    },
    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'filters': ['require_debug_false'],
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

GOOGLECHARTS_API = '1.1'
from settings_local import *
