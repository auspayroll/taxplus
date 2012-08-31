# Local Settings FIle
DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'dev1',                      # Or path to database file if using sqlite3.
        'USER': 'dev',                      # Not used with sqlite3.
        'PASSWORD': 'password',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',
        'OPTIONS': {
        'init_command': 'SET storage_engine=MyISAM',
        }
    }
}

MAP_URL = "http://devtile.propertymode.com.au"
SITE_URL = "http://dev1.propertymode.com.au"