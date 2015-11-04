"""
Serves two purposes.
1. Loads the DB with some dummy data from which we can start to tweak
   the API into shape.
2. Is proof of concept for using Google to turn a resort name into an address,
   latitude, and longitude. All three will be useful for actually calculating
   users' travel times.

Works thusly:
- Uses the sample API key from SnoCountry (SnoCountry.example) to call the 
  getResortList API endpoint for each state which has a ski hill (stored in
  the states variable below...manually copied from their site).
- The API returns three sample resorts from each state, including their
  name, and SnoCountry ID. These two are of primary interest to us as far as
  the return from the SnoCountry API goes.
- The name returned via the SnoCountry API is then fed into the Google Places
  API, which returns the resort info, which includes latitude, longitude,
  and a formatted address.
"""

import json
from urllib.request import urlopen

try:
    from mountains.models import Mountain
except ImportError: # not running in Django, gotta whip up a nice sys.path
    import sys
    sys.path.append("/Users/maxwellskala/projects/shredcast/shredcast_app")
    from mountains.models import Mountain


states = [
    'AK', 'ID', 'OR', 'WA', 'AZ', 'CA', 'NV', 'CO', 'MT', 'NM', 'UT', 'WY',
    'IA', 'IL', 'IN', 'MI', 'MN', 'MO', 'ND', 'OH', 'SD', 'WI', 'CT', 'MA',
    'ME', 'NH', 'NJ', 'NY', 'PA', 'RI', 'VT', 'AL', 'GA', 'MD', 'NC', 'TN',
    'VA', 'WV',
]

def decode_http_response(url):
    """Open the given URL and return the JSON decoded HttpResponse."""
    response = urlopen(url)
    str_response = response.readall().decode('utf-8')
    data = json.loads(str_response)
    return data


def get_example_resorts(state_abbrev):
    """Take two-letter state code and return SnoCountry API list for that state."""
    api_url = ('http://feeds.snocountry.net/getResortList.php?apiKey='
        'SnoCountry.example&states=%(state)s&resortType=alpine&output=json') % \
        {'state' : state_abbrev}
    data = decode_http_response(api_url)
    resorts_list = data['items']
    return resorts_list


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
    data = decode_http_response(api_url)
    data = data['results']
    results['latitude'] = data[0]['geometry']['location']['lat']
    results['longitude'] = data[0]['geometry']['location']['lng']
    results['address'] = data[0]['formatted_address']
    results['google_id'] = data[0]['id']
    return results


def save_resorts_info(state_abbrev_list):
    """
    Take list of state codes and save relevant info to database.
    """
    for state_abbrev in state_abbrev_list:
        for resort in get_example_resorts(state_abbrev):
            snocountry_id = resort['id']
            name = resort['resortName']
            mountain_details = get_resort_location(name)
            Mountain.objects.get_or_create(
                name=name, address=mountain_details['address'],
                latitude=mountain_details['latitude'],
                longitude=mountain_details['longitude'],
                google_place_id=mountain_details['google_id'],
                snocountry_id=snocountry_id
            )


save_resorts_info(states)
