from django import forms
from django.conf import settings

from users.models import UserLocation
from utils import api_utils


class UserLocationForm(forms.ModelForm):
    """Validate our incoming user location data."""

    class Meta:
        model = UserLocation
        fields = ('address', 'drive_time', 'going_today', )

    def clean_address(self):
        api_friendly_address = self.cleaned_data['address'].replace(' ', '+')
        api_key = settings.GOOGLE_MAPS_API_KEY
        api_url = ('https://maps.googleapis.com/maps/api/geocode/json?address=%(address)s&' 
            'key=%(key)s') % {'address': api_friendly_address, 'key': api_key}
        response = api_utils.decode_http_response(api_url)
        data = response['results']
        if len(data) > 1: # found more than one location for address, need something more specific
            self.add_error('address', 'Invalid address')
        else:
            return self.cleaned_data['address']

    def save(self):
        address = self.cleaned_data['address']
        drive_time = self.cleaned_data['drive_time']
        going_today = self.cleaned_data['going_today']

        user_location = UserLocation.objects.create(address, drive_time, going_today)
        return user_location
