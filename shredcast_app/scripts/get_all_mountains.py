"""
Script to gather all the mountains from the SnoCountry API using the example
API key. Test to see how many mountains they really have, and if this is a
feasible method of checking that.

Works by incrementing theoretical mountain IDs from 000000 to 999999,
checking if each corresponds to a mountain based on the API return.
If a mountain is found at a given ID, it is stored.
"""

import json
from urllib.request import urlopen

try:
    from mountains.models import Mountain
    from utils import api_utils
except ImportError: # not running in Django, gotta whip up a nice sys.path
    import sys
    sys.path.append("/Users/maxwellskala/projects/shredcast/shredcast_app")
    from mountains.models import Mountain
    from utils import api_utils


def get_resort_location(resort_name):
    """
    Take resort dict and return dict with resort location info.

    The resort dict is the decoded JSON from a SnoCountry getResortList call.
    It contains lots of extraneous information, all that is needed is the
    resort name, which is then fed to the Google Places API. From the Google
    Places API response is extracted a latitude, longitude, and formatted
    street address, which is returned in a dict.
    """
    results = {'address': '', 'latitude':0.000000, 'longitude':0.000000}
    resort_name = resort_name.replace(' ', '+')
    api_url = ('https://maps.googleapis.com/maps/api/place/textsearch/json?'
        'query=%(resort_name)s&key=AIzaSyDZai-ebT6Kq1_RoDU7bdoshKdQe63RR4w') % \
        {'resort_name' : resort_name}
    data = api_utils.decode_http_response(api_url)
    data = data['results']
    results['latitude'] = data[0]['geometry']['location']['lat']
    results['longitude'] = data[0]['geometry']['location']['lng']
    results['address'] = data[0]['formatted_address']
    results['google_id'] = data[0]['id']
    return results


for i in range(0, 1000000):
    if i > 10000:
        break
    i = str(i).zfill(6)
    print(i)
    api_url = ('http://feeds.snocountry.net/conditions.php?'
        'apiKey=SnoCountry.example&ids=%s') % i
    data = api_utils.decode_http_response(api_url)
    if int(data['totalItems']) == 0:
        continue
    else:
        try:
            data = data['items'][0]
            resort_name = data['resortName']
            resort_snocountry_id = data['id']
            mountain_details = get_resort_location(resort_name)
            Mountain.objects.get_or_create(
                name=resort_name, address=mountain_details['address'],
                latitude=mountain_details['latitude'],
                longitude=mountain_details['longitude'],
                google_place_id=mountain_details['google_id'],
                snocountry_id=resort_snocountry_id, )
            print(resort_name)
        except: # catch anything!
            print(data) # let's see what got fucked up
