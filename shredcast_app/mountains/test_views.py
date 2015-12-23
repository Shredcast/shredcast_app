from django.test import TestCase, Client

from mountains.models import Mountain, SnowReport, WeatherReport, TrailReport
from users.models import UserLocation


class TestMountainResultsView(TestCase):
    """Test the UserLocationView."""

    def setUp(self):
        self.client = Client()

    def test_mountain_results_view_errors_without_address(self):
        """The UserLocationView should redirect to itself if no address.

           If the user fails to provide an address to the UserLocationView,
           it should redirect to itself with error notifications.
        """
        request_data = dict(
            drive_time='5',
            going_today='True', )

        response = self.client.get('/results/', request_data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('address', response.context['errors'])
        templates_used = [template.name for template in response.templates]
        self.assertIn('users/user_location.html', templates_used)

    def test_mountain_results_view_errors_without_drive_time(self):
        """The UserLocationView should redirect to itself if no drive_time.

           If the user fails to provide a drive_time to the UserLocationView,
           it should redirect to itself with error notifications.
        """
        request_data = dict(
            address='5421 Ora Street, San Jose, CA 95129',
            going_today='True', )

        response = self.client.get('/results/', request_data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('drive_time', response.context['errors'])
        templates_used = [template.name for template in response.templates]
        self.assertIn('users/user_location.html', templates_used)

    def test_mountain_results_view_errors_with_bad_address(self):
        """The UserLocationView should redirect to itself if bad address given.

           If the user fails to provide a valid address (checked via Google),
           it should redirect to itself with error notifications.
        """
        request_data = dict(
            address='5421',
            drive_time='5',
            going_today='True', )

        response = self.client.get('/results/', request_data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('address', response.context['errors'])
        templates_used = [template.name for template in response.templates]
        self.assertIn('users/user_location.html', templates_used)

    def test_mountain_results_view_handles_no_results(self):
        """The UserLocationView should redirect to itself if no mountains are found."""
        request_data = dict(
            address='5421 Ora Street, San Jose, CA 95129',
            drive_time='1',
            going_today='False', )

        response = self.client.get('/results/', request_data)

        self.assertEqual(response.status_code, 200)
        self.assertIn('no_results', response.context['errors'])
        templates_used = [template.name for template in response.templates]
        self.assertIn('users/user_location.html', templates_used)

    def test_mountain_results_view_creates_user_location(self):
        """Upon hitting the UserLocationView, a UserLocation model is created.
        """
        user_locations = UserLocation.objects.all()
        self.assertEqual(user_locations.count(), 0)

        request_data = dict(
            address='5421 Ora Street, San Jose, CA 95129',
            drive_time='5',
            going_today='False', )

        response = self.client.get('/results/', request_data)

        self.assertEqual(response.status_code, 200)
        user_locations = UserLocation.objects.all()
        self.assertEqual(user_locations.count(), 1)

    def test_mountain_results_view_returns_mountains_properly(self):
        """Docstring here. Make sure mountains are returned as the template expects them."""
        pass

    def test_mountain_results_view_returns_at_most_10_mountains(self):
        """Docstring here."""
        pass

    def test_mountain_results_view_returns_10_best_mountains(self):
        """Docstring here. Basically, test that 10 mountains returned have best shred scores."""
        pass
