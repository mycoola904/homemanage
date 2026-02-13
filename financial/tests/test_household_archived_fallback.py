from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from financial.models import Household, HouseholdMember


User = get_user_model()


class HouseholdArchivedFallbackTests(TestCase):
    def test_archived_session_household_falls_back_to_active_membership(self):
        user = User.objects.create_user("archived", "archived@example.com", "pass-1234")
        archived_household = Household.objects.create(
            name="Archived Household",
            slug="archived-household",
            is_archived=True,
            created_by=user,
        )
        active_household = Household.objects.create(
            name="Active Household",
            slug="active-household",
            created_by=user,
        )
        HouseholdMember.objects.create(
            household=archived_household,
            user=user,
            role=HouseholdMember.Role.OWNER,
            is_primary=True,
        )
        HouseholdMember.objects.create(
            household=active_household,
            user=user,
            role=HouseholdMember.Role.OWNER,
            is_primary=False,
        )

        self.client.force_login(user)
        session = self.client.session
        session["current_household_id"] = str(archived_household.id)
        session.save()

        response = self.client.get(reverse("household:home"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.session.get("current_household_id"), str(active_household.id))

    def test_all_archived_memberships_redirect_to_no_access(self):
        user = User.objects.create_user("onlyarchived", "onlyarchived@example.com", "pass-1234")
        archived_household = Household.objects.create(
            name="Archived Only Household",
            slug="archived-only-household",
            is_archived=True,
            created_by=user,
        )
        HouseholdMember.objects.create(
            household=archived_household,
            user=user,
            role=HouseholdMember.Role.OWNER,
            is_primary=True,
        )

        self.client.force_login(user)
        response = self.client.get(reverse("household:home"))

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.headers["Location"], reverse("household:no-household-access"))
