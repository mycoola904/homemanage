from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from households.models import Household, HouseholdMember


User = get_user_model()


class AdminUserCreationSettingsTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_superuser("user-admin", "user-admin@example.com", "pass-1234")
        self.create_url = reverse("household:settings-users-create")
        self.household_one = Household.objects.create(name="Maple Home", slug="maple-home", created_by=self.admin)
        self.household_two = Household.objects.create(name="Cedar Home", slug="cedar-home", created_by=self.admin)

    def test_admin_can_create_user_with_multiple_households(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            self.create_url,
            {
                "username": "newperson",
                "email": "newperson@example.com",
                "password": "Strong-pass-123",
                "household_ids": [str(self.household_one.id), str(self.household_two.id)],
            },
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        created = User.objects.get(username="newperson")
        self.assertTrue(created.check_password("Strong-pass-123"))
        memberships = HouseholdMember.objects.filter(user=created)
        self.assertEqual(memberships.count(), 2)
        self.assertEqual(
            set(str(membership.household_id) for membership in memberships),
            {str(self.household_one.id), str(self.household_two.id)},
        )
        self.assertContains(response, 'id="settings-user-panel"')
        self.assertContains(response, "newperson")

    def test_user_create_normalizes_email_input(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            self.create_url,
            {
                "username": "normalize-me",
                "email": "  MixedCase@Example.COM  ",
                "password": "Strong-pass-123",
                "household_ids": [str(self.household_one.id)],
            },
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 200)
        created = User.objects.get(username="normalize-me")
        self.assertEqual(created.email, "mixedcase@example.com")

    def test_user_create_rejects_duplicate_username_or_email(self):
        User.objects.create_user("dupuser", "dup@example.com", "pass-1234")
        self.client.force_login(self.admin)

        duplicate_username_response = self.client.post(
            self.create_url,
            {
                "username": "dupuser",
                "email": "different@example.com",
                "password": "Strong-pass-123",
                "household_ids": [str(self.household_one.id)],
            },
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(duplicate_username_response.status_code, 400)
        self.assertContains(duplicate_username_response, "Username already exists", status_code=400)

        duplicate_email_response = self.client.post(
            self.create_url,
            {
                "username": "different-user",
                "email": "DUP@example.com",
                "password": "Strong-pass-123",
                "household_ids": [str(self.household_one.id)],
            },
            HTTP_HX_REQUEST="true",
        )
        self.assertEqual(duplicate_email_response.status_code, 400)
        self.assertContains(duplicate_email_response, "Email already exists", status_code=400)

    def test_user_create_rejects_weak_password(self):
        self.client.force_login(self.admin)

        response = self.client.post(
            self.create_url,
            {
                "username": "weakpass",
                "email": "weakpass@example.com",
                "password": "12345",
                "household_ids": [str(self.household_one.id)],
            },
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 400)
        self.assertContains(response, "This password", status_code=400)

    def test_user_create_blocked_when_no_households_exist(self):
        Household.objects.all().delete()
        self.client.force_login(self.admin)

        response = self.client.post(
            self.create_url,
            {
                "username": "blocked-user",
                "email": "blocked@example.com",
                "password": "Strong-pass-123",
                "household_ids": [],
            },
            HTTP_HX_REQUEST="true",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(User.objects.filter(username="blocked-user").exists())
        self.assertContains(response, "Create a household before creating user accounts", status_code=400)
