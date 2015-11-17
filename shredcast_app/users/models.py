from datetime import datetime

from django.db import models
from django.conf import settings

from utils import api_utils
from mountains.models import Mountain, SnowReport


class UserLocationManager(models.Manager):
    """Handles creation of UserLocations.

    Uses the Google Geocoding API to turn a user-given address into a lat/long
    which are then stored in the UserLocation model, along with the time of
    creation.
    """

    def create(self, address, drive_time):
        """Log a new UserLocation.

        Create a new UserLocation model and save it to the database.
        Turn address into latitude and longitude, and record an inserted
        timestamp. Then save.
        """
        inserted = datetime.now()
        address = address.replace(' ', '+')

        api_url = ('https://maps.googleapis.com/maps/api/geocode/json?'
            'address=%(address)s&key=%(key)s') % \
            {'address': address, 'key': settings.GOOGLE_PLACES_API_KEY}
        response = api_utils.decode_http_response(api_url)
        data = response['results'][0]['geometry']['location']
        latitude = data['lat']
        longitude = data['lng']
        user_location = UserLocation(
            address=address,
            drive_time=float(drive_time),
            latitude=latitude,
            longitude=longitude,
            inserted=inserted,
        )
        user_location.save()
        return user_location


class UserLocation(models.Model):
    """Record of user location/drive time entries.

    Is used to run our algorithm which uses user location/drive time.
    """

    address = models.CharField(max_length=255)
    drive_time = models.FloatField() # hours
    latitude = models.FloatField(blank=True, null=True)
    longitude = models.FloatField(blank=True, null=True)
    inserted = models.DateTimeField()

    objects = UserLocationManager()

    def get_mountains_in_radius(self):
        """Return list of mountains in conservative range of self.

        Use Mountain's estimated_minutes_from_point(lat, long) method to
        filter out all of the Mountains which could not possibly be within
        self.drive_time. Return a list of all remaining Mountains.
        """
        mountains = Mountain.objects.all()
        mountains_in_radius = []
        for mountain in mountains:
            estimated_drive_time = mountain.estimated_minutes_from_point(
                self.latitude, self.longitude) # minutes
            estimated_drive_time = estimated_drive_time / 60 # hours
            if estimated_drive_time <= self.drive_time:
                mountains_in_radius.append(mountain)

        return mountains_in_radius

    def is_mountain_in_range(self, mountain):
        """Return True if actual drive time to mountain < drive_time."""
        actual_drive = mountain.exact_minutes_from_point(
            self.latitude, self.longitude) # minutes
        actual_drive = actual_drive / 60 # hours, duh
        return actual_drive <= self.drive_time

