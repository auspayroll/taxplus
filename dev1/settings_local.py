# Local Settings FIle
#DATABASES = {
#    'default': {
#        'ENGINE': 'django.contrib.gis.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.

#        'NAME': 'dev1',                      # Or path to database file if using sqlite3.
#        'USER': 'dev',                      # Not used with sqlite3.
#        'PASSWORD': 'password',                  # Not used with sqlite3.
#        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
#        'PORT': '',
#        'OPTIONS': {
#        'init_command': 'SET storage_engine=MyISAM',
#        }
#    }
#}

MAP_URL = "http://devtile.propertymode.com.au"
SITE_URL = "http://dev1.propertymode.com.au"
COLOR_PROVINCE = "#FF0000"
COLOR_COUNCIL = "#00ff00"
COLOR_DISTRICT = "#0000FF"
COLOR_SECTOR = "#FFFFFF"
COLOR_HOUSE = "#FFFF00"
COLOR_DECLAREDVALUE = "#020F0"
COLOR_TAX = "#FFC0CB"

#### This variable is for javascript ###
DATE_FORMAT = "dd/mm/yy"



#### This variable is for modelform datefield ###
DATE_INPUT_FORMATS = ('%d/%m/%Y', '%b. %d, %Y', '%b %d %Y', '%b. %d %Y', '%B %d %Y', '%d %B %Y', '%d %b %Y')
DATE_INPUT_FORMAT = '%d/%m/%Y'

#import logging
#logging.basicConfig(
#    level = logging.DEBUG,
#    format = '%(asctime)s %(levelname)s %(message)s',
#)

#DEBUG = False
