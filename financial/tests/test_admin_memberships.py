from uuid import uuid4

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from households.models import Household, HouseholdMember


User = get_user_model()


class AdminMembershipSettingsTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser("membership-admin", "membership-admin@example.com", "pass-1234")
        self.member_user = User.objects.create_user("member-user", "member-user@example.com", "pass-1234")
        self.owner_user = User.objects.create_user("owner-user", "owner-user@example.com", "pass-1234")

        self.household = Household.objects.create(name="Membership Home", slug="membership-home", created_by=self.admin)
        HouseholdMember.objects.create(
            household=self.household,
            user=self.owner_user,
            role=HouseholdMember.Role.OWNER,
            is_primary=True,
        )

        self.add_url = reverse(
            "household:settings-memberships-add",
            kwargs={"household_id": self.household.id},
        )

    def test_admin_can_add_membership_and_duplicate_add_is_idempotent(self):
        self.client.force_login(self.admin)

        first_response = self.client.post(
            self.add_url,
            {"user_id": self.member_user.id, "role": HouseholdMember.Role.MEMBER},
            HTTP_HX_REQUEST="true",
        )
        second_response = self.client.post(
            self.add_url,
            {"user_id": self.member_user.id, "role": HouseholdMember.Role.MEMBER},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 200)
        self.assertEqual(
            HouseholdMember.objects.filter(household=self.household, user=self.member_user).count(),
            1,
        )
        self.assertContains(second_response, 'id="settings-membership-panel"')

    def test_admin_can_remove_membership_and_remove_absent_is_idempotent(self):
        HouseholdMember.objects.create(
            household=self.household,
            user=self.member_user,
            role=HouseholdMember.Role.MEMBER,
        )
        remove_url = reverse(
            "household:settings-memberships-remove",
            kwargs={"household_id": self.household.id, "user_id": self.member_user.id},
        )
        self.client.force_login(self.admin)

        first_response = self.client.post(remove_url, HTTP_HX_REQUEST="true")
        second_response = self.client.post(remove_url, HTTP_HX_REQUEST="true")

        self.assertEqual(first_response.status_code, 200)
        self.assertEqual(second_response.status_code, 200)
        self.assertFalse(HouseholdMember.objects.filter(household=self.household, user=self.member_user).exists())

    def test_membership_add_rejects_unknown_user_or_unknown_household(self):
        self.client.force_login(self.admin)

        unknown_user_response = self.client.post(
            self.add_url,
            {"user_id": 999999, "role": HouseholdMember.Role.MEMBER},
            HTTP_HX_REQUEST="true",
        )
        unknown_household_url = reverse(
            "household:settings-memberships-add",
            kwargs={"household_id": uuid4()},
        )
        unknown_household_response = self.client.post(
            unknown_household_url,
            {"user_id": self.member_user.id, "role": HouseholdMember.Role.MEMBER},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(unknown_user_response.status_code, 400)
        self.assertContains(unknown_user_response, "Selected user does not exist", status_code=400)
        self.assertEqual(unknown_household_response.status_code, 400)
        self.assertContains(unknown_household_response, "Household not found", status_code=400)

    def test_membership_remove_blocks_last_owner_removal(self):
        remove_owner_url = reverse(
            "household:settings-memberships-remove",
            kwargs={"household_id": self.household.id, "user_id": self.owner_user.id},
        )
        self.client.force_login(self.admin)

        response = self.client.post(remove_owner_url, HTTP_HX_REQUEST="true")

        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "must retain at least one owner", status_code=400)
        self.assertTrue(HouseholdMember.objects.filter(household=self.household, user=self.owner_user).exists())

    def test_membership_add_updates_role_without_duplicate_membership(self):
        HouseholdMember.objects.create(
            household=self.household,
            user=self.member_user,
            role=HouseholdMember.Role.MEMBER,
        )
        self.client.force_login(self.admin)

        response = self.client.post(
            self.add_url,
            {"user_id": self.member_user.id, "role": HouseholdMember.Role.ADMIN},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        membership = HouseholdMember.objects.get(household=self.household, user=self.member_user)
        self.assertEqual(membership.role, HouseholdMember.Role.ADMIN)
        self.assertEqual(HouseholdMember.objects.filter(household=self.household, user=self.member_user).count(), 1)

    def test_membership_add_rejects_non_integer_user_id(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            self.add_url,
            {"user_id": "not-a-number", "role": HouseholdMember.Role.MEMBER},
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "Enter a whole number", status_code=400)
