from django.test import TestCase

from mountains.models import Mountain
from users.models import UserLocation


class TestUserLocationModel(TestCase):
    """Test the creation and methods of the UserLocationModel."""

    def setUp(self):
        self.user_location = UserLocation.objects.create(
            '5421 Ora Street, San Jose, CA 95129',
            '20',
            False, )
        self.mountain_one, created = Mountain.objects.get_or_create(
            name='Alta',
            address=('Highway 210, Little Cottonwood Canyon, Alta, UT 84092,'
                'United States'),
            latitude=40.590829,
            longitude=-111.62877,
            google_place_id='4dbc30f34f550cc50cb8c4c212f1dc13f833543f',
            snocountry_id='801001', )
        self.mountain_two, created = Mountain.objects.get_or_create(
            name='Killington Mountain Resort',
            address='Killington Peak, Mendon, VT 05701 United States',
            latitude=43.6647,
            longitude=72.7933,
            google_place_id='4dbc30f34f550cc50cb8c4c212f1dc13f833543f',
            snocountry_id='801001', )

        mountains_in_radius = self.user_location.get_mountains_in_radius()
        self.assertEqual(len(mountains_in_radius), 1) # Chamonix is not a 20 hour drive from CA
        self.assertEqual(mountains_in_radius[0].name, self.mountain_one.name)

    def test_creation_gets_lat_long(self):
        """Every UserLocation model should have a lat/long on creation.

        When UserLocation models are created using an address, that address
        should be used to get a latitude and longitude for that UserLocation.
        """
        self.assertEqual(UserLocation.objects.all().count(), 1)
        UserLocation.objects.create(
            '5421 Ora Street, San Jose, CA 95129', 
            '6', 
            False, )
        self.assertEqual(UserLocation.objects.all().count(), 2)
        new_location = UserLocation.objects.filter(drive_time=6)[0]
        self.assertIs(type(new_location.latitude), float)
        self.assertIs(type(new_location.longitude), float)

    def test_get_mountains_in_radius(self):
        """Return the mountain(s) within a conservative radius of this."""
        mountains_in_radius = self.user_location.get_mountains_in_radius()
        self.assertEqual(len(mountains_in_radius), 1) # Killington is not a 20 hour drive from CA
        self.assertEqual(mountains_in_radius[0].name, self.mountain_one.name)

    def test_is_mountain_in_range(self):
        """The UserLocation model should tell if a Mountain is within its drive_time.
        
        @TODO: find a way to not use the Google Maps API for this.
        """
        self.assertTrue(self.user_location.is_mountain_in_range(self.mountain_one))
        self.assertFalse(self.user_location.is_mountain_in_range(self.mountain_two))
