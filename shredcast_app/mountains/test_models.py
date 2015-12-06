from datetime import datetime

from django.test import TestCase

from mountains.models import Mountain, SnowReport, WeatherReport, TrailReport
from utils.api_utils import APIError


class TestMountainModel(TestCase):
    """Test the creation and methods of the Mountain model."""

    def setUp(self):
        self.old_reports_datetime = datetime(2015, 1, 1, 12, 0, 0)

        self.mountain, created = Mountain.objects.get_or_create(
            name='Alta',
            address=('Highway 210, Little Cottonwood Canyon, Alta, UT 84092,'
                'United States'),
            latitude=40.590829,
            longitude=-111.62877,
            google_place_id='4dbc30f34f550cc50cb8c4c212f1dc13f833543f',
            snocountry_id='801001', )

        SnowReport.objects.get_or_create(
            mountain=self.mountain,
            date_time=self.old_reports_datetime,
            snow_last_48=4,
            avg_base_depth_max=50,
            primary_condition='Packed Powder',
            snow_next_24=3,
            snow_next_48=6,
            snow_next_72=8,
            snow_next_week=12, )

        WeatherReport.objects.get_or_create(
            mountain=self.mountain,
            date_time=self.old_reports_datetime,
            today_base_temp=28,
            today_summit_temp=16,
            today_temp_low=24,
            today_temp_high=31,
            today_weather='Mostly Sunny',
            today_wind=12,
            tomorrow_temp_low=25,
            tomorrow_temp_high=29,
            tomorrow_weather='Partly Cloudy',
            tomorrow_wind=15, )

        TrailReport.objects.get_or_create(
            mountain=self.mountain,
            date_time=self.old_reports_datetime,
            max_trails=108,
            max_miles=45,
            max_acres=2500,
            max_lifts=15,
            open_trails=50,
            open_miles=25,
            open_acres=1500,
            open_lifts=7,
            parks_open=2,
            park_features=12,
            trail_map_small='totallybsurl',
            trail_map_large='evenmorebsurl', )

    def test_estimate_minutes_from_point(self):
        """Return a float."""
        result = self.mountain.estimated_minutes_from_point(40.0, -100.0)
        self.assertIs(type(result), float)

    def test_exact_minutes_from_point_failure(self):
        """The exact_minutes_from_point function should elegantly fail.

           If provided an impossible drive (i.e. Alta to Paris in this test),
           the function should raise an APIError.
        """
        self.assertRaises(
            APIError, 
            lambda: self.mountain.exact_minutes_from_point(48.8567, 2.3508))

    def test_exact_minutes_from_point(self):
        """Return a float.

        @TODO: figure out a way to test this without actually hitting the
        Google API.
        """
        result = self.mountain.exact_minutes_from_point(40.0, -100.0)
        self.assertIs(type(result), float)

    def test_get_latest_report(self):
        """Result in the creation of new Report objects in the DB.

        Also delete any old reports for the given Mountain.

        @TODO: figure out a way to test this without actually hitting the
        SnoCountry API.
        """
        snow_reports = SnowReport.objects.filter(mountain=self.mountain)
        weather_reports = WeatherReport.objects.filter(mountain=self.mountain)
        trail_reports = TrailReport.objects.filter(mountain=self.mountain)
        self.assertEqual(snow_reports.count(), 1)
        self.assertEqual(weather_reports.count(), 1)
        self.assertEqual(trail_reports.count(), 1)
        self.assertEqual(snow_reports[0].date_time, self.old_reports_datetime)
        self.assertEqual(weather_reports[0].date_time, 
                         self.old_reports_datetime)
        self.assertEqual(trail_reports[0].date_time, self.old_reports_datetime)

        self.mountain.get_latest_report()

        snow_reports = SnowReport.objects.filter(mountain=self.mountain)
        weather_reports = WeatherReport.objects.filter(mountain=self.mountain)
        trail_reports = TrailReport.objects.filter(mountain=self.mountain)
        self.assertEqual(snow_reports.count(), 1) # should have deleted old one
        self.assertEqual(weather_reports.count(), 1) # same as above
        self.assertEqual(trail_reports.count(), 1) # same as above
        self.assertNotEqual(snow_reports[0].date_time, 
                            self.old_reports_datetime)
        self.assertNotEqual(weather_reports[0].date_time, 
                            self.old_reports_datetime)
        self.assertNotEqual(trail_reports[0].date_time, 
                            self.old_reports_datetime)

    def test_calculate_shred_score(self):
        """Test that shred scores are calculated correctly.

        Currently, if today=True, then the shred score is simply the sum of
        SnowReport.snow_last_48 and SnowReport.avg_base_depth_max. Otherwise,
        it is SnowReport.snow_last_48 + snow_next_24.
        """
        snow_report = SnowReport.objects.get(mountain=self.mountain)
        today_shred_score = (snow_report.snow_last_48 + 
            snow_report.avg_base_depth_max)
        tomorrow_shred_score = (snow_report.snow_last_48 + 
            snow_report.snow_next_24)

        self.assertEqual(self.mountain.calculate_shred_score(True),
                         today_shred_score)
        self.assertEqual(self.mountain.calculate_shred_score(False),
                         tomorrow_shred_score)
