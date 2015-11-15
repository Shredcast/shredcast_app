from django.shortcuts import render
from django.views.generic import View

from django.conf import settings



class UserLocationView(View):
    """Get user location and drive time."""

    def get(self, request, *args, **kwargs):
        return render(request, 
                      'mountains/user_location.html',
                      {'api_key': settings.GOOGLE_MAPS_API_KEY})


class MountainResultsView(View):
    """Return best mountains for the user based on location and drive time."""

    def get(self, request, *args, **kwargs):
        
        
        return render(request,
                      'mountains/mountain_results.html',
                      {'request': request})
