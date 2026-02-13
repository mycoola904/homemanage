from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from financial.models import Account, AccountStatus, AccountType
from households.models import Household, HouseholdMember


User = get_user_model()


class AccountsIndexViewTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(
            username="alex",
            email="alex@example.com",
            password="complex-pass-123",
        )
        self.household = Household.objects.create(
            name="Alex Household",
            slug="alex-household",
            created_by=self.user,
        )
        HouseholdMember.objects.create(
            household=self.household,
            user=self.user,
            role=HouseholdMember.Role.OWNER,
            is_primary=True,
        )
        self.url = reverse("financial:accounts-index")

    def test_redirects_anonymous_users(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/auth/login/", response.headers["Location"])

    def test_lists_accounts_in_expected_order(self):
        Account.objects.create(
            user=self.user,
            household=self.household,
            name="Savings Reserve",
            institution="Civic",
            account_type=AccountType.SAVINGS,
            status=AccountStatus.ACTIVE,
            current_balance=1250,
        )
        Account.objects.create(
            user=self.user,
            household=self.household,
            name="Checking Everyday",
            institution="Metro",
            account_type=AccountType.CHECKING,
            status=AccountStatus.ACTIVE,
            current_balance=255.30,
        )
        Account.objects.create(
            user=self.user,
            household=self.household,
            name="Loan Refi",
            institution="Metro",
            account_type=AccountType.LOAN,
            status=AccountStatus.PENDING,
            current_balance=-15000,
        )

        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        rows = response.context["account_rows"]
        self.assertEqual([row.name for row in rows], [
            "Checking Everyday",
            "Savings Reserve",
            "Loan Refi",
        ])
        self.assertTrue(response.context["has_accounts"])  # Spec FR-013 full dataset
        self.assertContains(response, "Preview")
        self.assertContains(response, "Open")
        self.assertContains(response, "Edit")
        self.assertContains(response, "Delete")

    def test_empty_state_includes_cta(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No accounts yet")
        self.assertContains(response, "Add Account")
        self.assertContains(response, reverse("financial:accounts-new"))
        self.assertFalse(response.context["has_accounts"])
