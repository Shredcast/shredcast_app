import json
from urllib.request import urlopen
from datetime import datetime

from django.db import models
from django.conf import settings

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

    def estimated_minutes_from_point(self, latitude, longitude):
        """Return the drive time from this Mountain to the given point.

        Underestimate the drive time from this resort's latitude and
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

    def exact_minutes_from_point(self, latitude, longitude):
        """Return the exact drive time from this Mountain to the given point.

        Use the Google Maps API to calculate the driving distance between this
        Mountain and the given latitude and longitude. Time is in minutes.
        """
        api_args = {
            'key' : settings.GOOGLE_PLACES_API_KEY,
            'start' : str(self.latitude) + ',' + str(self.longitude),
            'end' : str(latitude) + ',' + str(longitude),
        }
        api_url = ('https://maps.googleapis.com/maps/api/distancematrix/json?'
            'origins=%(start)s&destinations=%(end)s&key=%(key)s') % api_args
        response = urlopen(api_url)
        str_response = response.readall().decode('utf-8')
        data = json.loads(str_response)
        seconds_drive = data['rows'][0]['elements'][0]['duration']['value']
        minutes_drive = int(seconds_drive) / 60
        return minutes_drive

    def get_latest_snow_report(self):
        """Update the latest snow report for this Mountain.

        Use the SnoCountry API to retrieve the most updated snow report
        for this Mountain, and store it in a SnowReport model.
        """
        api_args = {
            'key' : settings.SNOCOUNTRY_API_KEY,
            'mtn_id' : self.snocountry_id,
        }
        api_url = ('http://feeds.snocountry.net/conditions.php?apiKey=%(key)s&'
            'ids=%(mtn_id)s') % api_args
        response = urlopen(api_url)
        str_response = response.readall().decode('utf-8')
        data = json.loads(str_response)
        data = data['items'][0]
        report_datetime_string = data['reportDateTime']
        report_datetime = datetime.strptime(report_datetime_string, 
                                            '%Y-%m-%d %H:%M:%S')
        snow_report_dict = {
            'mountain' : self,
            'datetime' : report_datetime,
            'snow_last_48' : data['snowLast48Hours'],
            'avg_base_depth_max' : data['avgBaseDepthMax'],
            'snow_next_24' : data['predictedSnowFall_24Hours'],
            'snow_next_48' : data['predictedSnowFall_48Hours'],
            'snow_next_72' : data['predictedSnowFall_72Hours'],
            'snow_next_week' : data['predictedSnowFall_7days']
        }

        # SnoCountry API returns snow measurements as strings, and we want to
        # store them as ints. So here we loop through the above dict and cast
        # all strings to ints. If the API returned an empty string (''), we
        # assume that measurement was 0.
        for key, value in snow_report_dict.items():
            if key in ['datetime', 'mountain']:
                continue # Ignore non snow measurements
            snow_report_dict[key] = int(value) if value else 0

        # Delete outdated reports and create the new one
        SnowReport.objects.filter(mountain=self).delete()
        SnowReport.objects.create(**snow_report_dict)

    def calculate_shred_score(self):
        """Estimate desirability of snow on self.

        Using the latest SnowReport for self, calculate how good the snow
        currently is for the resort represented by self.
        """
        latest_report = SnowReport.objects.get(mountain=self)
        new_snow = latest_report.snow_last_48 + latest_report.snow_next_24
        return new_snow


class SnowReport(models.Model):
    """Represents a snow report for a particular mountain.

    All snow measurements are recorded in inches.
    """

    mountain = models.ForeignKey('Mountain')
    datetime = models.DateTimeField()
    avg_base_depth_max = models.PositiveIntegerField()
    snow_last_48 = models.PositiveIntegerField()
    snow_next_24 = models.PositiveIntegerField()
    snow_next_48 = models.PositiveIntegerField()
    snow_next_72 = models.PositiveIntegerField()
    snow_next_week = models.PositiveIntegerField()

