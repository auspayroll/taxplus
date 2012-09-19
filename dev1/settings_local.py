# Local Settings FIle
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'kct',                      # Or path to database file if using sqlite3.
        'USER': 'kctuser',                      # Not used with sqlite3.
        'PASSWORD': 'kct123456',                  # Not used with sqlite3.
        'HOST': 'localhost',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',
        'OPTIONS': {
        }
    }
}


MAP_URL = "http://tile.st.propertymode.com.au"
SITE_URL = "http://kt.st.propertymode.com.au"


import logging
logging.basicConfig(
    level = logging.DEBUG,
    format = '%(asctime)s %(levelname)s %(message)s',
)

#DEBUG = False
