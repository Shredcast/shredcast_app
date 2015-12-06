from django.shortcuts import render
from django.views.generic import View

from django.conf import settings

from mountains.models import Mountain, SnowReport, WeatherReport, TrailReport
from users.models import UserLocation
from users.forms import UserLocationForm
from utils.api_utils import APIError


class MountainResultsView(View):
    """Return best mountains for the user based on location and drive time."""

    def get(self, request, *args, **kwargs):
        form = UserLocationForm(request.GET)
        if form.is_valid():
            user_location = form.save()
            today = user_location.going_today
            mountains = user_location.get_mountains_in_radius()
            sorted(mountains, 
                   key=lambda mountain: mountain.calculate_shred_score(today))
            final_mountains = []
            for mountain in mountains:
                if len(final_mountains) >= 10:
                    break
                try:
                    exact_drive_time = mountain.exact_minutes_from_point(
                        user_location.latitude,
                        user_location.longitude)
                    if user_location.drive_time < exact_drive_time / 60:
                        continue

                    snow_report = SnowReport.objects.get(mountain=mountain)
                    weather_report = WeatherReport.objects.get(mountain=mountain)
                    trail_report = TrailReport.objects.get(mountain=mountain)
                    mountain_dict = dict(
                        drive_time=exact_drive_time / 60,
                        snow_report=snow_report.serialized(),
                        weather_report=weather_report.serialized(),
                        trail_report=trail_report.serialized(), )
                    final_mountains.append(mountain_dict)
                except APIError as e:
                    continue

            if (len(final_mountains) > 0):
                context = dict(mountains=final_mountains)  
                return render(request,
                              'mountains/mountain_results.html',
                              context)
            else :
                context=dict(errors=dict(no_results=True),
                             api_key=settings.GOOGLE_MAPS_API_KEY)
                return render(request,
                               'users/user_location.html',
                               context)
        else:
            errors = form.errors.as_data()
            return render(request,
                          'users/user_location.html',
                          dict(errors=errors, 
                               api_key=settings.GOOGLE_MAPS_API_KEY))
