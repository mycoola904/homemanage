from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from financial.models import Household, HouseholdMember


User = get_user_model()


class HouseholdLoginSelectionTests(TestCase):
    def _create_membership(self, *, user, household_name, slug, is_primary):
        household = Household.objects.create(name=household_name, slug=slug, created_by=user)
        HouseholdMember.objects.create(
            household=household,
            user=user,
            role=HouseholdMember.Role.OWNER,
            is_primary=is_primary,
        )
        return household

    def test_login_selects_single_membership_household(self):
        user = User.objects.create_user("single", "single@example.com", "pass-1234")
        household = self._create_membership(
            user=user,
            household_name="Single Household",
            slug="single-household",
            is_primary=True,
        )

        response = self.client.post(
            reverse("login"),
            {"username": "single", "password": "pass-1234"},
            follow=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session.get("current_household_id"), str(household.id))

    def test_login_prefers_primary_membership(self):
        user = User.objects.create_user("primary", "primary@example.com", "pass-1234")
        fallback = self._create_membership(
            user=user,
            household_name="Fallback Household",
            slug="fallback-household",
            is_primary=False,
        )
        primary = self._create_membership(
            user=user,
            household_name="Primary Household",
            slug="primary-household",
            is_primary=True,
        )

        self.client.post(
            reverse("login"),
            {"username": "primary", "password": "pass-1234"},
            follow=True,
        )

        self.assertNotEqual(str(fallback.id), str(primary.id))
        self.assertEqual(self.client.session.get("current_household_id"), str(primary.id))

    def test_login_falls_back_to_first_deterministic_membership(self):
        user = User.objects.create_user("fallback", "fallback@example.com", "pass-1234")
        first = self._create_membership(
            user=user,
            household_name="First Household",
            slug="first-household",
            is_primary=False,
        )
        self._create_membership(
            user=user,
            household_name="Second Household",
            slug="second-household",
            is_primary=False,
        )

        self.client.post(
            reverse("login"),
            {"username": "fallback", "password": "pass-1234"},
            follow=True,
        )

        self.assertEqual(self.client.session.get("current_household_id"), str(first.id))
