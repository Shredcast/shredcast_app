from .base import *

import dj_database_url

DATABASES['default'] =  dj_database_url.config()

# Enable Persistent Connections
DATABASES['default']['CONN_MAX_AGE'] = 500

# Simplified static file serving.
# https://warehouse.python.org/project/whitenoise/

STATICFILES_STORAGE = 'whitenoise.django.GzipManifestStaticFilesStorage'