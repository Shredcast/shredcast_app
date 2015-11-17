"""
Serves two purposes.
1. Loads the DB up with some snow report data so that development can begin
   on the API/algorithm for the frontend.
2. Serves as proof of concept (and a code basis) for what will eventually
   be our snow report gathering task, which will run all day to ensure
   that our snow data is up to date.
"""

import json
from urllib.request import urlopen

import django

try:
    from mountains.models import Mountain
except ImportError: # not running in Django, gotta whip up a nice sys.path
    import sys
    sys.path.append("/Users/maxwellskala/projects/shredcast/shredcast_app")
    from mountains.models import Mountain

django.setup()

mountains = Mountain.objects.all()
for mountain in mountains:
    mountain.get_latest_snow_report()
