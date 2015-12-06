from django.shortcuts import render
from django.views.generic import View

from django.conf import settings

class UserLocationView(View):
    """Get user location and drive time."""

    def get(self, request, *args, **kwargs):
        return render(request, 
                      'users/user_location.html',
                      dict(api_key=settings.GOOGLE_MAPS_API_KEY))
