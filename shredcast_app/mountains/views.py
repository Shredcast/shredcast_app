from django.shortcuts import render
from django.views.generic import View

from django.conf import settings

from mountains.models import Mountain, SnowReport, WeatherReport
from users.models import UserLocation



class UserLocationView(View):
    """Get user location and drive time."""

    def get(self, request, *args, **kwargs):
        return render(request, 
                      'mountains/user_location.html',
                      {'api_key': settings.GOOGLE_MAPS_API_KEY})


class MountainResultsView(View):
    """Return best mountains for the user based on location and drive time."""

    def sort_mountains(self, mountain_list, day):
        """Return given mountain list, sorted by snowfall."""
        mountain_score_tuples = []
        for mountain in mountain_list:
            mountain_score_tuples.append(
                (mountain, mountain.calculate_shred_score(day)))

        sorted_mountain_tuples = sorted(
            mountain_score_tuples,
            key=lambda mountain: -mountain[1])

        return sorted_mountain_tuples

    def filter_mountains(self, mountain_list, user_location):
        """Return the given mountain list, filtered of out-of-range mountains.

        Loop the given mountain_list, and if a mountain isn't within driving
        range of user_location.drive_time, discard it. Once 10 reachable
        mountains are found, return them.
        """
        best_snow_in_range = []
        for mountain in mountain_list:
            if len(best_snow_in_range) >= 10:
                break
            if user_location.is_mountain_in_range(mountain[0]):
                best_snow_in_range.append(mountain[0])

        return best_snow_in_range

    def get_mountain_reports(self, mountain_list):
        """Return a list containing serialized mountain snow reports."""
        reports_list = []
        for mountain in mountain_list:
            snow_report = SnowReport.objects.get(mountain=mountain)
            weather_report = WeatherReport.objects.get(mountain=mountain)
            reports_list.append(dict(
                snow_report=snow_report.serialized(),
                weather_report=weather_report.serialized(), ))

        return reports_list

    def get(self, request, *args, **kwargs):
        address = request.GET.get('address')
        drive_time = request.GET.get('drive_time')
        shred_day = request.GET.get('shred_day')

        user_location = UserLocation.objects.create(address, drive_time)
        mountains_in_radius = user_location.get_mountains_in_radius()
        sorted_mountain_tuples = self.sort_mountains(mountains_in_radius, shred_day)
        best_snow_in_range = self.filter_mountains(
            sorted_mountain_tuples, user_location)
        mountain_reports = self.get_mountain_reports(best_snow_in_range)

        context = dict(mountains=mountain_reports) # need to tell view which day the shred is happening

        return render(request,
                      'mountains/mountain_results.html',
                      context)
