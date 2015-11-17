from django.shortcuts import render
from django.views.generic import View

from django.conf import settings

from mountains.models import Mountain, SnowReport
from users.models import UserLocation



class UserLocationView(View):
    """Get user location and drive time."""

    def get(self, request, *args, **kwargs):
        return render(request, 
                      'mountains/user_location.html',
                      {'api_key': settings.GOOGLE_MAPS_API_KEY})


class MountainResultsView(View):
    """Return best mountains for the user based on location and drive time."""

    def sort_mountains(self, mountain_list):
        """Return given mountain list, sorted by snowfall."""
        mountain_score_tuples = []
        for mountain in mountain_list:
            mountain_score_tuples.append(
                (mountain, mountain.calculate_shred_score()))

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
        """Return a list of dicts containing mountain snow reports.

        For each mountain in list, create a dict like so:
        dict(
            name: string,
            address: string,
            avg_base_depth: int,
            snow_last_48: int,
            snow_next_24: int,
            snow_next_48: int,
            snow_next_72: int,
            snow_next_week: int, )

        @TODO: make this a method of SnowReport (basically a serialized function),
               clean up this docstring a bit
        """
        reports_list = []
        for mountain in mountain_list:
            snow_report = SnowReport.objects.get(mountain=mountain)
            report_dict = dict(
                name=mountain.name,
                address=mountain.address,
                avg_base_depth=snow_report.avg_base_depth_max,
                snow_last_48=snow_report.snow_last_48,
                snow_next_24=snow_report.snow_next_24,
                snow_next_48=snow_report.snow_next_48,
                snow_next_72=snow_report.snow_next_72,
                snow_next_week=snow_report.snow_next_week, )
            reports_list.append(report_dict)

        return reports_list

    def get(self, request, *args, **kwargs):
        address = request.GET.get('address')
        drive_time = request.GET.get('drive_time')

        user_location = UserLocation.objects.create(address, drive_time)
        mountains_in_radius = user_location.get_mountains_in_radius()
        sorted_mountain_tuples = self.sort_mountains(mountains_in_radius)
        best_snow_in_range = self.filter_mountains(
            sorted_mountain_tuples, user_location)
        mountain_reports = self.get_mountain_reports(best_snow_in_range)

        context = dict(mountains=mountain_reports)

        # create some kind of UserResult model to record what we send back to the user
        # (it should foreign key to the UserLocation model so we know what the user asked for)

        return render(request,
                      'mountains/mountain_results.html',
                      context)
