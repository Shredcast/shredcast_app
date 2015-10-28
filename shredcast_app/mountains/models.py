from django.db import models

from geopy.distance import vincenty

class Mountain(models.Model):
    """Represents a ski resort at which users may get their shred on.

    The address field is formatted like so: 
    1111 Somestreet Way, Somecity, AB 123456
    """
    
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    latitude = models.FloatField()
    longitude = models.FloatField()
    google_place_id = models.CharField(max_length=255, default='')
    snocountry_id = models.CharField(max_length=255, default='')

    def estimate_minutes_from_point(self, latitude, longitude):
        """Return the drive time from this mountain to the given point.

        Underestimate the drive time from this mountain's latitude and
        longitude to the given latitude and longitude. The driver is
        assumed to maintain a constant speed of 80 miles per hour and to
        be driving in a straight line. 

        Return value is a float representing drive time in minutes.
        """
        mountain_coords = (self.latitude, self.longitude)
        target_coords = (latitude, longitude)
        miles_apart = vincenty(mountain_coords, target_coords).miles
        minutes_drive = (miles_apart / 80) * 60
        return minutes_drive
