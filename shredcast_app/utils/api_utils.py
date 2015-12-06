"""Utils for dealing with API calls."""

import json
from urllib.request import urlopen


class APIError(Exception):
    """Exception for handling API errors."""

    def __init__(self, api, attempted_url, response):
        self.api = api
        self.attempted_url = attempted_url
        self.response = response

    def __str__(self):
        string = 'API Error for %(api)s with attempted url %(url)s' % \
            {'api': self.api, 'url': self.attempted_url}
        return string


def decode_http_response(url):
    """Open the given URL and return the JSON decoded HttpResponse."""
    response = urlopen(url)
    str_response = response.readall().decode('utf-8')
    data = json.loads(str_response)
    return data