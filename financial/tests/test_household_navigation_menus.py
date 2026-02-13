from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from financial.models import Household, HouseholdMember


User = get_user_model()


class HouseholdNavigationMenusTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("menuuser", "menuuser@example.com", "pass-1234")
        self.household = Household.objects.create(name="Menu Household", slug="menu-household", created_by=self.user)
        HouseholdMember.objects.create(
            household=self.household,
            user=self.user,
            role=HouseholdMember.Role.OWNER,
            is_primary=True,
        )

    def test_household_namespace_renders_finance_entry(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("household:home"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Household Home")
        self.assertContains(response, "Finance")

    def test_financial_namespace_renders_accounts_menu_entry(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse("financial:accounts-index"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Accounts")
