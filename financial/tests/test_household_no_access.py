from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


User = get_user_model()


class HouseholdNoAccessTests(TestCase):
    def test_household_home_redirects_to_no_access_for_user_without_memberships(self):
        user = User.objects.create_user("nomember", "nomember@example.com", "pass-1234")
        self.client.force_login(user)

        response = self.client.get(reverse("household:home"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], reverse("household:no-household-access"))

    def test_no_access_page_returns_403(self):
        user = User.objects.create_user("nomember2", "nomember2@example.com", "pass-1234")
        self.client.force_login(user)

        response = self.client.get(reverse("household:no-household-access"))

        self.assertEqual(response.status_code, 403)
        self.assertContains(response, "No household access", status_code=403)
