from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from households.models import Household


User = get_user_model()


class AdminHouseholdSettingsTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser("house-admin", "house-admin@example.com", "pass-1234")
        self.create_url = reverse("household:settings-households-create")

    def test_admin_can_create_household_from_settings(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            self.create_url,
            {"name": "River House"},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Household.objects.filter(name="River House").count(), 1)
        self.assertContains(response, 'id="settings-household-panel"')
        self.assertContains(response, "River House")

    def test_household_create_requires_name(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            self.create_url,
            {"name": "   "},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Household.objects.count(), 0)
        self.assertContains(response, "This field is required.", status_code=400)

    def test_household_create_rejects_normalized_duplicate_name(self):
        Household.objects.create(name="Sunny Home", slug="sunny-home", created_by=self.admin)
        self.client.force_login(self.admin)

        response = self.client.post(
            self.create_url,
            {"name": "  sunny   HOME  "},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Household.objects.count(), 1)
        self.assertContains(response, "already exists", status_code=400)
