from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from financial.models import Account, AccountStatus, AccountType
from households.models import Household, HouseholdMember


User = get_user_model()


class BillPayIndexTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user("alex", "alex@example.com", "pass-1234")
        self.household = Household.objects.create(name="Alex Household", slug="alex-household", created_by=self.user)
        HouseholdMember.objects.create(
            household=self.household,
            user=self.user,
            role=HouseholdMember.Role.OWNER,
            is_primary=True,
        )
        self.url = reverse("financial:bill-pay-index")

    def test_requires_authentication(self):
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 302)
        self.assertIn("/auth/login/", response.headers["Location"])

    def test_filters_liability_accounts_and_sorts_due_day(self):
        Account.objects.create(
            user=self.user,
            household=self.household,
            name="Checking Household",
            institution="Civic",
            account_type=AccountType.CHECKING,
            status=AccountStatus.ACTIVE,
            current_balance=1200,
        )
        Account.objects.create(
            user=self.user,
            household=self.household,
            name="Card B",
            institution="Issuer",
            account_type=AccountType.CREDIT_CARD,
            status=AccountStatus.ACTIVE,
            current_balance=-200,
            payment_due_day=18,
            minimum_amount_due=30,
        )
        Account.objects.create(
            user=self.user,
            household=self.household,
            name="Loan A",
            institution="Lender",
            account_type=AccountType.LOAN,
            status=AccountStatus.ACTIVE,
            current_balance=4000,
            payment_due_day=5,
            minimum_amount_due=150,
        )
        Account.objects.create(
            user=self.user,
            household=self.household,
            name="Other C",
            institution="Utility",
            account_type=AccountType.OTHER,
            status=AccountStatus.ACTIVE,
            current_balance=80,
            payment_due_day=None,
            minimum_amount_due=20,
            online_access_url="https://utility.example/pay",
        )

        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        rows = response.context["rows"]
        self.assertEqual([row.name for row in rows], ["Loan A", "Card B", "Other C"])
        self.assertContains(response, "Bill Pay")
        self.assertContains(response, "https://utility.example/pay")

    def test_url_empty_state_renders_dash(self):
        Account.objects.create(
            user=self.user,
            household=self.household,
            name="Loan No URL",
            institution="Lender",
            account_type=AccountType.LOAN,
            status=AccountStatus.ACTIVE,
            current_balance=1500,
            payment_due_day=12,
            minimum_amount_due=45,
        )

        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Loan No URL")
        self.assertContains(response, "—")

    def test_fast_mode_toggle_defaults_off_on_initial_load(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="bill-pay-fast-mode"')
        self.assertNotContains(response, 'id="bill-pay-fast-mode" type="checkbox" class="checkbox checkbox-sm" checked')

    def test_fast_mode_inline_status_container_is_present(self):
        self.client.force_login(self.user)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'id="bill-pay-fast-mode-status"')
        self.assertContains(response, 'aria-live="polite"')
