from django.test import TestCase

from users.forms import UserLocationForm
from users.models import UserLocation


class TestUserLocationForm(TestCase):
    """Test the UserLocationForm."""

    def setUp(self):
        pass

    def test_form_errors_without_address(self):
        """The form should error without a provided address."""
        form_data = dict(drive_time='4', going_today='True')
        form = UserLocationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('address', form.errors.as_data())

    def test_form_errors_with_bad_address(self):
        """The form should error when provided an invalid address."""
        form_data = dict(drive_time='4', going_today='True', address='5421')
        form = UserLocationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('address', form.errors.as_data())

    def test_form_errors_without_drive_time(self):
        """The form should error without a provided drive time."""
        form_data = dict(address='San Jose, CA 95129', going_today='False')
        form = UserLocationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('drive_time', form.errors.as_data())

    def test_form_defaults_going_today_to_false(self):
        """The form should default going_today to false if not given."""
        form_data = dict(address='San Jose, CA 95129', drive_time='2')
        form = UserLocationForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.assertFalse(form.cleaned_data['going_today'])

    def test_form_save_creates_user_location(self):
        """The saving of a valid form should create a new UserLocation."""
        self.assertEqual(UserLocation.objects.all().count(), 0)
        form_data = dict(address='San Jose, CA 95129', going_today='True', drive_time='3')
        form = UserLocationForm(data=form_data)
        self.assertTrue(form.is_valid())
        form.save()
        self.assertEqual(UserLocation.objects.all().count(), 1)
        new_user_location = UserLocation.objects.all()[0]
        self.assertEqual(new_user_location.address, 'San Jose, CA 95129')
        self.assertEqual(new_user_location.going_today, True)
        self.assertEqual(new_user_location.drive_time, 3)
