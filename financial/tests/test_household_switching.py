from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from financial.models import Household, HouseholdMember


User = get_user_model()


class HouseholdSwitchingTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("switcher", "switcher@example.com", "pass-1234")
        self.household_a = Household.objects.create(name="A Household", slug="a-household", created_by=self.user)
        self.household_b = Household.objects.create(name="B Household", slug="b-household", created_by=self.user)
        HouseholdMember.objects.create(
            household=self.household_a,
            user=self.user,
            role=HouseholdMember.Role.OWNER,
            is_primary=True,
        )
        HouseholdMember.objects.create(
            household=self.household_b,
            user=self.user,
            role=HouseholdMember.Role.OWNER,
            is_primary=False,
        )

    def test_switch_updates_session_and_redirects_home(self):
        self.client.force_login(self.user)
        response = self.client.post(reverse("household:switch"), {"household_id": str(self.household_b.id)})

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], reverse("household:home"))
        self.assertEqual(self.client.session.get("current_household_id"), str(self.household_b.id))

    def test_switch_to_non_member_returns_403(self):
        outsider = User.objects.create_user("outsider", "outsider@example.com", "pass-1234")
        outsider_household = Household.objects.create(name="Outsider", slug="outsider", created_by=outsider)

        self.client.force_login(self.user)
        response = self.client.post(reverse("household:switch"), {"household_id": str(outsider_household.id)})

        self.assertEqual(response.status_code, 403)
