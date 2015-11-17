"""Utils for dealing with API calls."""

import json
from urllib.request import urlopen


def decode_http_response(url):
    """Open the given URL and return the JSON decoded HttpResponse."""
    response = urlopen(url)
    str_response = response.readall().decode('utf-8')
    data = json.loads(str_response)
    return data