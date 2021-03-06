import json
from urllib.request import urlopen
from datetime import datetime

from django.db import models
from django.conf import settings

from geopy.distance import vincenty

from utils import api_utils


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
        Mountain and the given latitude and longitude. Time is a float in 
        minutes.
        """
        api_args = {
            'key' : settings.GOOGLE_PLACES_API_KEY,
            'start' : str(self.latitude) + ',' + str(self.longitude),
            'end' : str(latitude) + ',' + str(longitude),
        }
        api_url = ('https://maps.googleapis.com/maps/api/distancematrix/json?'
            'origins=%(start)s&destinations=%(end)s&key=%(key)s') % api_args
        data = api_utils.decode_http_response(api_url)
        try:
            seconds_drive = data['rows'][0]['elements'][0]['duration']['value']
        except KeyError:
            raise api_utils.APIError('google_places', api_url, data)

        minutes_drive = int(seconds_drive) / 60
        return minutes_drive

    def get_latest_report(self):
        """Update the latest snow/weather/trail reports for this Mountain.

        Use the SnoCountry API to retrieve the most updated snow report
        for this Mountain, and store it in a SnowReport model, as well
        as storing the most updated weather report for this Mountain in
        a WeatherReport model.
        """
        api_args = {
            'key' : settings.SNOCOUNTRY_API_KEY,
            'mtn_id' : self.snocountry_id,
        }
        api_url = ('http://feeds.snocountry.net/conditions.php?apiKey=%(key)s&'
            'ids=%(mtn_id)s') % api_args
        data = api_utils.decode_http_response(api_url)
        data = data['items'][0]
        report_datetime_string = data['reportDateTime']
        report_datetime = datetime.strptime(report_datetime_string, 
                                            '%Y-%m-%d %H:%M:%S')
        snow_report_dict = {
            'mountain' : self,
            'date_time' : report_datetime,
            'snow_last_48' : data['snowLast48Hours'],
            'avg_base_depth_max' : data['avgBaseDepthMax'],
            'primary_condition': data['primarySurfaceCondition'],
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
            if key in ['date_time', 'mountain', 'primary_condition']:
                continue # Ignore non snow measurements
            try:
                snow_report_dict[key] = int(float(value)) if value else 0
            except ValueError: # probably got something like '1 - 2' for snow
                new_value = value.split()[0]
                snow_report_dict[key] = int(float(new_value)) if new_value else 0 

        # Delete outdated reports and create the new one
        SnowReport.objects.filter(mountain=self).delete()
        SnowReport.objects.create(**snow_report_dict)

        weather_report_dict = {
            'mountain': self,
            'date_time': report_datetime,
            'today_base_temp': data['forecastBaseTemp'],
            'today_summit_temp': data['forecastTopTemp'],
            'today_temp_low': data['weatherToday_Temperature_Low'],
            'today_temp_high': data['weatherToday_Temperature_High'],
            'today_weather': data['weatherToday_Condition'],
            'today_wind': data['weatherToday_WindSpeed'],
            'tomorrow_temp_low': data['weatherTomorrow_Temperature_Low'],
            'tomorrow_temp_high': data['weatherTomorrow_Temperature_High'],
            'tomorrow_weather': data['weatherTomorrow_Condition'],
            'tomorrow_wind': data['weatherTomorrow_WindSpeed'],
        }
        # Once again casting our string measurements to ints where applicable
        for key, value in weather_report_dict.items():
            if key in ['mountain', 'date_time', 
                       'today_weather', 'tomorrow_weather']:
                continue
            weather_report_dict[key] = int(float(value)) if value else 0

        WeatherReport.objects.filter(mountain=self).delete()
        WeatherReport.objects.create(**weather_report_dict)

        trail_report_dict = {
            'mountain': self,
            'date_time': report_datetime,
            'max_trails': data['maxOpenDownHillTrails'],
            'max_miles': data['maxOpenDownHillMiles'],
            'max_acres': data['maxOpenDownHillAcres'],
            'max_lifts': data['maxOpenDownHillLifts'],
            'open_trails': data['openDownHillTrails'],
            'open_miles': data['openDownHillMiles'],
            'open_acres': data['openDownHillAcres'],
            'open_lifts': data['openDownHillLifts'],
            'parks_open': data['numberTerrainParksOpen'],
            'park_features': data['numberTerrainParkFeatures'],
            'trail_map_small': data['tnTrailMapURL'],
            'trail_map_large': data['lgTrailMapURL'],
        }
        # casting again
        for key, value in trail_report_dict.items():
            if key in ['mountain', 'date_time', 'trail_map_small', 
                       'trail_map_large']:
                continue
            trail_report_dict[key] = int(float(value)) if value else 0

        TrailReport.objects.filter(mountain=self).delete()
        TrailReport.objects.create(**trail_report_dict)

    def calculate_shred_score(self, today):
        """Estimate desirability of snow on self.

        Using the latest SnowReport for self, calculate how good the snow
        currently is for the resort represented by self.
        """
        latest_report = SnowReport.objects.get(mountain=self)
        if today:
            new_snow = latest_report.snow_last_48 + latest_report.avg_base_depth_max
        else:
            new_snow = latest_report.snow_last_48 + latest_report.snow_next_24
        return new_snow


class SnowReport(models.Model):
    """Represents a snow report for a particular mountain.

    All snow measurements are recorded in inches.
    """

    mountain = models.ForeignKey(Mountain)
    date_time = models.DateTimeField()
    avg_base_depth_max = models.PositiveIntegerField()
    primary_condition = models.CharField(max_length=100, blank=True, null=True)
    snow_last_48 = models.PositiveIntegerField()
    snow_next_24 = models.PositiveIntegerField()
    snow_next_48 = models.PositiveIntegerField()
    snow_next_72 = models.PositiveIntegerField()
    snow_next_week = models.PositiveIntegerField()

    def serialized(self):
        """Return a dict of self and the name and address of self.mountain."""
        result = dict(
            name=self.mountain.name,
            address=self.mountain.address,
            date_time=self.date_time,
            avg_base_depth=self.avg_base_depth_max,
            snow_last_48=self.snow_last_48,
            snow_next_24=self.snow_next_24,
            snow_next_48=self.snow_next_48,
            snow_next_72=self.snow_next_72,
            snow_next_week=self.snow_next_week, )
        return result


class WeatherReport(models.Model):
    """Represents a weather report for a particular mountain.

    Temperatures are in Fahrenheit and wind speeds in miles per hour.
    """

    mountain = models.ForeignKey(Mountain)
    date_time = models.DateTimeField()
    today_base_temp = models.IntegerField()
    today_summit_temp = models.IntegerField()
    today_temp_low = models.IntegerField()
    today_temp_high = models.IntegerField()
    today_weather = models.CharField(max_length=100) # e.g. 'Partly Cloudy'
    today_wind = models.IntegerField()
    tomorrow_temp_low = models.IntegerField()
    tomorrow_temp_high = models.IntegerField()
    tomorrow_weather = models.CharField(max_length=100)
    tomorrow_wind = models.IntegerField()

    def serialized(self):
        """Return a dict of self and the name and address of self.mountain."""
        result = dict(
            name=self.mountain.name,
            address=self.mountain.address,
            date_time=self.date_time,
            today_temp_low=self.today_temp_low,
            today_temp_high=self.today_temp_high,
            today_weather=self.today_weather,
            today_wind=self.today_wind,
            tomorrow_temp_low=self.tomorrow_temp_low,
            tomorrow_temp_high=self.tomorrow_temp_high,
            tomorrow_weather=self.tomorrow_weather,
            tomorrow_wind=self.tomorrow_wind, )
        return result


class TrailReport(models.Model):
    """Represents a trail report for a particular mountain."""

    mountain = models.ForeignKey(Mountain)
    date_time = models.DateTimeField()
    max_trails = models.PositiveIntegerField()
    max_miles = models.PositiveIntegerField()
    max_acres = models.PositiveIntegerField()
    max_lifts = models.PositiveIntegerField()
    open_trails = models.PositiveIntegerField()
    open_miles = models.PositiveIntegerField()
    open_acres = models.PositiveIntegerField()
    open_lifts = models.PositiveIntegerField()
    parks_open = models.PositiveIntegerField()
    park_features = models.PositiveIntegerField()
    trail_map_small = models.CharField(max_length=256) # URL
    trail_map_large = models.CharField(max_length=256) # URL

    def serialized(self):
        """Return a dict of self and the name and address of self.mountain."""
        result = dict(
            name=self.mountain.name,
            address=self.mountain.address,
            date_time=self.date_time,
            max_trails=self.max_trails,
            max_miles=self.max_miles,
            max_acres=self.max_acres,
            max_lifts=self.max_lifts,
            open_trails=self.open_trails,
            open_miles=self.open_miles,
            open_acres=self.open_acres,
            open_lifts=self.open_lifts,
            parks_open=self.parks_open,
            park_featuers=self.park_features, )
        return result
