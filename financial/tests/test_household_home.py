from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from households.models import Household, HouseholdMember


User = get_user_model()


class HouseholdHomeTests(TestCase):
    def test_household_home_renders_launcher(self):
        user = User.objects.create_user("homeuser", "homeuser@example.com", "pass-1234")
        household = Household.objects.create(name="Home Household", slug="home-household", created_by=user)
        HouseholdMember.objects.create(
            household=household,
            user=user,
            role=HouseholdMember.Role.OWNER,
            is_primary=True,
        )

        self.client.force_login(user)
        response = self.client.get(reverse("household:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Household")
        self.assertContains(response, "Finance")
