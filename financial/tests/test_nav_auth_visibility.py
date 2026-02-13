from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from households.models import Household, HouseholdMember


User = get_user_model()


class NavAuthVisibilityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("nav-user", "nav-user@example.com", "pass-1234")
        self.admin = User.objects.create_superuser("nav-admin", "nav-admin@example.com", "pass-1234")
        self.household = Household.objects.create(name="Nav Household", slug="nav-household", created_by=self.user)
        HouseholdMember.objects.create(
            household=self.household,
            user=self.user,
            role=HouseholdMember.Role.OWNER,
            is_primary=True,
        )
        HouseholdMember.objects.create(
            household=self.household,
            user=self.admin,
            role=HouseholdMember.Role.ADMIN,
            is_primary=True,
        )

    def test_anonymous_nav_shows_login_and_hides_modules(self):
        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Login")
        self.assertNotContains(response, "Finance")
        self.assertNotContains(response, "Settings")

    def test_authenticated_non_admin_nav_hides_login_and_settings(self):
        self.client.force_login(self.user)

        response = self.client.get(reverse("household:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Finance")
        self.assertNotContains(response, "Login")
        self.assertNotContains(response, "Settings")

    def test_authenticated_user_without_household_hides_finance(self):
        no_household_user = User.objects.create_user("no-household", "no-household@example.com", "pass-1234")
        self.client.force_login(no_household_user)

        response = self.client.get(reverse("home"))

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Finance")
        self.assertNotContains(response, "Settings")
        self.assertNotContains(response, "Login")

    def test_authenticated_admin_nav_shows_settings(self):
        self.client.force_login(self.admin)

        response = self.client.get(reverse("household:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Settings")
        self.assertNotContains(response, "Login")

    def test_anonymous_users_redirect_to_login_for_finance_route(self):
        url = reverse("financial:accounts-index")

        response = self.client.get(url)

        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={url}", fetch_redirect_response=False)

    def test_anonymous_users_redirect_to_login_for_household_module_routes(self):
        routes = [
            reverse("household:home"),
            reverse("household:no-household-access"),
            reverse("household:settings-index"),
        ]

        for route in routes:
            with self.subTest(route=route):
                response = self.client.get(route)
                self.assertEqual(response.status_code, 302)
                self.assertRedirects(response, f"{reverse('login')}?next={route}", fetch_redirect_response=False)
