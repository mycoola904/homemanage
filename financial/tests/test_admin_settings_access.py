from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from households.models import Household, HouseholdMember


User = get_user_model()


class AdminSettingsAccessTests(TestCase):
    def setUp(self):
        self.member = User.objects.create_user("member", "member@example.com", "pass-1234")
        self.admin = User.objects.create_superuser("settings-admin", "settings-admin@example.com", "pass-1234")
        self.target_user = User.objects.create_user("target", "target@example.com", "pass-1234")

        self.household = Household.objects.create(name="Settings Home", slug="settings-home", created_by=self.admin)
        HouseholdMember.objects.create(
            household=self.household,
            user=self.member,
            role=HouseholdMember.Role.MEMBER,
            is_primary=True,
        )
        HouseholdMember.objects.create(
            household=self.household,
            user=self.admin,
            role=HouseholdMember.Role.ADMIN,
            is_primary=True,
        )

        self.settings_index_url = reverse("household:settings-index")
        self.settings_household_create_url = reverse("household:settings-households-create")
        self.settings_user_create_url = reverse("household:settings-users-create")
        self.settings_membership_add_url = reverse(
            "household:settings-memberships-add",
            kwargs={"household_id": self.household.id},
        )
        self.settings_membership_remove_url = reverse(
            "household:settings-memberships-remove",
            kwargs={"household_id": self.household.id, "user_id": self.target_user.id},
        )

    def test_settings_requires_login_for_anonymous_users(self):
        response = self.client.get(self.settings_index_url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(
            response,
            f"{reverse('login')}?next={self.settings_index_url}",
            fetch_redirect_response=False,
        )

    def test_settings_forbids_authenticated_non_admin_user(self):
        self.client.force_login(self.member)

        response = self.client.get(self.settings_index_url)

        self.assertEqual(response.status_code, 403)

    def test_settings_index_allows_admin(self):
        self.client.force_login(self.admin)

        response = self.client.get(self.settings_index_url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Settings")

    def test_settings_mutation_endpoints_forbid_authenticated_non_admin_user(self):
        self.client.force_login(self.member)
        endpoint_cases = [
            (self.settings_household_create_url, {"name": "Another Household"}),
            (
                self.settings_user_create_url,
                {
                    "username": "new-user",
                    "email": "new-user@example.com",
                    "password": "pass-1234",
                    "household_ids": [str(self.household.id)],
                },
            ),
            (self.settings_membership_add_url, {"user_id": self.target_user.id, "role": "member"}),
            (self.settings_membership_remove_url, {}),
        ]

        for url, payload in endpoint_cases:
            with self.subTest(url=url):
                response = self.client.post(url, payload)
                self.assertEqual(response.status_code, 403)

    def test_settings_mutation_endpoints_require_login_for_anonymous_users(self):
        endpoint_cases = [
            (self.settings_household_create_url, {"name": "Another Household"}),
            (
                self.settings_user_create_url,
                {
                    "username": "new-user",
                    "email": "new-user@example.com",
                    "password": "pass-1234",
                    "household_ids": [str(self.household.id)],
                },
            ),
            (self.settings_membership_add_url, {"user_id": self.target_user.id, "role": "member"}),
            (self.settings_membership_remove_url, {}),
        ]

        for url, payload in endpoint_cases:
            with self.subTest(url=url):
                response = self.client.post(url, payload)
                self.assertEqual(response.status_code, 302)
                self.assertRedirects(
                    response,
                    f"{reverse('login')}?next={url}",
                    fetch_redirect_response=False,
                )

    def test_settings_mutation_endpoints_accept_admin_auth(self):
        self.client.force_login(self.admin)
        endpoint_cases = [
            (self.settings_household_create_url, {"name": "Another Household"}),
            (
                self.settings_user_create_url,
                {
                    "username": "new-user",
                    "email": "new-user@example.com",
                    "password": "pass-1234",
                    "household_ids": [str(self.household.id)],
                },
            ),
            (self.settings_membership_add_url, {"user_id": self.target_user.id, "role": "member"}),
            (self.settings_membership_remove_url, {}),
        ]

        for url, payload in endpoint_cases:
            with self.subTest(url=url):
                response = self.client.post(url, payload)
                self.assertNotEqual(response.status_code, 403)
